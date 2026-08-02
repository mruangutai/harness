#!/usr/bin/env python3
"""Mirror a feature to GitHub Issues — one-way, outbound, never a gate (DEC-138).

  gh-sync.py open  <feature-dir>          plan approved -> milestone + parent + one issue per T-NN
  gh-sync.py close-task <feature-dir> T-NN    task's commit landed -> close its issue
  gh-sync.py abandon <feature-dir> --reason-file <path>  feature abandoned -> close subs
                                           not_planned, close the milestone, post the reason
  gh-sync.py ship  <feature-dir> [--body-file <path>]  shipped -> close the milestone,
                                           close the parent only if `open` created it, and
                                           post --body-file on any recorded parent if given

TRUTH DIRECTION IS THE POINT. PLAN.md is approval-gated and is the only source; this
script projects it outward. It never reads GitHub state back into harness state —
a wiki-editable UI feeding an approval-gated artifact is the DEC-19 bypass shape.

NEVER A GATE. Every environmental failure — sync off, no repo pinned, gh missing,
gh unauthenticated, network down — prints one loud SKIP line and exits 0, because a
flow that fails on its *mirror* has inverted its priorities (SPEC §12 precedent for
branch/PR ops). Exit 1 is reserved for caller errors (bad args, missing files):
those are bugs in the dispatch, not the environment, and must be visible.

REPO IS PINNED, NEVER INFERRED. Every gh call passes --repo/-R from harness.json's
`github.repo`, recorded once at init under the user's eyes. Inferring from the cwd's
origin remote works right up until a fork or renamed remote publishes issues to the
wrong org silently — the one failure here that is both outward-facing and quiet.

LABELS DERIVE, MECHANICALLY (DEC-138 am.3): change_type config/scaffolding/infra/ci
-> `chore`; bugfix -> `bug`; anything else unlabeled. `harness` marks provenance on
every issue. No agent judgment at sync time.

IDEMPOTENT. `open` records issue numbers into feature.yaml (`github:` block) as it
creates; a re-run (resume after interruption — DEC-131 taught us flows die mid-step)
skips anything already recorded rather than duplicating.

Testable offline: GH_SYNC_GH overrides the gh binary (test-gh-sync.py points it at a
fake that logs calls and returns canned JSON).
"""
import json
import os
import re
import shutil
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.realpath(__file__)))
from gh_issues import internal_id_args, attach_sub_issue_args

GH = os.environ.get("GH_SYNC_GH", "gh")

CHORE_TYPES = {"config", "scaffolding", "infra", "ci"}


def skip(msg):
    """Environmental no-go: one loud line, exit 0. The mirror never gates."""
    print(f"gh-sync: SKIP — {msg}")
    sys.exit(0)


def die(msg):
    """Caller error: the dispatch itself is wrong. Visible, exit 1."""
    print(f"gh-sync: ERROR — {msg}")
    sys.exit(1)


def post_body_path(path, flag):
    """Validate a --body-file-style path argument (DEC-138 am.6: the mirror never composes
    text — the path itself is passed to gh, never its contents). Every failure here is a
    caller error, never environmental: an empty or unreadable file would otherwise reach
    gh(), get rejected, and be reported as a SKIP that silently posts no reason at all."""
    if path is None:
        die(f"{flag} is required")
    if not os.path.isfile(path):
        die(f"{path} is not a file")
    if os.path.getsize(path) == 0:
        die(f"{path} is empty")
    try:
        open(path, encoding="utf-8").read()
    except OSError as e:
        die(f"{path} is unreadable ({e})")
    return path


def gh(args, capture=True):
    r = subprocess.run([GH] + args, capture_output=True, text=True)
    if r.returncode != 0:
        # Mid-flight environmental failure (network, auth expiry). Still not a gate.
        skip(f"gh {' '.join(args[:3])}… failed: {(r.stderr or r.stdout).strip()[:200]}")
    return r.stdout.strip() if capture else ""


# ---------- config ----------

def load_config(root):
    p = os.path.join(root, ".harness", "harness.json")
    if not os.path.isfile(p):
        skip("no .harness/harness.json — project not onboarded")
    try:
        cfg = json.load(open(p))
    except Exception as e:
        skip(f"harness.json unreadable ({e})")
    g = cfg.get("github") or {}
    if not g.get("sync"):
        skip("github.sync is not enabled for this project")
    repo = g.get("repo")
    if not repo or "/" not in str(repo):
        skip("github.repo is not pinned — run /harness-init --upgrade to record it")
    if shutil.which(GH) is None:
        skip(f"{GH} not on PATH")
    if subprocess.run([GH, "auth", "status"], capture_output=True).returncode != 0:
        skip("gh is not authenticated")
    return repo


