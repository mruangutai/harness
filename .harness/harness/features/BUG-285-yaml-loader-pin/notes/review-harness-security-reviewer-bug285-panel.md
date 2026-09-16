# Security review — BUG-285 canonical feature.json reader

BLUF: **PASS.** The diff closes the fail-open defect without opening a new one. One real,
low-severity, advisory finding (nested-JSON `RecursionError` falls through to a generic
"unexpected failure" in `factory_decompose.py`, vs. the specific refusal it produced pre-fix)
— not a mutation risk, not a crash exposed to the operator, no privilege delta. No must_fix.

## What was checked, and the result

**1. One implementation (claim 1) — CONFIRMED.** Integer coercion lives only in
`feature_json_write.opt_int` (`.claude/skills/harness/bin/feature_json_write.py:180-196`).
`gh-sync.py`'s private `_opt_int` is deleted (was `gh-sync.py:512-524` pre-fix); both callers
now route through `load_feature_json`.

**2. Absent vs. malformed distinguishable by BOTH callers (claim 2) — CONFIRMED.**
`load_feature_json` (`feature_json_write.py:113-165`) returns `None` only on `os.path.exists`
failing; every other failure mode (`OSError`/`UnicodeDecodeError` on read, `JSONDecodeError`,
duplicate key, non-mapping) raises `FeatureJsonError`. Traced to both call sites:
`gh-sync.py load_recorded` (`gh-sync.py:547-553`) re-raises as `SystemExit` before any `gh`
subprocess call; `factory_decompose.py load_factory` (`factory_decompose.py:121-125`) refuses
via `factory_cli.refuse` → `SystemExit`. Verified `SystemExit` is not intercepted between
either raise point and the interpreter: `gh-sync.py` has no bare `except Exception`/
`except BaseException` wrapping any `load_recorded()` call site (checked all 7 —
`open`/`start-task`/`recover-terminal`/`abandon`/`ship`/`record-pr`/`status`, `load_recorded`
is the first statement in each, ahead of any `gh` call); `factory_cli.run`
(`factory_cli.py:72-96`) explicitly lets `SystemExit` through its own `except SystemExit`
before the `except BaseException` catch-all beneath it.

**3. Duplicate-key rejection (claim 3) — CONFIRMED for both touched callers; ONE unrelated
bypass exists but is pre-existing and out of scope.** `_reject_duplicate_keys`
(`feature_json_write.py:98-110`) is `load_feature_json`'s `object_pairs_hook`
(`feature_json_write.py:157`) and both callers go through it — verified with
`tests/unit/test-feature-json-reader.py` (21/21 pass, includes duplicate-key cases) run
directly. A second, unrelated parse path in the *same module*, `parse_doc`
(`feature_json_write.py:58-79`), does **not** pass `object_pairs_hook` and would take
last-wins on a duplicate key — but it is called only from `feature-json-merge.py`'s
`_apply` (pre-existing, unchanged by this diff, in the write-merge CLI, not the read path
BUG-285 fixes) and belongs to the "other ~10 `feature.json` readers... issue #1594" carve-out.
Named per dispatch instruction; not scored as this diff's defect.

**4. Non-UTF-8 refusal (claim 4-adjacent) — CONFIRMED.** `load_feature_json`'s own
`open(path, "rb")` + `.decode("utf-8")` is inside the same `try` as the `OSError` catch
(`feature_json_write.py:148-152`), so a non-UTF-8 file can no longer escape `gh-sync.py`'s
old bare `except OSError`. Both callers turn it into a named refusal, not a traceback.

**5. Fail-open-to-mutation (claim 4) — CONFIRMED CLOSED.** Every `gh` mutation-adjacent
command function calls `load_recorded` first; a malformed file raises `SystemExit` there,
before `gh issue create`/`gh api`/etc. is ever reached. No path in the diff re-introduces
"malformed reads as empty" for `gh-sync.py`'s mutating commands.

