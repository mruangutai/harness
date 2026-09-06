# Plan fix cycle 3 — BUG-1305 — re-keying Mode-A prevention on a minted run identity

**BLUF: the acquisition refusal is gone and Mode-A prevention now keys on `run_uid`, a `uuid4().hex`
minted by check-domain.sh's PostToolUse mode and carried by the checkpoint itself. The refusal is the
Issue #1124 compare re-keyed onto that field, inside the existing `if prior_state:` ladder — so no
refusal can fire on an empty or absent prior, and the recovering owner the panel found is refused by
nothing. The backfill and its invariant are retired; the detection invariant is self-limiting
instead. Panel ranks 1-6 all applied, none declined.**

## The mechanism, end to end

| Moment | Host | What happens |
|---|---|---|
| Mint | `check-domain.sh` POST, `elif target:` at :1930-1950 | effective uid = landed doc's `run_uid`, else witness's, else `mint_uid()`; `inject_uid()` appends one `run_uid:` line by TEXT (no YAML round-trip); `record_seed()` writes the witness with the same value, in the same call |
| Refuse | `check-domain.sh` PRE, inside `if prior_state:` at :1530-1574, after the #1124 run_id compare | `uid_conflict(prior_doc, doc)` — prior carries a uid and incoming carries a different one, or none → deny. Write **and** Edit (Edit content is reconstructed at :1905-1923) |
| Detect | `check-state.sh` per-run-dir loop at :1426 | witness uid vs checkpoint uid disagreeing → violation. Witness absent, or either side carrying no uid → silent |

Minting has no other possible host, and the plan says so (D-12): a PRE hook cannot alter a payload,
leads hold no shell, and **no program in the tree writes a run `state.yaml`** (grepped across
`.claude/skills/harness/bin/` — only guards read it). POST is the only place a shell observes every
governed write. The cost — the POST reporter becomes a one-line writer — is the decision, not a
detail.

**The legacy window is harmless by construction, not by hope.** Until a directory receives one
POST-governed landing it carries no uid and no witness: refused by nothing new, reported by nothing.
That is *today's* behaviour byte for byte, which is why no backfill exists. A directory leaves legacy
on its own at its next governed write.

**No birth-timing gap.** Witness and uid are minted in the same POST call, and the effective-uid
order makes every half-finished state converge: uid injected without a witness → next POST records
the file's value; witness without an injected uid → next POST injects the witness's value. A
recovering owner therefore gets its *original* identity back rather than a fresh one.

## The four properties, and where each is proven

| Property | Proven at |
|---|---|
| (i) a resumed owner is never refused | `uid_conflict` equal-value row (T-01); T-09 case "THE RESUMED OWNER"; SC-01(e); T-08 direction-two pair 2 |
| (ii) an owner recovering a zeroed or deleted checkpoint is never refused | the refusal sits **inside** `if prior_state:`, so the ladder is not entered — T-09 fail-open rows a and b; T-02's two recovering-owner cases; SC-01(d); SC-07 |
| (iii) a foreign run with equal seed fields IS refused | T-09 "THE MODAL COLLISION" Write and Edit cases (incoming carries no uid — the state any run that never wrote a checkpoint is in); SC-01(b) and (c) |
| (iv) nothing historical or sibling-tree can redden the invariant | it judges only directories where witness **and** checkpoint carry a uid — T-03's Z and L cases, SC-09, plus the recorded control-plane-root run in T-08 |

## Disposition by panel rank

- **1 + 2 (one decision).** Mechanism re-specified (D-11). T-09 kept in place, re-aimed — retiring it
  would have orphaned `depends_on` in T-06 and T-08, which the dispatch protects. Every refusal keyed
  on prior-empty or prior-absent is deleted. T-09's false claim about `prior_state == ""` is replaced
  by the measured statement that **two** paths produce it (`check-domain.sh:1508-1518`).
- **3.** The Advisor's Q2c fallback is now the mechanism, recorded as D-11 with the reason the
  second-identity-signal route collapsed (cycle 2's F-01 measured that a session identity cannot
  separate a resumed owner from a foreign run). No accept-the-residual binary is carried up.
- **4.** T-10 retired in place (DO-NOT-EXECUTE, `status: abandoned`, `verify:` asserting its own note
  does not exist, station preserved). SC-09 amended from "detection is total" to "detection is
  self-limiting" (D-13).
- **5.** REQ-08 restated as freely strikeable, with the price named: striking it costs collision
  **frequency**, not correctness.
- **6.** New T-11 — one probe, two steps, `route_reachable:` / `guard_fires:` recorded at column 0,
  `## Reported` section mandatory if the route is reachable and unguarded. SC-11 grades it.
- **7.** No action; T-04 and T-08 left as the panel confirmed them.

## The residual, bounded by nature

A foreign run that **reads the prior checkpoint and copies its `run_uid`** is indistinguishable from
the owner. That is deliberate forgery, not the accidental slug reuse #1305 records. `run_uid` is a
collision-avoidance token, not a capability — which is also why T-09's refusal message may print the
value, and must, because the owner needs the exact line to carry forward.

## Open questions for the operator

- **Q1 (non-blocking).** The one knowingly new refusal: an owner that rewrites its checkpoint and
  drops `run_uid` is refused. Mitigated three ways (message names the line; POST re-injects the field
  into every landing; harness-team/SKILL.md:54-55 gains the carry-forward sentence in T-09). It is
  disclosed in REQ-01 and pinned in T-08 — strike it only with the mechanism.
- **Q2 (non-blocking).** `glossary.md` gains no `run_uid` row: pm holds no write grant on it and no
  task lists it. Add it to T-09 if you want the vocabulary recorded there.
