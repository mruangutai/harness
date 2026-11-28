# Send-back criteria — run 02

## draft (revision per c1 rulings) — written before dispatch; met at seq-2

1. T-04 deletes `.harness/harness/docs/org.html` (no rewrite); SC-10 grep and T-04 verify no longer name org.html; no remaining SC/task text prescribes org.html table rows. pm confirmed by grep that nothing live links to org.html (or raised a NEW open question naming the linker).
2. No SC, task intent, verify or test name `case_stray_status_file_is_inert` or `run_retired_status_file_is_ungated`; SC-03 carries no tests/ exemption beyond the frozen `prior-*` fixtures; SC-05/SC-06 no longer require a test or fixture naming the file; no string-construction workaround (e.g. "STATE" + ".md") smuggles it back. The proof that the gates are gone is stated (removal + a grep/inspection, or a live-behavior test not naming the file).
3. A new SC (or explicit ship gate) states that harness-validator-lead G-01 and harness-code-reviewer G-05 (`.harness/harness/expertise/`) are dropped before ship via this feature's distillation, with a verify; no build task edits expertise.
4. SC-01 / T-07 drop the Q-03 conditional: the kaya copy is deleted, inventory fixed.
5. BRIEF's "Open at signature" questions Q-01..Q-07/GC-03 are replaced by recorded rulings citing notes/answers-2026-11-28-plan-c1.md (build waits for FEAT-2643; no re-add gate; historical mentions stay per DEC-205; Q-05 check root is the main checkout, sparse not widened, #2701).
6. `plan-merge.py check --file <plan.yaml> --root /Users/molchairuangutai/GitHub/harness` exits 0, receipt quoted. No `panel:`/`approval:` write; plan `pending`.
7. Digest lists every task id changed (the scope reader's re-read set).

## apply (c2 panel) — written before dispatch

1. SC-03 and T-07 carry no `prior-*` exclusion; both prior fixtures no longer name the file; the plan states how each fixture's behavioural control is preserved; no split/constructed spelling. If a fixture is byte- or hash-pinned or a decision mandates it frozen, pm raises a NEW open question instead of editing around it.
2. One accepted-digest definition (excludes typed and legacy refused returns; distinguishes none-accepted from accepted-with-no-questions) is used identically by BRIEF SC-02/SC-10, D-01, the playbook text (T-03), SPEC text (T-04) and DEC-129 text (T-05).
3. T-02 SC-06 case uses otherwise-valid payloads, asserts each budget's own diagnostic, strips lines before selecting Routing lines.
4. T-01 range grep either parses interval endpoints or narrows the grammar and its claim at the cited line.
5. record-panel --cycle 2, set-panel (only the c2 findings remedied marked resolved with resolved_by), check --root main checkout: all exit 0, receipts quoted. No `approval:`.
6. Digest lists every task id changed in apply.
