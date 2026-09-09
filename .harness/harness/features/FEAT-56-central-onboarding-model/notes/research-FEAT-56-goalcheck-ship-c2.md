# Ship goal-check — FEAT-56, cycle 2

**The feature meets its goal pending only the UAT.** Eleven of the sixteen criteria BRIEF lists are
`met` at `review_sha` 8ff5197f (`SC-01`–`SC-06`, `SC-08`, `SC-10`, `SC-13`, `SC-14`, `SC-16`); three
(`SC-11`, `SC-12`, `SC-15`) are `pending_uat`; **SC-07 is `not_met` on its own words** — `--kind
integration` exits 1, on exactly the six D-14 cases and nothing else; and `SC-09` is **struck in
`BRIEF.md`** — replaced there by SC-11/SC-12 — so it is graded nowhere below. 11 met + 1 not_met +
3 pending_uat + 1 struck = 16. All eleven REQs are covered by a met SC except REQ-06, whose only
automated cover is the red SC-07.

**Every grade below was taken fresh at this pin.** No grade is inherited: `git diff --stat 8ff5197f
HEAD` shows one file changed (`feature.json`, the re-pin record), so the working tree the commands
ran against IS the pinned tree for every source, doc, config and test file. Content criteria were
additionally read through `git show 8ff5197f:<path>`.

## Automated criteria — command run, exit code observed

| SC | Verdict | Evidence |
|---|---|---|
| SC-01 | met | T-10's `verify` block run **verbatim** (string cross-checked against `plan.yaml:1287-1316` — identical, no mismatch); final `check-instruction-paths.py` printed `scanned 62 file(s), 0 violation(s)`; block exit **0** |
| SC-02 | met | `git show 8ff5197f:.claude/skills/harness-init/SKILL.md` carries `git config --get core.hooksPath \|\| echo "(unset)"` at **:74** and `git config core.hooksPath .claude/skills/harness/hooks` at **:81**; `test-hooks-install.py` exit **0** |
| SC-05 | met | `tests/unit/test-fleet-product-config.py` → `18/18 checks passed`, exit **0** (reproduces the `12f74ea8` result, but this is the grade of record) |
| SC-06 | met | `run-unit-tests.sh --kind unit` exit **0**; 4 `^FAIL ` lines, all inside `test-factory-claim-mutation.py` (log 1018-1028), which itself reports `PASS` — the by-design mutation proof. `pool: 8 workers, 34 files`. Baseline matched exactly |
| SC-07 | **not_met** | `run-unit-tests.sh --kind integration` exit **1**. See the honest reading below |
| SC-08 | met | `check-instruction-paths.py` → `scanned 62 file(s), 0 violation(s)`, exit **0**; `check-omp-port.py` → `OMP port surface: ok`, exit **0** |
| SC-10 | met | `python3 -c "import yaml;yaml.safe_load(open('.claude/skills/harness/templates/team-config.yaml'))"` exit **0** |
| SC-13 | met | four clauses, each taken separately — below |
| SC-14 | met | `tests/integration/test-onboarding-split.py` exit **0**, incl. `harness-init/SKILL.md: does not match 'claude --version'` and `does not match '2.1.217'`, and both synthetic ordering controls (correct passes / reversed fails) |
| SC-16 | met | seven separate reads — below |

### SC-07, graded on its own text

Its text is `exits 0 … with no case reporting a skip for a missing skill anchor`. It **exits 1**, so
it is `not_met`. Do not read it as green.

The failing set is EXACTLY the accepted six, all in `test-check-plan-routes.py`, all one cause:
`case_04`, `case_05`, `case_15`, `case_17` (each printing `MANIFEST …/harness/.harness/team-config.yaml`)
and `case_19d`, `case_19d2` (each printing the `DEVIATION … .harness/team-config.yaml differs from`
line). The seventh `^FAIL` line, `FAIL test-check-plan-routes.py`, is `run_pool.py`'s per-file
rollup, not a case. `pool: 8 workers, 51 files, 70.81s`. Independently corroborated: bare
`check-plan-routes.py` reports `1 violation(s) across 5 plan(s)`, exit 1, that one violation being
the same team-config.yaml deviation. **No second violation of any kind, and no case reporting a skip
for a missing skill anchor** — the ~18 `skip` matches in the log are all unrelated assertion text.

