# Probe (g) — degenerate `fleet.yaml` values, FEAT-15 T-01/T-02

Follow-up to `review-harness-security-reviewer-2026-08-11-01-validator.md`'s "Degenerate fleet
values" bullet, which asserted the outcomes without per-target evidence. Re-derived here: live
`check-domain.sh` fired as a subprocess against synthetic fixture roots (manifest granting
`harness-documentor` `.harness/allowed/**`), for the three named targets — including a genuine
`tempfile.mkdtemp()` path under `/var/folders/...` (not a hand-substituted `/private/tmp` stand-in),
to settle whether the panel's F1 `/tmp`→`/private/tmp` symlink finding also bites here. Script and
fixtures at `/private/tmp/claude-501/.../scratchpad/run_probe.py` (session scratchpad, not
committed).

**Bottom line: only g1 reaches `select_base` with a live degenerate value. g2, g3, g4, g5 never get
there — `factory_config.load_fleet` rejects all four before `resolve_fleet` returns, so they fail
closed exactly like an unparseable fleet.yaml (existing case (b)/(c) in `test-check-domain.py`).
g1 is category (C): a REFUSAL that should have been no-verdict — the REQ-05/SC-07 inversion — but
it inverts toward MORE refusal, not a wrongful permit. No (B) found anywhere in g1-g5. The symlink
question does not move this: `/var`→`/private/var` is a real symlink on this machine, confirmed
(`os.path.islink("/var") == True`), but `commonpath([anything_absolute, "/"]) == "/"` regardless of
which spelling is used, so g1's effect is identical for the declared and realpath forms.**

## Table

| Variant | fleet.yaml value | Loads? | (i) owned-in-root | (ii) `/tmp/scratch.py` | (iii) real `/var/folders/.../x.py` (`tempfile.mkdtemp()`) | Category | Reachable via ordinary editing? |
|---|---|---|---|---|---|---|---|
| g1 | `workspace_root: "/"` | **yes** (`os.path.isabs("/")` True) | exit 0 (unaffected — harness-root branch checked first) | exit **2**, "under the factory workspace but belongs to no repository" | exit **2**, same message, target `/var/folders/y3/nd_jssrd5dq8lbds73f0fy5m0000gn/T/tmp3q58m5p2/x.py` | **(C)** inversion — was exit 0/silent, now exit 2 | Yes — plausible operator typo (e.g. a broken template substitution leaving a bare `/`) |
| g2 | `workspace_root: ""` | no — `load_fleet` raises `fleet key invalid: workspace_root` | exit 2 (whole-project fail-closed) | exit 2 (same) | exit 2 (same) | (A) fail-closed, noisy — global, not target-specific | Yes — blank value left in the field |
| g3 | `repos: []` | no — `load_fleet` raises `fleet key invalid: repos` | exit 2 (whole-project fail-closed) | exit 2 | exit 2 | (A) | Yes — deleting all repo entries |
| g4 | `repos: [{name: widget, ...}]` (no `/`) | no — `load_fleet` raises `fleet repo entry invalid: repos[].name` | exit 2 (whole-project fail-closed) | exit 2 | exit 2 | (A) | Yes — forgetting the `owner/` prefix |
| g5 | `workspace_root: workspaces` (relative) | no — same `os.path.isabs` check as g2 | exit 2 (whole-project fail-closed) | exit 2 | exit 2 | (A) | Yes — relative-path typo |

Raw exit codes/stderr captured verbatim by the probe run; g1's three targets' stderr all read:
`check-domain: BLOCKED — <target> is under the factory workspace but belongs to no repository
declared in <fleet_path>.`

## g1 in detail — the one live finding

`workspace_root: "/"` is the **only** one of the five that passes `factory_config.load_fleet`'s
validation (`os.path.isabs("/")` is `True`) and reaches `select_base` unmodified. Because
`inside(child, "/")` is `os.path.commonpath([child, "/"]) == "/"`, which is `True` for every
absolute path, **branch 3** ("under `workspace_root`, no declared repo → exit 2") now catches
everything that used to fall to branch 4 ("outside both bases → no verdict", REQ-05/SC-07). Verified
against all three requested target shapes — `/tmp/scratch.py` and a genuine `/var/folders/...` path
minted fresh by `tempfile.mkdtemp()` (real symlinked-ancestor case, not a `/private` stand-in) — both
flip from silent exit 0 to exit 2 with the "belongs to no repository" message.

