# ALTITUDE-1 approved scope ruling

Main transmitted the advisor's ruling under operator-delegated authority: APPROVE the capability; PM must fold it into the pending plan before final check and the single goalcheck. This resolves ALTITUDE-1's scope question, not the operator's final plan signature.

Binding conditions from Main:
1. Boolean classifies_tests defaults TRUE when absent, preserving existing kinds. Add kind.get("classifies_tests", True) in _is_test_path's kind filter (code_grade.py:466-472); offenders() and select_control_candidate() inherit it. One filter in test-suite-layout.py local _running_kinds (:353), sole consumer hygiene_uncertified (:493). Correct _is_test_path docstring's conflated rule.
2. code_grade.py exists identically under .claude/skills/harness/bin/ and .agents/skills/harness/bin/: land both mirrors per convention.
3. Set classifies_tests: false for typecheck in live .harness/harness.json AND .claude/skills/harness/templates/harness.json (same broad detect). No upgrade-config.py change: additive merge already works; no validator rejects unknown kind keys. Update _test_kinds_note only if it enumerates kind fields.
4. Synthetic unit test-code-grade.py regression: flagged kind whose detect matches -> _is_test_path False; flag absent -> unchanged True. Synthetic hygiene_uncertified case: flagged kind patterns skipped. Existing live-config suite-layout cases become activation regression once typecheck active.
5. Capability strictly BEFORE T-04 status flip, as task between T-02 and T-04 or explicit T-04 precondition. Red-first: offenders()/hygiene_uncertified() against config copy with active typecheck, flag absent.
6. Fold semantics into already planned D-01 amendment of DEC-213, no second decision number. Correct DEC-213's 'only mechanical consumer' sentence if amendment touches clause. New surfaces (both code_grade mirrors, both unit tests, template) in lanes main-session-direct under DEC-174.
7. Correct rationale: half (a) LATENT, not live: code_grade grades only changed Python files via _changed_python_files (:438), so no TS file reaches bar today; no active bar-3 downgrade claim. Half (b) LIVE: suite-layout offenders()/hygiene_uncertified() fail at activation. Narrow detect was rejected because it encodes false coverage, not because QA maps files through detect. DEC-213 already names _is_test_path as detect's only mechanical consumer.

Keep no-test_matrix-change and all other settled constraints. This is authorized scope expansion from Main, not product lead's independent design choice. No implementation in this plan run.
