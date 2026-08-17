# Receipt — harness-dev-ops — FEAT-22 T-08 verify fixture probe (2026-08-16)

**awk:** `awk --version` → `awk version 20200816` (BWK/one-true-awk, macOS default). `awk -W version` → unsupported (`awk: unknown option -W ignored`, then ran with `-W` as a filename-equivalent no-op; not a real answer path on this awk).

## Clause under test

```
awk '/^### DEC-189 amendment 1/{f=1} f{b=b" "$0} END{gsub(/[ \t]+/," ",b); if (b ~ /[Tt]he correct figure is [Oo][Nn][Ee] of the four/) print "FIGURE"}' "$d" \
  | grep -q FIGURE || { echo "amendment does not carry the mandated corrective phrase"; exit 1; }
```

Each variant is its own fixture file under the scratchpad
(`fixtures/v1.md` … `v6.md`, `v0-no-heading.md`), heading `### DEC-189 amendment 1 (2026-08-16) — clarification` present in v1–v6.

## Results

| Variant | Body span (verbatim) | Exit |
|---|---|---|
| V1 | `**the correct figure is ONE of the four.**` (whole-span bold) | **0** |
| V2 | `the correct figure is **ONE** of the four.` (interior bold on ONE) | **1** |
| V3 | `` the correct figure is `ONE` of the four. `` (interior code span) | **1** |
| V4 | `> ... the correct figure is` / `> ONE of the four.` (blockquote, 2 lines) | **1** |
| V5 | `- the correct figure is ONE of the four.` (bullet, span starts the bullet) | **0** |
| V6 | `The correct figure is one of the four named paths.` (sentence-case, trailing words) | **0** |
| No heading | `### DEC-189 amendment 1` heading absent entirely from file | **1** (fail closed) |

## Reading

The clause fails closed when the heading is absent (exit 1, correct). Among headed variants, it
false-REDs (exit 1) on any markup token — `**`, `` ` ``, or a blockquote `> ` prefix — that lands
*inside* the mandated phrase, because `gsub` only collapses whitespace and never strips inline
markup, so the literal marker character breaks contiguity of "is ONE of". It passes (exit 0) for
whole-span bold (V1, markup wraps the phrase from outside), a bullet where the phrase starts right
after `- ` (V5), and sentence-case with trailing prose (V6, case-insensitive class already covers
this). Net: 3/6 headed variants false-RED under interior markup; the heading-absence guard holds.
