"""Anonymous, opt-in Web Push delivery for newly ingested AMU notices."""

import json
import logging
from datetime import datetime, timezone
from pathlib import Path

from pywebpush import WebPushException, webpush
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.notice import Notice
from app.models.push_subscription import PushSubscription

logger = logging.getLogger(__name__)


def _private_key() -> str | None:
    if settings.vapid_private_key:
        return settings.vapid_private_key
    if settings.vapid_private_key_file:
        try:
            return Path(settings.vapid_private_key_file).read_text(encoding="utf-8")
        except OSError:
            logger.exception("VAPID private key file could not be read")
    return None


def push_enabled() -> bool:
    return bool(_private_key() and settings.vapid_public_key and settings.vapid_subject)


def upsert_subscription(
    session: Session,
    endpoint: str,
    p256dh: str,
    auth: str,
    user_agent: str | None = None,
) -> PushSubscription:
    row = session.scalar(select(PushSubscription).where(PushSubscription.endpoint == endpoint))
    if row is None:
        row = PushSubscription(endpoint=endpoint, p256dh=p256dh, auth=auth)
        session.add(row)
    row.p256dh = p256dh
    row.auth = auth
    row.user_agent = (user_agent or "")[:500] or None
    row.active = True
    row.failure_count = 0
    row.last_seen_at = datetime.now(timezone.utc)
    session.commit()
    return row


def delete_subscription(session: Session, subscription_id) -> bool:
    row = session.get(PushSubscription, subscription_id)
    if row is None:
        return False
    session.delete(row)
    session.commit()
    return True


def delete_subscription_by_endpoint(session: Session, endpoint: str) -> bool:
    row = session.scalar(select(PushSubscription).where(PushSubscription.endpoint == endpoint))
    if row is None:
        return False
    session.delete(row)
    session.commit()
    return True


def send_notice_notifications(session: Session, notices: list[Notice]) -> int:
    """Send one push per active subscription. Returns successful deliveries."""
    if not notices or not push_enabled():
        return 0
    subscriptions = list(session.scalars(select(PushSubscription).where(PushSubscription.active.is_(True))))
    sent = 0
    for subscription in subscriptions:
        ok = True
        for notice in notices[:10]:
            payload = json.dumps({
                "title": "New AMU CS notice",
                "body": notice.title[:240],
                "url": "/notices",
                "tag": f"amu-notice-{notice.id}",
            })
            try:
                webpush(
                    subscription_info={
                        "endpoint": subscription.endpoint,
                        "keys": {"p256dh": subscription.p256dh, "auth": subscription.auth},
                    },
                    data=payload,
                    vapid_private_key=_private_key(),
                    vapid_claims={"sub": settings.vapid_subject},
                    ttl=86400,
                )
                sent += 1
            except WebPushException as exc:
                status = getattr(getattr(exc, "response", None), "status_code", None)
                if status in (404, 410):
                    subscription.active = False
                    session.commit()
                    logger.info("Removed expired push subscription %s", subscription.id)
                    ok = False
                    break
                subscription.failure_count += 1
                if subscription.failure_count >= 5:
                    subscription.active = False
                ok = False
                logger.warning("Push delivery failed (%s): %s", status, exc)
            except Exception as exc:
                subscription.failure_count += 1
                ok = False
                logger.warning("Unexpected push delivery failure: %s", exc)
        if ok:
            subscription.failure_count = 0
            subscription.last_seen_at = datetime.now(timezone.utc)
    session.commit()
    return sent