**6. Refusal shape preserved (claim 5) — CONFIRMED for the ordinary refusal path**
(`factory_decompose.py:121-125`, comment explicitly notes the shape is unchanged). See the
one exception under Findings below.

**7. Parser substitution as a trust change — NOT a deserialization-hole closure; recorded
explicitly since the dispatch asked.** Pre-fix `factory_decompose.load_factory` used
`harness_yaml.load_file`, which is `yaml.load(text, Loader=_StrictSafeLoader)` where
`_StrictSafeLoader` subclasses `CSafeLoader`/`SafeLoader` (`harness_yaml.py:131-134`) — the
safe variant throughout, incapable of arbitrary Python object construction. The YAML-loader
import is confirmed gone from `factory_decompose.py`'s read path (no `harness_yaml` reference
remains in `load_factory`). This diff removes a YAML dependency for consistency/parity
reasons, not because the prior loader was unsafe — there was no deserialization hole to close.

**8. Information disclosure — checked, no finding.** `FeatureJsonError`
(`feature_json_write.py:87-97`) embeds `path` and `str(e)`. Empirically verified (`python3 -c`
repro): `json.JSONDecodeError.__str__` carries only a stage description plus
line/column/char offset, never a content excerpt; `_reject_duplicate_keys`'s message names
only the offending *key* (a schema field name such as `github`/`milestone`), never its value.
This is equal-to-or-less exposure than the YAML error messages it replaces (PyYAML messages
can include a content excerpt around the error mark). `feature.json` content (issue/milestone
numbers, status) reaching a refusal line is not a new class of exposure for this repo's
threat model — these are already-public GitHub identifiers, not secrets, and no refusal
prints the parsed document itself, only the parse failure description.

## Findings

**LOW (advisory, no must_fix) — nested-JSON DoS message-quality regression, `factory_decompose.py` only.**
Reproduced empirically: a ~1,000,000-deep nested JSON array fed to `load_feature_json` raises
a raw `RecursionError` ("Stack overflow (used 16352 kB)...") that is **not** a `ValueError`
and escapes the `except ValueError` clause at `feature_json_write.py:157-158`.
- For `gh-sync.py`: **not a regression** — its pre-fix reader called the identical bare
  `json.loads(text)` (`git show 6cb113f4:.../gh-sync.py:566`), so the same crash already
  existed pre-fix; confirmed no `except`/`except BaseException` wraps `load_recorded()`
  call sites either before or after this diff, so this class of input already produced an
  uncaught traceback on `6cb113f4`.
- For `factory_decompose.py`: pre-fix, the same crafted file hit `harness_yaml.load_file`,
  whose libyaml-backed loader raises its *own* stack-depth guard as `yaml.YAMLError`
  (reproduced: `YamlParseError failed to parse YAML in test: Stack overflow (used 16353 kB)`),
  which `load_factory`'s old `except harness_yaml.YamlParseError` caught cleanly and refused
  via `factory_cli.refuse`, naming the file. Post-fix, the `RecursionError` instead falls
  through `load_factory`'s `except feature_json_write.FeatureJsonError` untouched, but IS
  still caught by `factory_cli.run`'s outer `except BaseException` trap
  (`factory_cli.py:88-96`), which prints a generic `"unexpected failure: RecursionError: ..."`
  (not naming feature.json specifically) and exits `EXIT_REFUSED`. No raw traceback reaches
  the operator by default (`FACTORY_DEBUG=1` is opt-in), no mutation is attempted, and
  crafting this input already requires the same write access to `feature.json` that would
  let an actor rewrite it to anything else — no privilege delta. This is a message-quality
  narrowing, not a DoS or crash newly exposed to an attacker without prior write access.

No other findings. Unbounded-file-size read, non-integer/oversized `feature.json`, and
generic large-document-DoS angles were checked and are unchanged from pre-fix (both old
readers already did an unbounded full-file read); not scored.

## Non-applicable categories (checked, no surface)
No auth, no network-input parsing, no SQL, no templating, no new dependency, no secrets in
this diff (grepped the full diff, not only the named files — none found).
