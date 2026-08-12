# FEAT-14 plan revision — one board status vocabulary — 2026-08-11

**BLUF.** The revision landed. `phase` and `status` collapse into one `status` field carrying the six
board columns. Two required gates were going dark and now each has a task and a criterion: T-11
(`check-plan-routes.py`) and T-12 (INV-17). The plan `safe_load`s at **12 tasks / 13 decisions** and
`check-plan-routes.py` reports **0 violations across 1 plan**. `approval.status` is `pending`.

Two things the orchestrator must fix — outside my grant, reported not touched:
`STATE.md` and `notes/handoff-plan.md`. Details at the end.

---

## 1. HEAD, measured

```
$ git rev-parse HEAD
a29ad06b3d8b972ce0c9ad0717cb2f12473b455f
```

`lanes.resolved_at` re-pinned from `06ae963` to `a29ad06`.

## 2. check-plan-routes.py on the revised plan

```
$ CLAUDE_PROJECT_DIR=/Users/molchairuangutai/GitHub/harness \
    python3 .claude/skills/harness/bin/check-plan-routes.py \
    .harness/features/FEAT-14-feature-json-schema/plan.yaml
OK T-01 granted to harness-backend-dev, harness-dev-ops
OK T-02: declared main-session-direct (.claude/skills/harness-init/SKILL.md, CLAUDE.md ungranted)
OK T-03 granted to harness-dev-ops
UNRESOLVED-GLOB T-04 .harness/features/*/feature.yaml
DEVIATION T-04 .harness/features/FEAT-14-feature-json-schema/feature.yaml granted to harness-orchestrator but declared main-session-direct
OK T-05 granted to harness-backend-dev, harness-dev-ops
DEVIATION T-06 .claude/skills/harness/bin/check-state.sh, .claude/skills/harness/bin/check-domain.sh, .claude/skills/harness/bin/validate-digest.py, .claude/skills/harness/bin/test-check-state.py, .claude/skills/harness/bin/test-check-domain.py, .claude/skills/harness/bin/test-validate-digest.py granted to harness-backend-dev, harness-dev-ops but declared main-session-direct
OK T-07: declared main-session-direct (.claude/skills/harness/templates/feature.json, .claude/skills/harness/templates/gitignore.snippet, .claude/skills/harness/templates/harness.json, .claude/skills/harness/templates/team-config.yaml, .claude/skills/harness/SKILL.md, .claude/skills/harness-team/SKILL.md, .claude/skills/harness-spec-driven/SKILL.md, .claude/agents/harness-orchestrator.md, .claude/commands/harness.md, .harness/team-config.yaml ungranted)
UNRESOLVED-GLOB T-08 .harness/features/*/feature.yaml
DEVIATION T-08 .harness/features/FEAT-14-feature-json-schema/feature.yaml granted to harness-orchestrator but declared main-session-direct
OK T-09 granted to harness-documentor
OK T-10 granted to harness-documentor
OK T-11 granted to harness-backend-dev, harness-dev-ops
DEVIATION T-12 .claude/skills/harness/bin/check-state.sh, .claude/skills/harness/bin/test-check-state.py granted to harness-backend-dev, harness-dev-ops but declared main-session-direct
0 violation(s) across 1 plan(s)
```

**Violations 0. Plan count 1** (this plan only; the tree-wide run below is the other number).

### The one departure from the dispatch, and why the dispatch's own tie-breaker chose it

Item 7 said to make T-04/T-08's `files:` lists consistent with the 17-feature corpus and **verify
against `check-plan-routes.py`**. Enumerating all 17 literal paths does **not** pass:

```
VIOLATION T-04: 54 machine-field lines — budget is 50 per task (DEC-182). ...
VIOLATION T-08: 61 machine-field lines — budget is 50 per task (DEC-182). ...
```

