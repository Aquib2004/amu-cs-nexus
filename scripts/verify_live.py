#!/usr/bin/env python
r"""Verify a live AMUCS Nexus deployment end to end.

The site is served from one origin: FastAPI answers both the /api routes and
the static export. That removes the whole class of failure this script used to
chase - a CORS allowlist that never listed the frontend, a frontend behind
Vercel Deployment Protection, and a bundle built without NEXT_PUBLIC_API_URL.
There is no second origin now, so those three cannot happen.

What still can happen, and is invisible to a server-side health check:

  1. The API is up but its database probe fails.
  2. The export was never deployed (Render has no Node, so frontend/out is
     committed; if it goes missing the API still answers and the UI 404s).
  3. The frontend middleware shadows the API, so unknown routes stop returning
     JSON - the regression a mount caused and the backend tests caught.
  4. The shipped bundle still points at http://localhost:8000, which only
     fails for real visitors.

Usage:
    python scripts/verify_live.py
    python scripts/verify_live.py --api https://amucs-nexus-api.onrender.com

Exit status is 0 only when every check passes, so it is usable in CI.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import urllib.error
import urllib.request


class _NoRedirect(urllib.request.HTTPRedirectHandler):
    """Follow no redirects.

    urlopen follows 3xx automatically, so a service parked behind a login wall
    would hand back the login page as status 200 and look healthy. Seeing the
    redirect is the whole point of the check.
    """

    def redirect_request(self, req, fp, code, msg, headers, newurl):  # noqa: ANN001
        return None


_OPENER = urllib.request.build_opener(_NoRedirect)

DEFAULT_API = "https://amucs-nexus-api.onrender.com"
# No trailing slash: Vercel canonicalises /chat/ to /chat with a 308, and this
# script deliberately follows no redirects. /chat works on both origins.
DEFAULT_PAGE = "/chat"
TIMEOUT = 45


def _get(url: str, *, method: str = "GET", headers: dict[str, str] | None = None):
    """Return (status, response_headers, body_bytes). Never raises for HTTP codes."""
    request = urllib.request.Request(url, method=method, headers=headers or {})
    try:
        with _OPENER.open(request, timeout=TIMEOUT) as response:
            return response.status, dict(response.headers), response.read()
    except urllib.error.HTTPError as exc:  # 3xx/4xx/5xx are still informative
        return exc.code, dict(exc.headers or {}), exc.read()
    except urllib.error.URLError as exc:
        return 0, {}, str(exc.reason).encode("utf-8", "replace")


def _check(label: str, ok: bool, detail: str) -> bool:
    print(f"{'PASS' if ok else 'FAIL'}  {label}")
    if not ok:
        print(f"      -> {detail}")
    return ok


def main() -> int:
    parser = argparse.ArgumentParser(description="Verify a live AMUCS Nexus deployment.")
    parser.add_argument("--api", default=DEFAULT_API, help="Base URL the site is served from")
    parser.add_argument("--page", default=DEFAULT_PAGE, help="Nested route to check")
    args = parser.parse_args()

    api = args.api.rstrip("/")
    results: list[bool] = []

    # 1. Health, including the live database probe.
    status, _, body = _get(f"{api}/api/health")
    health: dict = {}
    try:
        health = json.loads(body.decode("utf-8"))
    except (ValueError, UnicodeDecodeError):
        pass
    ok = status == 200 and health.get("status") == "ok" and health.get("database") == "ok"
    results.append(_check("API health", ok, f"status={status} body={body[:200]!r}"))

    # 2. The homepage must come back as HTML from that same origin. A JSON body
    #    here means the export is not deployed and FastAPI is answering "/".
    status, _, body = _get(f"{api}/")
    is_html = b"<!doctype html>" in body[:300].lower() or b"<html" in body[:400].lower()
    detail = (
        "the API is serving / but the export is missing - frontend/out was not deployed"
        if status == 200 and not is_html
        else f"status={status} body={body[:160]!r}"
    )
    results.append(_check("Homepage served as HTML", status == 200 and is_html, detail))

    # 3. A nested route must resolve to its own index file. This is what proves
    #    the committed export is present, not just that something answers /.
    status, _, body = _get(f"{api}{args.page}")
    ok = status == 200 and b"<!doctype html>" in body[:300].lower()
    results.append(
        _check(f"Nested route {args.page} resolves", ok, f"status={status} body={body[:160]!r}")
    )

    # 4. The middleware must not own API paths: an unknown API route has to
    #    keep returning the JSON error shape, not the exported 404 page.
    status, _, body = _get(f"{api}/api/not-a-route")
    try:
        payload = json.loads(body.decode("utf-8"))
    except (ValueError, UnicodeDecodeError):
        payload = {}
    ok = status == 404 and isinstance(payload.get("detail"), str)
    results.append(
        _check(
            "Unknown API route still returns JSON 404",
            ok,
            f"status={status} body={body[:160]!r}",
        )
    )

    # 5. The shipped bundle must use the same-origin relative base. A localhost
    #    fallback only ever fails for real visitors, never for curl.
    status, _, body = _get(f"{api}/")
    if status == 200 and b"<!doctype html>" in body[:300].lower():
        chunk_urls = sorted(set(re.findall(rb"/_next/static/[A-Za-z0-9_/.-]+\.js", body)))[:12]
        leaked: str | None = None
        for url in chunk_urls:
            _, _, chunk = _get(api + url.decode("ascii", "ignore"))
            if b"localhost:8000" in chunk:
                leaked = url.decode("ascii", "ignore")
                break
        ok = bool(chunk_urls) and leaked is None
        detail = (
            f"bundle chunk {leaked} falls back to http://localhost:8000"
            if leaked
            else ("no bundle chunks found in the page" if not chunk_urls else "")
        )
        results.append(_check("Bundle uses the same-origin API base", ok, detail))
    else:
        results.append(
            _check("Bundle uses the same-origin API base", False, "skipped: homepage did not load")
        )

    print()
    passed = sum(results)
    print(f"{passed}/{len(results)} checks passed")
    if passed == len(results):
        print(f"Live: {api}")
    return 0 if passed == len(results) else 1


if __name__ == "__main__":
    sys.exit(main())
