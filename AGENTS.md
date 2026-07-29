# Antigravity Agent Rules for DunderHunt

1. **Read product-spec.md before implementation**: Ensure all domain rules and API contracts strictly match the specifications defined in `docs/product-spec.md`.
2. **Never modify architecture without documenting the decision**: Any change to schemas, pipelines, or endpoints must be reflected in `docs/architecture.md`.
3. **Use typed schemas for every API boundary**: Pydantic v2 schemas in the backend and TypeScript interfaces in the frontend are mandatory for all API requests, responses, and internal service boundaries.
4. **Never place prompts directly inside application logic**: All prompt templates must reside in `backend/app/prompts/` with versioning, system instructions, and structured schemas.
5. **Every LLM call must use structured output**: Unstructured markdown prose from LLM calls is strictly forbidden. Use Pydantic JSON schemas or JSON mode.
6. **Every feature requires tests**: Unit tests for backend services (ingestion, fit scoring, contact discovery, application state transitions) and benchmark tests must be maintained in `backend/tests/`.
7. **Never add external APIs without documenting cost and rate limits**: Any third-party integration must include error handling and caching to control costs.
8. **Never introduce LinkedIn scraping as a dependency**: Contact discovery must rely on public search queries, search APIs, company pages, and GitHub. The system must operate seamlessly even if LinkedIn is unreachable.
9. **Never automatically contact people**: Outreach message generation is decision-support only. Drafts are presented to the user for review.
10. **Never automatically apply to jobs**: Application submission is strictly performed by the human user.
11. **Preserve user control over Apply, Outreach, Save, and Skip**: The core product principle is "AI performs the analysis. The user makes the decision."
12. **Prefer deterministic logic over LLM reasoning when possible**: Hard filters (work authorization, location, explicit company exclusions) and string normalization must run deterministically before calling an LLM.
13. **Cache external search results**: Contact searches and job page fetching must use caching (in-memory or Redis) to avoid redundant requests.
14. **Keep expensive research behind explicit user actions**: Do not run deep company or contact discovery automatically; run them only when the user explicitly clicks "Find Contact".
15. **Don't overengineer V1**: Focus on a single-user decision-support system with pristine UX and zero fluff.
