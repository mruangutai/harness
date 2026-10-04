# BUG-2003 QA c1 — pin c2170e26

**PASS.** Matrix floor met, suite green, every automated SC has a discriminating pre-fix red.

## Gate runs (this run, tree HEAD = pin c2170e26; only feature.json dirty)
- `python3 tests/unit/test-omp-hooks.py` → exit 0; bun **107 pass / 0 fail**, 417 expect() (matches main's 107/107).
- `env -u HARNESS_AGENT_TYPE run-unit-tests.py --kind all` → exit 0, pool 118 files, 126 PASS lines, no FAIL file; `test-omp-hooks.py` ran inside it (107 pass).
- Matrix: bugfix has `always: []`; `unit` fires on `touches_runtime_code` (adapter .ts changed) → satisfied by test-omp-hooks.py, 107 named tests. `integration` clause (fix confined to tests/docs) not triggered. `__bug_class__` placeholder inert (G-08). Other kinds are excluded/locally_run/unresolved and not touched.

## Fail-first (own reproduction, disposable pin checkout)
Pin tree with adapter reverted to 7fba7e1d (`git checkout 7fba7e1d -- harness-hooks.ts`) and the pin's test file: 103 pass / 4 fail — the same 4 named in `notes/receipt-t01-fail-first.txt`:
1. agent:// and xd://report_issue skip the domain gate on both routes and stages (SC-01)
2. every other scheme is refused by name and never reaches check-domain.py (SC-02)
3. an edit MV destination is judged by the same scheme rule (SC-02)
4. an allowed URI never exempts a sibling file or a refused URI in the same edit (SC-03 mixed)
Pin removed after. Tier: natural RED (reproduced + retained receipt).

## SC mapping (omp-hooks.test.ts at pin)
- SC-01: :1054 (write/edit x pre/post, zero check-domain calls, no block).
- SC-02: :1066 (10 refused targets incl. xd://report_issue/extra suffix, xd ast_edit/lsp/recall/reflect, conflict, local, vault, ssh, novel; name asserted in pre reason and post error), :1083 (MV).
- SC-03: :1093 mixed allowed+FORBIDDEN asserts verbatim reason, post text array `["ok","Harness post-write check: …"]`, exact gate calls `[[] ,"Edit",{file_path}]` and `[--post …]`; allowed+refused URI blocks by name with no domain call. :1134 forbidden file write: exact pre `{block,reason}`, post composed error, tool_name Write, payload with content, harness_feature. :1121 ordinary payloads. :1155 main session write/edit pre+post for conflict://1 and real file → undefined and zero check-domain calls. c0's V1 gaps are closed. Controls are green-before (not red-first, per brief).
- SC-05: all of the above exercise write/edit, pre/post, mixed.
- SC-04 is inspection, not QA's.

## Coverage gaps
None blocking. Advisory: main-session check asserts no `check-domain.py` calls but not "no calls at all"; the FORBIDDEN stub keys on `file_path`, so an adapter that sent a different key for a real file would still fail the exact-payload assertions (fine). Bash branch untouched/unasserted by this change.

Only my own evidence examined the post-c0 additions (O-07); independent panel peers judge separately.
