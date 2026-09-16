# AMUCS Nexus - AI layer

The AI layer holds LLM, embeddings, retrieval, RAG, orchestration, tools, and evaluation code. It is intentionally separate from the backend so AI concerns do not blur into API/application logic.

> STATUS: Structure only. No AI code exists yet. No LangChain, LangGraph, or MCP is added.

## Directory intent

- `prompts` - prompt templates and design.
- `providers` - LLM/provider abstractions (provider-agnostic interfaces).
- `embeddings` - embedding models and interfaces.
- `retrieval` - keyword, semantic, hybrid, and reranking logic.
- `rag` - context construction and answer generation (with citations).
- `orchestration` - future stateful workflows (e.g. LangGraph only if justified).
- `tools` - application tools and potential MCP integration (later).
- `evaluation` - RAG benchmarks and evaluation metrics.
- `tests` - AI layer tests.

## Boundaries

Do not confuse these concepts:

- **RAG** provides retrieved information to the LLM before generating an answer.
- **LangChain** is an optional framework abstraction for LLM/retrieval workflows.
- **LangGraph** is an optional stateful orchestration mechanism.
- **MCP** is an optional standardized interface for tools/resources.

The project uses plain, explicit code first and only adopts these frameworks when an actual requirement exists.
