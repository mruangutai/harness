# Receipt — FEAT-53 KPI bundle repair

PASS — the committed dashboard bundle now ships Astryx CSS, sums KPI 6 unattributed breakdowns, and treats the specified zero-feature Throughput payload as unavailable.

- Task: `T-14`; branch: `feat/FEAT-53`; commit: `e88201e9949321bd981a44567aa6fdcb79955c62`.
- Fail-first command: `npm --prefix .claude/skills/harness/bin/dashboard/client test -- --run src/kpi-content.test.tsx src/panels.test.tsx`.
  - RED: 2 files / 7 tests, 3 failed expectations: tile could not find `26 of 40 commits unattributed`; tile could not find `91 features lack a ship record or approval date` and rendered `0`; panel could not find `26 of 40 commits unattributed` and rendered `0 of 40`.
- Green command: `npm --prefix .claude/skills/harness/bin/dashboard/client test -- --run src/kpi-content.test.tsx src/panels.test.tsx`.
  - GREEN: 2 files, 7 tests passed, 22 runtime assertions (8 tile, 14 panel).
- Build command: `npm --prefix .claude/skills/harness/bin/dashboard/client run build`.
  - PASS: Vite built 2,930 modules; emitted `dist/assets/index-BGeYwNXA.css` (188,908 bytes) and `dist/assets/index-DnXu7ssi.js`.
- CSS inspection command: `python3 -c "import pathlib,re;root=pathlib.Path('.claude/skills/harness/bin/dashboard/client');source=(root/'src/main.tsx').read_text();imports=['@astryxdesign/core/reset.css','@astryxdesign/core/astryx.css','@astryxdesign/theme-neutral/theme.css'];positions=[source.index(f\"import '{item}';\") for item in imports];assert positions == sorted(positions) and positions[-1] < source.index(\"import { Theme }\"), 'CSS imports not reset/core/theme before application imports';html=(root/'dist/index.html').read_text();match=re.search(r'href=\"\\./([^\"]+\\.css)\"',html);assert match, 'index.html has no generated CSS asset';asset=root/'dist'/match.group(1);assert asset.is_file() and asset.stat().st_size > 0, f'missing or empty {asset}';print(f'css-import-order=reset/core/theme; css-asset={asset}; bytes={asset.stat().st_size}')"`.
  - PASS: `dist/index.html` references `.claude/skills/harness/bin/dashboard/client/dist/assets/index-BGeYwNXA.css`; it exists and is non-empty.

## Committed paths

- `.claude/skills/harness/bin/dashboard/client/src/main.tsx`
- `.claude/skills/harness/bin/dashboard/client/src/tiles.tsx`
- `.claude/skills/harness/bin/dashboard/client/src/panels.tsx`
- `.claude/skills/harness/bin/dashboard/client/src/kpi-content.test.tsx`
- `.claude/skills/harness/bin/dashboard/client/src/panels.test.tsx`
- `.claude/skills/harness/bin/dashboard/client/dist/index.html`
- `.claude/skills/harness/bin/dashboard/client/dist/assets/index-BGeYwNXA.css`
- `.claude/skills/harness/bin/dashboard/client/dist/assets/index-DnXu7ssi.js`

## Authorized amendment metadata

- task: `T-13`; field: `files`; was: signed seven-file list ending in `package-lock.json`; now: signed list plus `.claude/skills/harness/bin/dashboard/client/dist/`; reason: bind regenerated committed bundle artifacts.
- task: `T-13`; field: `verify`; was: `npm --prefix .claude/skills/harness/bin/dashboard/client test -- --run src/routes.test.tsx && npm --prefix .claude/skills/harness/bin/dashboard/client run build`; now: the build command and CSS inspection command recorded above, in that order; reason: prove exact reset/core/theme source order and a non-empty generated CSS asset referenced by committed `dist/index.html`.
- task: `T-14`; field: `files`; was: signed six-file list from `tiles.tsx` through `kpi-content.test.tsx`; now: signed list plus `.claude/skills/harness/bin/dashboard/client/dist/`; reason: bind regenerated behavior bundle artifacts.
- task: `T-14`; field: `verify`; was: `npm --prefix .claude/skills/harness/bin/dashboard/client run build && python3 -c "import pathlib,sys;s=''.join(p.read_text() for p in pathlib.Path('.claude/skills/harness/bin/dashboard/client/src').rglob('*.tsx') if not p.name.endswith('.test.tsx'));[sys.exit('missing '+k) for k in ['NoShipRecords','PreCapability','GradingCaveat','UnavailableValue','/kpi/','/work/'] if k not in s];[sys.exit('forbidden '+k) for k in ['107','122','/features','/kpis'] if k in s]"`; now: `npm --prefix .claude/skills/harness/bin/dashboard/client test -- --run src/kpi-content.test.tsx src/panels.test.tsx`; reason: independently cover KPI 6 tile, KPI 6 panel, and KPI 1 unavailable observable output.
