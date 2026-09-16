# Parity survey — `load_recorded` vs `load_factory`, 13 input classes, all measured

**BLUF.** Of 13 input classes fed as identical bytes to both readers, **4 give a caller the same
answer and 9 differ**. Of the 9, **6 carry the measured FEAT-14 incident class** — a `feature.json`
that is PRESENT and MALFORMED read by `load_factory` as "nothing is mirrored", indistinguishable
from the legitimate absent-file empty record. The other 3 differ in the safe direction
(`load_factory` refuses or returns a record where `load_recorded` does not) and one of those exposes
a defect on `load_recorded`'s side, not `load_factory`'s.

## How this was measured

One throwaway probe at `/tmp/bug285-probe/probe.py` (tempdir only; nothing added under `tests/`).
It loads each reader from `.claude/skills/harness/bin/` with
`importlib.util.spec_from_file_location` + `module_from_spec` + `exec_module`, the pattern
`tests/integration/gh_sync_support.py:844-850`'s `load_gh_sync` already uses, with `BIN` on
`sys.path` so `factory_decompose`'s siblings import. For each class it writes the SAME bytes in
BINARY mode into a fresh `tempfile.TemporaryDirectory` and calls both readers under
`redirect_stdout`/`redirect_stderr`, classifying only what a caller observes: `REFUSE` (SystemExit
+ exit code + whether the captured output names the `feature.json` path), `UNCAUGHT` (+ the escaping
class), or `RETURN` (+ empty-vs-populated, compared against `_empty_factory()` and
`load_recorded`'s own default dict). **Confirmed run** at HEAD `6cb113f4`, 13/13 rows live.

## The table

`SAME`/`DIFFERENT` is the **material** verdict — does a caller get a different answer about this
input — not a byte-diff of return values. The two readers have different contracts by design:
`load_recorded` refuses to protect a sync, `load_factory` returns a record.

|input class|`load_recorded`|`load_factory`|verdict|incident class|judgement|
|---|---|---|---|---|---|
|file absent|RETURN empty|RETURN empty|SAME|n/a|Both read a legitimate first sync (`gh-sync.py:556-557`, `factory_decompose.py:114-115`). Correct, and staying|
|file empty (0 bytes)|REFUSE exit 1, names path|RETURN empty|**DIFFERENT**|**YES**|`json.loads("")` raises; `harness_yaml` returns `None`, which falls to the non-mapping guard at `factory_decompose.py:124-125`. This IS the truncating-write window FEAT-14 was about|
|present, not valid JSON (`{ not: valid json [[[`)|REFUSE exit 1, names path|REFUSE exit 2, names path|SAME|n/a|Same answer — refuse, path named, nothing created. Exit codes differ (bare `SystemExit` vs `factory_cli.refuse` → `EXIT_REFUSED`, `factory_cli.py:50-52`) and D-11 keeps that deliberately|
|non-UTF-8 bytes (`\xff\xfe…`)|**UNCAUGHT `UnicodeDecodeError`**|REFUSE exit 2, names path|**DIFFERENT**|NO|Neither fails open, so not the incident class. `gh-sync.py:558-564` wraps the `encoding="utf-8"` read in `except OSError` only, so the decode error escapes as a traceback; the parse guard at `:567` that DOES name `UnicodeDecodeError` is never reached. Mirror image of the REQ-06 shape, on the other reader|
|top-level list (`[1, 2]`)|REFUSE exit 1, names path|RETURN empty|**DIFFERENT**|**YES**|`gh-sync.py:578-582` guards the type; `factory_decompose.py:124-125` returns the empty factory, so a present file reads as nothing recorded|
|top-level scalar string (`"x"`)|REFUSE exit 1, names path|RETURN empty|**DIFFERENT**|**YES**|Same guard pair, same fail-open|
|top-level scalar int (`3`)|REFUSE exit 1, names path|RETURN empty|**DIFFERENT**|**YES**|Same guard pair, same fail-open|
|block key absent (`{"feature_id": "F1"}`)|RETURN empty|RETURN empty|SAME|n/a|A mapping with nothing recorded yet (`gh-sync.py:583-586`). Legitimate on both sides|
|block key present, NOT a mapping (`{"github": "x", "factory": "x"}`)|REFUSE exit 1, names path|RETURN empty|**DIFFERENT**|**YES**|The already-measured row, reproduced live. `gh-sync.py:588-594` refuses; `load_factory` takes `f = doc.get("factory")`, finds a non-dict, returns empty at `factory_decompose.py:127-128`|
|block mapping, wrong-typed members (`{"…": {"parent": "7", "issues": "nope"}}`)|RETURN **populated**|RETURN **empty**|**DIFFERENT**|**YES**|`gh-sync`'s `_opt_int` coerces `"7"` → `7` (`:512-524`); `load_factory` admits only real ints (`:134-135`) and dict `issues` (`:138-141`), so a recorded parent #7 reads as no parent. Present, malformed, read as nothing recorded — same class, reached by coercion policy rather than by a type guard|
|duplicate block keys (`{"github":…,"factory":…}` twice)|RETURN populated (last wins)|REFUSE exit 2, names path|**DIFFERENT**|NO|Fails closed, so not the incident class. `harness_yaml` raises `DuplicateKeyError`; `json.loads` silently last-wins. The divergence is `load_factory` over-refusing input JSON permits|
|YAML-only block mapping (`github:\n  parent: 40\n…`)|REFUSE exit 1, names path|RETURN **populated**|**DIFFERENT**|NO|No empty read, so not the incident class, but this is the parser-choice divergence REQ-05/REQ-07 name: `load_factory` accepts a document no JSON writer produced and no JSON reader accepts|
|valid JSON, well-formed block (control)|RETURN populated|RETURN populated|SAME|n/a|**The green row.** Both read the record. Proves the probe distinguishes a refusing reader from a broken one|

## Probe output, quoted for the DIFFERENT rows

```
file empty (0 bytes)                       | REFUSE: SystemExit code=1 names_path=True | RETURN: empty record                     | DIFFERENT
non-UTF-8 bytes                            | UNCAUGHT: UnicodeDecodeError             | REFUSE: SystemExit code=2 names_path=True | DIFFERENT
top-level list                             | REFUSE: SystemExit code=1 names_path=True | RETURN: empty record                     | DIFFERENT
top-level scalar string                    | REFUSE: SystemExit code=1 names_path=True | RETURN: empty record                     | DIFFERENT
top-level scalar int                       | REFUSE: SystemExit code=1 names_path=True | RETURN: empty record                     | DIFFERENT
block key present, NOT a mapping           | REFUSE: SystemExit code=1 names_path=True | RETURN: empty record                     | DIFFERENT
block mapping, wrong-typed members         | RETURN: populated record                 | RETURN: empty record                     | DIFFERENT
duplicate block keys                       | RETURN: populated record                 | REFUSE: SystemExit code=2 names_path=True | DIFFERENT
YAML-only block mapping                    | REFUSE: SystemExit code=1 names_path=True | RETURN: populated record                 | DIFFERENT
EXIT_REFUSED = 2
issubclass(UnicodeDecodeError, ValueError) = True
issubclass(UnicodeDecodeError, json.JSONDecodeError) = False
```

Row 2 (`not valid JSON`) is quoted as SAME above: `REFUSE code=1 names_path=True` against
`REFUSE code=2 names_path=True` — the probe's raw diff says DIFFERENT, the material verdict is SAME.

## What the survey establishes

1. **The incident class is 6 input classes wide, not 1.** Empty file, three non-mapping documents,
   a non-mapping block key, and a wrongly-typed block member all make `load_factory` return the
   empty record for a file that is PRESENT. Absence and corruption are indistinguishable to its
   caller across all six. The operator's standing ruling — absent stays empty — is untouched by any
   of them.
2. **The wrong-typed-members row was not previously recorded anywhere.** It is the sixth member of
   the class and it is not reached by the two type guards the record already names; it is reached by
   `_opt_int`'s coercion diverging from `load_factory`'s strict `isinstance`.
3. **`load_recorded` carries the REQ-06 defect shape too**, on non-UTF-8 bytes: a traceback, not a
   refusal, because `:558-564` catches only `OSError`.

## Open questions

- **Q1 (non-blocking):** the non-UTF-8 `UNCAUGHT UnicodeDecodeError` out of `load_recorded`
  (`gh-sync.py:558-564`) is a defect outside every current REQ and SC. It is the same shape REQ-06
  protects `load_factory` against. Separate ticket, or widen this bug? Not absorbed here.
- **Q2 (non-blocking):** the duplicate-key row has `load_factory` refusing what JSON permits. BRIEF
  already discloses the post-fix loss of that refusal; nothing to decide unless the operator wants
  the refusal preserved.
