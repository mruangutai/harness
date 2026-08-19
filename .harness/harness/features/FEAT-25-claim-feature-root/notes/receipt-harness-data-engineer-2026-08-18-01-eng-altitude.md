# ALTITUDE receipt — FEAT-25, plan surface — harness-data-engineer

One concrete finding; everything else checked and confirmed at the right depth.

## Finding 1 — `plan_path()` restates a join `task()` already builds, in the same class

`plan.yaml` T-02 intent step 1 (lines 250-257), landing in
`.claude/skills/harness/bin/factory_claim.py`'s `_BlockerCache`.

T-02 adds `plan_path(feature) -> os.path.join(self._features_root, feature, "plan.yaml")` as a
new method. `_BlockerCache.task()` already builds the identical expression inline at
`factory_claim.py:101` (`path = os.path.join(self._features_root, feature, "plan.yaml")`), read
during this angle's pass. After T-02 lands, the class states "how to build a feature's plan.yaml
path" twice: once inline in `task()`, once as the new `plan_path()` method — both in the same
class, both touched by the same task.

**Cost**: a future edit to the join (e.g. inserting a repo segment for unit 7's per-repository
root) has two call sites to find inside one class, and nothing enforces they move together —
`test-factory-claim.py`'s coverage would have to specifically assert `plan_path()` and `task()`'s
internal path agree, which T-02 does not ask for. Low probability, but the fix is inside T-02's
own scope so there is no reason to accept the residual.

**Alternative**: have `task()` call `self.plan_path(feature)` instead of rebuilding the join
inline — a one-line change, same task, same file, no scope reopened. `plan_loaded()`'s required
sharing of `task()`'s *caching* path (T-02 intent, "populate the cache by calling the same private
load") does not by itself dedupe this *path-string* construction; they are two different pieces of
duplication and the intent only names the first.

Severity: low. Class: advisory (functionally harmless — three tokens, same value both places —
but free to fix inside the task already touching this code).

**fold-in**

## Checked, no finding

- **T-02's new `_BlockerCache` methods (`plan_path`, `plan_loaded`, `root_exists`) and the new
  `_blocker_reason_text` branch**: right home. `_BlockerCache` already owns per-feature caching
  state (`_plans`, `_issue_maps`) and two public readers (`task()`, `issue_number()`); the three
  additions are the same shape, not new state or a new abstraction bolted onto a caller.
  `_blocker_reason_text` already owns exactly "map a gate tuple to a diagnostic string" for
  `edge_i`/`unresolvable`/`open` — the new `no_plan` branch is the same job, not a special case
  routed around it. **leave.**

- **T-03's `READER_TABLE` row and pattern pair** (`layout_migration.py`, features block): the
  legacy/migrated pair the plan writes is character-identical to the existing
  `check-plan-routes.py` row two lines above it (same comma-form legacy, same `[^,)]+` migrated
  generalisation, same `# balance: (` placement — verified by counting the stray literal `)`
  inside the `[^,)]` character class against the row's own `Row(` / trailing `)` pairing). The
  plan's quoted audit (candidate pattern, then a broader pattern for the same concept, confirming
  the broader adds only what the narrow one already caught) is the exact procedure the PATTERN
  RULE at `layout_migration.py:20-25` demands, not a shortcut of it — and T-03 additionally
  requires re-running all five greps after T-01 lands and stopping if the legacy pattern still
  matches, which is the audit re-verified against the real post-fix file rather than trusted from
  a stale note. **leave.**

- **The migrated-path form's several spellings** (D-01 prose, T-01's verify grep, T-03's row
  pattern, `layout_fixtures.STUB`'s fragment): not drift-prone copies of one rule — they are
  different consumers by design. D-01/T-01 state the *literal* three-segment join
  `factory_claim.py` actually uses (source of truth: the code itself, `factory_claim.py:43` after
  T-01). T-03's regex and the STUB's `_seg` placeholder are deliberately *generic* — they exist to
  match "some migrated repo-segment," the detector's actual job (per the PATTERN RULE and the
  MIXED-FOREVER rule's category-1 code-shaped resolution), not to restate D-01's specific choice
  of segment. If the literal segment ever changed, T-03's pattern still matches without edit. Not
  a case of "several authorities for one fact." **leave.**

- **The known advisory on T-01's three ungated prose corrections** (`factory_claim.py:25-27`
  docstring, `test-factory-claim.py:5`, `test-factory-integration.py:31`): confirmed by reading
  T-01's verify block in full — every grep and Python assertion targets the comma-form join or the
  ok-line/case-count machinery; none targets the slash-form prose text the intent also requires.
  The advisory is accurate as carried. **Confirmed, not re-reported.**

## Return

No other ALTITUDE findings.
