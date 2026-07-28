#!/usr/bin/env python3
"""Mirror a feature to GitHub Issues — one-way, outbound, never a gate (DEC-138).

  gh-sync.py open  <feature-dir>          plan approved -> milestone + one issue per T-NN
  gh-sync.py close-task <feature-dir> T-NN    task's commit landed -> close its issue (+ absorbed)
  gh-sync.py ship  <feature-dir>          user accepted shipped -> close the milestone

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
    return {
        "feat": feat,
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
    rec = {"milestone": None, "issues": {}}
    m = re.search(r"^github:\s*$(.*?)(?=^\S|\Z)", t, re.M | re.S)
    if m:
        blk = m.group(1)
        n = re.search(r"^\s*milestone:\s*(\d+)", blk, re.M)
        rec["milestone"] = int(n.group(1)) if n else None
        rec["issues"] = {k: int(v) for k, v in re.findall(r"^\s{4}(T-\d+):\s*(\d+)", blk, re.M)}
    return rec


def save_recorded(feat_dir, rec):
    p = os.path.join(feat_dir, "feature.yaml")
    t = read(p)
    t = re.sub(r"^github:\s*$.*?(?=^\S|\Z)", "", t, flags=re.M | re.S).rstrip("\n") + "\n"
    lines = ["github:", f"  milestone: {rec['milestone']}", "  issues:"]
    lines += [f"    {tid}: {num}" for tid, num in sorted(rec["issues"].items())]
    open(p, "w").write(t + "\n".join(lines) + "\n")


# ---------- commands ----------

def cmd_open(feat_dir, repo):
    brief, tasks, rec = parse_brief(feat_dir), parse_tasks(feat_dir), load_recorded(feat_dir)

    if rec["milestone"] is None:
        desc = (f"{brief['problem']}\n\n**Goal:** {brief['goal']}\n\n## Definition of done\n"
                + "\n".join(f"- [ ] {sid}: {txt}" for sid, txt in brief["scs"]))
        out = gh(["api", "-X", "POST", f"repos/{repo}/milestones",
                  "-f", f"title={brief['feat']}", "-f", f"description={desc}"])
        rec["milestone"] = json.loads(out)["number"]
        print(f"gh-sync: milestone #{rec['milestone']} created for {brief['feat']}")
    else:
        print(f"gh-sync: milestone #{rec['milestone']} already recorded — skipping")

    for task in tasks:
        if task["id"] in rec["issues"]:
            print(f"gh-sync: {task['id']} already issue #{rec['issues'][task['id']]} — skipping")
            continue
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
    save_recorded(feat_dir, rec)


def cmd_close_task(feat_dir, tid, repo):
    rec = load_recorded(feat_dir)
    if tid not in rec["issues"]:
        skip(f"{tid} has no recorded issue — nothing to close (was `open` run?)")
    tasks = {t["id"]: t for t in parse_tasks(feat_dir)}
    gh(["issue", "close", str(rec["issues"][tid]), "--repo", repo], capture=False)
    print(f"gh-sync: closed issue #{rec['issues'][tid]} for {tid}")
    for n in tasks.get(tid, {}).get("absorbs", []):
        gh(["issue", "close", n, "--repo", repo], capture=False)
        print(f"gh-sync: closed absorbed issue #{n}")


def cmd_ship(feat_dir, repo):
    rec = load_recorded(feat_dir)
    if rec["milestone"] is None:
        skip("no recorded milestone — nothing to close")
    gh(["api", "-X", "PATCH", f"repos/{repo}/milestones/{rec['milestone']}",
        "-f", "state=closed"])
    print(f"gh-sync: milestone #{rec['milestone']} closed")


def main():
    if len(sys.argv) < 3:
        die("usage: gh-sync.py open|close-task|ship <feature-dir> [T-NN]")
    cmd, feat_dir = sys.argv[1], sys.argv[2]
    if not os.path.isdir(feat_dir):
        die(f"{feat_dir} is not a directory")
    root = os.path.abspath(os.path.join(feat_dir, "..", "..", ".."))
    repo = load_config(root)
    if cmd == "open":
        cmd_open(feat_dir, repo)
    elif cmd == "close-task":
        if len(sys.argv) < 4:
            die("close-task needs a T-NN")
        cmd_close_task(feat_dir, sys.argv[3], repo)
    elif cmd == "ship":
        cmd_ship(feat_dir, repo)
    else:
        die(f"unknown command {cmd!r}")


if __name__ == "__main__":
    main()
