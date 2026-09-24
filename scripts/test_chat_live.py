# scripts/test_chat_live.py - verify the live chat endpoint end-to-end.
import json
import sys
import time

import httpx

START = time.time()

def report(status, payload):
    print(f"[{time.time() - START:.1f}s] {status}: {payload}", flush=True)

try:
    r = httpx.post(
        "http://localhost:8000/api/chat",
        json={"question": "How many nodes does the Research Lab have and what fields does it support?"},
        timeout=120,
    )
    data = r.json()
    ans = data.get("answer", "")[:400]
    report(f"PROVIDER={data.get('provider')} NOTICE={bool(data.get('notice'))}",
           {"status": r.status_code, "answer": ans,
            "sources": len(data.get("sources", []))})
except Exception as exc:
    report("ERROR", repr(exc))