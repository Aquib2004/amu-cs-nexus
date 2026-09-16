# AMUCS Nexus - Sequence Diagrams

> TARGET ARCHITECTURE - not all components are implemented yet.

Sequence diagrams show the order of messages between components for one scenario.

## Chat / question answering

```mermaid
sequenceDiagram
    autonumber
    participant U as User
    participant FE as Frontend (Next.js)
    participant API as FastAPI
    participant RS as Retrieval service
    participant DB as PostgreSQL
    participant PV as pgvector
    participant LLM as LLM provider

    U->>FE: ask a question
    FE->>API: POST /api/chat {question}
    API->>RS: route and run query
    RS->>DB: structured / metadata query (if applicable)
    DB-->>RS: structured evidence
    RS->>PV: hybrid vector search
    PV-->>RS: relevant chunks + scores
    RS-->>API: evidence set (chunks + source metadata)
    API->>LLM: build context from evidence + ask
    LLM-->>API: generated answer
    API-->>FE: {answer, citations, sources}
    FE-->>U: render answer with clickable sources
```

Notes:

- The retrieval step may be skipped for questions that only need structured data (e.g. a date-filtered notice list).
- The answer always carries citations so the user can open the original source.

## Search (no LLM)

```mermaid
sequenceDiagram
    autonumber
    participant U as User
    participant FE as Frontend (Next.js)
    participant API as FastAPI
    participant RS as Retrieval service
    participant DB as PostgreSQL
    participant PV as pgvector

    U->>FE: search "computer vision papers"
    FE->>API: GET /api/search?q=...
    API->>RS: run search
    RS->>PV: vector + keyword search
    PV-->>RS: chunks + documents
    RS->>DB: load source metadata
    DB-->>RS: document records
    RS-->>API: ranked results
    API-->>FE: results with source links
    FE-->>U: show result list
```

Search is a first-class path that does not require chat.

## Ingestion (one crawl batch)

```mermaid
sequenceDiagram
    autonumber
    participant ING as Ingestion pipeline
    participant SRC as Official source
    participant PRS as Parser / Cleaner
    participant CH as Chunker
    participant EMB as Embedder
    participant IDX as Indexer
    participant DB as PostgreSQL
    participant PV as pgvector

    ING->>SRC: discover and fetch URLs
    SRC-->>ING: HTML / PDF content
    ING->>PRS: parse and clean
    PRS-->>ING: clean text + metadata
    ING->>CH: chunk text
    CH-->>ING: chunks
    ING->>EMB: embed chunks
    EMB-->>ING: vectors
    ING->>IDX: write records + vectors
    IDX->>DB: insert document/chunk metadata
    IDX->>PV: insert embeddings
    DB-->>ING: acknowledged
    PV-->>ING: acknowledged
```

