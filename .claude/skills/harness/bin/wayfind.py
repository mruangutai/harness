#!/usr/bin/env python3
"""Wayfinding map operations against GitHub Issues (DEC-166).

WHY A SCRIPT AND NOT PROSE: three of these operations are traps if hand-typed.
The sub-issue API takes the child's internal `id`, NOT its `number` — passing the
number silently attaches the wrong issue or 422s. The frontier is a compound query
(open AND every blocker closed AND unassigned) that no single `gh` invocation
expresses. And a ticket created without its `wayfinder:<type>` label is invisible
to every later query. Prose loses all three; a script cannot.

MUTATIONS ARE DRY-RUN BY DEFAULT. Every subcommand that writes prints the calls it
would make and exits 0; `--apply` performs them. This touches a shared,
human-visible surface, so the plan is shown first, dry-run then apply.

  wayfind.py map <map#>                      # low-res view: destination, decisions, frontier
  wayfind.py frontier <map#>                 # takeable tickets only (open, unblocked, unclaimed)
  wayfind.py round <map#>                    # the frontier as ONE numbered round + research to fire
  wayfind.py chart "<destination title>"     # create the map issue  [--apply]
  wayfind.py ticket <map#> <type> "<title>"  # create a ticket as a sub-issue  [--apply]
  wayfind.py block <ticket#> --by <ticket#>  # native blocked_by edge  [--apply]
  wayfind.py claim <ticket#>                 # assign to @me — the claim  [--apply]
  wayfind.py resolve <ticket#> --body "<text>" --gist "<one line>"   # comment + close + gist  [--apply]
  wayfind.py resolve <ticket#> --file <path> --gist "<one line>"    # same, body from a file

Exit 0 = done (or planned). Exit 1 = a problem the caller must surface.
Repo comes from .harness/harness.json `github.repo`, pinned at init and never
re-inferred (DEC-138). github.sync false, or gh missing/unauthenticated -> exit 1
with the markdown-fallback instruction; wayfinding then runs in files-only mode.

Every gh call goes through factory_gh (FACTORY_GH is the one binary override). Reads
fail CLOSED: a failed or unparseable read raises GhError, caught once in cli(), so an
outage can never make a blocked ticket eligible or let resolve write after an
unverified parent. Only blockers and parent_of treat a genuine HTTP 404 as absence.
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.realpath(__file__)))
import artifact_accessors
import factory_gh
import gh_issues as ghi
import harness_boundary

TYPES = ("research", "prototype", "grilling", "task")
LABELS = {"wayfinder:map": ("0e8a16", "A wayfinding effort map (DEC-166)")}
for _t in TYPES:
    LABELS[f"wayfinder:{_t}"] = ("1d76db", f"Wayfinding ticket: {_t}")


def die(msg, code=1):
    print(f"wayfind: {msg}", file=sys.stderr)
    sys.exit(code)


def cfg():
    r = harness_boundary.root_above(os.getcwd())
    if r is None:
        die("no .harness/team-config.yaml found walking up from here — run inside an "
            "onboarded project.")
    p = os.path.join(r, ".harness", "harness.json")
    try:
        gh = artifact_accessors.load_harness_json(p)["github"]
    except artifact_accessors.ArtifactAccessError as e:
        die(f"cannot read {p} ({e})")
    if not gh["sync"]:
        die("github.sync is off — wayfinding runs in local-markdown mode "
            "(.harness/efforts/<slug>/MAP.md). This script is the tracker mode only.")
    return gh["repo"]  # the schema requires a pinned owner/name repo whenever sync is on


def gh_json(args):
    """The strict-JSON value of a gh read; GhError on any launch, exit or JSON failure."""
    return factory_gh.run_gh(args, json_out=True)


# gh exits 1 for EVERY HTTP error; its explicit not-found marker is the only absence signal.
_HTTP_404 = "(HTTP 404)"


ABSENT = object()  # a confirmed 404 — distinct from any successful JSON value, null included


def gh_json_or_absent(args):
    """gh_json, except that a genuine 404 returns ABSENT: a COMPLETED gh process (integer,
    non-zero status — None is a launch failure) whose captured stderr carries "(HTTP 404)".
    Exit 1 alone, other 404 digits and any status-zero result (even malformed JSON with a 404
    in stderr) raise GhError. Local on purpose: only blockers and parent_of may read absence."""
    result = factory_gh.try_gh(args, json_out=True)
    if result.ok:
        return result.value
    if isinstance(result.status, int) and result.status != 0 and _HTTP_404 in result.stderr:
        return ABSENT
    raise result.error


def unusable(args, value, want):
    """GhError for a successful read whose payload is not the shape the caller needs."""
    return factory_gh.GhError(args, 0, json.dumps(value), "",
                              f"gh {' '.join(args[:2])} returned an unusable payload",
                              args[1] if len(args) > 1 else "gh",
                              f"expected {want}; only a confirmed HTTP 404 means absence")


def require(args, value, ok, want):
    """value itself when ok; otherwise the typed unusable GhError, raised before any decision."""
    if not ok:
        raise unusable(args, value, want)
    return value


# The decision-field checks (M1, FEAT-2452 c2). Every field frontier or resolve DECIDES on is
# checked before the decision, so a malformed successful payload can never read as "closed",
# "unclaimed" or "no section": it is unusable, exactly like a failed read.
def _string(value):
    return isinstance(value, str)


def _list(value):
    return isinstance(value, list)


def _state(value):
    """An issue state: a string whose lowercase is open or closed. Missing, null, unknown and
    non-string states are unusable, never 'not open'."""
    return isinstance(value, str) and value.lower() in ("open", "closed")


def _number(value):
    """A positive integer issue number; bool, 0, negatives, strings and floats are not."""
    return type(value) is int and value >= 1


def _fields(value, **checks):
    """value is a JSON object whose every named field passes its check."""
    return isinstance(value, dict) and all(check(value.get(f)) for f, check in checks.items())


def _list_of(value, item_ok):
    return isinstance(value, list) and all(item_ok(item) for item in value)


def _labels(value):
    """gh's labels: a list of label objects, each with a string name."""
    return _list_of(value, lambda label: _fields(label, name=_string))


