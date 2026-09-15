# STATE

## Current

- feature: BUG-1563-inv35-multiline-quoted-scalar
- plan upgrade: signed by the operator on 2026-09-15 with 1 round / 45 minutes and decision record `notes/answers-upgrade-plan.md`
- GitHub mirror: parent #1701; T-01 #1702 done; T-02 #1703 attached; plan station `building`
- active work: T-02 `Add focused INV-35 unit-kind behavior coverage`, station `building`
- execution route: main-session-direct under DEC-174/179; no Harness lead or member may mutate the test
- only implementation file: `tests/unit/test-check-state-inv35.py`; no production or integration-test change is authorized
- required behavior: the focused test invokes the real `.claude/skills/harness/bin/check-state.sh` against isolated temporary Harness fixtures; multiline single- and double-quoted `notes` with continuation-line `#217` are silent, while unquoted `notes: close out #217` produces an INV-35 finding naming `#217`
- proof: demonstrate this same focused test fails against the pre-T-01 checker, then passes against the completed checker; direct command is `python3 tests/unit/test-check-state-inv35.py`
- completion receipt needed: RED and GREEN command evidence, commit SHA with `[harness:t-02]`, and confirmation that only the planned file changed
- cycles_used: 2 of 10; this is the one signed rework round

## Open Questions

- None.
