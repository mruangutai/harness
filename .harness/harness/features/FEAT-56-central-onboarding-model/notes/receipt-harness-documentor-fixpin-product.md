# Receipt — harness-documentor — FEAT-56 fix-build-pin-heading (run `fixpin-product`)

**BLUF (plan, written before the edit).** `.harness/harness/docs/BUILD.md:88` still asserted the
CLI-pin doctrine that the paragraph at `:96-99` disclaims. Two edits, one file: reword `:88` to
introduce the band table as the record it is, and re-wrap `:96-99` (whitespace only) to the file's
prevailing prose width. Nothing else in BUILD.md, no other file.

## Before-state (verbatim, at spawn; file clean per `git status --porcelain`)

Heading, `:88`:

```
**Version bands — the behavior changed three times, so the CLI version must be pinned:**
```

Paragraph, `:96-99`:

```
**CLI ≥ 2.1.217 is the floor for all three spawn env vars** — a compatibility fact to check against the
bands above, declared nowhere in config — and set the depth explicitly to `3` in every project. Setting
it explicitly is correct in *all* bands — relying on the
default means the org silently reshapes the next time it moves.
```

Measured prevailing prose width (non-table lines): mode/ceiling ≈ 99–102 columns, so the target wrap
is ≤ 100 (`awk '{print length}' | sort -n | uniq -c` on `grep -v '^|'` output). `:98` breaking at 50
columns is the ragged line.

Baseline `grep -c cli_min_version .harness/harness/docs/BUILD.md` → `0`, exit 1 (token absent
before the edit; must stay absent).

Non-goals confirmed untouched by design: the `Verified 2026-07-26 … Requires CLI ≥ 2.1.217`
platform-claims heading and its rows (~`:517`, `:521-526`), the band table `:90-94`, all other files.

## After-state evidence

### 1 — heading, before → after (verbatim)

Before (`:88`):

```
**Version bands — the behavior changed three times, so the CLI version must be pinned:**
```

After (`:88-89`, wrapped like the `**Belt-and-suspenders, …**` lead-in three paragraphs below):

```
**Version bands — the nesting default changed three times across CLI versions, which is why the
depth is set explicitly rather than inferred from the version in play:**
```

Why it is consistent with the paragraph beneath it: the paragraph presents `2.1.217` as a
compatibility fact the reader checks against the bands and "declared nowhere in config", and tells
the reader to set the depth explicitly; the new heading introduces the table as the version-by-version
record that justifies setting the depth explicitly, and gives no instruction to pin a CLI version.

### 2 — the forbidden token stays absent

```
$ grep -q cli_min_version .harness/harness/docs/BUILD.md ; echo $?
1
```

`grep -q` exit 1 = no match, so T-20's `! grep -q …` assertion still holds.

### 3 — diff confined to the two edits (2 hunks)

`git diff -- .harness/harness/docs/BUILD.md | grep -c '^@@'` → `2`.

```
@@ -85,7 +85,8 @@ matcher, so one registration each serves the whole roster.
 > page prose says "by default, a subagent can't spawn subagents of its own", which describes the
 > 2.1.217–218 band only; `env-vars` is authoritative and says the default is 3.

-**Version bands — the behavior changed three times, so the CLI version must be pinned:**
+**Version bands — the nesting default changed three times across CLI versions, which is why the
+depth is set explicitly rather than inferred from the version in play:**

 | CLI version | Nesting default | Configurable |
 |---|---|---|
@@ -93,10 +94,10 @@ matcher, so one registration each serves the whole roster.
 | 2.1.217 – 2.1.218 | **1** (off) | yes |
 | **≥ 2.1.219** | **3** (on) | yes |

-**CLI ≥ 2.1.217 is the floor for all three spawn env vars** — a compatibility fact to check against the
-bands above, declared nowhere in config — and set the depth explicitly to `3` in every project. Setting
-it explicitly is correct in *all* bands — relying on the
-default means the org silently reshapes the next time it moves.
+**CLI ≥ 2.1.217 is the floor for all three spawn env vars** — a compatibility fact to check against
+the bands above, declared nowhere in config — and set the depth explicitly to `3` in every project.
+Setting it explicitly is correct in *all* bands — relying on the default means the org silently
+reshapes the next time it moves.

 **Belt-and-suspenders, and the actually-reliable mechanism:** "members are always leaves" is enforced
 independently by **omitting `Agent` from every member's `tools:` list**. Do that regardless of the
```

(The diff body above is quoted; its `-`/`+` markers are git's.) The band table lines
`| CLI version …`, `|---|---|---|`, and the three data rows appear only as context, so they are
byte-identical; the platform-claims heading and rows near `:518`/`:527` are absent from the diff
entirely, i.e. untouched.

New line widths (bytes, then columns after discounting the 3-byte `—`/`≥`): 97→95, 72, 103→99,
101→99, 97→95, 32. All at or under the file's prevailing prose ceiling of ~100 columns; the old
50-column break at `:98` is gone.

### 4 — token identity of the re-wrapped paragraph

```
$ git show HEAD:.harness/harness/docs/BUILD.md | sed -n '96,99p' | tr -s '[:space:]' '\n' > /tmp/fp_old.txt
$ sed -n '97,100p' .harness/harness/docs/BUILD.md   | tr -s '[:space:]' '\n' > /tmp/fp_new.txt
$ diff /tmp/fp_old.txt /tmp/fp_new.txt ; echo $?
0
```

Zero output, exit 0: the 60-token whitespace-separated sequence (words, punctuation and emphasis
markers alike) is identical before and after. Edit 2 is whitespace-only.

### 5 — decision anchors and index UNAFFECTED

```
$ env -u HARNESS_AGENT_TYPE python3 .claude/skills/harness/bin/check-decision-anchors.py
examined 34 anchor(s), 0 failed
exit=0
$ env -u HARNESS_AGENT_TYPE python3 .claude/skills/harness/bin/gen-decisions-index.py --stdout \
    | diff - .harness/harness/docs/DECISIONS-INDEX.md
exit=0
```

The `diff` printed zero bytes — emptiness is the pass condition here. 34 anchors examined, as
expected; neither DECISIONS.md nor the index was touched.

### 6 — working tree

```
$ git status --porcelain
 M .harness/harness/docs/BUILD.md
 M .harness/harness/features/FEAT-56-central-onboarding-model/plan.yaml
?? .harness/harness/features/FEAT-56-central-onboarding-model/notes/receipt-harness-dev-ops-t14-eng.md
?? .harness/harness/features/FEAT-56-central-onboarding-model/notes/receipt-harness-documentor-fixpin-product.md
```

Attribution: `BUILD.md` and `receipt-harness-documentor-fixpin-product.md` are mine. `plan.yaml` is
the product-lead's run-state checkpoint (`ShipCentralOnboarding.FixBuildPinDoctrine`), not mine.
`receipt-harness-dev-ops-t14-eng.md` belongs to `ShipCentralOnboarding.BuildT14.T14CommandPort`
(T-20/T-14 sibling, dev-ops). I read neither and edited neither. Sibling `bin/**` and `tests/**`
work (T-14, T-17) had not landed as of this snapshot; if it appears later it is not mine. Nothing
committed, HEAD untouched, and I ran no project-wide suite, formatter or linter — only the two
scoped decision checks item 5 names.
