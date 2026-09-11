# Research — BUG-285 foldq7 · the able-to-fail evidence D-09 and SC-14 cite

**D-06's "four of seven disagree" REPRODUCES EXACTLY, and D-08's six-input membership is
confirmed.** Re-measured at `6cb113f4` (worktree `BUG-285-yaml-loader-pin`), both readers run over
the same seven inputs by a throwaway harness. The four disagreeing inputs are the four D-06 names,
and no fifth. This note is what `plan.yaml` D-09 and `BRIEF.md` **Verification gaps** point at as
SC-14's able-to-fail evidence: the pre-change tree IS the mutant, so no third mutation probe is
needed (D-09).

One finding, in the other direction, at the bottom: **`check-plan-routes.py` exits 0 from BOTH
cwds** — the worktree-side DEVIATION this cycle was told to expect does not reproduce.

## 1 · Pre-change disagreement table — measured, not restated

Verdict is `accept` | `refuse` | `escape:<Class>`. `refuse` = `SystemExit`.

| # | input | `gh-sync.load_recorded` | `factory_decompose.load_factory` | agree |
|---|---|---|---|---|
| 1 | valid JSON mapping `{"feature_id":"F1","github":{"parent":40}}` | accept | accept | ✅ |
| 2 | absent file | accept | accept | ✅ |
| 3 | empty file | **refuse** | accept | ❌ |
| 4 | malformed JSON `{ not: valid json [[[` | refuse | refuse | ✅ |
| 5 | YAML-only block mapping `feature_id: F1\ngithub:\n  parent: 40\n` | **refuse** | accept | ❌ |
| 6 | non-UTF-8 bytes `bytes([0xff,0xfe]) + b"trash"` | **escape:UnicodeDecodeError** | refuse | ❌ |
| 7 | non-mapping document `[1, 2]` | **refuse** (`:578`) | accept (empty factory) | ❌ |

`DISAGREEING INPUTS: 4 of 7 — empty file, YAML-only block mapping, non-UTF-8 bytes, non-mapping
document.` Identical to D-06. Rows 1–6 are D-08's six-input set (row 7 excluded as the surviving
divergence) — **membership confirmed as written.**

Why each row is red where it is red: row 3, `json.loads("")` raises `JSONDecodeError` while
`harness_yaml` returns `None` and falls to `load_factory`'s `isinstance` guard at
`factory_decompose.py:124`; row 5, YAML-only syntax is a mapping to one reader and a parse error to
the other; row 6 is the escape below; row 7 is D-08's deliberate survivor.

**Two accept-controls (rows 1–2) are in the set**, so a reader that refused everything fails
SC-14 in the other direction — the substitute D-09 offers for a mutation probe.

## 2 · Escape probe transcript — verbatim

```
>>> open('<tmpdir>/feature.json', "wb").write(bytes([0xff, 0xfe]) + b"trash")
>>> load_recorded(feat_dir)
UnicodeDecodeError: 'utf-8' codec can't decode byte 0xff in position 0: invalid start byte
SystemExit raised: NO
```

No `SystemExit`, no refusal message, no file named — a traceback where every other malformed input
refuses. This is REQ-09's defect and SC-12's pre-change red state.

Companion measurement for D-10's dead-member claim, same run:
`json.loads("") -> JSONDecodeError`, and `json.loads(<str>)` on undecodable-bytes text
→ `JSONDecodeError`. `json.loads` handed a `str` never raises `UnicodeDecodeError`, so that member
of the parse guard at `:567` cannot fire.

## 3 · Verified line anchors — `.claude/skills/harness/bin/gh-sync.py` @ `6cb113f4`

All seven read at source this cycle, all correct as cited in `plan.yaml` T-04 and `BRIEF.md`:

| line | content |
|---|---|
| `527` | `def load_recorded(feat_dir):` |
| `528` | docstring: `"""Read the github: block from feature.json with json.load (B-5: converged with` — **the false convergence claim SC-15 corrects** (continues `factory_decompose.py's reader` on `:529`) |
| `559-560` | `with open(path, encoding="utf-8") as f:` / `text = f.read()` |
| `561` | `except OSError as e:` — the guard that lets the decode failure escape |
| `566` | `doc = json.loads(text)` |
| `567` | `except (ValueError, UnicodeDecodeError) as e:` — the dead member |
| `578` | `if not isinstance(doc, dict):` — the non-mapping guard, row 7's refusal |

