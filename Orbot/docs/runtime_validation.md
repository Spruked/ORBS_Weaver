# Three-runtime organization validation

Validated on Windows, 2026-10-20.

- Communication/memory/SKG tests: 27 passed.
- Runtime boundary tests: 3 passed.
- Migrated RAL authority-path tests: 8 passed.
- Migrated ROS bridge contract tests: 10 passed.
- Cognition/Governance and Motion: independent subprocess startup and live
  loopback health checks passed; test processes stopped afterward.
- Root `npm run typecheck` and `npm run build:dev`: passed. The latter avoids
  the deploy-time database migration. Existing CSS import ordering warning remains.
- Desktop `npm --prefix desktop run build`: passed.
- Repository scan: only root `.git`; no mode-160000 Git submodule entries.

Root `npm test`: 58 passed, 3 test files failed to load. Existing missing
helpers include `scripts/check-auth-invariant.mjs`, `scripts/with-app-env.mjs`,
and the helper imported by `scripts/brand-check.test.mjs`. These tests and
imports predate this runtime organization and remain unresolved; this is not
a claim that the full repository test suite passes.

The supervisor's full three-process lifecycle has not been exercised against
the active user memory service. Startup checks reject occupied ports; run it
after stopping the standalone Communication service gracefully. Live health
does not demonstrate end-to-end permit issuance, actuation, or correspondence.