# ---------- parsing (same hand-rolled discipline as the rest of bin/ — stdlib only) ----------

def read(p):
    if not os.path.isfile(p):
        die(f"{p} does not exist")
    return open(p, encoding="utf-8").read()


def section(text, heading):
    m = re.search(rf"^## {re.escape(heading)}\s*$(.*?)(?=^## |\Z)", text, re.M | re.S)
    return m.group(1).strip() if m else ""


def parse_brief(feat_dir):
    t = read(os.path.join(feat_dir, "BRIEF.md"))
    feat = os.path.basename(os.path.abspath(feat_dir))
    scs = re.findall(r"^- (SC-\d+):\s*(.+?)(?=^- SC-\d+:|\Z)", section(t, "Success Criteria"),
                     re.M | re.S)
    h1 = t.split("\n", 1)[0]
    parts = h1.split("—", 2)
    phrase = parts[2].strip() if len(parts) >= 3 else ""
    return {
        "feat": feat,
        "phrase": phrase,
        "problem": section(t, "Problem"),
        "goal": section(t, "Goal"),
        "scs": [(sid, " ".join(body.split())[:200]) for sid, body in scs],
    }


def parse_tasks(feat_dir):
    """Both task formats, like INV-4 (DEC-129): `### T-NN — title` blocks and `- T-NN:` items."""
    t = read(os.path.join(feat_dir, "PLAN.md"))
    tasks = []
    for m in re.finditer(r"^(?:###\s*|-\s*)(T-\d+)\b[ —:-]*(.*?)$(.*?)(?=^(?:###\s*|-\s*)T-\d+\b|^## |\Z)",
                         t, re.M | re.S):
        tid, title, body = m.group(1), m.group(2).strip(" —:-"), m.group(3)
        def field(name):
            f = re.search(rf"^\s*-?\s*{name}:\s*(.+)$", body, re.M)
            return f.group(1).strip() if f else ""
        absorbs = re.findall(r"#(\d+)", field("absorbs"))
        tasks.append({"id": tid, "title": title or tid, "body": body.strip(),
                      "change_type": field("change_type"), "traces": field("traces"),
                      "absorbs": absorbs})
    if not tasks:
        die(f"no T-NN tasks parse from {feat_dir}/PLAN.md")
    return tasks


def type_label(change_type):
    if change_type in CHORE_TYPES:
        return "chore"
    if change_type == "bugfix":
        return "bug"
    return None


# ---------- feature.yaml github block (text ops — no yaml dependency) ----------

def load_recorded(feat_dir):
    t = read(os.path.join(feat_dir, "feature.yaml"))
    rec = {"milestone": None, "parent": None, "parent_origin": None, "attached": [], "issues": {}}
    m = re.search(r"^github:\s*$(.*?)(?=^\S|\Z)", t, re.M | re.S)
    if m:
        blk = m.group(1)
        n = re.search(r"^\s*milestone:\s*(\d+)", blk, re.M)
        rec["milestone"] = int(n.group(1)) if n else None
        p = re.search(r"^\s*parent:\s*(\d+)", blk, re.M)
        rec["parent"] = int(p.group(1)) if p else None
        po = re.search(r"^\s*parent_origin:\s*(created|adopted)\b", blk, re.M)
        rec["parent_origin"] = po.group(1) if po else None
        a = re.search(r"^\s*attached:\s*\[([^\]]*)\]", blk, re.M)
        if a:
            rec["attached"] = [x.strip() for x in a.group(1).split(",") if x.strip()]
        rec["issues"] = {k: int(v) for k, v in re.findall(r"^\s{4}(T-\d+):\s*(\d+)", blk, re.M)}
    return rec


def save_recorded(feat_dir, rec):
    p = os.path.join(feat_dir, "feature.yaml")
    t = read(p)
    t = re.sub(r"^github:\s*$.*?(?=^\S|\Z)", "", t, flags=re.M | re.S).rstrip("\n") + "\n"
    lines = [
        "github:",
        f"  milestone: {rec['milestone']}",
        f"  parent: {rec['parent'] if rec['parent'] is not None else 'none'}",
        f"  parent_origin: {rec['parent_origin'] or 'none'}",
        f"  attached: [{', '.join(rec['attached'])}]",
        "  issues:",
    ]
    lines += [f"    {tid}: {num}" for tid, num in sorted(rec["issues"].items())]
    open(p, "w").write(t + "\n".join(lines) + "\n")


