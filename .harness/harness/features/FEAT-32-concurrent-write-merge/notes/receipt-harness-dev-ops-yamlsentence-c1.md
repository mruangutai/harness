# Receipt — harness-dev-ops — yamlsentence-c1 (FEAT-32)

## What changed

Docstring-only fix in `.claude/skills/harness/bin/harness_yaml.py` (lines 4-6 region). The old
universal claim ("Every other module in this tree that needs YAML imports THIS module, never
`yaml` directly") was false as of `plan-merge.py`'s new plain `import yaml`. Replaced with a
sentence that keeps the true D-12 claim (this is still the only guarded
`try: import yaml / except ImportError:`), names the one exception, states why
(`plan-merge.py` is required to import PyYAML plainly), and states the consequence: it parses
under plain PyYAML semantics, not this module's `DuplicateKeyError` strictness — the two loaders
disagree about what counts as a valid plan file.

New text (verbatim):

> D-12: this is the ONLY `try: import yaml / except ImportError:` in the whole
> tree. It parses nothing itself — it exits or grants. Every other module in
> this tree that needs YAML imports THIS module, never `yaml` directly — with
> one named exception, `plan-merge.py`, which is required to import PyYAML
> plainly. That tool therefore parses under plain PyYAML semantics, not this
> module's duplicate-key strictness (`DuplicateKeyError`, raised below): the
> two loaders disagree about what counts as a valid plan file.

## Independent verification of the premise

`grep -rn "^import yaml\|^\s*import yaml" --include="*.py" .` under `.claude/skills/harness/bin/`,
excluding `test-*.py`: only `harness_yaml.py:18` (inside its own guarded try/except) and
`plan-merge.py:37`. Confirms the dispatch's premise directly rather than trusting it.

## Verify (all four, exit codes observed)

1. `python3 -c "import sys; sys.path.insert(0, '.../bin'); import harness_yaml"` — exit 0
2. `python3 .../test-harness-yaml.py` — all `ok`, exit 0
   `python3 .../test-harness-yaml-corpus.py` — 16/16 checks passed, exit 0
3. `git diff --numstat -- .../harness_yaml.py` — `5 1 .claude/skills/harness/bin/harness_yaml.py`
   `git diff` confirms the only hunk touched is inside the module docstring (lines 4-9 region);
   no code, import, or line outside that paragraph moved.
4. `bash .../run-unit-tests.sh --check-kinds` — "check-kinds: the script arrays and
   test_kinds.integration.detect agree." — exit 0

## Scope discipline

Comment/docstring text only — no code, import, or behaviour changed. Did not touch
`plan-merge.py`, `plan.yaml`, `BRIEF.md`, `.gitignore`, or any file besides `harness_yaml.py`.
Left the tree dirty (not staged, not committed) per DEC-153.
