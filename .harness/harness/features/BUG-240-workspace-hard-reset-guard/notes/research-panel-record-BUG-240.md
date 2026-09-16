# Panel repair + record — BUG-240 — cycle 0

**BLUF: all three ruled findings are closed in plan text, the panel is recorded with five
re-derived ids, and nothing else moved.** `plan.yaml` is the only file changed. `BRIEF.md` is
**unchanged** — its self-detection constraint does not forbid `root_from_script`. T-01's `verify:`
is **unchanged** — no case name and no expected colour moved. `approval: pending` and
`status: plan` are untouched; no commit, no station change, no new task.

## Acceptance command, literal output

```
$ python3 -c "import yaml; d=yaml.safe_load(open('plan.yaml')); p=d['panel']; print(d['approval']['status'], d['status'], p['last_run'], p['cycle'], len(p['readers']), len(p['findings']), sorted(f['disposition'] for f in p['findings']))"
pending plan 2026-09-07-01-validator 0 2 5 ['open', 'open', 'resolved', 'resolved', 'resolved']
```

## The three repairs

1. **Findings 1+2, one seam — done, in T-02's `intent`** (`plan.yaml:298-313`). The guard's
   resolver is now `harness_boundary.root_from_script(_BIN_DIR)`; the intent carries the reason so
   no later reader restores `resolve_root` (env read at `harness_boundary.py:66-94`, stderr
   `discarding …` line at `:82-86`, `root_from_script`'s zero-env/zero-fs contract at `:57-64`).
   The now-inapplicable `strict=False because …` sentence is dropped; the `realpath` comparison,
   the bare-`.harness`-directory prohibition, the two refusals, the ordering, the docstring and
   no-bypass paragraphs are byte-unchanged.
2. **Finding 2's residue — done, in T-01's `intent`** (`plan.yaml:147-157`). One hygiene paragraph:
   `prev = os.environ.pop("HARNESS_PROJECT_DIR", None)` before the run, restored in `finally`,
   required in cases 2 and 5 (stderr-content assertions) and in the real-git drivers (cases 2, 3, 4).
   Reason stated at source: `factory_config` delegates root resolution to `resolve_root` itself
   (`factory_config.py:56-58`), so a polluted operator/agent shell reddens a correct build through
   *that* resolution, not through the guard. Popping from `os.environ` also strips it from any
   child process the fixtures spawn. No case renamed, no check name added.
3. **Finding 3 — done, in T-01's `intent`** (`plan.yaml:213-226`). The "spelled out because the
   named helpers cannot express it" paragraph is deleted; case 5 is now `checkout_path(wr)` +
   `checkout_path(wr)/.git` + stub aimed at `checkout_path(wr)` + `run_main` with
   `Recorder(porcelain="")`. Case 5's stub is `lambda: checkout_path(wr)` (`:206`). Sentinel
   `setattr`/`delattr` try/finally kept; assertions unchanged. **Not generalised to case 6** —
   `plan.yaml:229-231` still creates `checkout_path(wr)/.harness/team-config.yaml` and now says
   in-line that the marker is load-bearing for D-01.

**Residual `write_fleet` / repo-name-override mentions in case 5 are prohibitions, not
instructions** (`plan.yaml:217-218`: "no fleet repo-name override, no hand-built fleet dict, no
`write_fleet` call and no hand-rolled `_main` driver"), matching the dispatch's own phrasing. A bare
grep for the token will hit; read the sentence.

## BRIEF.md — unchanged, and why

`BRIEF.md:48-53` requires reuse of `harness_boundary`, forbids a fourth private walk-up copy, and
forbids probing a bare `.harness` DIRECTORY. `MARKER = .harness/team-config.yaml` appears as a
parenthetical gloss identifying the module's constant, **not** as a mandated probe. `root_from_script`
is `harness_boundary`, adds no copy, and probes nothing — no clause is contradicted. Nothing edited.

## `verify:` re-check — both directions, 8 for 8

Names grepped in T-01 `verify` ↔ names in T-01 `intent`: 8 present each way, no orphan either
direction (mechanical cross-check over the written file). Expected red set is still cases 1, 2, 3, 5
— case 5's stub is still installed unconditionally, so it is still red pre-T-02 — so `grep -c
'^FAIL  ' = 4` stands against the orchestrator's 30 ok / 0 FAIL baseline at 6d969ed. `verify:`
not amended; still a literal `|` block (`plan.yaml:102`).
`check-plan-routes.py` on this plan: `0 violation(s)`, exit 0.

## The five recorded findings — ids re-derived AFTER writing

| id | reader | severity | disposition | resolved_by |
|---|---|---|---|---|
| `PF-77b1ddb6889fe9e108e4325b66c41a40` | scope | med | resolved | T-02 |
| `PF-a6616ff1558ea680fc77f54d42579e21` | should-not-exist | info | resolved | T-01 |
| `PF-1414b1a16d9c271f2793225d4ea61f1f` | should-not-exist | med | resolved | T-01 |
| `PF-d795aab03bf4a49e7ef3ef6614024cdf` | should-not-exist | low | open | — |
| `PF-ff733189ddbdfca901c0d587800cb8c4` | scope | low | open | — |

Summaries were extracted programmatically from the digest's ranked table (row Summary cell,
pipe-delimiters trimmed, backticks/`**`/em-dashes intact) and each id computed by
`panel_findings.py` from that exact string; all five then re-derived from the values **as written in
`plan.yaml`** and matched. Both readers recorded `status: ran` (`scope`/harness-code-reviewer,
`should-not-exist`/fable-advisor); no skip recorded. Severities are each reader's own, never reassigned.

Findings 4 and 5 stay `open` with no `resolved_by`: no change was made for either, finding 4's
implied remedy was assessed and rejected by the panel lead (SC-06 is `verify: inspection`, so case
7's substring scan is REQ-06's only automated tripwire), and finding 5 is the operator's to strike or
keep at signature. Neither risk is accepted here — acceptance is `approval.rulings`, the main
session's write.

## Open question for the tier above

`factory_config` resolves its root at **import** time (`factory_config.py:56-58`), so a discarding
line caused by a polluted shell is emitted once, before any case body runs, and lands on the real
stderr rather than in a case's captured buffer. The hygiene paragraph is still correct and is the
only thing that protects a subprocess-launched driver, but for the in-process drivers it is
belt-and-braces rather than the load-bearing fix. Non-blocking; noted so nobody later reads it as
the whole of finding 2's cure.
</content>
<parameter name="i">Writing the artifact