D-14 is the operator's standing acceptance of that single owner-manifest deviation; it expires at
merge, when the owner manifest becomes this branch's manifest. It is disclosed in `BRIEF.md:324-335`
(`## Verification gaps`, "One gate is KNOWN-RED on this branch until merge, by construction"). The
grade stays red; the acceptance is why the red does not block ship.

### SC-13 — four clauses, four verdicts

1. `sync-command-adapters.py --check` exit **0**.
2. Each door asserted alone via `git cat-file -e 8ff5197f:` — `.omp/commands/harness.md` (119 lines),
   `harness-plan.md` (37), `harness-ship.md` (35), `harness-grilling.md` (15). Four EXISTS, no count used.
3. `test-sync-command-adapters.py` exit **0**, `15/15 cases passed`, carrying `ok orphan Claude-only
   door fails --check` and `ok orphan failure names the file`.
4. `test-check-omp-port.py` exit **0**, `36/36 cases passed`, carrying `ok harness-plan.md missing is
   named in check-omp-port output` plus the same for `harness-ship.md` and `harness-grilling.md`.

### SC-16 — seven reads, one per file

`cli_min_version` absent from the loaded mapping of all five configs at the pin:
`.harness/harness.json` (19 keys), `templates/harness.json` (16), `templates/examples/harness.kaya-ai.json`
(7), `.harness/team-config.yaml` (8), `templates/team-config.yaml` (8). Both YAML blobs also match
neither `cli_min_version` nor `floor for the spawn env vars` (grep count 0 each). Docs:
`BUILD.md` matches `cli_min_version` **0 times**; `DECISIONS.md` matches it at **:977** and the band
row `2.1.172` at **:962** — both inside DEC-83, which spans `:953-991`.

## Inspection criteria — re-confirmed at THIS pin, one file at a time

**SC-03 — met. Six sites, six citations** (`git show 8ff5197f:.claude/skills/harness/bin/…`):

