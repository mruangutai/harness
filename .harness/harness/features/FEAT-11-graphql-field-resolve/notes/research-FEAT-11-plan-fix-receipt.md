# Receipt — FEAT-11 plan-fix — three plan-contract must_fix closed

**Path note:** the dispatch asked for `notes/receipt-harness-pm-plan-fix.md`. `check-domain.sh`
BLOCKS that path for `harness-pm` — `receipt-*.md` is granted only to the five dev roles
(`team-config.yaml:145,159,172,185,200`); pm's notes grant is `notes/research-*.md`. Not worked
around. This file is the receipt, at the only path the guard permits.

**BLUF: all three must_fix are closed as text fixes. No task, criterion, requirement or decision was
added, removed or weakened. Both approval fields still read `pending`. `yaml.safe_load` parses
plan.yaml (1 task, 4 decisions), `verify:` is still a `|` block (17 newlines survive the load), and
`check-plan-routes.py` exits 0 with 0 violations.**

## 1. MF-2a — the four falsified-claim sites

### Site A — `plan.yaml:46`, D-04 `because` (one unwrapped line)

OLD (opening clause):
> REQ-02 binds the field and option failures to behave exactly as they do today, and _validate_stations (factory_decompose.py:255-268) plus the Redy typo case (test-factory-decompose.py:1035) read those messages. The wording names a command …

NEW (opening clause, final line `plan.yaml:46`):
> REQ-02 binds the field and option failures to behave exactly as they do today. The wording names a command …

Only the falsified leg was deleted. Leg (i) is kept verbatim. The rest of the value — the
human-instruction argument, "Recorded as a decision … operators learn the string …", the "ACCEPTED,
not resolved" sentence and the awkward-row point — is byte-for-byte unchanged (exact-string
replacement of the opening clause only). No new leg was added: the raising-dependency was **not**
introduced here, per the ruling.

### Site B — `plan.yaml:202-204` (was `:201-202`), inside T-01 `intent:`

OLD:
> D-04: keep that next_step byte-identical to the two
> existing sites at factory_gh.py:206-210 and :251-256, so _validate_stations and the Redy
> typo case see the same text they see today. Do not tidy it.

NEW:
> D-04: keep that next_step byte-identical to the two
> existing sites at factory_gh.py:206-210 and :251-256, because operators learn the string
> and a reword is expensive to undo. Do not tidy it.

The D-04 instruction, the `:206-210` / `:251-256` citations and "Do not tidy it." are intact.

### Site C — `BRIEF.md:20-22` (Goal), aligned to `DESIGN.md:27-32`

OLD:
> Nothing about the factory's observable behaviour changes: the station-name and option-name error
> paths that `_validate_stations` and the `Redy` typo case depend on behave exactly as they do today.

NEW (final lines 20-22):
> Nothing about the factory's observable behaviour changes: the station-name and option-name error
> paths behave exactly as they do today, same error type and same named value. What
> `_validate_stations` depends on is that a missing field still **raises** — it propagates that error
> without reading its text.

### Site D — `BRIEF.md:61-66`, SC-04's justification

OLD trailing clause:
> so `_validate_stations` and the `Redy` typo case are unaffected.

NEW trailing clause:
> and `_validate_stations` is therefore unaffected: it propagates `project_field_options`' `GhError`
> without reading its text (`factory_decompose.py:255-268`), so what it depends on is that a missing
> field still raises. The `Redy` case is an option typo whose operator-facing message
> `_validate_stations` builds itself (`factory_decompose.py:264-268`), and it never reaches
> `factory_gh` at all.

No fifth site. The wide enumeration is the lead's; my own two-token check —
`grep -n "Redy\|_validate_stations"` over both files at final state — finds **zero** surviving
instances in `plan.yaml` and exactly the four rewritten lines in `BRIEF.md` (`:21, :62, :64, :65`).

## 2. SC-04's testable clauses — byte-identical

BEFORE:
> A field the board does not offer raises `GhError` naming the field; an option the field does
>   not offer raises `GhError` naming the option. Both messages still name the field/option value,

