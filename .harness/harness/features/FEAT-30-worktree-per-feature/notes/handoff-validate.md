# Handoff — FEAT-30-worktree-per-feature, validate → fix/ship — written at cafa28a, seq-3

## Next

**Get the Q1 ruling, then close F-1.** The write guard is allow-by-omission and this diff added two
first-party write CLIs downstream of that one recognition step. **(a)** invert the default for known
first-party write tools [enforcement, operator]; **(b)** each tool self-validates identity and
destination — require `--agent`, validate `--file` against its domain, new exit code [**squad-appliable**,
one eng-lead cycle, the immediate close F-1 asks for]; **(c)** a running post-write audit [operator].
After the ruling: apply, re-run both suites, **re-pin `review_sha` at the new tip**, and re-review at
least `expertise-merge.py` — the apply moves the tip and invalidates the panel verdict now standing on
the other fifteen files. Six cycles remain of thirteen. Briefing:
`notes/ship-review-2026-08-21-04-validator.md`.

## Trust

- Panel **FAIL**, `severity_max: high`, one `must_fix`; goal-check **PASS**, 11 of 12 `met`, SC-01
  `met-with-caveat` — `runs/2026-08-21-04-validator/digest.md`, `runs/2026-08-21-05-product/digest.md`
  — verified-at cafa28a
- **F-1 reproduced by me, not relayed:** `harness-documentor`, `harness-code-reviewer` and
  `harness-orchestrator` each get rc=0 writing arbitrary paths via `expertise-merge.py` while `echo >`
  to the same targets is rc=2; against a COPY of `check-domain.sh`, 67,976 → 71 bytes at exit 0 —
  verified-at cafa28a
- `review_sha` = **`a76d69a`**, committed; tip `cafa28a` is past it and the intervening commits change
  only state, notes and `SPEC.md` — `feature.json` — verified-at cafa28a
- `cycles_used` **7 of 13**; all five validate segments reported ZERO send-backs — verified-at cafa28a
- Suites at the pin: unit exit 0, integration exit 0, zero FAIL, three runs each — verified-at cafa28a
- **T-03's red proof is INERT:** its `WORKTREES_SEGMENT` mutation leaves 38/38 parity cases green;
  `checkout_relative` → `return None` reddens 33 of 38 plus 5 of 8 deep-layout. The constant has no use
  in the grant re-basing path at all — verified-at cafa28a
- **F-ALT-1 is REFUTED:** flipping `REFUSE_ON_DIRTY`, `REQUIRE_LANDED`, `UNION_APPLY` to `False` reddens
  their suites 4/13/12, exit 1 all three — verified-at cafa28a
- Two-level layout has **zero live instances**; the only live tree is one-segment FEAT-31 and governance
  inside it matches root both directions — `git worktree list`, `--resolve` — verified-at cafa28a
- Mirror unsynced, 11 INV-26 rows; `close-task` is **denied to agents** by the permission classifier as
  outward-facing — `check-state.sh` — verified-at cafa28a
- `remove` has no cwd guard and no test for one — `cmd_remove` GATE 1-3 — verified-at cafa28a

## Dead ends

- Do NOT dispatch remedy (b) before the Q1 ruling — it is one of three options the operator is choosing
  between, and applying it unreviewed moves the pin — source: my authority boundary
- Do NOT re-run qa, simplify or docs; all three PASSed at this pin, zero send-backs — verified-at cafa28a
- Do NOT read the headline suite counts as test counts: "213" is `^PASS ` lines, only 16 per-script, and
  738 further case results print as `ok ` — verified-at cafa28a
- Do NOT attribute the contradictory signed intent to T-05 — it is **T-04's** (`plan.yaml:736-739` vs
  `:861-863`) — source: review panel
- Do NOT narrow `expertise-merge.py`'s `ENTRY_RE` to match `check-expertise.sh`: narrowing makes the line
  fail the regex so `parse_expertise` drops it silently. Validate instead — source: review panel
- Do NOT touch `.claude/worktrees/FEAT-31`, FEAT-26 or FEAT-28, and do NOT put a `phase:` key in
  `feature.json` — the shape gate denies it — verified-at cafa28a
- Issue **#626** is out of scope, though possibly one entry short (DEC-95, `DECISIONS-INDEX.md:114`).
  Ship-refresh is a legitimate SKIP: no `INDEX.md` map exists — verified-at cafa28a

## Working set

- `…/notes/ship-review-2026-08-21-04-validator.md` — operator briefing, backlog B-1..B-18 with IDs
- `…/runs/2026-08-21-04-validator/digest.md` — the must_fix, four Qs, adequacy notes
- `…/notes/review-harness-security-reviewer-2026-08-21-04-validator.md` — F-1's live demonstration
- `…/STATE.md` — current truth and the seven open questions
