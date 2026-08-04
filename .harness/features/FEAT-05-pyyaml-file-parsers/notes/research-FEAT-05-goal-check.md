# Goal-check — FEAT-05 PyYAML file parsers — at `3cf20b0`

**Verdict: the goal is SUBSTANTIALLY delivered but NOT met as stated — one criterion contradicts
the Goal paragraph and a signed Constraint, and only the user can resolve it.** 10 of 14 SCs are
fully met on re-derived evidence: the regex readers are gone from the six scripts' `.yaml` read
paths, issue #11's fixture is proven fixed against the actual pre-change regex, the run inventory
is unchanged, the prerequisite gate exists, and SC-09's UAT pass still stands. **Four are below
that line: SC-02 partial, SC-03 partial, SC-04 not met, SC-14 met-with-a-hole.**

**The blocker.** `check-domain.sh:318-335` is a line-scan alternative selected on parser
availability. BRIEF Goal `:20-21` says "with **no second code path anywhere**"; BRIEF Constraints
`:48-49` says "**No line-scan alternative** … **no degraded mode in any converted script**";
`CLAUDE.md` says it a third time. `check-domain.sh` is a converted script. The in-code comment
reinterprets the constraint as covering only "READING the harness's own YAML in normal operation" —
that reinterpretation was written in the same commit that introduced the branch (`ff5ea45`), carries
no `D-NN`, and amends a signed Constraint. **That is the user's call, not mine and not the
implementer's.**

The dispatch said 13 SCs. **There are 14** — BRIEF Amendment 1 added SC-14 (`STATE.md:115` says so
outright). All 14 judged below.

## SC table

| SC | verify | verdict | evidence (re-derived at HEAD unless stated) |
|---|---|---|---|
| SC-01 | automated | **met** | `test-check-state.py` case (e) passes; I re-ran the **pre-change** regex (`71a2043`) on the identical fixture in-memory: it yields `[]` (run dropped, INV-6/7/8 silent) while `safe_load` yields the run. Narrowness: only INV-6 is asserted; INV-7/INV-8 evaluation is structural. |
| SC-02 | inspection | **partial** | `check-state.sh` at HEAD: **exit 0, 0 violations** — the load-bearing half holds. But the stated output shape ("INV-8 notes about pruned run dirs only") does not: 41 notes = **39 INV-8 + 2 INV-12** orphaned-run-dir notes for FEAT-05's own `runs/2026-08-03-01-validator` and `-05-validator`, unrecorded in its `feature.yaml`. `receipt-post-change-run-inventory.md:40` claims "40 notes, all INV-8" — not true at HEAD. |
| SC-03 | inspection | **partial** | Full census re-run. `check-state.sh` **7** regex calls (`:63 :64 :67 :93 :95 :106` markdown, `:501` over parsed dict keys) — matches the approval-Q2 answer key exactly. `gh-sync.py` 6 (markdown + one over parsed keys), `upgrade-config.py` **0**, `bash-write-guard.sh` 5 (shell/path), `cost-report.py` 2 (`:114` path, `:196` `^cost:` **writer**, sanctioned by D-04). **The exception: `check-domain.sh:319` `re.findall(r"^([A-Za-z_][A-Za-z0-9_-]*):", content, re.M)` is a YAML-content key scan on a `.yaml` read path that does not reach PyYAML.** |
| SC-04 | inspection | **not met (as written)** | `check-domain.sh:318` `if _no_parser:` is a **second parse path over the same data, branched on parser availability** — exactly what SC-04 forbids in three clauses. Introduced at `ff5ea45` (06:06 today), i.e. **after every SC-04 review** (`review-harness-code-reviewer-c0.md:72`, `-security-c0.md:177`, c1 at 21:33 yesterday). The automated proxy qa cited, `test_exactly_one_guarded_import_in_the_tree`, counts import guards, not fallback branches — it passes while the criterion fails. **This is the seventh verify-method defect.** Mitigating: the branch is confined to the one-session bootstrap grant, the code argues its case in-line, and it closed a real fail-open. It is a defensible *decision* — but it is not the criterion, and no D-NN records it. |
| SC-05 | automated | **met** | `test-check-domain.py:103` pair passes: subprocess against the real `check-domain.sh`, inherited env, bare `python3` inside the hook, no `PYTHONPATH` override — permitted write exit 0 AND forbidden exit 2 from one manifest. Suite re-run at HEAD. |
| SC-06 | automated | **met** | `test-bash-write-guard.py:143` same paired shape, same context. Corroborated live: this session's own `> $TMP/...` redirect outside my domain was **blocked by the guard** mid-goal-check. |
| SC-07 | inspection | **met** | `.claude/skills/harness-init/SKILL.md:38` "the seven prerequisites", `:45` `python3 -c 'import yaml'`, `:48` "STOP", `:53-55` the runnable PEP-668 pair. Second half: `git ls-files` and `ls` on both worktree and main checkout show **no** `requirements.txt` / `pyproject.toml` / `package.json` at root. Blemish: `:49-50` now asserts "there is no line-scan fallback anywhere in `bin/`", which `check-domain.sh:319` contradicts. |
| SC-08 | automated | **met** | `test-check-domain.py:284-317` drives the real hook with PyYAML hidden by a shadowing `yaml.py`: first invocation exits 0, marker written, and the install command is asserted on the **parsed `systemMessage`** channel (`:308`), not merely on stderr. All pass at HEAD. |
| SC-09 | uat | **met — the pass still stands** | Diffed `fd42409..3cf20b0`. `_marker_path` and `_resolve_identity` are **byte-identical**; `require_or_bootstrap`'s expiry decision is semantically identical (`return recorded == identity` → `if recorded == identity: return True` … `return False`). All changes are **additive output** (stderr reasons, `systemMessage`) plus grant-side scoping in the hooks; both hooks still open with `if not require_or_bootstrap(root): sys.exit(2)`. U-05's mechanism is unchanged, so **no re-run is required**. One caveat: U-05 observed a *silent* block, and the block now prints — a change in the direction the UAT itself asked for, unit-locked by `test-check-domain.py:333`. |
| SC-10 | automated | **met** | `test_bare_date_scalar_stays_str` and `test_int_and_bool_resolvers_are_not_stripped` (`test-harness-yaml.py:157,166`) pass; `test-check-state.py`'s fixture carries `cycles_used: 0` as a **YAML int** through the real script and the INV-7 `.isdigit()` path without raising. Caveat: `receipt-…-typed-value-sweep.md`'s `file:line` anchors are stale by ~9-11 lines at HEAD, and it is an *inspection* artifact for an *automated* SC — not admissible on its own. |
| SC-11 | inspection | **met** | I re-derived rather than accepting a reviewer's word: every `check(...)` label in `test-gh-sync.py` matched against the subcommand its nearest preceding `run([...])` invokes — all 57 agree (`abandon` labels invoke `abandon`, `ship`→`ship`, `backlog`→`backlog`, `close-task`→`close-task`). **Issue #12 is refuted.** |
| SC-12 | automated | **met** | `run-unit-tests.sh` at HEAD: **exit 0, 12 PASS, 0 FAIL, 0 MISCONFIGURED**, ≥ the 9-suite baseline. The five `skip` string matches are test-case *names* about gh-sync's SKIP behaviour; the runner emits no skip mechanism (`grep -n skip run-unit-tests.sh` → nothing). |
| SC-13 | inspection | **met** | Re-derived, not read: ran the pre-change regex and `safe_load` over each real `feature.yaml` at HEAD — FEAT-01 1/1, FEAT-02 4/4, FEAT-03 19/19, FEAT-04 15/15, FEAT-05 4/4, **ids identical set-for-set, zero drops**. Honest limit (already recorded at `STATE.md:106`): FEAT-03/FEAT-04's *pre-repair* files cannot parse at all, so the "before" side is a **post-repair** baseline, not a true pre-change one. |
| SC-14 | automated (unit) | **met as written, with a real residual hole** | `test-harness-yaml-corpus.py` passes 8/8, is in `run-unit-tests.sh`'s `SCRIPTS` array (position 11), scans **12 files** = every `.harness/**/*.yaml` (`find` agrees), names `file:line:column`, and carries four known-bad fixtures so it cannot go vacuously green. **Two defects:** (a) the negative case labelled "detects a duplicated top-level key" feeds `cost: 1\nfoo: [unclosed\n` — an unclosed flow sequence, **not a duplicate key**; (b) consequently the gate uses `yaml.safe_load`, which resolves `cost: 1\ncost: 2` to `{cost: 2}` silently, while the harness's own `harness_yaml.load_str` raises `DuplicateKeyError` on it — verified both. So a duplicate-key `.harness` file passes the corpus gate and then breaks `check-state.sh` and both hooks. SC-14's literal text says `safe_load`, so it is met; REQ-08's intent is not fully served. |

