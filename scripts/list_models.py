# scripts/list_models.py - list models available to the configured Gemini key.
import json
import sys
from pathlib import Path

import httpx

ROOT = Path(__file__).resolve().parents[1]
for _p in (str(ROOT), str(ROOT / "backend")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

from app.core.config import settings

key = settings.llm_api_key or settings.gemini_api_key
if not key:
    print("no key")
    raise SystemExit(0)

# Key in HEADER only, never in URL.
r = httpx.get(
    "https://generativelanguage.googleapis.com/v1beta/models",
    headers={"x-goog-api-key": key},
    timeout=30,
    verify=False,
)
print("status:", r.status_code)
if r.status_code != 200:
    print(r.text[:500])
    raise SystemExit(1)
models = r.json().get("models", [])
for m in models:
    name = m.get("name")
    methods = m.get("supportedGenerationMethods", [])
    if "embed" in name.lower() or any("embed" in mm for mm in methods):
        print(name, "->", methods)
print("total models:", len(models))