**This is a refusal, not a permit.** Every write anywhere on the filesystem outside the fixture root
becomes an actionable, correctly-worded BLOCKED — never an unauthorized allow. In-root
(control-plane, owned) writes are unaffected because `select_base` checks `inside(target, root)`
*before* the workspace branch, so g1 cannot ever grant something it shouldn't. The blast radius is
availability/noise: an agent's every scratch write outside the repo (which REQ-05 exists to leave
alone) starts getting refused, with no error anywhere in the fleet.yaml itself — it parses cleanly.
Matches the prior panel's "info-level... severe availability hazard from operator error" call;
this pass adds the exact per-target evidence (including the `/var/folders` symlink case) that call
was made without.

Severity: **info**. Threat model: this is not attacker-reachable — `fleet.yaml` is main-session-
owned config (P-07: value is operator-authored, no agent domain reaches it), so the only actor who
can produce `workspace_root: "/"` already holds the authority the value would misuse, and the
misuse direction is fail-closed (over-refusal), never a privilege grant. Not false-as-written against
the *shipped* configuration (P-05 does not fire) — SC-07 holds for the fleet.yaml actually in the
repo; it only breaks under a hypothetical operator misconfiguration this probe constructed to test.
No STRIDE category applies beyond a self-inflicted Denial-of-service on the operator's own
scratch-write ergonomics under that one misconfiguration.

## g2-g5 — reachability-closed at `factory_config.load_fleet`

All four are rejected by `load_fleet`'s own field validation (`workspace_root` must be absolute;
`repos` must be non-empty; each `repos[].name` must contain `/`) before `resolve_fleet` can return a
`workspace_root`/`bases` tuple at all. The `except Exception` in `resolve_fleet`
(`check-domain.sh:200-208`) catches the `FleetError` and exits 2 for **every** governed write in the
project, control-plane or not — the same behavior as case (b)/(c) in `test-check-domain.py` (broken
YAML, missing `workspace_root` key). This is deliberate fail-closed design, not a new gap: "the value
that identifies product paths is the one that failed... enforcement is CLOSED rather than partial."
No (B) or (C) outcome possible for these four — they never reach `select_base`.

## Coverage check (grepped, not assumed)

`test-check-domain.py` has no case for `workspace_root: "/"`, `workspace_root: ""`,
`repos: []`, a slash-less `repos[].name`, or a relative `workspace_root` (`grep -n "workspace_root"`
→ only the "omits workspace_root" case (c) and well-formed absolute-path fixtures; zero hits for any
of g1-g5's literal values across every `.py` in `bin/`). `test-factory-config.py` **does** cover the
`load_fleet`-level rejections that make g2-g5 reachability-closed: `(9) repos is missing`,
`(11) workspace_root is not absolute`, `(12) repos is empty`, `(14d) workspace_root is missing`, and
a slash-less-name mutation at line 119 — but never through `check-domain.sh`'s `resolve_fleet`/
`select_base`, and never `workspace_root: "/"` anywhere in the tree. g1 is the one gap with zero
coverage at either layer.

## Recommendation (non-blocking, info)

Not must_fix — g1 is fail-closed, and the **live** `.harness/factory/fleet.yaml` (re-read this
session, not cited from the prior panel note) declares `workspace_root:
/Users/molchairuangutai/GitHub/harness-factories` — checked directly: `os.path.exists()` is `False`
(the directory does not exist on this machine right now) and every ancestor that does exist
(`/`, `/Users`, `/Users/molchairuangutai`, `/Users/molchairuangutai/GitHub`) is confirmed
`os.path.islink() == False`. So this is not reachable against the current configuration. Worth a
one-line guard in `factory_config.load_fleet` rejecting `workspace_root == "/"` (or any value whose
`os.path.commonpath` with `/` covers everything) the next time the file is touched, since the
failure mode is silent (parses cleanly, no error) and the blast radius is every out-of-repo write on
the machine, not just the factory workspace.
