# FEAT-24 — arch-review fix pass — 2026-08-18

**All nine dispatched items are applied except one, which is declined with a reason (item 8's N-2
half). No decision text changed, approval is still `pending`, and no assertion was deleted or
weakened anywhere.** The plan is ready for the signature gate to re-open on it.

## Anchors re-derived at source before editing (not taken from the review)

| Claim | Verified at |
|---|---|
| `key_base = f"{where}.board"` — the double prefix | `factory_config.py:77` |
| stations message says "exactly ready, building and review" | `factory_config.py:106-107` |
| only caller passing `repos[<name>]`, deleted by T-02 | `factory_config.py:157` |
| `load_board` coerces a digit string; `_validate_board` rejects it | `gh_board.py:80-85` vs `factory_config.py:88` |
| `skip()` and `die()` both `print()` to **stdout** | `gh-sync.py:70-80` |
| an expected exception "is printed verbatim, not re-wrapped" | `factory_cli.py:77` |
| `derive_station(_pdoc)` called unwrapped | `check-state.sh:1180` |
| `os.access` is the import-time probe | `factory_config.py:41` |
| `check()` is the file's one case-dispatch point | `test-factory-config.py:30` |

## What each item became

- **F-1** — T-02 gains items 2a (`where` is the FULL prefix, `key_base` = `where`, docstring
  examples corrected) and 2b (stations message names the five). Full-key-path pins added to one
  case per entry point: `github.board.owner` present AND `github.board.board` absent, in T-02's
  `owner missing` board_for case and T-04's matching `load_board` case.
- **F-2** — a paragraph in T-04's intent (one commit with T-05; `check-state.sh` EXPECTED to exit 1
  between them; do not edit it, DEC-174; return on T-04's own verify) mirrored into T-05's intent.
  **N-3** got its own sentence in T-02 and T-03 — different task pair, so the F-2 note could not
  carry it.
- **F-3** — coercion moves inside `validate_board` (T-02 item 2c, mutating `board["number"]` so the
  caller sees the normalised int); T-04 item 1 deletes its own branch and the coerce/validate order
  question disappears. Item 2d forbids deleting the pinned case; its **driver** changes to a float
  or a non-digit string, ok-line text unchanged.
  Item 2c also pins the **return value**: `validate_board` returns the validated mapping. Today
  `_validate_board` returns `None` (raising was its whole job), but T-02 item 7 and T-04 item 1 both
  consume its return, so a strict reading of "keeps its current signature" would have made
  `board_for` return `None`.
- **gh-sync text contract** — one atomic edit: stderr, exit 2, `str(exc)` verbatim, `gh-sync:`
  prefix, with the reason `die()` is not reusable. Part C item 7 gains the `str(exc)` clause.
  **Strengthened beyond the dispatch:** the gh-sync test case now asserts exit status **2 exactly**
  and the key on **stderr**, because a non-zero assertion cannot see the divergence being pinned.
- **T-09 decoupling** — `depends_on: []`; `validate_board` and the `sys.path`/import lines removed
  from its verify; stray-key assertions (`set(st) != set(want)`, `"plan" in st`) and an
  `isinstance(st, dict)` guard added in their place; the paragraph justifying the coupling rewritten
  rather than left standing beside its own reversal.
- **D-10 enforceable** — T-07's verify gains a `gh api` read of kaya's config at `master` through
  `validate_board`, failing on unreadable / absent / malformed. This pushed T-07 to 59 machine-field
  lines (budget 50); the new block was compressed to 11 lines rather than trimming any existing
  assertion. T-07 now sits at 49.
- **Memo helper** — `clear_product_config_memo()` in `factory_config.py`, called as the first
  statement of `test-factory-config.py`'s `check()`. Confirmed at source that `check()` exists and
  every case routes through it. The one constraint this creates — a memo-sensitive case must make
  all its calls before its `check()` — is written into the task and applies only to the memoisation
  case, which already does.
- **`_validate_stations` survey correction** — the `factory_decompose.py` survey entry now says
  source unchanged, behaviour changed: three option names validated becomes five, live refuse at
  decompose time, fails closed. **N-4** applied: "one filesystem probe (`os.access`) to resolve the
  harness root."
- **#498 citation** — `BRIEF.md:3`, with the ledger-versus-execution-record rationale. Nothing else
  in the brief touched; `#336 D-07` in Constraints is a decision reference and stays.

## Declined

- **N-2** (D-06's reversibility cost: a sixth station key later is N cross-repository pull requests).
  Its only home is `D-06`'s `because`, and decisions are LEAVE. Raised as an open question instead.
- **The `what`-slot advisory** ("fleet key invalid" is wrong when the caller is `load_board`).
  Declined, not deferred: after F-1 both surviving callers pass the identical `where` value
  `github.board`, so `validate_board` cannot distinguish its caller without a new parameter — which
  contradicts T-02 item 2's kept signature — or a catch-and-re-wrap in `load_board`, which
  contradicts the `str(exc)`-verbatim rule this same pass just pinned. A caller-neutral rewrite for
  both is available and cheap, but the dispatch scoped the item to the `load_board` case only.
  Raised as an open question.

## Record correction

Neither of my research notes carried the mistaken account of the lost finding. `STATE.md:36` already
records the correct one ("Any record blaming the eng squad's collation for that is wrong"), and
`STATE.md` is not mine to edit. Nothing to correct.

## Open questions carried into the DIGEST

- D-10's `because` says "nothing in this repository can enforce it". T-07's new verify now does.
  The sentence is false as it stands; correcting it is a decision edit.
- N-2's home is D-06's `because`.
- Whether the `what` slot should become caller-neutral (one word, both call sites) rather than
  caller-scoped.