# ---------- commands ----------

def ensure_labels(repo, labels):
    """Create any missing labels first. LIVE SMOKE FINDING #1: GitHub rejects an issue
    create naming a label the repo does not define — new repos ship `bug` but not
    `harness`/`chore`. Errors here are swallowed (label already exists is the common
    case); the create call below is what surfaces a genuinely broken repo."""
    colors = {"harness": "5319e7", "chore": "cccccc", "bug": "d73a4a", "enhancement": "a2eeef"}
    for l in labels:
        subprocess.run([GH, "label", "create", l, "--repo", repo,
                        "--color", colors.get(l, "ededed"),
                        "--description", "created by harness gh-sync"],
                       capture_output=True)


def cmd_open(feat_dir, repo, parent_arg=None):
    brief, tasks, rec = parse_brief(feat_dir), parse_tasks(feat_dir), load_recorded(feat_dir)
    ensure_labels(repo, {"harness"} | {l for tk in tasks if (l := type_label(tk["change_type"]))})

    if rec["milestone"] is None:
        desc = (f"{brief['problem']}\n\n**Goal:** {brief['goal']}\n\n## Definition of done\n"
                + "\n".join(f"- [ ] {sid}: {txt}" for sid, txt in brief["scs"]))
        r = subprocess.run([GH, "api", "-X", "POST", f"repos/{repo}/milestones",
                            "-f", f"title={brief['feat']}", "-f", f"description={desc}"],
                           capture_output=True, text=True)
        if r.returncode == 0:
            rec["milestone"] = json.loads(r.stdout)["number"]
            print(f"gh-sync: milestone #{rec['milestone']} created for {brief['feat']}")
        else:
            # LIVE SMOKE FINDING #3: 422 when the title already exists — a previous run
            # created it and died before recording (or a human made one). Resolve by
            # lookup instead of failing; anything else is a real environmental skip.
            out = gh(["api", f"repos/{repo}/milestones", "-q",
                      f'[.[] | select(.title == "{brief["feat"]}") | .number] | first'])
            if not out or out == "null":
                skip(f"milestone create failed and no existing one matches: "
                     f"{(r.stderr or r.stdout).strip()[:200]}")
            rec["milestone"] = int(out)
            print(f"gh-sync: milestone #{rec['milestone']} recovered by title lookup")
        # LIVE SMOKE FINDING #2: record the milestone IMMEDIATELY. The first live run
        # created it, hit a downstream failure, exited before saving — and the re-run
        # 422'd on the orphan. The record-after-every-create rule applies to the
        # milestone too, not just issues (DEC-131, applied fully this time).
        save_recorded(feat_dir, rec)
    else:
        print(f"gh-sync: milestone #{rec['milestone']} already recorded — skipping")

    # D-01: the parent is adopted-or-created, its number recorded, never discovered.
    if rec["parent"] is not None:
        print(f"gh-sync: parent #{rec['parent']} already recorded — skipping")
    elif parent_arg is not None:
        rec["parent"] = int(parent_arg)
        rec["parent_origin"] = "adopted"
        save_recorded(feat_dir, rec)   # DEC-131: record immediately, same call as the number
        print(f"gh-sync: parent #{rec['parent']} adopted")
    else:
        title = f"{brief['feat']} — {brief['phrase']}" if brief["phrase"] else brief["feat"]
        body = f"{brief['problem']}\n\n**Goal:** {brief['goal']}"
        url = gh(["issue", "create", "--repo", repo, "--title", title,
                  "--body", body, "--label", "harness"])
        rec["parent"] = int(url.rstrip("/").rsplit("/", 1)[-1])
        rec["parent_origin"] = "created"
        save_recorded(feat_dir, rec)
        print(f"gh-sync: parent #{rec['parent']} created")

    for task in tasks:
        if task["id"] in rec["issues"]:
            print(f"gh-sync: {task['id']} already issue #{rec['issues'][task['id']]} — skipping")
        else:
            body = task["body"]
            if task["absorbs"]:
                body += "\n\nabsorbs: " + ", ".join(f"#{n}" for n in task["absorbs"])
            labels = ["harness"] + ([type_label(task["change_type"])] if type_label(task["change_type"]) else [])
            args = ["issue", "create", "--repo", repo,
                    "--title", f"{task['id']} — {task['title']}", "--body", body,
                    "--milestone", brief["feat"]]
            for l in labels:
                args += ["--label", l]
            url = gh(args)
            num = int(url.rstrip("/").rsplit("/", 1)[-1])
            rec["issues"][task["id"]] = num
            save_recorded(feat_dir, rec)   # after EVERY create — a crash mid-loop must not orphan issues
            print(f"gh-sync: {task['id']} -> issue #{num} [{', '.join(labels)}]")

        # Attach to the parent — a separate receipt from the create, so a crash between
        # recording the issue and attaching it is resumed rather than repeated or lost.
        if task["id"] in rec["attached"]:
            continue
        child_num = rec["issues"][task["id"]]
        child_id = gh(internal_id_args(repo, child_num))
        gh(attach_sub_issue_args(repo, rec["parent"], child_id), capture=False)
        rec["attached"].append(task["id"])
        save_recorded(feat_dir, rec)
        print(f"gh-sync: {task['id']} (issue #{child_num}) attached to parent #{rec['parent']}")
    save_recorded(feat_dir, rec)


