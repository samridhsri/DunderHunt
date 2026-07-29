# DunderHunt Product Specification & Architecture

## Core Problem & Product Principle
DunderHunt is a single-user decision-support job-search system designed for Sam.
Product Goal: **Turn a messy job search into a ranked queue of decisions, while keeping the final control with Sam.**

Principle: **AI performs the analysis. The user makes the decision.**

Every job ultimately results in one of four states:
- `APPLY`
- `APPLY + OPTIONAL OUTREACH`
- `SAVE`
- `SKIP`

And every job has **ONE NEXT ACTION**.

## V1 Capabilities
1. **Job Ingestion**: Paste Job URL, Job Description, or Title + Company.
2. **Job Deduplication**: Detect same URL, same company + role, or canonical fingerprint (`company|title|location`).
3. **Fit Analysis**: Score jobs against candidate profile using Layer 1 deterministic filters + Layer 2 AI evaluation.
4. **Job Queue**: Dashboard displaying Priority (A, B, C, Skip), Fit score (0-100), Status, and Next action.
5. **Optional Find Contact**: Explicit user button click searches public sources, ranks contacts, returns top 3.
6. **Application Tracking**: States: Discovered, Analyzing, Saved, Applied, Outreach, OA, Interview, Offer, Rejected, Withdrawn.

## System Architecture

```
Job Sources (URLs / Search) -> Job Ingestion (Extract + Normalize)
                              │
                              ▼
                        SQLite / PostgreSQL
                              │
                              ▼
                        Fit Pipeline (Rules + LLM)
                              │
                              ▼
                        Decision Layer (APPLY / SAVE / SKIP)
                              │
                     ┌────────┴────────┐
                     ▼                 ▼
              App Tracker           Outreach (OFF by default)
                                       │ (Find Contact click)
                                       ▼
                                Public Search -> Top 3 Contacts
```
