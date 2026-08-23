# REUSE receipt — FEAT-26 commit 9a30ea5, simplify-eng pass

BLUF: two real reuse findings, both in `gh-sync.py`/`check-state.sh`'s new INV-28 block;
neither is a fresh duplication invented by this commit — both are the third-or-later
near-identical copy of a shape the file already had, which the tasks' own intent
(model on the existing function/block) explicitly reproduced rather than factored.
Test-file additions checked and are clean: no re-implementation found there.

## Finding 1 — `_record_pr`'s read/validate prefix duplicates `_record_status`'s, verbatim minus one word

- File: `.claude/skills/harness/bin/gh-sync.py`
- Lines: `_record_status` 521-529 vs `_record_pr` 551-559 (both at HEAD, `git show 9a30ea5`
  hunk + `sed -n` re-check)
- Command run: `sed -n '521,533p' … > a.txt; sed -n '551,564p' … > b.txt; diff a.txt b.txt`
  — output: lines 6 and 9 of each slice differ only in the interpolated word
  (`"status not recorded"` vs `"pr not recorded"`); the open/`try`/`except (OSError,
  ValueError)`/`isinstance(doc, dict)` guard is otherwise character-identical across both
  functions.
- Summary: both functions open `feature.json`, catch `(OSError, ValueError)` on read,
  print-and-return on a not-a-dict document — nine lines apiece, restated rather than
  shared, immediately after `_record_pr`'s own docstring says it is deliberately modelled
  on `_record_status` ("mirror image... same read pattern... same one-line-and-return").
- Cost: two call sites now carry the load-and-validate contract in prose only. A third
  writer function (there will be one — `parent`, `milestone` and `github.*` fields all
  follow the same shape) either copies a tenth near-identical block or diverges from it
  silently; nothing forces the two existing copies to change together if the refusal
  behaviour is ever revised (e.g. adding a third exception type to catch), so a fix to
  one and not the other is the exact "forgotten spelling" failure this angle exists to
  catch.
- Alternative: a `_load_feature_doc_for_write(feat_dir, field_label)` helper returning
  `(doc, None)` on success or `(None, print-string)` on failure, taking `path` and the
  human label used in the two print messages (`"status"` / `"pr"`) as parameters; each
  caller does `doc, err = _load_feature_doc_for_write(...); if err: print(err); return`
  ahead of its own field-specific logic.
- Rank: **later-feature**. The duplication is 9 lines, harmless on its own, and factoring
  it now touches `_record_status` — a function this commit did not otherwise change —
  for no test-visible gain. Worth doing the next time a third writer of this shape lands.

## Finding 2 — INV-28's glob+parse-guard is INV-21's, restated a third time in the file

- File: `.claude/skills/harness/bin/check-state.sh`
- Lines: INV-21's gate+glob+parse guard 913-929 (17 lines incl. a `F-02` comment); INV-28's
  gate+glob+parse guard 1062-1070 (9 lines, no comment) — both at HEAD.
- Command run: `sed -n '913,916p;924,929p' check-state.sh` vs `sed -n '1062,1070p'
  check-state.sh` — output shows the two are line-for-line identical except the local
  variable name (`gdoc` vs `pdoc`) and the invariant id string interpolated into the
  `bad.append(...)` message (`INV-21` vs `INV-28`).
- Wider measurement: `grep -n 'for fy in glob.glob(os.path.join(H, "\*", "features",
  "\*", "feature.json"))' check-state.sh` returns 5 hits (lines 177, 573, 914, 953, 1063);
  `grep -c 'does not parse, so INV' check-state.sh` returns 4. INV-28 is not the second
  copy of this shape in the file, it is at minimum the fourth — this commit did not
  introduce the duplication, it added one more instance of a pattern already unfactored
  before it landed.
- Summary: `if cj and (cj.get("github") or {}).get("sync"): for fy in glob.glob(...): feat
  = os.path.basename(...); try: doc = harness_yaml.load_file(fy) or {} except Exception as
  e: bad.append(f"... does not parse, so INV-NN cannot be checked for it: {e}"); continue`
  is restated whole, a fourth time, immediately below a comment on the INV-21 block
  ("GATED ON github.sync, like INV-21 above") that already names the block it copies from.
- Cost: any future fix to the parse-failure message shape, or to what counts as
  "unreadable" (e.g. adding a not-a-dict guard consistently, which INV-21's neighbour
  INV-24 already handles differently via `YamlParseError` alone rather than bare
  `Exception`), has to be applied to four sites by hand; a grep for the string moved on
  one copy and not the others is exactly the kind of miss check-state.sh itself exists to
  catch in other files.
- Alternative: a small generator, `_iter_sync_features(cj, H)`, yielding `(feat, gdoc)`
  pairs (or raising/appending to a caller-supplied `bad` list on parse failure) once
  `github.sync` is confirmed on — each `INV-NN` block keeps its own per-feature logic
  after the `for feat, gdoc in _iter_sync_features(...):` line, but the gate check, the
  glob, and the parse-guard-with-message stop being copied prose.
- Rank: **later-feature**. Four sites already existed before this diff; refactoring them
  now would touch INV-21's and INV-24's blocks, which are out of this commit's scope and
  not what T-05 was dispatched to change. Worth raising as its own scoped task since the
  pattern is now at 4 occurrences, which is past the point where "no shared helper" reads
  as accidental rather than deliberate.

## Checked and clean — no finding

- `_pr_fixture` (test-gh-sync.py, new in this commit) wraps the existing `write_feature_json`
  helper rather than reimplementing feature.json construction — confirmed by reading
  `write_feature_json` (`test-gh-sync.py:101-108`) against `_pr_fixture`'s body: it builds
  a `fields` dict and calls `write_feature_json(path, **fields)`. This is the intended
  reuse shape, not a finding.
- `_inv28_fixture` (test-check-state.py, new in this commit) reuses the module-level
  `HARNESS_JSON_SYNC_ON`/`HARNESS_JSON_SYNC_OFF` constants and the existing `run(tmp)`
  helper. It does not reuse `make_fixture` (INV-21's single-feature builder) or
  `_inv26_fixture` (a much heavier board+plan+factory builder) because neither shape fits
  a multi-feature, status/pr-only fixture — checked by reading both at
  `test-check-state.py:40-49` and `:1312-1369`. Not a finding: the nearest existing
  helpers are a poor fit, not an overlooked good one.
- `cmd_closes` reuses `load_recorded` rather than re-parsing feature.json itself — no
  finding.

## Empty-return note

Neither finding above was invented by this commit in isolation — both are commit-added
instances of a shape the tree already had at least once before. If the bar is
"introduces a *brand-new* duplicate with no precedent in the file," this pass returns
empty. Reporting both anyway because the dispatch's own hypothesis named them and the
measured line ranges confirm the near-identical claim; ranking both `later-feature`
reflects that fixing them now would edit code outside this commit's scope.
