# AMUCS Nexus - System Overview

> TARGET ARCHITECTURE - NOT ALL COMPONENTS ARE IMPLEMENTED YET.
> This document describes how the system is intended to look. At the time of
> repository initialization only the skeleton and a health endpoint exist.

## What this project is

AMUCS Nexus is a domain-specific information retrieval and knowledge platform for publicly available official information about the AMU Department of Computer Science. It is NOT merely an AI chatbot. The central principle:

> Provide verifiable, source-grounded information rather than confident but unsupported answers.

## Components

The components are separated into logical subsystems. This is a `modular monolith`: one deployable system with clearly separated responsibilities, not microservices.

| Subsystem  | Responsibility                                      |
|------------|-----------------------------------------------------|
| frontend   | Presentation and client-side UX (React / Next.js)   |
| backend    | REST API and application logic (FastAPI)            |
| ingestion  | Acquiring and processing official source material   |
| database   | PostgreSQL + pgvector assets                        |
| ai         | LLM, embeddings, retrieval, RAG, evaluation        |
| shared     | Contracts shared across subsystems                  |
| infra      | Deployment and infrastructure                      |

## Target request flow

```text
                      +------------------+
                      |      User        |
                      +--------+---------+
                               |
                               v
                      +------------------+
                      |    Frontend      |
                      |  React / Next.js |
                      +--------+---------+
                               |
                             HTTPS
                               |
                               v
                      +------------------+
                      |     FastAPI      |
                      |    REST API      |
                      +--------+---------+
                               |
                               v
                      +------------------+
                      | Application     |
                      |     Layer       |
                      +--------+---------+
                               |
              +----------------+----------------+
              |                |                |
              v                v                v
       Structured       Retrieval          AI
         Data            Pipeline          Layer
              |                |                |
              +----------------+----------------+
                               |
                               v
                          Evidence
                               |
                               v
                              LLM
                               |
                               v
                      Answer + Sources
```

## Target ingestion flow

```text
Official AMU Sources
        |
        v
      Crawler
        |
        v
 HTML / PDF Parser
        |
        v
     Cleaner
        |
        v
 Metadata Extraction
        |
        v
     Chunking
        |
        v
    Embeddings
        |
        v
 PostgreSQL + pgvector
        |
        v
    Retrieval
```

## Query routing (target)

Not every query uses vector search. The system intends to distinguish:

- structured queries (e.g. "notices from September" -> date filtering)
- exact / keyword search
- semantic search
- document, notice, faculty, research retrieval
- unsupported / out-of-domain queries

The future RAG pipeline: query normalization -> intent/query routing -> hybrid retrieval -> metadata filtering -> reranking -> evidence set -> LLM -> citation validation -> answer.

## Source authority (target)

For university factual questions, official evidence is prioritized: official AMU/department sources, official documents, official archives, other institutional sources, then user-provided information, with general LLM knowledge last.

## Non-goals

AMUCS Nexus is NOT: an official AMU communication channel, a creator of university policy, guaranteed to know unpublished information, allowed to fabricate answers, an unrestricted general-purpose assistant, or a justification for blind scraping.

