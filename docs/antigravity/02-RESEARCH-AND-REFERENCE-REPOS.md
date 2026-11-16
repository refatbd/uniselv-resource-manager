# Design Research and Public Reference Repositories

This document identifies public repositories that can inform the redesign. Use them for principles, review methods, and documentation structure. Do not copy another product's branding, complete layout, assets, or code without checking the relevant license and obtaining approval.

## 1. Primary references

### A. Anti AI Slop UI
Repository: https://github.com/rwcod/anti-ai-slop-ui

Useful ideas:
- Begin with design intent, not component generation.
- Classify the surface before choosing a visual direction.
- Define tokens, layout strategy, motion rules, and a review gate.
- Evaluate whether the UI is specific to the actual product.

Apply to UNISELV:
- Write the visual thesis before editing CSS.
- Review Admin and Enduser separately because their jobs differ.
- Reject generic dashboard patterns that do not improve infrastructure operations.

### B. Microsoft Frontend Design Review Skill
Repository: https://github.com/microsoft/skills

Useful ideas:
- Review frictionless workflows, quality craft, and trustworthiness.
- Separate design review from creative design.
- Check accessibility, responsive behavior, and implementation quality.
- Make the design direction explicit before coding.

Apply to UNISELV:
- Every screen must make its primary task easy to find.
- Operational status must be trustworthy and understandable.
- Review the rendered page, not only source code.

### C. Design Distinctive UI
Repository: https://github.com/bugroo/design-distinctive-ui

Useful ideas:
- Convert the brief into surface, audience, primary job, tone, and constraints.
- Define one visual thesis and a structural fingerprint.
- Preserve existing routes, behavior, and application contracts.
- Treat loading, empty, error, and success as real states.
- Verify keyboard behavior and WCAG 2.2 AA.

Apply to UNISELV:
- Define one shared visual language across the plugin.
- Preserve PHP hooks, API contracts, JavaScript selectors, and Webuzo integration.
- Build and test real operational states.

### D. No Slop UI
Repository: https://github.com/LeoStehlik/no-slop-ui

Useful ideas:
- Review for decorative glass panels, gradients, fake metrics, card overload, vague copy, and unusable dashboards.
- Use a review checklist before accepting a design.
- Prefer real product screens over marketing-style hero sections inside an operational dashboard.

Apply to UNISELV:
- Avoid unnecessary cards and decorative effects.
- Do not make a resource console look like a generic AI landing page.
- Do not create fake telemetry or filler content.

### E. Design MD
Repository: https://github.com/VoltAgent/design-md

Useful ideas:
- Keep design taste in a readable, agent-friendly Markdown document.
- Document tokens, patterns, and rationale so future agents can follow the same system.
- Treat the design document as persistent project context.

Apply to UNISELV:
- Keep `DESIGN-SYSTEM.md` as the canonical visual reference.
- Update it when an approved token or component rule changes.

### F. Accessible Design System
Repository: https://github.com/richardstelmach/accessible-design-system

Useful ideas:
- Use semantic tokens rather than hard-coded values.
- Treat accessibility as architecture.
- Keep design tokens and component rules as a source of truth.

Apply to UNISELV:
- Use semantic CSS custom properties.
- Test colour contrast, keyboard access, and focus visibility in both Light and Dark themes.
- Avoid one-off component colours.

## 2. What not to copy

Do not blindly adopt:
- A fixed anti-design recipe.
- Another product's exact sidebar, card grid, typography, or brand palette.
- A ban on every gradient, rounded corner, or card regardless of context.
- A framework or dependency just because a reference repository uses it.
- A visual effect that does not help the user understand or complete an operational task.

The goal is not to replace one generic style with another. Every major design choice must answer:

**Why is this appropriate for UNISELV Resource Manager, this user, and this task?**

## 3. Research-to-implementation method

For each reusable idea:
1. Record the source repository and relevant file/section.
2. Summarize the principle in your own words.
3. Explain why it applies to this product.
4. Translate it into a UNISELV-specific rule.
5. Verify it against actual screens and users.
6. Check license terms before copying code or assets.

## 4. Research output

During the read-only audit, create `docs/antigravity/audit/REFERENCE-RESEARCH-NOTES.md` containing:
- References reviewed.
- Principles adopted.
- Principles rejected and why.
- Product-specific adaptations.
- Any code/assets considered for reuse and their license review status.