Refusal messages at `:562-564` (read) and `:572-574` (parse) are what SC-13 requires unchanged.

## 4 · Routing — `check-domain.sh --resolve`, quoted

```
$ check-domain.sh --resolve .claude/skills/harness/bin/gh-sync.py
harness-backend-dev
harness-dev-ops
EXIT=0

$ check-domain.sh --resolve tests/unit/test-feature-json-readers.py
harness-backend-dev
harness-dev-ops
harness-qa
EXIT=0
```

**T-04 is `harness-backend-dev` because qa does not resolve for the bin path at all** — it is denied,
not merely second choice. **T-05 is `harness-qa` because qa does resolve for `tests/unit/**`**, and
D-02's standing reason applies: qa's consult-when names writing regression tests and closing
coverage gaps, which is the whole of T-05. dev-ops resolves for both and is not chosen (test-runner
setup, not fixtures).

## 5 · Verification sweep — every item, literal output

- **(a) loader.** `harness_yaml.load_plan(plan.yaml)` → `dict`, keys
  `[approval, decisions, feature, lanes, panel, schema, source_issues, status, tasks]`;
  tasks `T-01..T-05`; decisions `D-01..D-11`. Parses. D-06/D-08/D-09 `because` tails survive intact
  (no `#`-truncation).
- **(b) protected tasks — every sha matches the record.**
  `intent`: T-01 `73412a4220ad01e5…` ✅, T-02 `d52c04e344317…` ✅, T-03 `0f16dcb0ab2e44…` ✅.
  `verify`: T-01 `7fee1afa6223d8…`, T-02 `e3f7e0752124409…`, T-03 `dca60b2a666d44…` (first recording
  of the verify shas; no prior value to contradict). **No protected byte moved.**
- **(c) approval / panel.** `{'date': '2026-09-09', 'approved_by': 'mruangutai', 'status':
  'approved'}` — untouched, not re-signed. `panel.last_run: 2026-09-11-02-planpanelc2-validator`,
  `cycle: 2`, 3 readers all `ran`, **6 findings, no new entry** (2 info open, 2 low open, 2 high
  `resolved`).
- **(d) `check-plan-routes.py` — exit 0, `0 violation(s) across 1 plan(s)`, cwd
  `/Users/molchairuangutai/GitHub/harness` (the graded invocation).** Five `OK T-0N granted to …`
  lines, `MANIFEST /Users/molchairuangutai/GitHub/harness/.harness/team-config.yaml`.

## Finding — the worktree-side DEVIATION does not reproduce

Run for contrast from cwd `…/worktrees/harness/BUG-285-yaml-loader-pin`, **both** via the
control-plane script and via the worktree's own copy: **exit 0, `0 violation(s)`, identical five
`OK` lines, and the same `MANIFEST` line naming the OWNER-root `team-config.yaml`** — no DEVIATION
from either. The manifest is resolved from the script's own location, not from cwd, so the
team-config skew that produced the earlier DEVIATION is gone at `6cb113f4`.

Consequence for the record: **panel finding `PF-142f3a51c0d0152899db48cf7cbdfe31` (low, open) no
longer reproduces.** It faulted `notes/research-BUG-285-panelfix-c2.md` for claiming exit 0 where
the worktree measured exit 1 with 1 violation; that note's claim is now the one that reproduces.
Disposition is the validator lead's to change, not pm's — raised as an open question, left `open`.

## Open questions

- **Q1 (non-blocking):** `PF-142f3a51c…` is stale — re-grade or close it.
- **Q2 (non-blocking, carried from D-05):** no `plan-merge.py` verb writes `lanes:`, so the
  single-row `lanes:` table cannot be updated for the new bin work. `check-plan-routes.py` never
  reads `lanes`, so this is a reporting defect, not a routing one.
