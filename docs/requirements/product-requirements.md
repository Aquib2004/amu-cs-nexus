# AMUCS Nexus - Product Requirements

Status: DRAFT - Phase 0, for review.

> TARGET/PRODUCT SPECIFICATION. Software is not built to match this yet.

## 1. Product vision

AMUCS Nexus is an open-source knowledge, search, document retrieval, and AI information platform for the Department of Computer Science, Aligarh Muslim University (AMU).

It helps people find and understand publicly available official information about the department - notices, announcements, academics, admissions, courses, syllabus, examinations, faculty, research, publications, PDFs, laboratories, facilities, and contact information.

The central principle:

> AMUCS Nexus provides verifiable, source-grounded information rather than confident but unsupported answers.

## 2. Problem statement

Official department information is spread across many pages and PDF documents on multiple official sites. Finding a specific notice or verifying a fact is slow and error-prone. A plain AI chatbot can be confident but wrong (hallucination) and offers no way to check its claims.

AMUCS Nexus solves both problems: it indexes official material so it can be searched, and it grounds AI answers in that material with citations back to the original source.

## 3. Primary users (personas)

| Persona | Role | Main need |
|---------|------|-----------|
| Prospective student | Applying / exploring | Admissions, courses, faculty, how the department works |
| Current student (UG/PG) | Studying | Notices, exam info, syllabus, documents, labs |
| Researcher / faculty | Working / publishing | Research areas, publications, papers, collaborators |
| Staff / visitor | Admin / visit | Contact info, facilities, department info |

## 4. Primary use cases

The user should eventually be able to:

- Search notices.
- Search documents.
- Find official information.
- Search faculty information.
- Find research information.
- Ask questions about available official information.
- Receive source-backed answers.
- Open the original source from an answer or result.

Search must be available directly (notices, documents, faculty, research) - it should never force the user through chat.

## 5. In scope (eventually)

Official, publicly available AMU / department information only. We do not handle private data (individual marks, personal records).

## 6. Out of scope (non-goals)

AMUCS Nexus is NOT:

- an official replacement for AMU communication;
- an authority that creates university policy;
- guaranteed to know unpublished information;
- allowed to fabricate answers;
- an unrestricted general-purpose assistant;
- an excuse to blindly scrape every website.

## 7. Source authority model (target)

For university factual questions, official evidence is prioritized:

1. Official AMU / department sources
2. Official university documents
3. Official archived sources
4. Other institutional sources
5. User-provided information
6. General LLM knowledge

The system must preserve source metadata (URL, dates, document type) so every claim can be traced.

## 8. Success criteria

- A user can find a notice, open the official source, and confirm it.
- A user can ask a question and receive an answer with citations that link to real sources.
- If the answer is not in the indexed official material, the system says it cannot verify it rather than guessing.
- A first-time contributor can clone, configure, and run the project from documentation alone.

