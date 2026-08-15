# FEAT-14 security review — did the write-path rewrite stay safe?

Range reviewed: `1bdfe3f..HEAD` (HEAD=`2dea9f9`, `review_sha`=`3abaedd`, remainder state-only).
Scope: `gh-sync.py`, `factory_claim.py`, `factory_decompose.py` write paths, per dispatch.

**BLUF: yes, with one pre-existing gap the rewrite had a chance to close and didn't.**
`factory_decompose.py`'s `write_factory` — the one the plan named — kept its
atomicity exactly as required. `gh-sync.py`'s `save_recorded` — a second writer to the
same file, not named in the plan's atomicity clause — is not atomic, and I traced that
gap to a concrete (if narrow) external-mutation consequence. Nothing here is a
regression introduced by this diff; both the non-atomicity and the silent-missing-file
read are byte-identical to pre-`1bdfe3f` code. severity_max is `med`, no must-fix.

## F1 (med) — `gh-sync.py:298` `save_recorded` is not atomic; a crash mid-write lands in exactly the state gh-sync treats as "nothing mirrored"

Evidence, quoted:

```
$ python3 -c "import inspect,importlib.util as ilu; s=ilu.spec_from_file_location('g','.claude/skills/harness/bin/gh-sync.py'); m=ilu.module_from_spec(s); s.loader.exec_module(m); print(inspect.getsource(m.save_recorded))"
def save_recorded(feat_dir, rec):
    p = os.path.join(feat_dir, "feature.json")
    doc = harness_yaml.load_file(p)
    doc["github"] = {...}
    with open(p, "w", encoding="utf-8") as f:
        json.dump(doc, f, indent=2)
        f.write("\n")
```

No `tempfile.mkstemp`, no `os.replace`. Compare `factory_decompose.py:174-180`
(`write_factory`, the one the plan named): `fd, tmp = tempfile.mkstemp(..., dir=dirpath)`
… `os.replace(tmp, path)` in a `try/except BaseException` that unlinks the temp file on
failure — this one is correct, same-directory, verified compliant.

`open(p, "w")` truncates the file **at open**, before any bytes are written. I confirmed
what a truncated read produces:

```
Probe B: zero-byte feature.json -> load_recorded()
=> {'milestone': None, 'parent': None, 'parent_origin': None, 'attached': [], 'issues': {}}
```

i.e. the *default/empty* record, silently, no exception. That is precisely the state the
dispatch names as externally destructive: `gh-sync open` reads a zero-byte (or
otherwise truncated) `feature.json` as "nothing is mirrored" and re-creates the
milestone/parent/issues that already exist on GitHub — a mutation `git reset` cannot
undo.

So the chain is: process killed (OOM, SIGKILL, power loss) during `save_recorded`'s
write window -> `feature.json` left zero-byte or partial -> next `gh-sync` invocation on
that feature silently re-files. The window is narrow (a few milliseconds of wall time)
and requires an external kill signal, not attacker input — hence `med`, not `high`.

**Correct-today vs regression:** NOT a regression. Pre-`1bdfe3f` `save_recorded` was
already `open(p, "w").write(...)` with no tempfile/replace:

```
$ git show 1bdfe3f:.claude/skills/harness/bin/gh-sync.py | sed -n '/^def save_recorded/,/^def /p'
def save_recorded(feat_dir, rec):
    p = os.path.join(feat_dir, "feature.yaml")
    t = read(p)
    ...
    open(p, "w").write(t + "\n".join(lines) + "\n")
```

Same non-atomic shape, same file. The plan (`plan.yaml:884-889`, T-05 item 4) explicitly
scoped "KEEP THE ATOMICITY EXACTLY AS IT IS — tempfile.mkstemp in the same directory,
then os.replace" **only to `write_factory`**; item 2 (`plan.yaml:868-878`, `save_recorded`)
specifies a plain `json.dump` with no atomicity requirement. The rewrite had a natural
opportunity to backport `write_factory`'s pattern to the sibling writer of the same file
and the plan didn't ask for it.

**Remedy:** mirror `write_factory`'s `tempfile.mkstemp(dir=dirpath)` + `fsync` +
`os.replace` in `save_recorded`. `gh-sync.py` is **not** a DEC-174 carve-out file, so
this is a normal fix cycle, not a main-session item.

**Not pinned against regression:** no test asserts `save_recorded` is atomic or
survives a simulated crash; `test-gh-sync.py`'s round-trip case (finding 2, confirmed
passing) checks key-preservation, not crash-safety.

## F2 (info, assessed-and-dismissed) — the missing-file path is unchanged, but its failure mode moved from a controlled `die()` to an uncaught exception

```
Probe A2: save_recorded() on a dir with NO feature.json
=> save_recorded raised YamlParseError: ... No such file or directory: '.../feature.json'
```

`harness_yaml.load_file` has no exists-check and `save_recorded` doesn't catch its
`YamlParseError`, so a missing file at `save_recorded` time is now an unhandled Python
traceback. Old `save_recorded` used a local `read()` helper (`git show
1bdfe3f:.claude/skills/harness/bin/gh-sync.py:123-126`) that did
`if not os.path.isfile(p): die(f"{p} does not exist")` — a clean message, same loud
failure, better presentation. Still loud either way (non-zero exit, visible), so this is
not a fail-open — a presentation-quality regression, not a security one. Reachable only
via a TOCTOU deletion of `feature.json` between `load_recorded`'s check and
`save_recorded`'s call in the same short-lived process; no code path in this diff
deletes the file. Not promoting as a finding; recording per P-12 so a later reviewer
doesn't re-raise it as unassessed.

