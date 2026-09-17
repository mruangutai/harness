# T-14 receipt — c1

## Verdict

PASS — the amended runtime-only literal scan and the accepted focused rendered-surface smoke both pass without a production-source change.

## Amendment

- Task: `T-14`
- Field: `verify`
- Was (exact): `npm --prefix .claude/skills/harness/bin/dashboard/client run build && python3 -c "import pathlib,sys;s=''.join(p.read_text() for p in pathlib.Path('.claude/skills/harness/bin/dashboard/client/src').rglob('*.tsx'));[sys.exit('missing '+k) for k in ['NoShipRecords','PreCapability','GradingCaveat','UnavailableValue','/kpi/','/work/'] if k not in s];[sys.exit('forbidden '+k) for k in ['107','122','/features','/kpis'] if k in s]"`
- Now (exact): `npm --prefix .claude/skills/harness/bin/dashboard/client run build && python3 -c "import pathlib,sys;s=''.join(p.read_text() for p in pathlib.Path('.claude/skills/harness/bin/dashboard/client/src').rglob('*.tsx') if not p.name.endswith('.test.tsx'));[sys.exit('missing '+k) for k in ['NoShipRecords','PreCapability','GradingCaveat','UnavailableValue','/kpi/','/work/'] if k not in s];[sys.exit('forbidden '+k) for k in ['107','122','/features','/kpis'] if k in s]"`
- Reason (exact): the production client module set is every `src/**/*.tsx` except `*.test.tsx`; T-13's `routes.test.tsx` contract requires retired-route literals, so excluding test modules lets this T-14 runtime-route scan enforce the same required and forbidden literals against production modules without changing T-13.

## Source and receipt hashes

- Accepted source commit: `7974fffaa5d4ad2f1870c1eef738c0345e74b8e2` (`7974fffa`).
- Prior c0 receipt SHA-256: `c00a70d5fb4e1ca65985cc3dd0795c78cc5c337707790ca9f043f88512a6223c`.

## Exact amended scoped verification

Command:

```text
npm --prefix .claude/skills/harness/bin/dashboard/client run build && python3 -c "import pathlib,sys;s=''.join(p.read_text() for p in pathlib.Path('.claude/skills/harness/bin/dashboard/client/src').rglob('*.tsx') if not p.name.endswith('.test.tsx'));[sys.exit('missing '+k) for k in ['NoShipRecords','PreCapability','GradingCaveat','UnavailableValue','/kpi/','/work/'] if k not in s];[sys.exit('forbidden '+k) for k in ['107','122','/features','/kpis'] if k in s]"
```

Verbatim output:

```text
> build
> vite build

vite v8.3.0 building client environment for production...
[warn] `inlineDynamicImports` option is deprecated, please use `codeSplitting: false` instead.
transforming...
✓ 2599 modules transformed.
rendering chunks...
computing gzip size...
dist/index.html                  0.32 kB │ gzip:   0.23 kB
dist/assets/index-DzoXKmQ_.js  697.35 kB │ gzip: 213.24 kB

[plugin builtin:vite-reporter] 
(!) Some chunks are larger than 500 kB after minification. Consider:
- Using dynamic import() to code-split the application
- Use build.rolldownOptions.output.codeSplitting to improve chunking: https://rolldown.rs/reference/OutputOptions/codeSplitting
- Adjust chunk size limit for this warning via build.chunkSizeWarningLimit.
✓ built in 152ms
```

## Focused rendered-surface smoke

Command:

```text
npm run test -- kpi-content.test.tsx gapstates.test.tsx
```

Verbatim output:

```text
> test
> vitest run kpi-content.test.tsx gapstates.test.tsx


 RUN  v5.0.1 /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-53/.claude/skills/harness/bin/dashboard/client


 Test Files  2 passed (2)
      Tests  2 passed (2)
   Start at  23:16:13
   Duration  821ms (import 47%, environment 40%, tests 7%, transform 5%, setup 1%, worker 1%)
```

## Scope record

- `files_touched`: `.harness/harness/features/FEAT-53-metrics-dashboard/notes/receipt-harness-frontend-dev-T-14-c1.md` only; no T-14 production module changed.
- `routes.test.tsx`, every T-13 file, `plan.yaml`, and generated `client/dist` were not edited or staged.
- No formatter, linter, or project-wide suite was run.