AFTER (`BRIEF.md:60-61`):
> A field the board does not offer raises `GhError` naming the field; an option the field does
>   not offer raises `GhError` naming the option. Both messages still name the field/option value,

Identical to the byte, comma included — only the word after the comma changed (`so` → `and`), which
begins the justification. Nothing was added to SC-04's testable content: the MF-2b assertion lives
in Part B only, per the dispatch's scoping over qa's wider bullet. `verify: automated  evidence:
unit` unchanged.

## 3. MF-1 — the sentinel clause, `plan.yaml:77-79`

Replaces the single `git diff --quiet HEAD` line with three clauses in the block's existing style:

```
test "$(python3 -c 'import hashlib,sys;print(hashlib.sha256(open(sys.argv[1],"rb").read()).hexdigest())' .claude/skills/harness/bin/test-factory-decompose.py)" = "f86899df74eca3b40c292b6e0f959ecd72a690ba5c7b92d54fcd847cceb9e5c3" || { echo "FAIL: test-factory-decompose.py content no longer matches its planned hash, so a dependent test file was edited and the public signatures moved"; exit 1; }
test "$(python3 -c 'import hashlib,sys;print(hashlib.sha256(open(sys.argv[1],"rb").read()).hexdigest())' .claude/skills/harness/bin/test-factory-claim.py)" = "44f6cf0a0f379869222f1628e3aeef6126927b043df10f9696437b4bd2e5eaac" || { echo "FAIL: test-factory-claim.py content no longer matches its planned hash, so a dependent test file was edited and the public signatures moved"; exit 1; }
test "$(python3 -c 'import hashlib,sys;print(hashlib.sha256(open(sys.argv[1],"rb").read()).hexdigest())' .claude/skills/harness/bin/test-factory-land.py)" = "f3ca25684b1350f7757b8c5b8ce1c0cd8b7e3d2577130e1c63dab4b8b481ea0f" || { echo "FAIL: test-factory-land.py content no longer matches its planned hash, so a dependent test file was edited and the public signatures moved"; exit 1; }
```

**Non-vacuity, one line:** the hash is taken over the file bytes, so committing before running
`verify:` cannot change it; and it names no commit, ref or merge base, so unrelated FEAT-12 commits
landing on `main` while T-01 is in flight cannot move it either. (`python3` not `shasum`: the block
already calls `python3` twice, and `shasum` is not universally present off Darwin.)

**Evidence chain — commands run and raw output, pm-reported.**

```
$ for f in test-factory-decompose.py test-factory-claim.py test-factory-land.py; do python3 -c 'import hashlib,sys;print(hashlib.sha256(open(sys.argv[1],"rb").read()).hexdigest(), sys.argv[1])' .claude/skills/harness/bin/$f; done
f86899df74eca3b40c292b6e0f959ecd72a690ba5c7b92d54fcd847cceb9e5c3 .claude/skills/harness/bin/test-factory-decompose.py
44f6cf0a0f379869222f1628e3aeef6126927b043df10f9696437b4bd2e5eaac .claude/skills/harness/bin/test-factory-claim.py
f3ca25684b1350f7757b8c5b8ce1c0cd8b7e3d2577130e1c63dab4b8b481ea0f .claude/skills/harness/bin/test-factory-land.py

$ git rev-parse HEAD
92d2723282d1cc1309ffa6e4c163df2b92cb2187

$ git status --porcelain <the three files>
(no output — clean)

$ git diff --stat 835b2976abd649fb814385d7d9b5b19fb7e1431a HEAD -- <the three files>
(no output — identical; exit 0)
```

So the pinned bytes are simultaneously HEAD's and `review_sha` 835b297's.

**Whole-block shell syntax, checked after the edit** (the new clauses nest `'…'` inside `$( )`
inside `"…"`): dumped `tasks[0].verify` from `yaml.safe_load` to a file — 17 lines — and
`bash -n` exits **0**. The loader and the shell parser both accept the block.