def cmd_close_task(feat_dir, tid, repo):
    rec = load_recorded(feat_dir)
    if tid not in rec["issues"]:
        skip(f"{tid} has no recorded issue — nothing to close (was `open` run?)")
    tasks = {t["id"]: t for t in parse_tasks(feat_dir)}
    gh(["issue", "close", str(rec["issues"][tid]), "--repo", repo], capture=False)
    print(f"gh-sync: closed issue #{rec['issues'][tid]} for {tid}")
    absorbed = tasks.get(tid, {}).get("absorbs", [])
    if absorbed:
        print(f"gh-sync: {tid} absorbs {', '.join('#' + n for n in absorbed)} — left open for the ship briefing")


def cmd_abandon(feat_dir, repo, reason_file):
    """Terminal state: closes every recorded sub-issue not_planned, closes the milestone,
    posts the reason on the parent, and closes the parent itself only if `open` created it
    (D-01) — an adopted parent, or one with no recorded origin, is left open. Writes no
    receipt: this is a closing action, not a recording one, so `feature.yaml` is untouched."""
    reason_file = post_body_path(reason_file, "--reason-file")
    rec = load_recorded(feat_dir)
    if rec["milestone"] is None and not rec["issues"]:
        skip("no recorded milestone or issues — nothing to abandon (was `open` run?)")

    if rec["parent"] is not None:
        gh(["issue", "comment", str(rec["parent"]), "--repo", repo,
            "--body-file", reason_file], capture=False)
        print(f"gh-sync: reason posted on parent #{rec['parent']}")
    else:
        print("gh-sync: no parent recorded — reason not posted")

    for tid, num in sorted(rec["issues"].items()):
        gh(["api", "-X", "PATCH", f"repos/{repo}/issues/{num}",
            "-f", "state=closed", "-f", "state_reason=not_planned"], capture=False)
        print(f"gh-sync: closed issue #{num} for {tid} (not_planned)")

    if rec["milestone"] is not None:
        gh(["api", "-X", "PATCH", f"repos/{repo}/milestones/{rec['milestone']}",
            "-f", "state=closed"])
        print(f"gh-sync: milestone #{rec['milestone']} closed")
    else:
        print("gh-sync: no milestone recorded — nothing to close")

    # D-01: the parent's fate follows its recorded origin, never unconditional leave-open.
    if rec["parent"] is not None:
        if rec["parent_origin"] == "created":
            gh(["api", "-X", "PATCH", f"repos/{repo}/issues/{rec['parent']}",
                "-f", "state=closed", "-f", "state_reason=not_planned"], capture=False)
            print(f"gh-sync: parent #{rec['parent']} closed (not_planned)")
        else:
            print(f"gh-sync: parent #{rec['parent']} left open "
                  f"(origin={rec['parent_origin'] or 'none'})")


