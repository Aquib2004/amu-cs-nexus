import ssl

import pytest

from app.core.tls import describe_tls, tls_context


def test_tls_context_always_verifies_certificates() -> None:
    """Verification must never be weakened by the AMU trust-store workaround."""
    context = tls_context()
    assert context.verify_mode == ssl.CERT_REQUIRED
    assert context.check_hostname is True


def test_tls_context_is_reusable_and_stable() -> None:
    first = tls_context()
    second = tls_context()
    assert isinstance(first, ssl.SSLContext)
    assert isinstance(second, ssl.SSLContext)
    assert first.verify_mode == ssl.CERT_REQUIRED


def test_describe_tls_returns_a_known_trust_store() -> None:
    assert describe_tls() in {"platform", "certifi", "system"}


def test_unknown_trust_store_falls_back_safely(monkeypatch) -> None:
    """A typo in AMU_TLS_TRUST must not silently disable verification."""
    from app.core import config, tls

    monkeypatch.setattr(config.settings, "tls_trust", "not-a-store")
    context = tls.tls_context()
    assert context.verify_mode == ssl.CERT_REQUIRED
    assert context.check_hostname is True


def test_certifi_mode_still_verifies(monkeypatch) -> None:
    """The opt-out bundle path must also keep verification enabled."""
    from app.core import config

    monkeypatch.setattr(config.settings, "tls_trust", "certifi")
    context = tls_context()
    assert context.verify_mode == ssl.CERT_REQUIRED
    assert context.check_hostname is True


def test_no_module_disables_tls_verification() -> None:
    """Guard against a future regression back to verify=False."""
    from pathlib import Path

    import app

    root = Path(app.__file__).resolve().parents[2]
    offenders: list[str] = []
    for folder in ("app",):
        for path in (root / folder).rglob("*.py"):
            text = path.read_text(encoding="utf-8", errors="ignore")
            if "verify=False" in text or "verify = False" in text:
                offenders.append(str(path.relative_to(root)))
    assert not offenders, f"TLS verification disabled in: {offenders}"