**Ran the three clauses as extracted from the loaded YAML:** clean tree → exit 0. Appended one
comment line to `test-factory-land.py` → the clause printed its FAIL message and exited 1; file
restored, `git status --porcelain` empty afterwards. (The old clause's post-commit vacuity is qa's
measured result; nothing was committed in this run.)

Stale self-reference fixed at `plan.yaml:393-394`: "The verify command fails the task if any of them
shows a diff" now reads "carries the sha256 of each of the three files as planned and fails the task
if any of them no longer matches." A new verify-note paragraph at `plan.yaml:410-422` records the
baseline (hashes observed at 92d2723, byte-identical to `review_sha` 835b297), both defeats, and
that a legitimate unrelated edit reddening the clause is correct behaviour.

**The new property the pin introduces, stated plainly:** a legitimate unrelated edit to any of the
three sentinel files before T-01 builds will redden T-01's verify. What keeps that from happening is
already recorded and already the lead's — `feature.yaml` `peer_feature_collision` has
`overlap_files: none` for FEAT-12, with only `run-unit-tests.sh` shared. This is a note, not a new
question.

## 4. MF-2b — the freeze now has teeth, in rendered form

Confirmed first that `str(exc)` carries `next_step`: `GhError.__init__` calls
`super().__init__(factory_cli.body(what, value, next_step))` (`factory_gh.py:43`). Constructed both
errors live:

```
'project field option not found: NotAnOption — field Station on owner project 3 does not offer it'
'project field not found: NoSuchField — field-list for owner project 3 does not offer it'
```

**Option string — `plan.yaml:281-293`**, appended to the option-not-offered bullet:

> ALSO ADD the D-04 freeze assertion, which exists nowhere in the tree today and is why the freeze
> can currently be reworded green: assert that str(exc) contains the RENDERED next_step for this
> case's own arguments, byte for byte. With this case's current arguments - project_field_set("owner",
> 3, "ITEM1", "Station", "NotAnOption") - the exact substring is
> **field Station on owner project 3 does not offer it**
> Assert the RENDERED string, never the braced template: the source wording is an f-string
> (factory_gh.py:251-256), so an assertion written against field {field} on {owner} project {number}
> does not offer it matches nothing, ever, and is a dead assertion that ships green. Substitute this
> case's own owner, number, field and option if you change them. GhError exposes no next_step
> attribute - str(exc) is built by factory_cli.body(what, value, next_step) at factory_gh.py:43 - so
> str(exc) is where the assertion goes.

**Field string — `plan.yaml:304-312`**, appended to the `project_field_options` bullet:

> ALSO ADD the D-04 freeze assertion for the OTHER frozen string, the one this error carries, for the
> same reason and in the same form: assert that str(exc) contains the RENDERED next_step for this
> case's own arguments, byte for byte. With this case's current arguments -
> project_field_options("owner", 3, "NoSuchField") - the exact substring is
> **field-list for owner project 3 does not offer it**
> Rendered, never braced: field-list for {owner} project {number} does not offer it matches nothing,
> ever. This is the correct and only home for that assertion - the resolver raises the field error
> once, in branch (d), and step 5 forbids a second copy of it.

Both assertions are on the rendered substring, both name the case's own owner/number/field/option,
and both instruct substitution if the build agent changes the arguments.

## 5. Approval fields — untouched

- `plan.yaml:5` → `status: pending` (`approved_by: none`, `date: none`)
- `BRIEF.md:177` → `status: pending`

## 6. Post-edit line numbers a downstream document needs

`BRIEF.md ## Verification gaps` heading: **line 129**; section body ends at **line 149**.
The bullet beginning "**The organization path is never exercised against a real org" now starts at
**BRIEF.md:137** (was 132; +5 from the Goal rewrite).

## Out of bounds, respected

No edit to `DESIGN.md`, the grilling artifact, `feature.yaml`, or any DEC-174 file. Q1, Q2 and the
SC-08 advisory (A-1) were not acted on and are not re-raised. No decision, REQ, SC or task added.
`check-docs.sh` / `check-state.sh` not run — `feature.yaml` `gate_status` records both as the lead's.
