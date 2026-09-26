from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.database import get_db
from app.schemas.notifications import (
    PushSubscriptionCreate,
    PushSubscriptionRead,
    SubscriptionDeleteResponse,
    VapidPublicKey,
)
from app.services.push import (
    delete_subscription,
    delete_subscription_by_endpoint,
    push_enabled,
    upsert_subscription,
)

router = APIRouter(prefix="/notifications", tags=["notifications"])


@router.get("/vapid-public-key", response_model=VapidPublicKey)
def vapid_public_key() -> VapidPublicKey:
    enabled = push_enabled()
    return VapidPublicKey(
        enabled=enabled,
        public_key=settings.vapid_public_key if enabled else None,
    )


@router.post("/subscriptions", response_model=PushSubscriptionRead, status_code=201)
def subscribe(
    payload: PushSubscriptionCreate,
    request: Request,
    db: Session = Depends(get_db),
) -> PushSubscriptionRead:
    if not push_enabled():
        raise HTTPException(status_code=503, detail="Browser notifications are not configured on this server")
    try:
        keys = payload.keys
        p256dh, auth = keys["p256dh"], keys["auth"]
        if not p256dh or not auth:
            raise KeyError
    except KeyError as exc:
        raise HTTPException(status_code=422, detail="Subscription keys must include p256dh and auth") from exc
    row = upsert_subscription(
        db,
        endpoint=str(payload.endpoint),
        p256dh=p256dh,
        auth=auth,
        user_agent=request.headers.get("user-agent"),
    )
    return PushSubscriptionRead.model_validate(row)


@router.delete("/subscriptions/by-endpoint", response_model=SubscriptionDeleteResponse)
def unsubscribe_by_endpoint(endpoint: str, db: Session = Depends(get_db)) -> SubscriptionDeleteResponse:
    if not delete_subscription_by_endpoint(db, endpoint):
        raise HTTPException(status_code=404, detail="Subscription not found")
    return SubscriptionDeleteResponse()


@router.delete("/subscriptions/{subscription_id}", response_model=SubscriptionDeleteResponse)
def unsubscribe(subscription_id, db: Session = Depends(get_db)) -> SubscriptionDeleteResponse:
    if not delete_subscription(db, subscription_id):
        raise HTTPException(status_code=404, detail="Subscription not found")
    return SubscriptionDeleteResponse()
