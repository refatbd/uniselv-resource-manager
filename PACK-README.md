# UNISELV Antigravity Design Pack

This pack contains the project instructions and design/QA specifications for a controlled redesign of UNISELV Resource Manager. The design supports a user-controlled Light/Dark theme switcher, with Light as the default and no automatic System mode.

## Files
- `ANTIGRAVITY.md` — master operating instructions and mandatory workflow.
- `docs/antigravity/01-PRODUCT-DESIGN-BRIEF.md` — product, users, jobs, visual thesis, scope.
- `docs/antigravity/02-RESEARCH-AND-REFERENCE-REPOS.md` — public GitHub references and how to apply them.
- `docs/antigravity/03-DESIGN-SYSTEM.md` — proposed visual tokens, components, themes, responsive and accessibility rules.
- `docs/antigravity/04-UI-SURFACE-INVENTORY.md` — known Admin/Enduser surfaces and UX requirements.
- `docs/antigravity/05-EXECUTION-PLAN.md` — staged redesign workflow.
- `docs/antigravity/06-SERVER-ACCESS-SAFETY.md` — server access, credentials, production safety, rollback.
- `docs/antigravity/07-QA-TEST-PLAN.md` — visual, functional, telemetry, responsive and accessibility tests.
- `docs/antigravity/08-ACCEPTANCE-CHECKLIST.md` — release acceptance criteria.
- `docs/antigravity/09-ANTIGRAVITY-FIRST-PROMPT.md` — copy/paste initial prompt for Gemini Antigravity.

## Installation
Copy `ANTIGRAVITY.md` to the repository root and copy the `docs/antigravity/` directory into the repository.

Open the repository in Gemini Antigravity and submit the prompt in `docs/antigravity/09-ANTIGRAVITY-FIRST-PROMPT.md`.

The first run is explicitly read-only. The requested design includes a Light/Dark switcher, with Light as the default and no automatic System mode. Do not authorize implementation or production access until the audit and visual proposal have been reviewed.
