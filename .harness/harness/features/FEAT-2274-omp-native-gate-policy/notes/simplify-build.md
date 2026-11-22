# SIMPLIFY — build seam, FEAT-2274

**Route.** build-phase step 3 sequences SIMPLIFY to `harness-eng-lead`. This plan is entirely
`execution_mode: main-session-direct`, and DEC-174 bars the main session from dispatching
`harness-eng-lead`. So the main session ran the four angles itself, as four parallel, read-only,
ungoverned `scout` readers (the FEAT-2225 precedent), one angle file each, and applied the
findings itself. Nobody in the validation tier took part.

**Scope.** `git diff 1e0b0149..c24acdd9 -- . ':!.harness/harness/features'` (30 files). Readers
were told what is settled: D-01, the outcome model, the two applicability classifiers, the
DEC-234 prologues, notice phase tags, the spawns allowlist deletion, DEC-205, and the rule that
assertions are never weakened.

| Angle | Reader | Findings |
|---|---|---|
| REUSE | `SimplifyReuse` | none |
| SIMPLIFICATION | `SimplifySimplification` | 1, applied |
| EFFICIENCY | `SimplifyEfficiency` | none (narrow TS classifiers run only on process failure) |
| ALTITUDE | `SimplifyAltitude` | none |

**Applied finding.** `branch-create-gate.py` `_command()`: the applicability preflight that T-01
added (`_payload_command`) made the legacy `_COMMAND_EXTRACTOR` subprocess fallback unreachable.
Both entry routes were checked before the apply:

- The `JSONDecodeError` route: every payload the lenient preflight accepts either passes the
  strict reader or is refused with a plain `ValueError` cause. Checked empirically for duplicate
  keys (top-level and nested), `NaN`, `Infinity`, `-Infinity`, a lone surrogate, and trailing
  whitespace.
- The `AttributeError` route: the preflight requires a mapping `tool_input`.

Removed: `_COMMAND_EXTRACTOR`, both fallback branches, and the subprocess call. A strict refusal
now returns no command. The canonical-reader inventory row `_command::json_string#1` is unchanged,
and no assertion was touched.

**Verification after the apply.**
- `test-branch-create-gate.py`: 80/80.
- `test-omp-native-gate-runtime.py`: 445/445.
- `test-check-plan-routes.py --canonical-reader-self-test`: only the two failures that predate
  this feature (`canonical_reader_live_inventory_names_no_plan`,
  `canonical_reader_audit_holds_without_a_feature_corpus`), identical at baseline `1e0b0149`.
