## 1.1.22 — 2026-10-22

- Modernize Admin Overview and Enduser Dashboard UI with illuminated neumorphic/glassmorphic gauge cards, dynamic liquid SVG circular fills (0%–100%), 7-bar undulating equalizers, animated sparkline telemetry curves, glowing live telemetry neon capsule badges, and instant zero-latency tab switching.
- Resolve syntax anomaly in frontend bundle and verify zero console errors/warnings in Chrome DevTools across all resolution viewports.
- Fix unmanaged PHP physical discovery breaking native plan save transactions and billing adapter synchronizations; isolate isolation reload loops strictly to explicitly managed PHP versions (`/var/lib/webuzo-isolation/installed.json`).
- Implement dynamic PHP onboarding (`webuzo-isolation.py onboard <version>`) and retirement (`webuzo-isolation.py retire <version>`) with automated compensating rollback and fail-closed checks against active tenant pools.
- Expose PHP lifecycle inspection and management through background daemon IPC with CSRF enforcement.
- Update configuration generator PHP version validator to dynamic regex pattern `/^php\d{2,3}$/`, supporting newly introduced PHP versions without validation failures.
- Transition automated test suites to dynamically provisioned, isolated disposable test fixtures (`disptest`) with comprehensive post-test cleanup, eliminating hardcoded historical account dependencies.
