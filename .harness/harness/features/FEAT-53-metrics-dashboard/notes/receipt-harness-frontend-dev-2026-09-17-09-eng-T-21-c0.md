# T-21 receipt

Commit: `c1d2da71` (`panels.tsx`, `panels.test.tsx`; `charts.tsx` was not changed because T-15 already contained the required outer `chart-shape-a` and `chart-shape-b` handles). No build was run; generated `client/dist` was untouched and remains uncommitted. DEC-229 amendment: verify-only; the signed command now reads Vitest 5's fresh `client/.vitest/json/output.json` carrier because stdout is non-JSON. Task files, success criteria, and decisions are unchanged.

## Fail-first evidence

With `charts.tsx` present but unimported, `npm --prefix .claude/skills/harness/bin/dashboard/client run --silent test -- src/panels.test.tsx --reporter=json` exited 1. Its JSON reporter recorded all three mandated cases failed (`numTotalTests: 3`, `numFailedTests: 3`) at `getByTestId`: Shape A and both Shape B handles were absent.

With temporary testid-only placeholders in `panels.tsx`, the same command exited 1 with all three mandated cases failed. The JSON reporter records each failure as `AssertionError: expected null not to be null` at the SVG subtree assertions: Shape A's SVG and both Shape B SVGs were absent. The placeholders were replaced with real `ShapeA`/`ShapeB` mounts before commit.

## Green evidence

The scoped command exited 0 after the real mounts. The JSON reporter at `client/.vitest/json/output.json` records `passed` for all exact mandated names:

- `KpiPanel chart mounts grading panel mounts the Shape A histogram`
- `KpiPanel chart mounts trend panel mounts the Shape B time series`
- `KpiPanel chart mounts merged PR panel mounts the Shape B weekly line`

The tests render real panels with hand-written complete payloads, assert Shape A's SVG plus all five labels including `Grade 3: 0`, and assert Shape B SVG paths and direct end labels. The merged fixture carries a null empty week with `no ship record in the week of 2026-09-08`, producing two contiguous runs.

## Amended signed verify

DEC-229's exact amended command was run:

```sh
rm -f .claude/skills/harness/bin/dashboard/client/.vitest/json/output.json && npm --prefix .claude/skills/harness/bin/dashboard/client run --silent test -- --reporter=json >/dev/null 2>&1 && python3 -c 'import json,pathlib,sys;s=pathlib.Path(".claude/skills/harness/bin/dashboard/client/.vitest/json/output.json").read_text();d=json.JSONDecoder().raw_decode(s[s.index("{"):])[0];p={a.get("fullName","") for t in d["testResults"] for a in t["assertionResults"] if a.get("status")=="passed"};w=["grading panel mounts the Shape A histogram","trend panel mounts the Shape B time series","merged PR panel mounts the Shape B weekly line"];m=[c for c in w if not any(c in n for n in p)];sys.exit(0 if not m else "not passed: "+", ".join(m))' && python3 -c "import pathlib,sys;s=pathlib.Path('.claude/skills/harness/bin/dashboard/client/src/panels.tsx').read_text();[sys.exit('retired route '+k) for k in ['/features','/kpis'] if k in s]"
```

The amended command was rerun after T-28's route repair and exited 0 with no output. The fresh JSON output records all three T-21 required reporter cases as `passed`, and the retired-route scan passed. `client/dist` remains `assets/.gitkeep` only; no generated content was committed. No additional source was edited or committed.
