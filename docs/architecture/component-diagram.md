# AMUCS Nexus - Component Diagram

> TARGET ARCHITECTURE - not all components are implemented yet.

## Diagram

```mermaid
flowchart TB
    User(["User\nStudent / Faculty / Visitor"])

    subgraph presentation["Frontend - React / Next.js"]
        UI["UI pages\nChat, Search, Notices, Documents, Faculty, Research"]
    end

    subgraph backend["Backend - FastAPI"]
        API["REST API\nrouters: health, notices, documents, faculty, search, chat, feedback"]
        SVC["Application services\napplication / business logic"]
        REPO["Repositories\ndata access"]
    end

    subgraph ingestion["Ingestion subsystem"]
        ING["Crawler -> Parser -> Cleaner -> Chunker -> Embedder -> Indexer"]
    end

    subgraph data["Data layer"]
        PG[("PostgreSQL\nstructured data + metadata")]
        PV[("pgvector\nchunk embeddings")]
        OBJ[("Object / file storage\nPDFs, raw files, snapshots")]
    end

    subgraph ai["AI layer"]
        RET["Retrieval\nkeyword / semantic / hybrid + rerank"]
        RAG["RAG\ncontext construction + citation validation"]
        EMB["Embeddings\nembedding providers"]
        LLM["LLM provider\nprovider-agnostic interface"]
    end

    User --> UI
    UI --|HTTPS|--> API
    API --> SVC
    SVC --> REPO
    SVC --> RET
    RET --> PG
    RET --> PV
    REPO --> PG
    RAG --> RET
    RAG --> LLM
    EMB --> RET
    ING --> PG
    ING --> PV
    ING --> OBJ
```

## Component responsibilities

| Component | Responsibility | Examples |
|-----------|----------------|----------|
| Frontend | Presentation and client UX | Chat, Search, Notices, Documents, Faculty, Research pages |
| REST API | Exposes resources/operations over HTTP | /api/notices, /api/search, /api/chat |
| Application services | Business logic and orchestration | Query routing, feedback handling |
| Repositories | Data access abstraction | Read/write records from PostgreSQL |
| Ingestion | Acquires and processes source material | Crawl, parse, clean, chunk, embed, index |
| Retrieval | Finds relevant content | Keyword + semantic + hybrid + rerank |
| RAG | Builds evidence-grounded answers | Context construction, citations |
| Embeddings | Turns text into vectors | Index-time and query-time embeddings |
| LLM provider | Generates answers from evidence | Provider-agnostic call |

## Why this shape

- **Single deployable system (modular monolith)**, not microservices. Separating each concern into a deployable service would add networking, deployment, and operational complexity with no current benefit.
- **The AI is one component**, not the whole product. Many use cases (searching notices, opening a PDF) do not need an LLM.
- **A clear data layer boundary** keeps retrieval and application logic separate from storage details.

