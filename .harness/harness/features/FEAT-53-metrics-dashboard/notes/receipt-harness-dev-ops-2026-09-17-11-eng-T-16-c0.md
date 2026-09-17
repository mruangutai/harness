# T-16 receipt — distributable dashboard bundle

**BLUF:** Commit `d46ccd9bc7d77585840d21eecd9cf17f5def04a7` replaces the `dist/.gitkeep` baseline with the complete tracked production bundle. The signed verification and live loopback smoke passed; the server was stopped.

## Bundle and commit evidence

- Commit: `d46ccd9bc7d77585840d21eecd9cf17f5def04a7` (`build(dashboard): commit client bundle`).
- Complete committed `dist` change list: deleted `.claude/skills/harness/bin/dashboard/client/dist/assets/.gitkeep`; added `.claude/skills/harness/bin/dashboard/client/dist/index.html`; added `.claude/skills/harness/bin/dashboard/client/dist/assets/index-hkwR5g06.js`.
- Current tracked distribution paths (`git ls-files`): `.claude/skills/harness/bin/dashboard/client/dist/index.html`; `.claude/skills/harness/bin/dashboard/client/dist/assets/index-hkwR5g06.js`. `git ls-files --error-unmatch` succeeded for both paths.
- JavaScript chunks: exactly 1 — `index-hkwR5g06.js`, 748904 bytes. `index.html` is 327 bytes; exact total is 749231 bytes, which is 1,250,769 bytes below the 2,000,000-byte ceiling.
- Source maps: 0 (`git ls-files` glob for `dist/*.map` and `dist/**/*.map` produced no paths).

## Signed T-16 verification

Executed exactly:

```text
npm --prefix .claude/skills/harness/bin/dashboard/client run build && git ls-files --error-unmatch .claude/skills/harness/bin/dashboard/client/dist/index.html && python3 .claude/skills/harness/bin/dashboard/serve.py --check
```

Result: exit 0. Vite 8.3.0 built 2926 modules in 163 ms and emitted `dist/index.html` (0.32 kB gzip 0.23 kB) and `dist/assets/index-hkwR5g06.js` (748.90 kB gzip 228.98 kB); `git ls-files --error-unmatch` printed the tracked index path; `serve.py --check` exited 0 without output.

## Live loopback smoke

- Started `python3 .claude/skills/harness/bin/dashboard/serve.py` at default `127.0.0.1:8971`, PID 70786.
- `GET /`: HTTP 200; `Content-Type: text/html; charset=utf-8`; body contains `<div id="root"></div>`.
- `GET /api/kpis?window=all`: HTTP 200; `Content-Type: application/json`; 166848-byte response parsed successfully via `python3 -m json.tool`.
- `GET /assets/index-hkwR5g06.js`: HTTP 200; exact `Content-Type: application/javascript; charset=utf-8` (not `text/plain`); `Content-Length: 748904`.
- Stopped process `feat53-dashboard-smoke`; Hub reported exit 143. `lsof -nP -iTCP:8971 -sTCP:LISTEN` then exited 1 with no output, proving no listener remained.

## Status invariant

Baseline before build and post-smoke before writing this receipt were identical:

```text
 M .harness/harness/features/FEAT-53-metrics-dashboard/feature.json
```

That remaining tracked modification is pre-existing host run metadata and was not altered. The committed distribution cutover is clean; the only expected subsequent untracked entry is this permitted receipt. The final status capture follows after receipt creation.

Final post-receipt status was:

```text
 M .harness/harness/features/FEAT-53-metrics-dashboard/feature.json
?? .harness/harness/features/FEAT-53-metrics-dashboard/notes/receipt-harness-dev-ops-2026-09-17-11-eng-T-16-c0.md
```

Classification: `feature.json` is the pre-existing host run metadata from the baseline; this receipt is the permitted run artifact. No other tracked or untracked mutation was introduced by the build or smoke exercise.
