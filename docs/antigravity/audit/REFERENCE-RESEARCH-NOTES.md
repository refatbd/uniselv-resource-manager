# UNISELV Resource Manager — Reference Research & Design Principles

> Stage A Deliverable — Synthesis of Public Repositories & UI Standards
> Grounded in `docs/antigravity/02-RESEARCH-AND-REFERENCE-REPOS.md` and the Precision Operations Console thesis.

---

## 1. Public References Evaluated

We audited the six public repositories specified in `02-RESEARCH-AND-REFERENCE-REPOS.md`:
1. `rwcod/anti-ai-slop-ui`
2. `microsoft/skills` (Frontend Design Review)
3. `bugroo/design-distinctive-ui`
4. `LeoStehlik/no-slop-ui`
5. `VoltAgent/design-md`
6. `richardstelmach/accessible-design-system`

---

## 2. Adopted Principles & UNISELV Translations

| Source Concept | Core Principle | UNISELV Resource Manager Application |
|---|---|---|
| **Anti-AI-Slop** | UI must feel specific to the actual operational task, not a template. | Eliminate generic marketing aesthetics (floating particles, wave animations behind needles, 16px border-radii, glowing gradients). Telemetry is operational evidence, not decoration. |
| **Microsoft Design Review** | Separate design critique from creative implementation; verify rendered pages, not just source code. | Evaluate actual rendered Webuzo screens across both Admin and Enduser panels under standard resolutions (1440x900 to 360x800) with realistic tenant load. |
| **Distinctive UI Thesis** | One structural fingerprint; preserve application routing and existing DOM contracts. | Maintain a unified **Precision Operations Console** visual language across both Admin and Enduser without making them identical. Preserve all Webuzo hooks, JavaScript DOM IDs, and daemon IPC contracts. |
| **No-Slop Review** | Avoid card overload and fake metrics; reject SaaS landing-page patterns in operational tools. | Organize dense tables and metrics into clear structural layers (Canvas → Inset Surfaces → Dividers) instead of wrapping every label in an elevated card. Lead with physical host headroom. |
| **Design MD** | Treat tokens and taste as persistent repository context. | Maintain canonical tokens in `03-DESIGN-SYSTEM.md` and translate them into clean, namespaced CSS custom properties (`--ur-*`). |
| **Accessible Design System** | Semantic tokens; accessibility as architecture. | Strict WCAG 2.2 AA compliance: visible keyboard focus rings (`--ur-focus: #A94F32` in Light, `#E0A080` in Dark), high-contrast status text, and tabular numerics (`font-variant-numeric: tabular-nums`). |

---

## 3. Rejected Patterns & Engineering Rationale

- **Rejected: Heavy "Cyberpunk / High-Contrast Neon Dark" Style:** While popular in developer tooling, neon-tinted dark themes clash with Webuzo's native panel chrome and reduce readability during long operational monitoring sessions. *Decision: Adopt a quiet, technical Graphite/Ink Dark theme paired with a crisp, warm Light theme.*
- **Rejected: CDN-Loaded External CSS Frameworks (Tailwind, Bootstrap):** Adding external CSS libraries risks style leakage into Webuzo's global navigation chrome and introduces external network dependencies. *Decision: Pure scoped CSS within `.uniselv-container` using native CSS variables.*
- **Rejected: Collapsing Detailed Kernel Metrics into a Generic "Health Score":** Server administrators need exact core-equivalent usage, cgroup swap, anonymous memory, and I/O throughput. Collapsing them into a single percentage score destroys diagnostic value. *Decision: Preserve exact numbers, units, and breakdowns.*