def cmd_backlog(feat_dir, repo, items):
    """User-accepted residual findings -> plain backlog issues (DEC-138 am.4).

    Called by the MAIN SESSION after the briefing decision, with one arg per accepted
    residual as `nature:title` (nature: bug|chore|enhancement). No milestone — these
    belong to no feature yet; a later plan cycle may absorb them. This is the only
    entry point for findings: digests never write to GitHub directly.
    """
    feat = os.path.basename(os.path.abspath(feat_dir))
    for item in items:
        nature, _, title = item.partition(":")
        if nature not in ("bug", "chore", "enhancement") or not title.strip():
            die(f"backlog item must be nature:title (bug|chore|enhancement), got {item!r}")
        labels = ["harness"] + ([nature] if nature != "enhancement" else [])
        args = ["issue", "create", "--repo", repo, "--title", title.strip(),
                "--body", f"Residual finding from {feat}, accepted at the ship briefing."]
        for l in labels:
            args += ["--label", l]
        url = gh(args)
        print(f"gh-sync: backlog issue #{url.rstrip('/').rsplit('/', 1)[-1]} [{', '.join(labels)}] — {title.strip()}")


def cmd_ship(feat_dir, repo, body_file=None):
    """Terminal state: PATCHes the milestone closed unconditionally, and — the mirror image
    of `abandon` step 4 — closes the parent only if `open` created it (D-01, SC-04): an
    adopted parent, or one with no recorded origin, is left open. Writes no receipt: this is
    a closing action, not a recording one, so `feature.yaml` is untouched."""
    if body_file is not None:
        body_file = post_body_path(body_file, "--body-file")
    rec = load_recorded(feat_dir)
    if rec["milestone"] is None:
        skip("no recorded milestone — nothing to close")

    # The comment is UNCONDITIONAL: posts on any recorded parent whatever its origin.
    if body_file is not None and rec["parent"] is not None:
        gh(["issue", "comment", str(rec["parent"]), "--repo", repo,
            "--body-file", body_file], capture=False)
        print(f"gh-sync: ship review posted on parent #{rec['parent']}")

    # D-01: the parent's close follows its recorded origin, never unconditional.
    if rec["parent"] is not None:
        if rec["parent_origin"] == "created":
            gh(["issue", "close", str(rec["parent"]), "--repo", repo], capture=False)
            print(f"gh-sync: parent #{rec['parent']} closed")
        else:
            print(f"gh-sync: parent #{rec['parent']} left open "
                  f"(origin={rec['parent_origin'] or 'none'})")
    else:
        print("gh-sync: no parent recorded — closing milestone only")

    # The milestone is unaffected by parent origin: it PATCHes closed in all three cases.
    gh(["api", "-X", "PATCH", f"repos/{repo}/milestones/{rec['milestone']}",
        "-f", "state=closed"])
    print(f"gh-sync: milestone #{rec['milestone']} closed")


def main():
    argv = sys.argv[1:]
    parent_arg = None
    if "--parent" in argv:
        i = argv.index("--parent")
        if i + 1 >= len(argv):
            die("--parent needs a value")
        parent_arg = argv[i + 1]
        argv = argv[:i] + argv[i + 2:]
    reason_file = None
    if "--reason-file" in argv:
        i = argv.index("--reason-file")
        if i + 1 >= len(argv):
            die("--reason-file needs a value")
        reason_file = argv[i + 1]
        argv = argv[:i] + argv[i + 2:]
    body_file = None
    if "--body-file" in argv:
        i = argv.index("--body-file")
        if i + 1 >= len(argv):
            die("--body-file needs a value")
        body_file = argv[i + 1]
        argv = argv[:i] + argv[i + 2:]
    if len(argv) < 2:
        die("usage: gh-sync.py open|close-task|abandon|ship|backlog <feature-dir> "
            "[T-NN | nature:title ...] [--parent <n>] [--reason-file <path>] [--body-file <path>]")
    cmd, feat_dir = argv[0], argv[1]
    if not os.path.isdir(feat_dir):
        die(f"{feat_dir} is not a directory")
    root = os.path.abspath(os.path.join(feat_dir, "..", "..", ".."))
    repo = load_config(root)
    if cmd == "open":
        cmd_open(feat_dir, repo, parent_arg)
    elif cmd == "close-task":
        if len(argv) < 3:
            die("close-task needs a T-NN")
        cmd_close_task(feat_dir, argv[2], repo)
    elif cmd == "abandon":
        cmd_abandon(feat_dir, repo, reason_file)
    elif cmd == "ship":
        cmd_ship(feat_dir, repo, body_file)
    elif cmd == "backlog":
        if len(argv) < 3:
            die("backlog needs at least one nature:title item")
        cmd_backlog(feat_dir, repo, argv[2:])
    else:
        die(f"unknown command {cmd!r}")


if __name__ == "__main__":
    main()
