# ADR-002 - AMU branding and the "YouRobo" assistant name

- Status: accepted
- Date: 2025-09
- Deciders: maintainers
- Related: ADR-001

## Context

The web UI references the Aligarh Muslim University mark (`/amu-logo.png`, an
official PNG downloaded from the AMU site) and introduces a named assistant,
"YouRobo", for the chat experience.

Two concerns must be kept distinct:

1. Using a university trademark to identify the institution a student project
   is about, versus implying official endorsement.
2. Naming a product feature ("YouRobo") versus claiming the whole platform is
   the assistant.

## Decision

- The AMU mark is used **only** in the header/favicon to identify the relevant
  institution. The README, footer, and docs state in all places that the site is
  **not an official AMU communication channel**.
- "YouRobo" is the **name of the chat assistant** (the "college AI assistant"
  persona), not the name of the platform. The product stays "AMUCS Nexus".
- The logo is committed to `frontend/public/amu-logo.png` so the app works
  offline and the exact bytes are reviewable.

## Consequences

- Users immediately recognise which university the site is about.
- No claim of official endorsement is made; if AMU objects, the mark can be
  removed from `public/` without touching any logic.
- The assistant persona can be renamed in one place (the chat page + prompts)
  without renaming the project.