def do(cmds, apply):
    """Run (or print) a list of gh argv lists, in order."""
    for c in cmds:
        if not apply:
            print("  would run: gh " + " ".join(c))
            continue
        out = factory_gh.run_gh(c)
        if out:
            print(f"  {out.splitlines()[-1]}")
    if not apply:
        print("DRY RUN — nothing changed. Re-run with --apply.")


def ensure_labels(repo, apply):
    have = {l["name"] for l in (gh_json(["label", "list", "-R", repo, "--limit", "200",
                                         "--json", "name"]) or [])}
    missing = [n for n in LABELS if n not in have]
    if missing:
        do([["label", "create", n, "-R", repo, "--color", LABELS[n][0],
             "--description", LABELS[n][1]] for n in missing], apply)


def issue_args(repo, num, fields):
    return ["issue", "view", str(num), "-R", repo, "--json", fields]


def issue(repo, num, fields="number,title,state,assignees,labels,body"):
    return gh_json(issue_args(repo, num, fields))


def checked_issue(repo, num, want, **checks):
    """issue() for a read a decision rests on: exactly the JSON fields named in `checks`, each
    passing its check, or the typed unusable GhError."""
    args = issue_args(repo, num, ",".join(checks))
    value = gh_json(args)
    return require(args, value, _fields(value, **checks), want)


def sub_issues(repo, num):
    """The map's tickets: a list of issue objects, each with a positive number and an open or
    closed state (frontier and map decide on both); anything else raises."""
    args = ["api", f"repos/{repo}/issues/{num}/sub_issues", "--paginate"]
    value = gh_json(args)
    return require(args, value, _list_of(value, lambda s: _fields(s, number=_number, state=_state)),
                   "a JSON list of issue objects, each with a positive number and an open or closed state")


def blockers(repo, num):
    """The issues blocking #num (404 = none). Any other payload that is not a list of issue
    objects, each with an open or closed state, raises."""
    args = ["api", f"repos/{repo}/issues/{num}/dependencies/blocked_by", "--paginate"]
    value = gh_json_or_absent(args)
    if value is ABSENT:
        return []
    return require(args, value, _list_of(value, lambda b: _fields(b, state=_state)),
                   "a JSON list of issue objects, each with an open or closed state")


def ticket_type(iss):
    for l in iss["labels"]:  # frontier verified a list of label objects with string names
        n = l["name"]
        if n.startswith("wayfinder:") and n.split(":", 1)[1] in TYPES:
            return n.split(":", 1)[1]
    return "?"


def frontier(repo, mapnum):
    """Open sub-issues whose every blocker is closed and which nobody has claimed. Every field
    decided on (states, numbers, assignees, labels) is verified before the decision."""
    out = []
    for s in sub_issues(repo, mapnum):
        if s["state"].lower() != "open":
            continue
        num = s["number"]
        if any(b["state"].lower() == "open" for b in blockers(repo, num)):
            continue
        full = checked_issue(repo, num, f"issue #{num} with its own number, a string title, an "
                             "assignees list and a list of named labels",
                             number=lambda n: _number(n) and n == num, title=_string,
                             assignees=_list, labels=_labels)
        if full["assignees"]:
            continue                      # claimed — another session owns it
        out.append(full)
    return out


