#!/usr/bin/env python3
"""Wayfinding map operations against GitHub Issues (DEC-166).

WHY A SCRIPT AND NOT PROSE: three of these operations are traps if hand-typed.
The sub-issue API takes the child's internal `id`, NOT its `number` — passing the
number silently attaches the wrong issue or 422s. The frontier is a compound query
(open AND every blocker closed AND unassigned) that no single `gh` invocation
expresses. And a ticket created without its `wayfinder:<type>` label is invisible
to every later query. Prose loses all three; a script cannot.

MUTATIONS ARE DRY-RUN BY DEFAULT. Every subcommand that writes prints the calls it
would make and exits 0; `--apply` performs them. Same precedent as deploy.sh: this
touches a shared, human-visible surface, so the plan is shown first.

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
"""
import json, os, subprocess, sys

sys.path.insert(0, os.path.dirname(os.path.realpath(__file__)))
import gh_issues as ghi

TYPES = ("research", "prototype", "grilling", "task")
LABELS = {"wayfinder:map": ("0e8a16", "A wayfinding effort map (DEC-166)")}
for _t in TYPES:
    LABELS[f"wayfinder:{_t}"] = ("1d76db", f"Wayfinding ticket: {_t}")


def die(msg, code=1):
    print(f"wayfind: {msg}", file=sys.stderr)
    sys.exit(code)


def root():
    r = os.environ.get("CLAUDE_PROJECT_DIR") or os.getcwd()
    # Walk up to the checkout holding .harness/, so cwd inside a feature dir still works.
    d = os.path.abspath(r)
    while d != "/":
        if os.path.isdir(os.path.join(d, ".harness")):
            return d
        d = os.path.dirname(d)
    die("no .harness/ found from here — run inside an onboarded project.")


def cfg():
    p = os.path.join(root(), ".harness", "harness.json")
    try:
        gh = (json.load(open(p)).get("github") or {})
    except Exception as e:
        die(f"cannot read {p} ({e})")
    if not gh.get("sync"):
        die("github.sync is off — wayfinding runs in local-markdown mode "
            "(.harness/efforts/<slug>/MAP.md). This script is the tracker mode only.")
    if not gh.get("repo"):
        die("github.sync is on but github.repo is not pinned — fix harness.json (DEC-138).")
    return gh["repo"]


def gh_json(args, allow_fail=False):
    r = subprocess.run([ghi.gh_bin()] + args, capture_output=True, text=True)
    if r.returncode != 0:
        if allow_fail:
            return None
        die(f"gh {' '.join(args[:3])}… failed: {(r.stderr or '').strip().splitlines()[-1:] or ''}")
    try:
        return json.loads(r.stdout or "null")
    except Exception:
        return r.stdout.strip()


def do(cmds, apply):
    """Run (or print) a list of gh argv lists, in order."""
    for c in cmds:
        if not apply:
            print("  would run: gh " + " ".join(c))
            continue
        r = subprocess.run([ghi.gh_bin()] + c, capture_output=True, text=True)
        if r.returncode != 0:
            die(f"gh {' '.join(c[:3])}… failed: {(r.stderr or '').strip()}")
        out = (r.stdout or "").strip()
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


def issue(repo, num, fields="number,title,state,assignees,labels,body"):
    d = gh_json(["issue", "view", str(num), "-R", repo, "--json", fields], allow_fail=True)
    if d is None:
        die(f"issue #{num} not readable in {repo}")
    return d


def sub_issues(repo, num):
    return gh_json(["api", f"repos/{repo}/issues/{num}/sub_issues", "--paginate"]) or []


def blockers(repo, num):
    return gh_json(["api", f"repos/{repo}/issues/{num}/dependencies/blocked_by",
                    "--paginate"], allow_fail=True) or []


def ticket_type(iss):
    for l in iss.get("labels", []):
        n = l["name"] if isinstance(l, dict) else str(l)
        if n.startswith("wayfinder:") and n.split(":", 1)[1] in TYPES:
            return n.split(":", 1)[1]
    return "?"


def frontier(repo, mapnum):
    """Open sub-issues whose every blocker is closed and which nobody has claimed."""
    out = []
    for s in sub_issues(repo, mapnum):
        if (s.get("state") or "").lower() != "open":
            continue
        num = s["number"]
        if any((b.get("state") or "").lower() == "open" for b in blockers(repo, num)):
            continue
        full = issue(repo, num, "number,title,assignees,labels")
        if full.get("assignees"):
            continue                      # claimed — another session owns it
        out.append(full)
    return out


def parent_of(repo, num):
    """The map a ticket belongs to, via the sub-issues parent endpoint (404 = no parent)."""
    p = gh_json(ghi.parent_args(repo, num), allow_fail=True)
    return p.get("number") if isinstance(p, dict) else None


def append_gist(repo, mapnum, line, apply):
    """Append ONE line under the map body's `## Decisions so far` (DEC-167).

    Read-modify-write on the issue body, because the alternative is a human remembering to
    hand-edit the map after every resolution — and a gist that is sometimes written is a map
    that silently stops being an index. Inserted at the END of the section so the list reads
    in resolution order.
    """
    body = issue(repo, mapnum, "body").get("body") or ""
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
    r = subprocess.run([ghi.gh_bin(), "issue", "edit", str(mapnum), "-R", repo, "--body-file", "-"],
                       input=new_body, capture_output=True, text=True)
    if r.returncode != 0:
        die(f"gh issue edit (map body) failed: {(r.stderr or '').strip()}")
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
        url = gh_json(["issue", "create", "-R", repo, "--label", f"wayfinder:{ttype}",
                       "--title", title, "--body", "## Question\n\n<the decision this resolves>\n"])
        num = str(url).rstrip("/").split("/")[-1]
        # THE TRAP: sub_issues takes the child's internal id, never its number.
        cid = issue(repo, num, "id")["id"] if isinstance(issue(repo, num, "id"), dict) else None
        cid = cid or gh_json(ghi.internal_id_args(repo, num))
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
        ti = issue(repo, t, "title")
        do([comment, ["issue", "close", t, "-R", repo]], apply)
        append_gist(repo, mapnum, f"- [#{t} {ti.get('title','')}]"
                    f"(https://github.com/{repo}/issues/{t}) — {gist}", apply)
        return 0

    die(f"unknown subcommand {sub!r}")


if __name__ == "__main__":
    sys.exit(main())
