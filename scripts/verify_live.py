#!/usr/bin/env python
r"""Verify a live AMUCS Nexus deployment end to end.

Checks the three things that are invisible until a real browser loads the page,
because each of them fails silently from the server's point of view:

  1. The API is up and its database probe passes.
  2. The API actually allowlists the frontend origin. A CORS misconfiguration
     still returns HTTP 200 to the server, so "the endpoint works" says nothing
     about whether a browser may read it.
  3. The frontend is publicly reachable (not behind Vercel Deployment
     Protection, which answers 302 to an SSO URL).
  4. The frontend bundle was built with NEXT_PUBLIC_API_URL. If the variable was
     missing at build time the client silently falls back to
     http://localhost:8000 and every request fails only for real visitors.

Usage:
    python scripts/verify_live.py
    python scripts/verify_live.py --api https://amucs-nexus-api.onrender.com \
        --frontend https://amu-cs-nexus-2dt6puysf-acme-c82b.vercel.app

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

    urlopen follows 3xx automatically, so a frontend parked behind a login wall
    would hand back the login page as status 200 and look healthy. Seeing the
    redirect is the whole point of the check.
    """

    def redirect_request(self, req, fp, code, msg, headers, newurl):  # noqa: ANN001
        return None


_OPENER = urllib.request.build_opener(_NoRedirect)

DEFAULT_API = "https://amucs-nexus-api.onrender.com"
DEFAULT_FRONTEND = "https://amu-cs-nexus-2dt6puysf-acme-c82b.vercel.app"
DEFAULT_API_HOST = "amucs-nexus-api.onrender.com"
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
    parser.add_argument("--api", default=DEFAULT_API, help="API base URL")
    parser.add_argument("--frontend", default=DEFAULT_FRONTEND, help="Frontend base URL")
    args = parser.parse_args()

    api = args.api.rstrip("/")
    frontend = args.frontend.rstrip("/")
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

    # 2. Preflight from the real frontend origin. 200 alone is not enough: the
    #    allowed-origin header is what the browser actually inspects.
    status, headers, _ = _get(
        f"{api}/api/search",
        method="OPTIONS",
        headers={
            "Origin": frontend,
            "Access-Control-Request-Method": "GET",
            "Access-Control-Request-Headers": "content-type",
        },
    )
    allow_origin = next(
        (v for k, v in headers.items() if k.lower() == "access-control-allow-origin"), ""
    )
    ok = allow_origin == frontend
    detail = (
        f"status={status} access-control-allow-origin={allow_origin or '<missing>'} "
        f"expected={frontend}"
    )
    results.append(_check("CORS preflight allows the frontend origin", ok, detail))

    # 3. Frontend must be public, not redirecting to a login wall.
    status, headers, body = _get(frontend + "/")
    location = next((v for k, v in headers.items() if k.lower() == "location"), "")
    redirected_to_sso = "vercel.com" in location and "sso" in location
    ok = status == 200 and not redirected_to_sso
    detail = f"status={status} location={location or '<none>'}"
    results.append(_check("Frontend is publicly reachable", ok, detail))

    # 4. The API origin must be baked into the shipped bundle.
    if ok:
        bundle_urls = re.findall(rb"/_next/static/[A-Za-z0-9_/.-]+\.js", body)
        api_host = DEFAULT_API_HOST.encode()
        found = False
        for url in sorted(set(bundle_urls))[:12]:
            _, _, chunk = _get(frontend + url.decode("ascii", "ignore"))
            if api_host in chunk:
                found = True
                break
            if b"localhost:8000" in chunk and api_host not in chunk:
                detail = "bundle falls back to http://localhost:8000; NEXT_PUBLIC_API_URL was not set at build time"
                break
        else:
            detail = "API origin not found in the first 12 bundle chunks"
        results.append(
            _check("Frontend bundle targets the live API", found, detail if not found else "")
        )
    else:
        results.append(
            _check("Frontend bundle targets the live API", False, "skipped: frontend did not load")
        )

    print()
    passed = sum(results)
    print(f"{passed}/{len(results)} checks passed")
    if passed == len(results):
        print(f"Live: {frontend}")
    return 0 if passed == len(results) else 1


if __name__ == "__main__":
    sys.exit(main())