## F3 (info, assessed-and-dismissed) — Q3's silent-missing-file read: unchanged, and the corpus it would misfire against no longer exists

`load_recorded`'s `if not os.path.exists(path): return rec` (`gh-sync.py:254-255`) is
byte-identical to the pre-`1bdfe3f` version (confirmed via `git show 1bdfe3f`) — this
predates FEAT-14 (T-06), not introduced by T-05's filename swap.

```
$ for d in .harness/features/*/; do
    echo "$d json=$([ -f "$d/feature.json" ] && echo yes || echo no) yaml=$([ -f "$d/feature.yaml" ] && echo yes || echo no)"
  done
# all 17 feature dirs: json=yes yaml=no
```

At HEAD the migration is complete: every feature dir carries `feature.json`, none
carries `feature.yaml`. **No reachable read/disk disagreement exists in the live corpus
today** — the state the T-05 prohibited-tool window (plan.yaml:935-942) was built to
prevent no longer exists because the window is closed. Correct-today, confirmed by
listing, not by argument.

Structural risk for a *future* feature dir created without a `feature.json` is
unchanged pre-existing behavior (same shape existed for a missing `feature.yaml`
before), and is **not pinned against regression**: `test-gh-sync.py` covers "no
`github:` block" (`_d2`, line ~747) but has no case for "no file at all" — confirmed
by grep (`grep -n "os.path.exists\|FileNotFoundError" test-gh-sync.py` finds nothing
in that vicinity).

## F4 (info, assessed-and-dismissed) — lost-update race between `save_recorded` and `write_factory`, same file, no locking

Both are full-document read-modify-write with no lock:

```
$ grep -n "flock|fcntl|lockf|filelock" gh-sync.py factory_decompose.py factory_claim.py
# no matches
```

Structurally a lost update is possible if both tools write the same `feature.json`
concurrently. Same shape pre-existing (old text-splicing also read-whole-file,
write-whole-file — no lock then either). Threat model: single-operator harness, not
multi-tenant; triggering this needs the operator/orchestrator (already fully trusted)
to run two write commands against the same feature dir at once — no privilege
escalation (P-02: an actor who already controls the value already holds the privilege
it grants). Not promoting.

## F5 — injection / path traversal: no surface

`feat_dir` is an operator-supplied CLI positional argument in all three tools,
unchanged shape from before this diff. `factory_gh.py`'s `gh` calls use list-form argv
(`[gh] + list(args)`, no `shell=True`) and is untouched by this diff. No new string
interpolation into a path or shell command was introduced in
`gh-sync.py`/`factory_claim.py`/`factory_decompose.py`. `check-plan-routes.py`'s
`feature_dir` comes from a directory walk over `.harness/features/*`, not external
input. No finding.

## F6 — data exposure: no surface

```
$ git diff 1bdfe3f..HEAD -- gh-sync.py factory_claim.py factory_decompose.py | grep -n "print(|stderr|sys.stderr"
# no output
```

No new stdout/stderr/log statements in the touched write-path files. No finding.

## F7 (info, doc-accuracy, not a vulnerability) — `factory_decompose.py`'s file-level invariant claim is now false as stated

`write_factory`'s docstring and the module docstring both assert `feature.json` "is
opened only for reading, never in a truncating mode" as a property of the file overall.
That's true only for `factory_decompose.py`'s own writes — `gh-sync.py:save_recorded`
opens the same file in truncating `"w"` mode (F1). Worth a comment fix alongside F1's
remedy; not itself a security finding.

## Not reviewed / explicitly out of scope here

- `check-domain.sh` write-time schema enforcement, `feature_schema.py`,
  `validate-feature-json.py` — DEC-174 carve-out (`check-domain.sh`) plus the parallel
  code reviewer's assigned surface. Observed only in passing: none of the three
  write-path tools call `feature_schema`/`validate-feature-json` before writing, so an
  eleven-key-schema violation written by `save_recorded`/`write_factory` is only caught
  at commit time by `check-domain.sh`, not at the moment the tool writes. This matches
  the feature's own description ("enforced at write time by check-domain.sh and in
  CI") — by design, not a gap I'm flagging.
- SC-04/SC-05/SC-16 automated-verification gap — already established by the qa gate,
  not re-reported.
- `check-domain.sh:866-922` fail-closed behaviour, vacuous-check hunt — parallel code
  reviewer's assigned surface.

## Test evidence (fixture suites only, per constraint 2 — no `gh`, no `--repo`, no live corpus mutation)

```
$ python3 .claude/skills/harness/bin/test-gh-sync.py 2>&1 | tail -3
ALL PASSED
$ python3 .claude/skills/harness/bin/test-factory-decompose.py 2>&1 | tail -1
174/174 checks passed.
$ python3 .claude/skills/harness/bin/test-factory-claim.py 2>&1 | tail -1
96/96 checks passed.
```

`git status --porcelain` before and after this review: unchanged apart from
pre-existing untracked notes files from other agents' parallel runs; no source path was
edited, no `gh`/`--repo`/sync/decompose/claim command was run against the live corpus.
