# FEAT-58 · cycle-3 goal-check fix — GC-01 and GC-02 both LANDED

**Both findings are applied and the census is now meetable with ZERO residual: every one of the 30
in-subject sites sits in a file some task's `files:` list already contains under `D-07`.** No task
was added, no `D-07` row invented, no `files:` list widened. `check-plan-routes.py` on this plan:
`0 violation(s) across 1 plan(s)`, exit 0 (10 TASK `DEVIATION` + 2 `OK`, no `MANIFEST` deviation).
`status: plan`, `approval.status: pending`, BRIEF `## Approval` and the 13 `panel` findings at
`disposition: open` untouched. 12 tasks / 13 decisions / SC-01..SC-15.

## GC-01 (high) — the census subject is narrowed to an ENUMERATION, and it is now satisfiable

**Subject, as written into `N-12`'s intent and `SC-14`:** a call to an enumeration primitive
(`glob.glob`, `glob.iglob`, `os.listdir`, `os.scandir`, `Path.iterdir`, shell `ls`, a shell glob
expansion) whose pattern names a `features` segment AND whose feature-id position is a wildcard or
absent — i.e. it enumerates FEATURE DIRECTORIES. One level of pattern indirection is resolved
(`pattern = …join(…)` on the line above the call), because four real sites are spelled that way.

**Out of subject, explicitly:** comments, docstrings, message strings, regex literals, code-shaped
string literals (implemented by TOKENIZING, not by a skip list); single-feature joins that never
enumerate; and any site **pinned or filtered to one caller-named feature id** — it never reports a
set of records, so it cannot narrow a count.

Both properties the census exists for are kept: HALF 1 stays quantified over **every** `.py`/`.sh`
under `bin/` and is explicitly forbidden a file allow-list; and it stays free of a time dimension —
no count pinned over the real tree, no mtime, no git range, no baseline file — with HALF 2's
scratch-directory exactly-one-finding proof intact and now required to be written in a spelling the
narrowed detector actually finds.

### The census, measured — 30 sites in 8 files

Observed 2026-09-10 at `5dda443b13b2b02e21e629f95416e177ba2f1274`, `bin/` clean at that sha
(`git status --porcelain -- .claude/skills/harness/bin` → 0 lines). Invocation:

```
python3 <script below> <wt>/.claude/skills/harness/bin
→ 30 sites in 8 files
```

**Which task writes what — the whole point of the finding:**

| File | sites | lines | writer per `D-07` |
|---|---|---|---|
| `check-state.sh` | 21 | 119,128,130,137,242,272,295,608,1151,1290,1312,1341,1376,1433,1576,1615,1726,2025,2127,2176,2371 | **N-06** |
| `check-plan-routes.py` | 2 | 678, 835 | **N-10** |
| `layout_migration.py` | 2 | 187, 188 | **N-10** |
| `board_lifecycle.py` | 1 | 477 | **N-10** |
| `validate-feature-json.py` | 1 | 44 | **N-10** |
| `merge-gate.py` | 1 | 134 | **N-07** |
| `check-domain.sh` | 1 | 1916 | **N-06** then **N-11** (N-11 PART 1 owns `:1916`) |
| `branch-create-gate.sh` | 1 | 89 | **N-11** |

**Residual: none.** The two sites the pinned-id rule excludes are exactly the two files with no
writer — `quarantine.py:120` (`args.feature` at the feature-id position) and
`feature-worktree.py:245-247` (`os.listdir` filtered by `args.id + "-"`, and the file is UNMODIFIED
BY CONSTRUCTION under `D-10`). The narrowing was not chosen to dodge them; they are the canonical
shape of "resolves one id" and are named in `N-12` as evidence of the rule, never as an allow-list.
The earlier subject's figure — "30 lines across 15 files", a bare assertion with no invocation — is
struck; the wide subject actually reaches 114 lines in 32 files.

### Markers the narrowing newly requires (1c) — added to the intent of the file's existing owner

- **`N-06`** gained `MARK ALL 21 SITES`. Its previous instruction marked the choke point only and
  said "do not touch the other 20", which left HALF 1 red on 20 sites. Reworded to **CHANGE NO
  BEHAVIOUR at the other 20**: a marker is a comment, not a behaviour edit. `:118-120` carries
  `active-feature`; the other 20 carry `checkout-local`.
- **`N-10`** PART 3 now says the lines are **six, not four** (four scripts, six enumerations) and
  names the per-file counts — exactly the set the census detects in its files.
- `N-07` PART 2 (`merge-gate.py:134`) and `N-11` PART 3 (`check-domain.sh:1916`,
  `branch-create-gate.sh:89`) already marked every site the census detects in their files.

### The fourth vocabulary value — `# corpus-scope: checkout-local` (1d), an authoring choice

Added at `plan.yaml` N-12 (the definition) and N-10 PART 3 (the restatement); the other three
citations reference the vocabulary by name rather than copying it, so there is no third copy to
drift. Meaning: *a corpus enumeration deliberately scoped to THIS CHECKOUT's materialised corpus —
it answers about this checkout, and a narrowed answer is the correct answer there.*

It earns its place on **20 real sites**, not on a hypothetical: `check-state.sh`'s sites downstream
of the choke point read what this checkout materialised, which the preflight has already asserted
equals the expected set — `active-feature` would be false in a full checkout and
`not-a-corpus-read` would simply be untrue. `check-domain.sh:1052-1062` `_SWEEP_PATTERNS` is the
canonical instance of the same semantics and **is not detected** by the narrowed subject (its
enumeration line carries no `features` segment), so it needs no marker and `D-02` stays untouched —
a cleaner outcome than marking it, which is why the value's justification moved to `check-state.sh`.
The vocabulary stays CLOSED: exactly one marker per detected site, from those four.

