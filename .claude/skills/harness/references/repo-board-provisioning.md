# Repository board provisioning and audit

The main session MUST read this procedure before provisioning or auditing a mirror-on
repository during `harness-add-repo` (DEC-158). The repository identity must already be
pinned under the user's eyes; skip the board entirely when `github.sync` is false.

Run the operator commands from the configured control plane. Board configuration belongs
in the repository's own `harness.json`, never in `fleet.yaml`; land config changes on the
repository's default branch through `harness-add-repo` step 1.

1. Run `python3 <HARNESS_CONTROL_PLANE_ROOT>/.agents/skills/harness/bin/board_lifecycle.py provision` and **read the exit code**:
   - `0`: provisioned or already correct.
   - `2`: the declaration is unusable; the message names the key and **nothing was written**.
   - `3`: a NEW project was created, linked, AND its Status field made to carry every declared
     station — one run, not two. Write its number into that project's `harness.json`
     `github.board.number` **before anything else runs**.
   - `4`: a project was created but a follow-up write FAILED — either the link, or the Status
     field after a successful link. **The project exists.** Record the number the message names
     **before retrying or doing other work**, or the retry creates a second board.
2. Respect the new/existing-board distinction: on a NEW board, `provision` replaces the
   declared `station_field`'s options with exactly your stations and prints what it removed.
   With `station_field: "Status"` (every board here), these are GitHub's default
   `Todo`/`In Progress`/`Done`. Any other name creates a new field and leaves `Status` as an
   unused column. Replacement touches only a board created in that same run: no items exist
   yet, so no card can lose its column. On an EXISTING board it only ever adds.
3. Provisioning works only for a **USER-OWNED board**. Every primitive queries `user(login:)`;
   an organization-owned project is refused with "organization-owned board not supported".
   Create and configure that by hand; `provision` exits 2 rather than doing something partial.
   Both repositories in the fleet today happen to be user-owned, so nothing else would surface this.
4. Run `python3 <HARNESS_CONTROL_PLANE_ROOT>/.agents/skills/harness/bin/board_lifecycle.py audit` and show the operator
   the WORKFLOW findings **verbatim**.
5. **All three workflows are a HARD GATE you cannot automate**: `Item closed`,
   `Auto-close issue`, and `Pull request merged`. No API enables them: all 31 ProjectV2
   mutations include `deleteProjectV2Workflow` and none creates or enables one, and
   `ProjectV2Workflow` exposes neither its trigger nor its action. **Only a click in the
   project's web UI turns them on.** Ask the operator to do it, then re-run the audit.
   Registration is not finished until it reports all three enabled.

This workflow check runs only during registration, never in `check-state.py` (which fires
at every door and pre-commit). A workflow switched off after registration is invisible
until the next registration run.