`BUDGETED_FIELDS` counts one line per `files:` entry, so 17 literals is 17 lines. **Accuracy note:
the original 14-path list measured exactly 50 — at the cap, with zero headroom** — so the three new
paths were not the whole story; my own `verify:` additions consumed part of it too. 14 was never
comfortable. Both lists are now
the glob `.harness/features/*/feature.yaml` **plus one literal anchor** (`FEAT-14`'s own path) kept
solely so the checker can resolve a lane and print the `DEVIATION` proof — a glob-only list produces
`UNRESOLVED-GLOB` and **no lane assertion at all**. The `lanes:` block already locks
`.harness/features/*/feature.yaml` to `main-session-direct`, so DEC-179 is satisfied at any corpus
size, and both tasks' `intent:` already declared the glob as the operating set. This did not re-open
the glob mechanism and did not re-derive the count.

## 3. safe_load counts

```
$ python3 -c "import yaml; d=yaml.safe_load(open('.../plan.yaml')); ..."
safe_load OK
tasks: 12
decisions: 13
task ids: ['T-01'..'T-12']
decision ids: ['D-01'..'D-07','D-09','D-10','D-11','D-12','D-13','D-08']
approval: {'status': 'pending', 'approved_by': None, 'date': None}
resolved_at: a29ad06
every task has traces/change_type/execution_mode/verify/intent/files
```

Success criteria live in `BRIEF.md`: **18** (SC-01..SC-18), 9 REQs, each SC exactly one `verify:`.

**Two `safe_load` failures were found and fixed during the pass** — plain scalars containing `": "`,
which YAML truncates or rejects. Both were in prose I had just written (`D-11`, `D-12`). This is
Expertise G-12's sibling and worth the reminder: a colon-space inside a plain scalar is a parse
error, not a silent truncation, so it fails loud — but only if you actually reload the file.

## 4. check-domain.sh --resolve, per new or changed literal path

```
.harness/features/FEAT-15-domain-product-base/feature.yaml     => harness-orchestrator
.harness/features/FEAT-16-factory-per-repo-board/feature.yaml  => harness-orchestrator
.harness/features/FEAT-17-guard-boundaries/feature.yaml        => harness-orchestrator
.claude/skills/harness/bin/check-plan-routes.py                => harness-backend-dev harness-dev-ops
.claude/skills/harness/bin/test-check-plan-routes.py           => harness-backend-dev harness-dev-ops
.claude/skills/harness/bin/check-state.sh                      => harness-backend-dev harness-dev-ops
.claude/skills/harness/bin/test-check-state.py                 => harness-backend-dev harness-dev-ops
```

Lanes locked accordingly: the three feature paths resolve to `harness-orchestrator`, which owns only
its own feature dir, so the `lanes:` row keeps them `main-session-direct` (unchanged). T-11's two
paths resolve to team and T-11 is `execution_mode: team`. T-12's two resolve to team **but
`check-state.sh` is a DEC-174 carve-out**, so T-12 is `main-session-direct` with the carve-out named
in `execution_reason` — same lane as T-06.

## 5. STEP ZERO — every reader of `status` / `phase`, and its disposition

The dispatch's literal scan — `grep -rn 'phase\|status'` over `bin/`, `.claude/hooks/`,
`.github/workflows/` — returns **183 lines**, and it is dominated by matches that carry none of this
vocabulary: `gh auth status`, subprocess *exit status*, HTTP `"status":"422"`, and `check-domain.sh`'s
own `_domain_phase` / *shape phase* flag. Pasted below verbatim is the **narrowed reader scan**, which
is the one that answers the question — every declaration, read, path-join and fixture of a feature's
`phase`/`status`, plus every hardcoded `feature.yaml`, with those four noise classes filtered out.
**247 lines**, every one of them dispositioned in the table that follows.

<details>
<summary>Verbatim: <code>grep -rn "get(\"phase|get('phase|PHASE_ORDER|SHIPPED_STATUSES|phase:|status:|feature\.yaml" .claude/skills/harness/bin/ .claude/hooks/ .github/workflows/ | grep -v 'auth status|exit status|"status":"4|_domain_phase|shape phase|domain phase'</code> — 247 lines, <code>bin/</code> is <code>.claude/skills/harness/bin/</code></summary>

```
bin/test-harness-yaml-corpus.py:11:  FEAT-03/feature.yaml:97        a sequence item opening with a backtick, a YAML
bin/test-harness-yaml-corpus.py:13:  FEAT-04/feature.yaml:77        `re-verified by me: presence 2` — a `: ` inside a
bin/test-harness-yaml-corpus.py:14:  FEAT-05/feature.yaml:55        multi-line plain scalar is read as a mapping key.
bin/test-harness-yaml-corpus.py:20:`FEAT-05/feature.yaml` was written the SAME DAY by an agent, so this is live
bin/test-validate-digest.py:118:  sc_status: []
bin/test-validate-digest.py:144:  sc_status: []
bin/test-validate-digest.py:165:  sc_status: []
bin/test-validate-digest.py:183:  sc_status: []
bin/test-validate-digest.py:265:  sc_status:
bin/test-validate-digest.py:287:  sc_status: []                   # [] if no goal-check ran
bin/test-validate-digest.py:332:  sc_status: []
bin/test-validate-digest.py:354:  sc_status: []
bin/test-validate-digest.py:374:  sc_status: []
bin/test-validate-digest.py:393:  sc_status: []
bin/test-validate-digest.py:427:  sc_status: []
bin/test-validate-digest.py:453:  sc_status: []
bin/test-validate-digest.py:478:  sc_status: []
bin/test-validate-digest.py:499:  sc_status: []
bin/test-validate-digest.py:625:  sc_status: []
bin/test-validate-digest.py:649:  sc_status: []
bin/test-validate-digest.py:670:  sc_status: []
bin/test-validate-digest.py:691:  sc_status: []
bin/test-validate-digest.py:717:  sc_status: []
bin/test-validate-digest.py:746:  status: shipped
bin/test-validate-digest.py:753:artifact: .harness/features/FEAT-01/feature.yaml
bin/test-validate-digest.py:761:  status: in_progress
bin/test-validate-digest.py:773:artifact: .harness/features/FEAT-01/feature.yaml
bin/test-validate-digest.py:818:  sc_status: []
bin/test-validate-digest.py:879:  sc_status: []
bin/test-validate-digest.py:1043:  sc_status: []
bin/test-check-plan-routes.py:226:            "  status: pending\n"))
bin/test-check-plan-routes.py:244:            "  status: pending\n"))
bin/test-check-plan-routes.py:262:            "  status: pending\n"))
bin/test-check-plan-routes.py:274:            "  status: pending\n"))
bin/test-check-plan-routes.py:284:            "  status: pending\n"))
bin/test-check-plan-routes.py:593:approval: {status: approved}
bin/test-check-plan-routes.py:602:    status: pending
bin/test-check-plan-routes.py:753:    # the number moves. `status: true` is a BOOL and `execution_reason: ""` is EMPTY on
bin/test-check-plan-routes.py:769:        "    status: true\n"
bin/test-check-plan-routes.py:832:            with open(os.path.join(fd, "feature.yaml"), "w") as f:
bin/test-check-plan-routes.py:833:                f.write(f"feature_id: FEAT-A\nstatus: {status}\n")
bin/test-check-plan-routes.py:845:        r = run(project_dir=td)              # no feature.yaml at all
bin/test-check-plan-routes.py:849:    # A feature.yaml THAT PARSES BUT IS NOT A MAPPING. This is the case the four statuses
bin/test-check-plan-routes.py:863:                        ("status_is_a_list", "status:\n  - shipped\n"),
bin/test-check-plan-routes.py:864:                        # A MAPPING WITH NO `status:` KEY AT ALL. Two shapes REACH
bin/test-check-plan-routes.py:882:            with open(os.path.join(fd, "feature.yaml"), "w") as f:
bin/test-check-domain.py:226:    r = fire(root, sp, "run_id: r1\nstatus: complete\n")
bin/test-check-domain.py:247:    r = fire(root, sp, "run_id: [unclosed\nstatus: complete\n")
bin/test-check-domain.py:392:                      content="run_id: r1\nstatus: complete\n")
bin/test-check-domain.py:957:# Measured before the fix, ONE 400-line feature.yaml against a 200-line budget:
bin/test-check-domain.py:980:    fy = os.path.join(fdir, "feature.yaml")
bin/test-check-domain.py:981:    rel_fy = ".harness/features/FEAT-X/feature.yaml"
bin/test-check-domain.py:1041:        post(f"feature.yaml at {_n} lines {'IS' if _want else 'is NOT'} over the 200 budget",
bin/test-check-domain.py:1051:        post(f"feature.yaml with {_c} comment lines {'IS' if _want else 'is NOT'} over 20",
bin/test-check-domain.py:1091:    with open(os.path.join(wt, "feature.yaml"), "w") as f:
bin/test-check-domain.py:1156:    _wfy = os.path.join(_wt, ".harness", "features", "FEAT-W", "feature.yaml")
bin/test-check-domain.py:1254:            f.write("schema_version: 1\nrun_id: pad\nstatus: complete\n")
bin/factory_decompose.py:13:written back into <feature-dir>/feature.yaml's `factory` block ATOMICALLY, so an interrupted
bin/factory_decompose.py:19:The only harness file this tool writes is feature.yaml, and it is spliced surgically —
bin/factory_decompose.py:95:    path = os.path.join(feat_dir, "feature.yaml")
bin/factory_decompose.py:182:    """Splice the `factory:` block into feature.yaml SURGICALLY and ATOMICALLY.
bin/factory_decompose.py:186:    feature.yaml. feature.yaml itself is opened only for reading, never in a truncating mode:
bin/factory_decompose.py:189:    path = os.path.join(feat_dir, "feature.yaml")
bin/factory_decompose.py:201:    fd, tmp = tempfile.mkstemp(prefix=".feature.yaml.", suffix=".tmp", dir=dirpath)
bin/test-harness-yaml.py:462:  status: approved
bin/test-harness-yaml.py:471:    status: pending
bin/factory_claim.py:20:issue number through that feature's `feature.yaml` `factory.issues` map, and finished-ness is
bin/factory_claim.py:88:    """Caches each feature's plan.yaml and feature.yaml so a single poll reads each file once —
bin/factory_claim.py:116:        """The blocker's issue number from that feature's feature.yaml `factory.issues` map, or
bin/factory_claim.py:119:            path = os.path.join(self._features_root, feature, "feature.yaml")
bin/factory_claim.py:136:    ("unresolvable", dep) — a depends_on entry has no feature.yaml issue-map entry;
bin/factory_claim.py:172:            f"issue #{num} depends_on {dep}, which has no recorded issue in feature.yaml "
bin/test-factory-decompose.py:221:    """Build a temporary feature directory: plan.yaml, BRIEF.md, feature.yaml, fleet.yaml.
bin/test-factory-decompose.py:228:    write_text(os.path.join(feat_dir, "feature.yaml"), factory_yaml_extra)
bin/test-factory-decompose.py:256:    write_text(os.path.join(feat_dir, "feature.yaml"), "")
bin/test-factory-decompose.py:288:    doc = yaml.safe_load(open(os.path.join(feat_dir, "feature.yaml"), encoding="utf-8").read())
bin/test-factory-decompose.py:332:    check("(2) feature.yaml records two issue numbers", len(fblock.get("issues") or {}) == 2,
bin/test-factory-decompose.py:334:    check("(2) feature.yaml records two item ids", len(fblock.get("items") or {}) == 2, fblock)
bin/test-factory-decompose.py:337:# 3. a second publish against a fully-recorded feature.yaml mutates and calls nothing
bin/test-factory-decompose.py:395:# 6. feature.yaml carries the issue number after the first creation even when the board
bin/test-factory-decompose.py:407:    check("(6) feature.yaml still carries the created issue number",
bin/test-factory-decompose.py:438:    check("(7) resume: feature.yaml now carries an item id",
bin/test-factory-decompose.py:468:# 9. feature.yaml carrying comments and a github block round-trips those bytes unchanged
bin/test-factory-decompose.py:486:    after = open(os.path.join(feat_dir, "feature.yaml"), encoding="utf-8").read()
bin/test-factory-decompose.py:548:    check("(12) feature.yaml records parent_origin created",
bin/test-factory-decompose.py:562:    check("(13) feature.yaml records parent 777 with parent_origin adopted",
bin/test-factory-decompose.py:697:    check("(20a) feature.yaml records the edge exactly as a successful call would",
bin/test-factory-decompose.py:716:    check("(20b) feature.yaml records NO parent receipt for that task",
bin/test-factory-decompose.py:747:    feature_yaml_path = os.path.join(feat_dir, "feature.yaml")
bin/test-factory-decompose.py:752:            check("(22) os.replace destination is the fixture's feature.yaml",
bin/test-factory-decompose.py:772:            check(f"(22) feature.yaml opened in mode {mode!r}: not truncating", not truncating,
bin/test-factory-decompose.py:786:    check("(22) feature.yaml WAS opened for reading at least once (anti-vacuum)",
bin/test-factory-decompose.py:788:    check("(22) feature.yaml was opened only for reading, never in a truncating mode",
bin/test-factory-decompose.py:793:# SC-20: plan.yaml and BRIEF.md are byte-identical after a publish; feature.yaml is the
bin/test-factory-decompose.py:816:    check("(SC-20) feature.yaml is the only file whose hash changed", changed == {"feature.yaml"},
bin/test-factory-decompose.py:967:    check("(D4-3) feature.yaml records the resolved existing item id",
bin/test-factory-decompose.py:1050:    write_text(os.path.join(feat_dir, "feature.yaml"), "")
bin/test-check-state.py:44:    with open(os.path.join(h, "features", "FEAT-TEST", "feature.yaml"), "w") as f:
bin/test-check-state.py:155:    feature.yaml — matched nothing and dropped the ENTIRE entry. Three invariants then
bin/test-check-state.py:169:        with open(os.path.join(h, "features", "FEAT-TEST", "feature.yaml"), "w") as f:
bin/test-check-state.py:181:    """A feature.yaml that does not parse is a VIOLATION, never a silent skip.
bin/test-check-state.py:192:        with open(os.path.join(h, "features", "FEAT-TEST", "feature.yaml"), "w") as f:
bin/test-check-state.py:196:        print(f"{'ok' if ok else 'FAIL'} - case (f): an unparseable feature.yaml is "
bin/test-check-state.py:222:        # phase: validate with NO handoff-plan.md / handoff-build.md -> INV-17 fires.
bin/test-check-state.py:223:        with open(os.path.join(h, "features", "FEAT-TEST", "feature.yaml"), "w") as f:
bin/test-check-state.py:224:            f.write("feature_id: FEAT-TEST\nphase: validate\n")
bin/test-check-state.py:242:    FEAT-05's own feature.yaml carried `review_sha: none` for its whole plan phase
bin/test-check-state.py:251:        with open(os.path.join(h, "features", "FEAT-TEST", "feature.yaml"), "w") as f:
bin/test-check-state.py:280:        with open(os.path.join(h, "features", "FEAT-TEST", "feature.yaml"), "w") as f:
bin/test-check-state.py:302:    is live, not theoretical: FEAT-06's own feature.yaml is exactly this shape
bin/test-check-state.py:310:        with open(os.path.join(h, "features", "FEAT-TEST", "feature.yaml"), "w") as f:
bin/test-check-state.py:331:    (1) A run that is `status: complete` and carries NO `cost:` block is CLEAN.
bin/test-check-state.py:352:            with open(os.path.join(h, "features", "FEAT-TEST", "feature.yaml"), "w") as f:
bin/test-check-state.py:360:                        "status: complete\n"
bin/test-check-state.py:394:        with open(os.path.join(h, "features", "FEAT-TEST", "feature.yaml"), "w") as f:
bin/test-check-state.py:395:            f.write(f"feature_id: FEAT-TEST\nphase: build\ncycles_used: 2\n"
bin/test-check-state.py:567:    "INV-23" in the output — so raising the feature.yaml budget from 200 to 250 left the
bin/test-check-state.py:578:        ("feature.yaml over", 201, 120, True,  False),
bin/test-check-state.py:591:            with open(os.path.join(fd, "feature.yaml"), "w") as f:
bin/test-check-state.py:596:            got_f = "INV-23 FEAT-TEST/feature.yaml is" in out
bin/test-check-state.py:600:            print(f"{'ok' if ok else 'FAIL'} - case (n/{label}): at {fl} feature.yaml / "
bin/test-check-state.py:602:                  f"[{'feature.yaml' if got_f else ''}{' ' if got_f and got_s else ''}"
bin/test-check-state.py:604:                  f" — wanted [{'feature.yaml' if want_f else ''}"
bin/test-check-state.py:670:approval: {status: approved}
bin/test-check-state.py:679:    status: pending
bin/test-check-state.py:703:            os.remove(os.path.join(fd, "feature.yaml"))
bin/test-check-state.py:704:            with open(os.path.join(fd, "feature.yaml"), "w") as f:
bin/test-check-state.py:705:                f.write("feature_id: FEAT-TEST\nstatus: in_review\n")
bin/test-check-state.py:707:                f.write(PLAN_YAML_OK.replace("status: approved", f"status: {status}"))
bin/test-check-state.py:855:    feature.yaml with no factory key at all, which INV-24 must ignore entirely.
bin/test-check-state.py:868:        with open(os.path.join(d, "feature.yaml"), "w") as f:
bin/test-check-state.py:963:    # widened to it). If INV-24 rejected the same shape, one legal feature.yaml would pass
bin/test-check-state.py:1022:        ("feature.yaml lines",  r"feature\.yaml is \{len\(lines\)\} lines — budget is (\d+)",
bin/test-check-state.py:1024:        ("feature.yaml comments", r"comment lines — budget is (\d+)",
bin/gh-sync.py:31:IDEMPOTENT. `open` records issue numbers into feature.yaml (`github:` block) as it
bin/gh-sync.py:208:# ---------- feature.yaml github block ----------
bin/gh-sync.py:247:    path = os.path.join(feat_dir, "feature.yaml")
bin/gh-sync.py:251:    # OSError into YamlParseError, so a missing feature.yaml reported as "does not
bin/gh-sync.py:305:    trailing comments in FEAT-03's feature.yaml alone). Nothing was removed, so
bin/gh-sync.py:315:    create rule). So the sequence was: milestone created on GitHub -> feature.yaml
bin/gh-sync.py:338:    p = os.path.join(feat_dir, "feature.yaml")
bin/gh-sync.py:466:    receipt: this is a closing action, not a recording one, so `feature.yaml` is untouched."""
bin/gh-sync.py:528:    a closing action, not a recording one, so `feature.yaml` is untouched."""
bin/test-factory-claim.py:231:    blocker naming T-99, which feature.yaml never maps)."""
bin/test-factory-claim.py:237:    write_yaml(os.path.join(demo, "feature.yaml"), {"factory": {"issues": {"T-01": 501}}})
bin/test-factory-claim.py:246:    write_yaml(os.path.join(block, "feature.yaml"), {
bin/check-state.sh:80:    return bool(m) and re.search(r"status:\s*approved", m.group(1), re.I) is not None
bin/check-state.sh:148:for fy in glob.glob(os.path.join(H, "features", "*", "feature.yaml")):
bin/check-state.sh:154:    # and the house style on 45 lines of FEAT-03's feature.yaml — silently dropped the
bin/check-state.sh:158:    # (feature.yaml:63-64) instead of fixing the parser. Same defect class as DEC-123
bin/check-state.sh:166:        bad.append(f"{feat}/feature.yaml does not parse, so INV-6..8 and INV-12 "
bin/check-state.sh:170:        bad.append(f"{feat}/feature.yaml is not a YAML mapping.")
bin/check-state.sh:283:            warn.append(f"{feat}: run dir {rid} exists on disk but feature.yaml does not "
bin/check-state.sh:434:# A feature whose phase: sits past a seam with no handoff note for the crossing lost the
bin/check-state.sh:436:# Only enforced when the feature declares phase: at all, so pre-DEC-159 features stay quiet.
bin/check-state.sh:437:PHASE_ORDER = ["plan", "build", "validate", "ship"]
bin/check-state.sh:439:for fy in glob.glob(os.path.join(H, "features", "*", "feature.yaml")):
bin/check-state.sh:441:    # F-02: parsed, not regex-scanned. `^phase:\s*(\S+)` misses a quoted value and a
bin/check-state.sh:447:        bad.append(f"{feat}/feature.yaml does not parse, so its phase invariants "
bin/check-state.sh:450:    _phase = str(_doc.get("phase", "")).strip() if isinstance(_doc, dict) else ""
bin/check-state.sh:451:    if _phase not in PHASE_ORDER:
bin/check-state.sh:453:    idx = PHASE_ORDER.index(_phase)
bin/check-state.sh:454:    for prev in PHASE_ORDER[:idx]:
bin/check-state.sh:479:# --- INV-18 (DEC-160): a feature with run dirs but no feature.yaml is invisible to
bin/check-state.sh:481:# Observed live: FEAT-03's plan phase ran to completion before feature.yaml existed.
bin/check-state.sh:486:    if os.path.isdir(rd) and os.listdir(rd) and not os.path.isfile(os.path.join(fdir, "feature.yaml")):
bin/check-state.sh:487:        bad.append(f"{os.path.basename(fdir)}: has runs/ but no feature.yaml — the feature is "
bin/check-state.sh:491:# --- INV-23 (DEC-150, mechanized — issue #132): the feature.yaml and STATE.md budgets,
bin/check-state.sh:506:for fy in sorted(glob.glob(os.path.join(H, "features", "*", "feature.yaml"))):
bin/check-state.sh:510:        warn.append(f"INV-23 {feat}/feature.yaml is {len(fl)} lines — budget is 200. It is "
bin/check-state.sh:514:        warn.append(f"INV-23 {feat}/feature.yaml has {nc} comment lines — budget is 20. "
bin/check-state.sh:515:                    f"Narrative commentary does not belong in feature.yaml (DEC-150).")
bin/check-state.sh:587:    # F-02, and this one had a LIVE fail-open the panel reproduced: `status: "complete"`
bin/check-state.sh:588:    # — quoted, legal YAML — does not match `^status:\s*complete`, so `complete` was
bin/check-state.sh:713:    for fy in glob.glob(os.path.join(H, "features", "*", "feature.yaml")):
bin/check-state.sh:726:            bad.append(f"{feat}/feature.yaml does not parse, so INV-21 cannot be "
bin/check-state.sh:750:# A feature.yaml with no `factory` block contributes nothing and is not a violation.
bin/check-state.sh:752:for fy in glob.glob(os.path.join(H, "features", "*", "feature.yaml")):
bin/check-state.sh:820:        # legal feature.yaml pass one invariant and hard-block on its twin (D-03).
bin/test-gh-sync.py:77:status: approved
bin/test-gh-sync.py:95:    open(os.path.join(feat, "feature.yaml"), "w").write(
bin/test-gh-sync.py:96:        f"feature_id: {feat_name}\nstatus: in_progress\n")
bin/test-gh-sync.py:223:    fy = open(os.path.join(feat, "feature.yaml")).read()
bin/test-gh-sync.py:224:    check("issue numbers recorded in feature.yaml",
bin/test-gh-sync.py:240:    # feature.yaml already carried the milestone before the last issue was created:
bin/test-gh-sync.py:306:    fy3 = open(os.path.join(feat3, "feature.yaml")).read()
bin/test-gh-sync.py:318:    open(os.path.join(feat4, "feature.yaml"), "w").write(
bin/test-gh-sync.py:319:        "feature_id: FEAT-05-export-fix\nstatus: in_progress\n"
bin/test-gh-sync.py:335:    fy4 = open(os.path.join(feat4, "feature.yaml")).read()
bin/test-gh-sync.py:364:    fy6 = open(os.path.join(feat6, "feature.yaml")).read()
bin/test-gh-sync.py:376:    open(os.path.join(featA, "feature.yaml"), "w").write(
bin/test-gh-sync.py:377:        "feature_id: FEAT-06-abandon-adopted\nstatus: in_progress\n"
bin/test-gh-sync.py:414:    open(os.path.join(featB, "feature.yaml"), "w").write(
bin/test-gh-sync.py:415:        "feature_id: FEAT-06-abandon-created\nstatus: in_progress\n"
bin/test-gh-sync.py:443:    open(os.path.join(featC, "feature.yaml"), "w").write(
bin/test-gh-sync.py:444:        "feature_id: FEAT-06-abandon-noorigin\nstatus: in_progress\n"
bin/test-gh-sync.py:456:    fyC = open(os.path.join(featC, "feature.yaml")).read()
bin/test-gh-sync.py:470:    open(os.path.join(featD, "feature.yaml"), "w").write(
bin/test-gh-sync.py:471:        "feature_id: FEAT-06-abandon-badfile\nstatus: in_progress\n"
bin/test-gh-sync.py:526:    open(os.path.join(featE, "feature.yaml"), "w").write(
bin/test-gh-sync.py:527:        "feature_id: FEAT-06-abandon-nomilestone\nstatus: in_progress\n"
bin/test-gh-sync.py:561:    open(os.path.join(featG, "feature.yaml"), "w").write(
bin/test-gh-sync.py:562:        "feature_id: FEAT-07-ship-created\nstatus: in_progress\n"
bin/test-gh-sync.py:590:    open(os.path.join(featH, "feature.yaml"), "w").write(
bin/test-gh-sync.py:591:        "feature_id: FEAT-07-ship-adopted\nstatus: in_progress\n"
bin/test-gh-sync.py:617:    open(os.path.join(featI, "feature.yaml"), "w").write(
bin/test-gh-sync.py:618:        "feature_id: FEAT-07-ship-noorigin\nstatus: in_progress\n"
bin/test-gh-sync.py:628:    fyI = open(os.path.join(featI, "feature.yaml")).read()
bin/test-gh-sync.py:644:    open(os.path.join(featJ, "feature.yaml"), "w").write(
bin/test-gh-sync.py:645:        "feature_id: FEAT-07-ship-bodyfile\nstatus: in_progress\n"
bin/test-gh-sync.py:670:    open(os.path.join(featK, "feature.yaml"), "w").write(
bin/test-gh-sync.py:671:        "feature_id: FEAT-07-ship-nobodyfile\nstatus: in_progress\n"
bin/test-gh-sync.py:692:    open(os.path.join(featL, "feature.yaml"), "w").write(
bin/test-gh-sync.py:693:        "feature_id: FEAT-07-ship-emptybodyfile\nstatus: in_progress\n"
bin/test-gh-sync.py:727:open(os.path.join(_d1, "feature.yaml"), "w").write(
bin/test-gh-sync.py:747:open(os.path.join(_d2, "feature.yaml"), "w").write("feature_id: F2\nphase: plan\n")
bin/test-gh-sync.py:749:check("T-06C: a feature.yaml with no github: block returns the default, does not raise",
bin/test-gh-sync.py:764:        ("bare", "feature_id: F1\ngithub:\n  parent: 40\nphase: ship\n"),
bin/test-gh-sync.py:765:        ("trailing comment", "feature_id: F1\ngithub:   # the mirror\n  parent: 40\nphase: ship\n"),
bin/test-gh-sync.py:766:        ("column-0 comment inside", "feature_id: F1\ngithub:\n  parent: 40\n# note\n  milestone: 9\nphase: ship\n"),
bin/test-gh-sync.py:767:        ("no block at all", "feature_id: F1\nphase: ship\n")):
bin/test-gh-sync.py:769:    open(os.path.join(_d, "feature.yaml"), "w").write(_body)
bin/test-gh-sync.py:771:    _txt = open(os.path.join(_d, "feature.yaml")).read()
bin/test-gh-sync.py:779:    check(f"finding 2: save_recorded round-trips a feature.yaml with a {_label}", _ok, _why)
bin/validate-digest.py:173:    # in feature.yaml.
bin/check-domain.sh:427:# does not name, and the one that explains its own evidence: the 226-line feature.yaml
bin/check-domain.sh:429:# 400-line feature.yaml payload: exit 2 as `harness-orchestrator`, exit 0 with no
bin/check-domain.sh:485:    # same 400-line feature.yaml measured exit 0 as `harness-orchestrator` and exit 2 as
bin/check-domain.sh:684:# with ONE 400-line feature.yaml payload against its 200-line budget:
bin/check-domain.sh:692:# own evidence: the 226-line feature.yaml it records was the MAIN SESSION's, so the tool
bin/check-domain.sh:725:    ".harness/features/*/feature.yaml",
bin/check-domain.sh:736:#   1. NO DEDUP. One over-budget feature.yaml, then five unrelated `ls` calls produced
bin/check-domain.sh:799:# rule, which is what this gate is for: `feature.yaml` 200/20 and `CLAUDE.md` 80 are
bin/check-domain.sh:855:            problems.append(f"feature.yaml is {len(lines)} lines — budget is 200. It is data a script "
bin/check-domain.sh:860:                            f"belong in feature.yaml.")
bin/check-domain.sh:967:        # all have one: expertise 150, feature.yaml 200/20, handoff 60, STATE.md 120.
bin/check-plan-routes.py:238:# carries. feature.yaml (200), STATE.md (120), handoff (60) and CLAUDE.md (80) all govern
bin/check-plan-routes.py:386:SHIPPED_STATUSES = ("shipped", "abandoned")
bin/check-plan-routes.py:392:    Reads `feature.yaml`'s `status:` with the real loader. An unreadable or absent
bin/check-plan-routes.py:393:    feature.yaml means NOT shipped — a feature we cannot classify is checked rather than
bin/check-plan-routes.py:399:    feature.yaml holding a YAML sequence reached `doc.get` on a list and raised
bin/check-plan-routes.py:410:    fy = os.path.join(feature_dir, "feature.yaml")
bin/check-plan-routes.py:422:    # `status: shipped  # with a trailing comment` is the live corpus's shape (FEAT-02,
bin/check-plan-routes.py:425:    # SHIPPED_STATUSES, which is the fail-CHECKED direction.
bin/check-plan-routes.py:427:    return bool(token) and token[0] in SHIPPED_STATUSES
bin/check-plan-routes.py:557:            # `status:` is a BORROWED SIGNAL and the honest name for it is era. It means
bin/check-plan-routes.py:559:            # only marker on disk — no feature.yaml carries schema_version — so it is used
```

</details>

The sites that read or assert a feature's `phase`/`status`, and every one of the above resolved:

| Site | Disposition |
|---|---|
| `check-state.sh:437` `PHASE_ORDER`, `:450` phase read, `:451` `continue`, `:453-455` handoff path | **T-12** |
| `check-state.sh:439` INV-17's `feature.yaml` glob | **T-06** (filename only), block otherwise T-12 |
| `check-state.sh:148,486,506,713,752` globs | **T-06** (filename only) |
| `check-plan-routes.py:386` `SHIPPED_STATUSES`, `:392-427` `_is_shipped` | **T-11** |
| `check-plan-routes.py:410` `feature.yaml` path join | **T-05** (filename only) |
| `test-check-plan-routes.py:828-838` status fixture loop, `:862-875` malformed-status cases | **T-11** |
| `test-check-state.py:224` `phase: validate` fixture (INV-17's only case), `:395` `phase: build` | **T-12** (both rewritten around `status`) |
| `test-check-state.py:705` `status: in_review` fixture | **T-12** |
| `test-gh-sync.py:747,764-767` `phase: plan` / `phase: ship` fixtures | **T-05** (fixtures are rewritten to `feature.json` there; the `phase` key must go with them) |
| `test-gh-sync.py` ~12 `status: in_progress` fixture writes (`:96,319,377,415,444,471,527,562,591,618,645,671,693`) | **T-05 item 5** (values, not just filenames) |
| `test-factory-decompose.py` ~20 `feature.yaml` fixture paths, `test-factory-claim.py:237,246` | **T-05 item 5** |
| `test-check-domain.py:980-1156` feature-document fixtures | **T-06** — these now pass through the schema, so accept-cases need legal values |
| `test-check-state.py:44,169,192,251,280,310,352,591,704,868` fixture `feature.yaml` writes | **T-06** (filenames) / **T-12** (the two carrying `phase`) |
| `test-harness-yaml-corpus.py:11-20` four `feature.yaml` citations | **T-05 item 6** — preserved verbatim as historical record, pinned at exactly 4 |
| `test-validate-digest.py:753,773` `artifact:` fixture paths | **T-06 item 3** (rename; they are test inputs) |
| `check-domain.sh:725` `_SWEEP_PATTERNS`, `:855-860` budget message | **T-06 item 2** |
| `factory_decompose.py:95,189,201`, `factory_claim.py:119` | **T-05 items 3-4** (filename only; neither reads status) |
| `gh-sync.py:247, :338` hardcoded `feature.yaml` | **T-05** — see below |
| `harness/SKILL.md:271-272` "Record your phase in `feature.yaml` `phase:`" | **T-07 item 3** (new) |
| `SPEC.md §11.3` `phase:` and four-value `status:` | **T-09** |
| `templates/feature.json` (new) `phase` placeholder | **T-07 item 1** |

### Deliberately untouched, with the reason

- **`check-state.sh:599`** — `str(sdoc.get("status","")).strip() == "complete"`. This is
  **`state.yaml`'s RUN status**, governed by `CHECKPOINT_KEYS` and DEC-154, which this feature puts
  out of scope. `complete` is also one of the old feature-file values (FEAT-10's), so any sweep for
  that literal lands here. Changing it breaks INV-15 and INV-16. **Named in T-12 item 4 so it is
  deliberately skipped rather than accidentally missed.**
- **`validate-digest.py:182-183`** and **`harness-orchestrator.md:69`** — the orchestrator DIGEST
  status enum. **D-13** rules it out of scope with a named reason. T-07 item 3 forbids touching line
  69 explicitly.
- **`branch-create-gate.sh:45`** `g.get("status_field")` — this is `harness.json`'s GitHub board
  field *name*, not a feature's status value. Untouched.
- **`factory_gh.py` / `test-factory-gh.py` / `test-factory-claim.py`** — every hit is `gh auth
  status`, an HTTP `"status":"422"`, or a subprocess exit status. Not this vocabulary.
- **`check-domain.sh:450-494`** `_domain_phase`, `_run_domain` — the hook's own PRE/POST phase flag.
  Unrelated to a feature's lifecycle. Untouched.
- **`test-factory-gh.py:173-183`** `"status": "Ready"` — already board-column shaped; these are
  GitHub Projects fixtures, not feature files. Untouched.

### `gh-sync.py` — the flagged file, resolved

`notes/handoff-plan.md` flags `:247` and `:255-256` as hardcoding `feature.yaml`. Verified at
`a29ad06`: **`gh-sync.py` reads and writes only the `github:` block** (`load_recorded` at `:247`,
`save_recorded` at `:338`). **It contains no reader of `status` or `phase` at all.** So it is a
**filename-rename-only** concern, already fully covered by T-05 item 2, which also replaces the
comment-preserving text splice with a JSON read-modify-write. No new task needed. The prohibited-tool
window in T-04/T-05/T-06/T-07/T-08 already covers the real hazard here: a missing file reads to
`load_recorded` as an empty record and re-files issues that already exist.

## 6. The 17-row migration table, measured from disk at `a29ad06`

| Feature | old `status` / old `phase` | new `status` |
|---|---|---|
| FEAT-01 | `abandoned` / — | `Done` |
| FEAT-02 | `shipped` / — | `Done` |
| FEAT-03-subissue-mirror | `shipped` / `ship` | `Done` |
| FEAT-04-decisions-index | `shipped` / `ship` | `Done` |
| FEAT-05-pyyaml-file-parsers | `shipped` / `ship` | `Done` |
| FEAT-06-team-layer-inv6 | `awaiting_user` / `validate` | `Review` |
| FEAT-07-verify-teeth-batch-probe | `in_review` / `ship` | `Review` |
| FEAT-08-remove-cost-tracking | `awaiting_user` / `ship` | `Review` |
| FEAT-09-plan-time-route-check | `shipping` / `ship` | **`Review`** |
| FEAT-10-software-factory | `complete` / `ship` | **`Done`** |
| FEAT-11-graphql-field-resolve | `awaiting_user` / `ship` | `Review` |
| FEAT-12-end-copy-distribution | `awaiting_user` / `ship` | `Review` |
| FEAT-13-single-issue-board-lookup | `in_review` / `ship` | `Review` |
| FEAT-14-feature-json-schema | `in_progress` / `plan` | `Plan` |
| FEAT-15-domain-product-base | `awaiting_user` / `plan` | **`Plan`** — see below |
| FEAT-16-factory-per-repo-board | `in_progress` / `plan` | `Plan` |
| FEAT-17-guard-boundaries | `in_progress` / `plan` | `Plan` |

**Both operator readings confirmed.** `shipping` → `Review` (built-validated-and-waiting-on-you,
before the PR and before the merge; `Done` means merged and closed). `complete` → `Done`.

**`blocked` → `Review`, stated explicitly** — a blocked feature is waiting on the operator. Verified:
the tree carries `blocked` as a status value **zero** times (the only `blocked` hit under
`.harness/features/*/feature.yaml` is prose inside FEAT-12's file). D-09 records that it is dropped
from the vocabulary deliberately, reversing the earlier keep-it-as-legal-but-unused rationale.

**FEAT-15 is the one row that departs from the ruling's literal wording** (`awaiting_user` → `Review`,
unqualified) and it is flagged as a non-blocking open question. Its `plan.yaml` is `approval:
pending` and its `notes/` holds **zero** handoff notes, so `Review` would assert it crossed the plan
and build seams it has not — a false record, and a fresh INV-17 violation once T-12 lands. `Ready` is
also wrong (`Ready` means signed). `Plan` is the only honest value. T-04 instructs the doer to re-read
its approval block rather than trust the row.

## 7. Expected post-migration route-checked set

Baseline, measured:

```
$ python3 .claude/skills/harness/bin/check-plan-routes.py     # tree-wide, at a29ad06
0 violation(s) across 12 plan(s)
```

Arithmetic over the census: 17 features, **16 carry a plan file** (FEAT-01 has neither `plan.yaml`
nor `PLAN.md`). Currently skipped = 4 `shipped` (FEAT-02/03/04/05) → 16 − 4 = **12**, matching the
run above.

After migration, `Done` skips. `Done` = FEAT-01, 02, 03, 04, 05, 10 — **six features, five of them
with plan files**. So 16 − 5 = **11 plans checked, and 11 ≥ 1**. FEAT-10 leaves the set; FEAT-09 stays
in it. Violations stay **0** (a feature leaving the checked set can only remove findings, and the set
is 0 today).

**The window between T-04 and T-11 was measured, not assumed** — the checker run with the skip tuple
emptied, which is the exact state T-04 leaves it in:

```
$ # SHIPPED_STATUSES = ()  (scratchpad copy)
35 violation(s) across 16 plan(s)
```

The four shipped features' `PLAN.md` files predate the route-check contract (`no files: line`), so
unskipping them is loud. Recorded in T-04 and T-11 so it reads as an expected window inside one PR,
not a regression.

## 8. INV-17 dry-run — the number the criterion rests on

The proposed `STATUS_ORDER` + `SEAM_NOTES` + two-element exemption, applied to all 17 features with
the statuses above:

```
EXEMPT FEAT-01 (Done)
EXEMPT FEAT-02 (Done)
NO VIOLATIONS
violations=0
```

`SEAM_NOTES`: `Backlog []`, `Plan []`, `Ready [plan]`, `Building [plan]`, `Review [plan, build]`,
`Done [plan, build, validate]`. Stems are **lowercase literals**, never derived from the status
values — deriving them yields `notes/handoff-Plan.md` against a lowercase file on disk, which passes
on this machine's case-insensitive filesystem and **fails on Linux CI**. 34 handoff notes on disk,
none renamed.

Had FEAT-15 taken the literal `Review`, this dry-run would raise **two** violations (no
`handoff-plan.md`, no `handoff-build.md`) — that is the mechanical evidence behind the departure.

## 9. What changed

**Decisions.** D-01, D-02, D-05, D-09 rewritten. D-02's entire backfill analysis replaced (not
patched) — there is no backfill; the surviving consequence is INV-17 losing its exemption carrier on
all 17 rather than on two. D-09 rewritten from a six-snake_case-value enum to the collapse.
**Four new:** D-10 (the survivor is named `status`), D-11 (capitalized, case-sensitive, no alias),
D-12 (INV-17 survives; seam table; stems decoupled; residual loss named), D-13 (digest enum out of
scope, with the `blocked`-has-no-column discriminator).

**Tasks added.** T-11 (`check-plan-routes.py` → `Done`, `FINISHED_STATUSES`, six-value fixture loop
plus a lowercase-`done` case, schema-subset assertion moved here from T-05); `depends_on: [T-04,
T-05]` — T-05 edits the same two files. T-12 (INV-17 rebuilt; `main-session-direct`, DEC-174);
`depends_on: [T-06]`. Both are in T-08's `depends_on`.

**Tasks rewritten.** T-01 (eleven keys, eight required, no `phase` property, six board values, new
fixtures: six per-value, a `phase`-must-be-rejected case, a lowercase-casing case). T-04 (two
preconditions — the main-session wait, and a board **read**; the collapse step with the 17-row table;
value normalization). T-05 (item 7 handed to T-11). T-06 (INV-17 and the PHASE_ORDER-equals-enum test
both **deleted**, not moved; explicit hands-off note so two tasks do not edit the same carve-out
lines). T-07 (new item 3 — the `phase` instruction rewritten, with the mission framing and line 69
explicitly protected). T-08 (17-path list → glob, `depends_on` += T-11/T-12, route-check assertion
with a non-zero plan-count floor added to `verify:`). T-09 (SPEC §11.3 rewritten around one field;
third decision entry). T-10 (three index rows).

**Criteria.** SC-01, SC-03, SC-06, SC-08, SC-14, SC-15 reworded; SC-07 wording tightened to "exits
exactly 3" (its assertion was already correct and was not touched). **SC-17** (route-check skips on
`Done` only; 0 violations across ≥1 plans, expected 11) and **SC-18** (INV-17 fires — two assertions
in opposite directions, explicitly not "exits 0") added.

**Dropped.** The test asserting the schema `phase` enum equals `PHASE_ORDER` as sets — nothing left
to pin on either side.

---

## 10. Findings from review, fixed before signature

Five defects were found in the two new tasks after they were written, and each is fixed. Recorded
because four of the five are the same shape and it recurs.

1. **Three self-contradicting `verify:` clauses** — my own P-08. T-11's verify forbade the literals
   `"shipped"` / `"abandoned"` anywhere in `check-plan-routes.py` while its `intent:` instructs a
   comment explaining that *Done absorbs abandoned as well as shipped*. T-12 had the same shape twice
   (`PHASE_ORDER`, and the `handoff-Plan` hazard the comment must name). A doer following the
   instruction would fail the check that demanded it. **Fixed**: both verifies now strip comments and
   check executable code only, and say so in the failure message. SC-18 was reworded to match, or the
   brief and the plan would have disagreed. Discriminating check run: `check-plan-routes.py` carries
   exactly **one** quoted occurrence, at `:386`, which T-11 replaces — so the blanket grep would have
   passed on arrival and failed only after a correct edit, the worst detection point.
2. **T-09 told the doer to take two DEC numbers** while requiring three entries and verifying
   `max(nums) >= 191`. **Fixed**: three numbers, with a note that the third is assigned at write time
   (D-04 and D-08 reserved 189 and 190; the collapse entry has no reserved number).
3. **T-11 and T-05 both write `check-plan-routes.py` and `test-check-plan-routes.py`** with no
   ordering. **Fixed**: `T-11 depends_on: [T-04, T-05]`.
4. **A fixture fell into the T-06/T-12 gap.** `test-check-state.py`'s INV-17 fixture needs T-06's
   filename rename *and* T-12's content rewrite. Left as written, T-06's renamed glob would match
   nothing and the case would pass **vacuously** while T-06's own verify went green. **Fixed**: T-06
   gets an explicit carve-out for the fixture *filename* only; T-12 owns the content.
5. **Line anchors into files an earlier task edits** — my own P-10. T-12 cited `check-state.sh`
   437/450/451/455, which T-06 shifts; T-11 cited 386/426/828, which T-05 shifts. **Fixed**: both
   tasks now anchor on content (`PHASE_ORDER = [`, `# --- INV-17 (DEC-159)`, `SHIPPED_STATUSES =`,
   `want_checked`) and open with an explicit anchor-on-content instruction.

**A sixth, found by widening the STEP ZERO scan** (§5 above): the fixture *values* move too, not only
the fixture filenames. `test-gh-sync.py` writes `status: in_progress` on roughly a dozen fixtures and
`phase:` on five; `test-factory-decompose.py`, `test-factory-claim.py` and `test-check-domain.py`
carry their own. `test-check-domain.py`'s matter most: after T-06 those payloads pass through the
schema, so an accept-case fixture carrying an old value would now be denied for a reason its case
never intended — green-looking, wrong cause. **Fixed**: explicit instructions added to T-05 item 5
and T-06's test list.

---

## Open questions for the operator

1. **FEAT-15 takes `Plan`, not `Review`** — the only departure from an explicit ruling. Reason above.
   Non-blocking.
2. **The orchestrator digest enum stays as it is** (D-13). Non-blocking; recorded so it is findable.
3. **`STATE.md` and `notes/handoff-plan.md` are stale and are outside my grant.** Both are
   orchestrator domain (`.harness/features/**`). What needs fixing:
   - the discharged `jsonschema`-not-installed claim (4.26.0 **is** installed);
   - every `phase`-related entry in `handoff-plan.md`'s `## Trust` and `## Dead ends` — voided by
     this revision. The rest of both sections stays live;
   - the stale FEAT-12/13/15 build-precondition roster (now FEAT-16 + FEAT-17);
   - the 12/14-feature corpus counts (now 17).
4. **The dispatch's claim that `.claude/agents/harness-orchestrator.md` instructs "Record your phase
   in `feature.yaml` `phase:`" is not borne out.** Verified at `a29ad06`: that file contains the word
   `phase` **zero** times. The instruction lives only at `harness/SKILL.md:271-272`. T-07 says so
   explicitly so the doer does not go looking for a second site and invent one.