def parent_of(repo, num):
    """The map a ticket belongs to, via the sub-issues parent endpoint (404 = no parent).
    Any other payload without a positive integer `number` raises GhError."""
    args = ghi.parent_args(repo, num)
    p = gh_json_or_absent(args)
    if p is ABSENT:
        return None
    return require(args, p, _fields(p, number=_number),
                   "an issue object with a positive integer number")["number"]


def append_gist(repo, mapnum, line, apply):
    """Append ONE line under the map body's `## Decisions so far` (DEC-167).

    Read-modify-write on the issue body, because the alternative is a human remembering to
    hand-edit the map after every resolution — and a gist that is sometimes written is a map
    that silently stops being an index. Inserted at the END of the section so the list reads
    in resolution order.
    """
    body = checked_issue(repo, mapnum, "an issue object with a string body", body=_string)["body"]
    head = "## Decisions so far"
    if head not in body:
        die(f"map #{mapnum} has no '{head}' section — fix the map body first; the gist has "
            f"nowhere to go and a decision recorded only on its ticket leaves no index.")
    before, rest = body.split(head, 1)
    # the section runs to the next top-level heading
    nxt = rest.find("\n## ")
    section, after = (rest[:nxt], rest[nxt:]) if nxt != -1 else (rest, "")
    section = section.rstrip("\n") + f"\n{line}\n"
    new_body = before + head + section + after
    if not apply:
        print(f"  would append to map #{mapnum} '## Decisions so far':\n    {line}")
        return
    factory_gh.run_gh(["issue", "edit", str(mapnum), "-R", repo, "--body-file", "-"], input=new_body)
    print(f"  gisted on map #{mapnum}")


def cmd_round(repo, mapnum):
    """Print the frontier as a numbered round to put to the user in ONE message (DEC-167).

    The one-ticket-per-session rule bounds how deep a single decision is explored; it never
    required serialising INDEPENDENT decisions. Tickets on the frontier are by definition
    unblocked by each other, so asking them together is faster and no less rigorous — as long
    as each carries a recommendation and HITL answers still come from the human.
    """
    f = frontier(repo, mapnum)
    hitl = [t for t in f if ticket_type(t) != "research"]
    afk = [t for t in f if ticket_type(t) == "research"]
    if afk:
        print(f"FIRE IN PARALLEL NOW ({len(afk)} research ticket(s) — no user needed):")
        for t in afk:
            print(f"  #{t['number']}  {t['title']}")
        print()
    if not hitl:
        print("No HITL tickets on the frontier — nothing to put to the user this round.")
        return
    print(f"ROUND — {len(hitl)} independent question(s). Ask them together, each with your "
          f"recommendation, then WAIT for the answers:")
    for i, t in enumerate(hitl, 1):
        print(f"  {i}. #{t['number']} [{ticket_type(t)}] {t['title']}")
    print("\nAfter the answers: resolve each ticket, then recompute — answers push the "
          "frontier outward and may graduate fog.")


def cmd_map(repo, mapnum):
    m = issue(repo, mapnum)
    print(f"# {m['title']}  (#{m['number']}, {m['state']})\n")
    print(m.get("body") or "(no body — the map needs Destination and Notes)")
    subs = sub_issues(repo, mapnum)
    closed = [s for s in subs if (s.get("state") or "").lower() != "open"]
    print(f"\n## Tickets — {len(subs)} total, {len(closed)} closed")
    for s in subs:
        st = "closed" if (s.get("state") or "").lower() != "open" else "open"
        print(f"  #{s['number']:<6} [{st:6}] {s['title']}")
    print("\n## Frontier (takeable now)")
    f = frontier(repo, mapnum)
    if not f:
        print("  (empty — every ticket is closed, blocked, or claimed. "
              "All closed and no fog left? The effort is plannable: hand the map to /harness-plan.)")
    for t in f:
        print(f"  #{t['number']:<6} [{ticket_type(t):9}] {t['title']}")


