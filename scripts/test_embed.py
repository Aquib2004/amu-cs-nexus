# scripts/test_embed.py - live test of the Gemini embedder with the configured key.
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
for _p in (str(ROOT), str(ROOT / "backend")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

from ai.providers.gemini_embed import GeminiEmbedder
from app.core.config import settings

key = settings.llm_api_key or settings.gemini_api_key
print("key configured:", bool(key))
if not key:
    print("NO KEY - embedder will not run; an embedder that raises ProviderError is expected")
    raise SystemExit(0)

emb = GeminiEmbedder(api_key=key)
vec = emb.embed("The MCA admission notice for the Department of Computer Science at AMU.")
print("embed() dims:", len(vec))
print("first 5:", [round(v, 4) for v in vec[:5]])

many = emb.embed_many(["Aligarh Muslim University computer science", "laboratory GPU workstations"])
print("embed_many() ->", len(many), "vectors, dims:", len(many[0]))