One further unmeetability fixed in passing, inside the same census: the "every owner-root marked
site imports `feature_corpus`" assertion now reads **NAMES** `feature_corpus` — `branch-create-gate.sh`
is POSIX sh and reaches the module through a `python3` call, so the import spelling would have
failed a correct `N-11`.

## GC-02 (med) — DoD point 2 is now graded at the CREATION surface

All three landed:

- **`REQUIRED_PATHS`** (`N-01`) gains `.harness/corpus`, flagged as the one entry that is not a
  tracked path, carrying its assertion form (`islink` + `realpath`) so `N-05` cannot degrade it to
  an existence check.
- **`N-05` GROUP 2** gains its own named case with its own failure message: `os.path.islink` on
  `<worktree>/.harness/corpus` AND `os.path.realpath` equal to the fixture owner root's
  `.harness/harness/features`. Never an exit status, never folded into the `BRIEF.md` clause.
- **`SC-01`** gains the same clause, plus the reason a bare `exists()` is inadmissible.

**The composition was verified, not adopted.** `N-05` GROUP 1b asserts group 2's required paths over
a bare `git worktree add`, so the corpus clause needs a subject on that arm: `post-checkout` fires
on `git worktree add` with cwd already inside the new tree (`N-05`'s own design point), `N-04` PART 1
makes that shim run `worktree-state.py --repair` (`D-03`), and `N-02` **check 3** is `CORPUS SYMLINK
PRESENT … Repair creates the symlink`. Both arms have a subject; recorded in GROUP 1b's intent, with
the caveat that the bare-route worktree must carry a feature-id basename or `N-02`'s scope guard
legitimately no-ops (and group 1's sparseness clauses fail first anyway).

## Record honesty

**One id moved: `SC-01` now also grades D-2 (DoD)** in `BRIEF.md`'s coverage table (`SC-02`
continues to grade the READ surface), and `N-05`'s `traces:` gained `REQ-02` to match. No REQ id and
no other SC id changed row; the note is written into the table so it is not ambiguous. No ledger row
was touched — the two evidence-form demotions (`N-09` PART 1 (b) / `AUDIT UNCHANGED`, `N-06`
`PRE-CHANGE REPRODUCTION`) remain visible in `## Verification gaps` where the operator signs.
`SC-14` is a NEW criterion, so narrowing it costs zero ledger coverage. GC-03 and GC-04 were out of
this segment and were not touched.

## Appendix — the enumerator, as run

```python
import io, os, re, sys, tokenize
P = {"glob", "iglob", "listdir", "scandir", "iterdir"}
PIN = re.compile(r"args\s*\.\s*(feature|id)\b")
SH = re.compile(r"glob\.i?glob\(|os\.(listdir|scandir)\(|\.iterdir\(|\bls\s|\bfor\s+\w+\s+in\s")
hits = {}
for f in sorted(os.listdir(sys.argv[1])):
    if not f.endswith((".py", ".sh")):
        continue
    src = open(os.path.join(sys.argv[1], f), errors="replace").read()
    lines, out = src.splitlines(), []
    if f.endswith(".py"):
        tk = [t for t in tokenize.generate_tokens(io.StringIO(src).readline)
              if t.type in (tokenize.NAME, tokenize.OP, tokenize.NUMBER, tokenize.STRING)]
        asg = {}
        for i, t in enumerate(tk):                      # one level of pattern indirection
            if t.type == tokenize.NAME and i + 1 < len(tk) and tk[i + 1].string == "=":
                asg.setdefault(t.string, []).append(
                    (t.start[0], " ".join(x.string for x in tk[i + 2:] if x.start[0] <= t.start[0] + 3)))
        for i, t in enumerate(tk):
            if t.type != tokenize.NAME or t.string not in P or tk[i + 1].string != "(":
                continue
            d, arg, j = 0, [], i + 1
            while j < len(tk):
                s = tk[j].string
                d += (s == "(") - (s == ")")
                if d == 0:
                    break
                if d >= 1 and s != "(":
                    arg.append(s)
                j += 1
            a = " ".join(arg)
            if re.fullmatch(r"\s*\w+\s*", a):
                pr = [r for ln, r in asg.get(a.strip(), []) if ln <= t.start[0]]
                a += pr[-1] if pr else ""
            if "features" in a and not (PIN.search(a)
                                        or PIN.search("".join(lines[t.start[0] - 1:t.start[0] + 2]))):
                out.append(t.start[0])
    else:
        for n, raw in enumerate(lines, 1):
            if raw.lstrip().startswith("#"):
                continue
            L = raw.split(" #")[0]
            if SH.search(L) and "features" in L and not PIN.search("".join(lines[n - 1:n + 2])):
                out.append(n)
    if out:
        hits[f] = out
print(sum(len(v) for v in hits.values()), "sites in", len(hits), "files")
for f, v in hits.items():
    print(" ", f, len(v), v)
```

This is a MEASUREMENT script, not the deliverable: `N-12` authors the real test, and the figure it
produces is deliberately not an assertion anywhere in the plan.

## Open

- Nothing blocking. The narrowed subject leaves `check-domain.sh:1052-1062` `_SWEEP_PATTERNS`
  undetected — deliberate (`D-02` does not change it) but it means a future editor who adds a
  corpus glob **as a pattern string in a list** consumed elsewhere is not caught by HALF 1. Not
  worth a detector that resolves list-valued indirection now; noted so a later cycle can decide.
