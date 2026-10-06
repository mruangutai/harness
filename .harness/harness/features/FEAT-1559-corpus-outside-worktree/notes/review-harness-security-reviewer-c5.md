# Security review — c5

**PASS — the c4 quoted-directory defect is closed; no new exploitable security regression found.** Exact pin `f8a67546bcb42b6a5fd4327398615a4cfc07ae4d`; delta `35587d8dfbf9178e21410c201601f7137fbfbbd6..f8a67546bcb42b6a5fd4327398615a4cfc07ae4d`. Full-feature census `e8d868f78a6ec43880598af5c5873f5daa8ba985..f8a67546bcb42b6a5fd4327398615a4cfc07ae4d`: 104 paths. Read BRIEF, plan decisions, prior security assessment, settled backlog and c4 receipt; receipt claims were not proof. `bin/` below means `.claude/skills/harness/bin/` at the pin.

## Scope and boundaries

IN: filesystem names crossing Git stdin parsing, repair work protection, corpus authority and gate refusal. Production readers/gates/hooks are security surfaces; tests are evidence; documentation/records are authority inputs. Delta changes only `worktree-state.py` production behavior, one integration regression and this feature's records. No new dependency, HTTP/SSRF, credential, spreadsheet or rendered UI surface. Full-diff secret-pattern sweep: no matches (`artifact://2203`).

- **T-01 / SC-01, SC-07:** `bin/worktree-state.py:143-164,209-212,330-333` encodes filesystem bytes into one ASCII C-quoted line per name for both sparse-checkout and hash-object. Quotes, backslashes and controls cannot introduce another record. List-form subprocess argv retains no-shell behavior; stdin paths are not CLI flags.
- **Work protection / fail-closed:** `bin/worktree-state.py:189-195,225-254,320-339,401-414` retains raw no-filter hashes, symlink type/content discrimination, all-path diagnosis before mutation, dirty refusal and explicit Git-error reports. `bin/feature_corpus.py:384-438` refuses unusable reports, not an empty clean population. Automatic repair hooks' exit0 is not a permission decision.
- **Owner corpus / T-01,T-03:** `bin/feature_corpus.py:156-169,204-223,327-345` requires owner identity and tracked/reached names, keeps missing own-feature records local and reads other landed records from owner main only. Entire module is byte-identical to previous pin, independently asserted through both `git show` endpoints. Encoding changes neither read destinations nor write grants. Ruling B and settled #2107/#2108/#2109, B1..B9, c4 grade-2 dismissals and SC-10/#2101 are not reopened.

## Independent targeted evidence

Managed exact-SHA pin; no full suite/build/lint/formatter; no authored source/tests/fixtures.

1. Existing `RecordBearingClasses.test_names_git_would_unquote_on_stdin_converge`: **PASS**, 1 case, 0.904s. Leading literal quote directory survives, hidden newline-name file disappears, verify exits0.
2. Independent encoder probe: **255/255 non-NUL byte roundtrips identical**, including surrogateescaped invalid UTF-8; exactly 255 ASCII framed lines. Encoder identity only, not end-to-end arbitrary-byte filesystem support.
3. Real Git `hash-object --no-filters --stdin-paths`: **7 distinct hashes match independent raw-content hashes in exact path order** for newline, tab, CR, backslash, quote, Unicode/leading space and flag-shaped basename. Distinct contents discriminate path substitution.
4. Initial index-based hash probe failed with KeyError on CR: existing text-mode structural Git reads normalize CR to LF. Direct encoder/Git identity probe then passed. The unchanged `feature_corpus.py` decoder predates this delta; no new exploit or regression established. Complete arbitrary-byte checkout support is not claimed.

Findings/must-fix/open questions: none. Earlier bisect limitation is not claimed exercised or resolved. Existing synthetic-fixture teardown removes private temporary directories; own managed pin removal exited0 before return. No full clone created; no sibling or owner records modified. Source files changed: none.
