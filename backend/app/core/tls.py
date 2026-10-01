"""Shared TLS trust configuration for outbound HTTPS clients.

Why this module exists
----------------------
The official AMU API host (``api.amu.ac.in``) serves a certificate for
``*.amu.ac.in`` issued by the intermediate CA ``GlobalSign RSA OV SSL CA 2018``,
but the server does **not** send that intermediate in the TLS handshake. The
only remaining way to build a chain is to have the intermediate available
locally.

``certifi`` (httpx's default trust store) contains neither that intermediate nor
its root ``GlobalSign Root CA - R3``, so verification fails with OpenSSL error
20 ("unable to get local issuer certificate"). The Windows/macOS system trust
store *does* have the issuer, which is why the same request succeeds in a
browser and fails in Python.

The fix is to trust the **platform** store instead of the certifi bundle. This
keeps full certificate verification enabled -- it is the opposite of disabling
verification -- and avoids pinning a certificate that will expire.

This is never a licence to set ``verify=False``: an unverified TLS connection
would accept any MITM certificate. Set ``AMU_TLS_TRUST=certifi`` to opt out of
the platform store if a deployment genuinely needs the bundled roots.
"""

from __future__ import annotations

import logging
import ssl

from app.core.config import settings

logger = logging.getLogger(__name__)

# Trust-store selection:
#   "platform" (default) -> OS trust store, handles AMU's missing intermediate
#   "certifi"            -> pinned certifi bundle (previous behaviour)
#   "system"             -> Python default context (same as platform today)
_TRUST_STORES = {"platform", "certifi", "system"}


def _build_context() -> ssl.SSLContext:
    """Return an SSLContext with verification enabled and hostname checking on."""
    context = ssl.create_default_context()
    # These are the secure defaults; they are set explicitly so that no caller
    # path can silently weaken them.
    context.check_hostname = True
    context.verify_mode = ssl.CERT_REQUIRED
    return context


def tls_context() -> ssl.SSLContext:
    """Return the shared SSL context for outbound HTTPS.

    Verification is ALWAYS enabled. The returned context is safe to pass as
    ``verify=`` to httpx, requests, or any stdlib HTTPS caller.
    """
    mode = (settings.tls_trust or "platform").strip().lower()
    if mode not in _TRUST_STORES:
        logger.warning(
            "Unknown AMU_TLS_TRUST=%r; falling back to the platform trust store. "
            "Valid values: %s",
            mode,
            ", ".join(sorted(_TRUST_STORES)),
        )
        mode = "platform"

    if mode == "certifi":
        try:
            import certifi

            return ssl.create_default_context(cafile=certifi.where())
        except Exception:  # pragma: no cover - certifi ships with httpx
            logger.warning("certifi trust store unavailable; using the platform store.")
    return _build_context()


def describe_tls() -> str:
    """Return a short, log-safe description of the active trust store."""
    return (settings.tls_trust or "platform").strip().lower()
