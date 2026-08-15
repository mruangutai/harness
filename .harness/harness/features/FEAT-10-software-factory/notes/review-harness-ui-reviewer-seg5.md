# UI-reviewer delta review — FEAT-10 seg5 (Mode A, pre-build)

**Verdict: FAIL.** MF-2 is not closed — a genuine, textual internal contradiction survives the
revision, and it is exactly the candidate the dispatch named. Everything else closes or discharges.

## MF-1..MF-7 verdict table

| ID | Verdict | Pointer |
|---|---|---|
| MF-1 wedge | **not closed as claimed, but downgraded to a stated note** | `plan.yaml:676-710` (skip-and-continue loop) fixes the *original* wedge (scan stops at first unclaimable). The residual named in the dispatch is real and unaddressed: an item claimed at `create_ref` (step 5b) but never bookkept (step 6, agent dies) is open, unlabelled, unassigned — it passes the 5a pre-filter forever and its `create_ref` fails forever (`plan.yaml:681-696`, `700-707`). Cost per poll per stale item is one `issue_view` + one refused `create_ref`, unbounded in N. Work behind it stays reachable (loop never stops), so this is **degradation, not a wedge**. `DESIGN.md:69-70`'s REQ-01 gap names only the board *under-reporting* `building` — it does not name unbounded accumulation or per-poll cost. `digest.md:12`'s "the wedge is structurally impossible" **overclaims**: true of the original mechanism, not of this residual. Grade `med` — note, not a gate. |
| MF-2 exit-2 "nothing mutated" | **NOT CLOSED — high, must_fix** | `plan.yaml:593` claims "every exit-2 path before the first `create_issue` leaves the recorder with zero mutating calls." But `plan.yaml:599-600`'s own test case — `create_issue` raising `KeyError` → exit 2 — is such a path, and by then `ensure_labels` (step 5, `plan.yaml:529-537`) has already run: `plan.yaml:571` names it "the first mutation," `:587` asserts by call order that it precedes `create_issue`, and `:386-388` shows it is `gh label create --repo <repo> --force`, a remote write. So `DESIGN.md:92-94` and `:101`'s PONR row, and `SC-14` (`BRIEF.md:145-147`, "zero mutating calls... on every refusal path reached before it"), are **false for `factory_decompose`** — not a residual the document states, a claim the document makes that a test case in the same file falsifies. This is the same defect class the squad already spent a send-back cycle on (`digest.md:110-111`, SC-02/SC-13). Two remedies, either closes it: (a) restate the PONR as `ensure_labels` and add "up to five labels created in the target repo (idempotent)" to the "what exit 2 can leave" column, and fix `:593`'s test claim to match; or (b) carve `ensure_labels` out by name in C-3 the way exit-3's no-mutation guarantee is carved out for `factory_claim`, and re-word SC-14 to say so. `factory_land` (`plan.yaml:905-910`, steps 1-2 confirmed local-only) and `factory_claim` (`:727-734`, candidate scan confirmed mutation-free including refused `create_ref`) and `factory_workspace` (`:831-834`, all mutation local/disposable, no GitHub write at all) all check out clean — this is isolated to `factory_decompose`. |
| MF-3 Q3 contradiction | **closed** | `DESIGN.md:176-177` — Q3 marked RESOLVED by D-09, no "pending/do not implement ahead of" hedge survives anywhere in the file. |
| MF-4 failure grammar | **closed** | `T-11` (`plan.yaml:184-226`) matches C-3's declared shapes exactly: `message()` builds the five-part line, the trap's `unexpected failure: <type>` carve-out matches `DESIGN.md:129-131`, `nothing_to_do`'s three-part form (`plan.yaml:196-198`) matches `DESIGN.md:131-132`, and the two distinct exit-1 stderr lines (`no work available` / `no claimable work`, `T-05` steps 4 and 5c) both route through the same three-part form with different `why`. |
| MF-5 pagination | **discharged** | `DESIGN.md:110-121` — server-side query bounded by the ready column (`is:open` ∧ station), `project_items` raising on truncation, and an explicit lifecycle statement (station is the signal, nothing archives, growth accepted, #186 owns reaping). A different, stronger fix than the one asked for; measured facts cited match `notes/research-FEAT-10-claim-atomicity.md` and the probe. |
| MF-6 assignee semantics | **dissolved, confirmed** | `plan.yaml:690-696` — the tool tests only non-emptiness of `assignees`, never a login comparison, outside the self-ownership branch (`:683-689`, which reads `--as` for re-entry, not "the assignee"). No read-back comparison survives to be ambiguous. |
| MF-7 T-01 cites no clause | **closed, with an unenforced corner (note)** | `plan.yaml:129-137` — T-01 cites C-1's naming rule and states both load-bearing clauses (one word; 1:1 to a predicate). But T-01's `verify:` (`:102`) only checks the three station keys are non-empty strings, and `T-05` step 2 (`:644-650`) validates that each name **exists** on the board's field — a two-word option name passes both gates and then silently matches nothing once interpolated into the query string, the same silent-empty failure class the design guards against elsewhere. Nothing machine-checks the "one word" clause. `med` — note, not a gate. |

## New material — SC-12..15, T-12

- **SC-12** (`BRIEF.md:134-139`): binds both branches. `plan.yaml`'s T-05 test list has a
  create-succeeds case (order asserted, `:753-755`) and a create-refused case under `--issue`
  (exit 3, zero mutating calls, `:763-764`). Closed.
- **SC-13** (`BRIEF.md:140-143`): the criterion's own text binds only the **one-skip** case ("still
  yields a claim of the next claimable item"). The all-candidates-skipped → exit 1 `no claimable
  work` path — the one that actually falsifies the wedge — is bound by a unit test
  (`plan.yaml:756-758`, "create_ref returning False for every one of three candidates exits 1...
  ZERO mutating calls") and again at the process level by T-12 (`plan.yaml:1141-1143`). So the
  *behaviour* is tested twice; the **SC wording** covers only half of it. Cosmetic gap, not a gate —
  worth a wording fix at signature since a signable contract should say what its own tests prove.
- **SC-14** (`BRIEF.md:145-147`): is the criterion MF-2 falsifies for `factory_decompose` — see above.
- **SC-15** (`BRIEF.md:148-151`): confirmed by T-12's real-process exit-status assertions.
- **T-12** (`plan.yaml:1092-1156`): a genuine fork-level integration test of the five entry points —
  stub `gh`/`git` binaries, real `subprocess.run`, cwd outside the checkout, SC-10/SC-15 cases plus
  the three "plus, once each" cases including the all-refused-candidates process-level case. No
  defect found. The `change_type`/`depends_on`/matrix-ordering question (Q5) is eng-lead's, not
  audited here per the LEAVE LIST.

## Not verifiable from source

Rendered board/CLI output is not checkable from markdown and YAML alone — noted per role limits, not
a finding against this delta (unchanged from seg3).
