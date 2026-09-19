# T-03 receipt — component dependency repair

## Result

`@testing-library/dom` is now an exact direct dev dependency at `10.4.1`, satisfying `@testing-library/react@16.3.3`'s `^10.0.0` peer requirement. The original missing-DOM failure is eliminated, but the configured component command still cannot pass because it next fails on the pre-existing undeclared `@stylexjs/stylex` peer required by `@astryxdesign/core@0.6.2`. Adding that peer is outside this task's explicitly DOM-only manifest/lock scope.

## Fail-first evidence

QA's pinned failure is recorded in `notes/review-harness-qa-c0.md:20-23` and `runs/validate-validator/digest.md:52,59`: five component suites stopped before collection because `@testing-library/dom` was absent. I reproduced that pre-change state:

```text
$ npm --prefix .claude/skills/harness/bin/dashboard/client run test
Test Files  5 failed (5)
Error: Cannot find module '@testing-library/dom'
Require stack:
- .../node_modules/@testing-library/react/dist/pure.js
```

## Dependency inspection

- Added direct dev dependency: `@testing-library/dom: "10.4.1"` (`client/package.json:24`).
- Lock root metadata declares the same exact pin (`client/package-lock.json:18-29`).
- Its lock entry is `10.4.1`, with the registry resolution and integrity recorded at `client/package-lock.json:858-876`.
- `@testing-library/react` remains pinned at `16.3.3`; every pre-existing manifest pin remains unchanged (`client/package.json:22-30`).
- The lock diff changes only the new direct DOM peer and its transitive resolution metadata (142 lock insertions; no deletions); no existing lock entry changed.

`npm install --package-lock-only --ignore-scripts --save-dev --save-exact @testing-library/dom@10.4.1` first exposed the repository's existing Astryx `core@0.6.2` / `theme-neutral@0.5.2` peer conflict; rerunning with `--legacy-peer-deps` preserved those existing pins and generated the minimal DOM lock resolution.

## Scoped verification

```text
$ npm --prefix .claude/skills/harness/bin/dashboard/client run test
Test Files  5 failed (5)
Error: Cannot find package '@stylexjs/stylex' imported from .../node_modules/@astryxdesign/core/dist/AppShell/AppShell.js
```

This proves the repaired dependency progressed past the prior `@testing-library/react/dist/pure.js` DOM import. The remaining failure is an independent Astryx peer-resolution defect: `@astryxdesign/core@0.6.2` declares `@stylexjs/stylex: ^0.19.0` (`node_modules/@astryxdesign/core/package.json:669-673`), but neither manifest nor lock declares it. No source, test, runner, or additional dependency was changed.

```text
$ HARNESS_UI_FEATURE=FEAT-53-metrics-dashboard HARNESS_UI_RUN_ID=plan-list npm --prefix .claude/skills/harness/bin/dashboard/client run test:ui -- --list
> test:ui
> playwright test --config playwright.config.ts --list
Total: 23 tests in 6 files
```

The exact signed T-03 UI list command exited 0 and remains at exactly 23 tests in 6 files.