## REQ coverage

REQ-02 (SC-01), REQ-03 (SC-07), REQ-04/05 (SC-08, SC-09), REQ-06 (SC-10), REQ-07 (SC-02, SC-13) all
traced. **REQ-01 is partial on two counts**: `cost-report.py:196`'s `^cost:` splice remains (sanctioned
by D-04, writers stay line-based) and `check-domain.sh:319`'s key scan is new. **REQ-08 partial** —
see SC-14(b).

## What would settle the two partials

- **SC-03 / SC-04:** either remove `check-domain.sh:318-335`'s scan, or amend the BRIEF with a D-NN
  that carves out "parser-unavailable bootstrap session" and re-state SC-04 accordingly. No review
  has ever seen this code; the c1 panel closed 14 hours before it was written.
- **SC-14(b):** point the corpus gate at `harness_yaml.load_file` instead of `yaml.safe_load`, and
  give the mislabelled negative case a real duplicate-key fixture.
- **SC-02:** record or prune the two orphaned FEAT-05 run dirs so the output matches the stated shape.

## Process notes for the ship decision

- `4092b38`, `ff5ea45`, `222412a` — three code commits, two of them `[high]` fixes — landed **after**
  all four review artifacts and after qa-c1. They carry regression tests (all green at HEAD), but no
  independent eyes.
- Amendment 2 honoured: nothing here credits or faults `225cc98`.
- **Doc drift the propagation checker did not catch.** `check-docs.sh` exits **0** (measured), while
  `harness-init/SKILL.md:49` states "there is no line-scan fallback anywhere in `bin/`" and
  `CLAUDE.md`'s Constraints say the same. Both are false at HEAD. If the user rules to keep
  `check-domain.sh:318-335`, those two sentences need amending with it.
- SC-01's "…and exit 0 on the pre-change parser" half: I proved the **drop** by running the old
  regex; the **exit 0** follows because an empty `runs` list gives INV-6/7/8 nothing to append. That
  half is inference from code, not a measured exit code.
- Harness defect worth raising: `harness-pm` cannot write a scratch tempdir from Bash (the guard
  denied `> $TMP/...`), which blocks the natural way to run an old-vs-new script comparison. I
  worked around it with in-memory re-derivation; a goal-checker that cannot build a fixture is one
  step from accepting assertions.