def main():
    a = [x for x in sys.argv[1:] if x != "--apply"]
    apply = "--apply" in sys.argv
    if not a:
        print(__doc__.strip()); return 1
    sub, repo = a[0], cfg()

    if sub == "map":
        cmd_map(repo, a[1]); return 0

    if sub == "round":
        cmd_round(repo, a[1]); return 0

    if sub == "frontier":
        f = frontier(repo, a[1])
        for t in f:
            print(f"#{t['number']}\t{ticket_type(t)}\t{t['title']}")
        if not f:
            print("(frontier empty)")
        return 0

    if sub == "chart":
        ensure_labels(repo, apply)
        do([["issue", "create", "-R", repo, "--label", "wayfinder:map",
             "--title", f"Effort — {a[1]}",
             "--body", "## Destination\n\n<one or two lines>\n\n## Notes\n\n"
                       "## Decisions so far\n\n## Not yet specified\n\n## Out of scope\n"]], apply)
        return 0

    if sub == "ticket":
        mapnum, ttype, title = a[1], a[2], a[3]
        if ttype not in TYPES:
            die(f"type {ttype!r} must be one of {list(TYPES)}")
        ensure_labels(repo, apply)
        if not apply:
            print(f"  would create ticket [{ttype}] {title!r} as a sub-issue of #{mapnum}")
            print(f"  would attach via: gh api repos/{repo}/issues/{mapnum}/sub_issues "
                  f"-F sub_issue_id=<the new issue's internal id, NOT its number>")
            print("DRY RUN — nothing changed. Re-run with --apply.")
            return 0
        create = ["issue", "create", "-R", repo, "--label", f"wayfinder:{ttype}",
                  "--title", title, "--body", "## Question\n\n<the decision this resolves>\n"]
        num = str(factory_gh.issue_number_from_url(create, factory_gh.run_gh(create)))
        # THE TRAP, and it has TWO layers. sub_issues takes the child's internal id,
        # never its number -- and `gh issue view --json id` returns the GraphQL NODE
        # id (`I_kwDO...`), not the REST integer the endpoint wants. The node id is
        # truthy, so an `or` fallback after it never runs and every attach 422s.
        # Only the REST route is correct here (review of PR #4).
        cid = gh_json(ghi.internal_id_args(repo, num))
        do([ghi.attach_sub_issue_args(repo, mapnum, cid)], True)
        print(f"  ticket #{num} [{ttype}] attached to map #{mapnum}")
        return 0

    if sub == "block":
        t = a[1]
        by = a[a.index("--by") + 1] if "--by" in a else die("block needs --by <ticket#>")
        bid = gh_json(ghi.internal_id_args(repo, by))
        do([ghi.blocked_by_args(repo, t, bid)], apply)
        return 0

    if sub == "claim":
        do([["issue", "edit", a[1], "-R", repo, "--add-assignee", "@me"]], apply)
        return 0

    if sub == "resolve":
        t = a[1]
        # Inline --body is the DEFAULT path (DEC-167): the ticket comment is the canonical
        # record, so a local file per decision would be a second copy that drifts. --file
        # exists for genuinely long bodies and for pasting a linked asset's summary.
        if "--body" in a:
            body = a[a.index("--body") + 1]
            comment = ["issue", "comment", t, "-R", repo, "--body", body]
        elif "--file" in a:
            path = a[a.index("--file") + 1]
            if not os.path.isfile(path):
                die(f"{path} not found")
            comment = ["issue", "comment", t, "-R", repo, "--body-file", path]
        else:
            die("resolve needs --body \"<text>\" or --file <path>")
        if "--gist" not in a:
            die("resolve needs --gist \"<one line>\" — the map is an index, and a decision "
                "recorded only on its ticket leaves the map silently incomplete (DEC-167). "
                "One line: what was decided, not how.")
        gist = a[a.index("--gist") + 1]
        mapnum = parent_of(repo, t)
        if mapnum is None:
            die(f"ticket #{t} has no parent map — attach it first "
                f"(wayfind.py ticket <map#> <type> …), or this is not a wayfinding ticket.")
        ti = checked_issue(repo, t, "an issue object with a string title", title=_string)
        do([comment, ["issue", "close", t, "-R", repo]], apply)
        append_gist(repo, mapnum, f"- [#{t} {ti['title']}]"
                    f"(https://github.com/{repo}/issues/{t}) — {gist}", apply)
        return 0

    die(f"unknown subcommand {sub!r}")


def cli():
    """The CLI entry: one GhError catch turns any gh failure into the wayfind-prefixed
    diagnostic and exit 1, never a traceback; the functions above stay typed for tests."""
    try:
        return main()
    except factory_gh.GhError as error:
        die(f"gh {' '.join(error.argv[:3])}… failed: {error}")


if __name__ == "__main__":
    sys.exit(cli())