| Site | Citation |
|---|---|
| `check-instruction-paths.py` | **:18** — `MAIN_SESSION_ONLY` lists `"harness-add-repo"` |
| `check-state.sh` | **:111**, **:287** (unconfigured/half-onboarded clone → `/harness-init` *in this clone*), **:408**, **:2375** (both `--upgrade`). Four remedies, zero registration ones |
| `check-domain.sh` | **:386-388** — "That path is the control plane's own manifest; a product repository never carries one. Run /harness-init in the control-plane clone." |
| `upgrade-config.py` | docstring **:2-6** (control-plane clone; a fleet member's copy must be committed to its default branch); remedies **:191-192** and **:234-236** |
| `gh-sync.py` | **:255-256** — "for a fleet member, that file lives in the member's own repository on its default branch" |
| `layout_migration.py` | **:122-131** — "The fleet declaration is the one file only the control plane carries: products are DECLARED IN it, never holders OF it", above `MARKER = .harness/factory/fleet.yaml` |

**SC-04 — met. 23 files, 23 citations.** Names the right artifact: `commands/harness.md` **:14-18**
(init → add-repo → `/harness-plan`); `commands/harness-grilling.md` **:8**;
`harness-grilling/SKILL.md` **:23**; `templates/README.md` **:3,:8-12,:21**; `templates/harness.json`
**:2,:166**; `templates/team-config.yaml` **:3**; `references/github-mirror.md` **:15,:18,:23**;
`docs/SPEC.md` **:134,:136,:148,:462**; `docs/BUILD.md` **:380,:384,:960**; `docs/DECISIONS.md`
**:7023** (DEC-221, the new entry); `docs/DECISIONS-INDEX.md` **:221**; `docs/org.html`
**:328-329**; `README.md` **:192**; `.harness/README.md` **:6,:9,:19,:86-87**;
`.omp/agents/harness-dev-ops.md` **:53,:55** and its `.claude/agents/` adapter **:52,:54**.

Seven files in the union correctly name **neither** artifact, and for six of them that is a
*measured removal*, not an omission — each carried a wrong onboarding claim at `12f74ea8` and now
points at `/harness-plan`: `commands/harness-plan.md` (`12f74ea8:18-19` routed to `/harness-init`
"including registration in fleet.yaml" → now **:19** `/harness-plan`); `templates/BRIEF.md`
(`:1` → `/harness-plan writes the first draft`); `templates/PLAN.md` (`:2`);
`templates/DESIGN.md` (`:5` → `Established by /harness-plan`);
`.omp/agents/harness-visual-designer.md` **:42** and its adapter **:41** (`Established under
/harness-plan`). The seventh, `commands/harness-ship.md`, matched nothing at either pin — it is in
the union for the adapter regeneration, and vacuously conforms.

## UAT criteria

`SC-11`, `SC-12`, `SC-15` → **pending_uat**. Not met and not failed by me. Script:
`notes/uat-FEAT-56-c2.md`.

## REQ coverage — every REQ by id

| REQ | Covered by | Verdict |
|---|---|---|
| REQ-01 | SC-14 (met), SC-11 (pending_uat) | covered — and the substance holds: `harness-init/SKILL.md:3,:9,:242` names `harness-add-repo` as the artifact owning registration |
| REQ-02 | SC-02 (met) | covered |
| REQ-03 | SC-03 (met), SC-08 (met) | covered |
| REQ-04 | SC-04 (met) | covered |
| REQ-05 | SC-05 (met) | covered |
| REQ-06 | SC-06 (met), **SC-07 (not_met)** | covered by SC-06 only; the integration half is red under D-14 |
| REQ-07 | SC-01 (met), SC-12 (pending_uat) | covered — substance verified beyond SC-01's verify: the skill carries `## Preflight` (**:26**), the three ordered steps (**:43, :81, :96**), the Issues mirror and board (**:96, :110**), and closes on `/harness-plan` (**:152**) |
| REQ-08 | SC-14 (met) | covered |
| REQ-09 | SC-13 (met), SC-15 (pending_uat) | covered |
| REQ-10 | SC-13 clauses 3-4 (met) | covered |
| REQ-11 | SC-16 (met) | covered — substance verified: the band survives in `BUILD.md:88-93` (`2.1.172 – 2.1.216`) as well as in DEC-83 |

## The three closing answers

1. **Is every REQ covered by a met SC?** Yes for ten of eleven. **REQ-06** is the exception: its
   automated cover splits into SC-06 (met) and SC-07 (`not_met` under D-14). No REQ's *only* cover is
   `pending_uat` — REQ-01, REQ-07 and REQ-09 each additionally hold a met automated criterion.
2. **Any SC met in LETTER while its REQ is unmet in SUBSTANCE?** No — I looked at the three most
   exposed pairs and each substance claim holds at the pin (REQ-01's naming, REQ-07's five named
   parts, REQ-11's band survival; all cited above). One readability wart, not a substance gap:
   `commands/harness-plan.md:19` now reads "route to `/harness-plan` per the Gate check in step 0" —
   a self-reference, because the real routing gate lives in `commands/harness.md:14-18` which
   harness-plan.md delegates to. Advisory, not a finding.
3. **Anything TRUE that BRIEF never asked for?** Two, both **new, not covered**, and neither adopted
   by me. (a) The `.omp/commands/` doors now carry a **delegation guard** — four cases in
   `test-check-omp-port.py` assert no `.omp/commands/*` door delegates to `.claude/commands` — landed
   in the pin commit itself; BRIEF's SC-13 asked only for existence plus a reddening check. (b) The
   authoring direction **inverted for Claude Code**: `.claude/commands/*.md` are now generated
   (banner at `commands/harness-plan.md:1`, "do not edit"), with `.omp/commands/` canonical. REQ-09
   asked for reachability under OMP, not for Claude's doors to become derived artifacts. Both are
   consistent with DEC-221's canonical-door-root ruling. **Recommendation: report both to the
   operator in the briefing as delivered-beyond-brief facts; adopt neither as a criterion.**
