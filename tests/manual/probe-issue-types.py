#!/usr/bin/env python3
"""Host-only live probe against the real GitHub API (FEAT-55, REQ-11, T-10).

Run on a credentialled host:

    python3 tests/manual/probe-issue-types.py

This is the ONE check in this feature that touches the real API. Every other
criterion runs against a fake; this file must NEVER import a fixture, never set
GH_SYNC_GH, and never fall back to a canned response - a fixture-derived pass here
would make the single live gate a no-op.

IT CREATES NOTHING BY DEFAULT (D-19). The default invocation is READ-ONLY: it reports
the capability verdict (and, when present, the declared type names) for the configured
`github.repo` and exits 0. Creating a throwaway issue happens only under the explicit
opt-in:

    python3 tests/manual/probe-issue-types.py --create-in <owner/name>

which classifies capability against TARGET instead of the configured repository -
TARGET need not be the configured repo - and, only when TARGET declares the type a
real create would use, creates one throwaway issue, reads its type back over the
GraphQL API, and closes the issue whether or not the read-back matched.

Exactly one line is ever printed with the `probe-issue-types: ` prefix, and it is
always one of: LIVE PASS, CAPABILITY PRESENT, CAPABILITY ABSENT, SKIP.
"""
import argparse
import json
import os
import shutil
import subprocess
import sys
from datetime import datetime, timezone

# Same sys.path anchor idiom as tests/integration/test-gh-sync.py:11-16.
_HERE = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.abspath(os.path.join(_HERE, "..", ".."))
_BIN = os.path.join(_ROOT, ".claude", "skills", "harness", "bin")
sys.path.insert(0, _BIN)
import gh_issue_types  # noqa: E402

# Deliberately hardcoded, never GH_SYNC_GH: this script must never see a fixture gh.
GH = "gh"


def _verdict(line):
    print(f"probe-issue-types: {line}")
    sys.stdout.flush()


def _skip(reason):
    _verdict(f"SKIP {reason}")
    sys.exit(0)


def _load_config():
    path = os.path.join(_ROOT, ".harness", "harness.json")
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    except (OSError, ValueError):
        return {}


def _classify(repo):
    # NEVER append --repo here: `gh api graphql` rejects it ("unknown flag") on the
    # gh CLI version this probe was verified against - owner/name already travel as
    # GraphQL variables inside capability_query_args(repo), which is the whole of
    # what a graphql call needs. gh-sync.py's detect_issue_types appends --repo
    # anyway; that call path is exercised only against test-gh-sync.py's fake gh,
    # which accepts any flag, so the incompatibility is invisible there (see this
    # probe's own receipt/open_questions for the live finding).
    r = subprocess.run(
        [GH] + gh_issue_types.capability_query_args(repo),
        capture_output=True, text=True)
    return gh_issue_types.classify_capability(r.returncode, r.stdout)


def _report_or_skip(repo, on_available):
    """Classify `repo` and dispatch the shared absent/query_failed outcomes.

    `on_available(declared)` handles the one outcome that differs between the
    default invocation (print CAPABILITY PRESENT) and the opt-in (attempt a live
    create); everything else - the wording and exit behaviour of ABSENT and
    query_failed - is identical on both paths (T-10 intent sections 3-4 and 6)."""
    state, declared, message = _classify(repo)
    if state == "absent":
        _verdict(f"CAPABILITY ABSENT {repo} declares no native issue types")
        sys.exit(0)
    if state == "query_failed":
        _skip(f"capability query failed on {repo} ({message})")
    on_available(declared)


def _print_capability_present(repo, declared):
    names = ", ".join(sorted(declared))
    _verdict(f"CAPABILITY PRESENT {repo} declares native issue types {names}")
    sys.exit(0)


def _read_back_issue_type(target, number):
    owner, name = target.split("/", 1)
    query = (
        "query=query{ repository(owner:\"%s\",name:\"%s\"){ issue(number:%s){ "
        "issueType { name } } } }" % (owner, name, number)
    )
    r = subprocess.run([GH, "api", "graphql", "-f", query], capture_output=True, text=True)
    try:
        doc = json.loads(r.stdout)
    except (ValueError, TypeError):
        return None
    repository = (doc.get("data") or {}).get("repository") or {}
    issue = repository.get("issue") or {}
    issue_type = issue.get("issueType") or {}
    return issue_type.get("name")


def _create_and_apply(target, type_id):
    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    title = f"probe-issue-types scratch {timestamp}"
    r = subprocess.run(
        [GH, "issue", "create", "--repo", target, "--title", title,
         "--body", "created by tests/manual/probe-issue-types.py (FEAT-55 T-10 live probe); "
                   "safe to delete", "--label", "harness"],
        capture_output=True, text=True)
    if r.returncode != 0:
        _skip(f"capability query failed on {target} ({(r.stderr or r.stdout).strip()[:200]})")
    number = r.stdout.strip().rsplit("/", 1)[-1]
    node_id = subprocess.run(
        [GH] + gh_issue_types.node_id_args(target, number),
        capture_output=True, text=True).stdout.strip()
    subprocess.run([GH] + gh_issue_types.apply_type_args(node_id, type_id), capture_output=True)
    return number


def _live_pass(target, cfg, declared):
    overrides = gh_issue_types.overrides_from_config(cfg)
    type_name = gh_issue_types.type_for_parent(overrides)
    if gh_issue_types.missing_types({type_name}, declared):
        _skip(gh_issue_types.refusal_text(target, type_name, gh_issue_types.PARENT_KEY))
    type_id = declared[type_name]
    number = _create_and_apply(target, type_id)
    try:
        observed = _read_back_issue_type(target, number)
    finally:
        subprocess.run([GH, "issue", "close", number, "--repo", target], capture_output=True)
    if observed == type_name:
        _verdict(
            f"LIVE PASS {target} created issue {number}, read back native type {observed}, "
            f"closed it - remove it with gh issue delete {number} --repo {target} --yes")
        sys.exit(0)
    print(
        f"probe-issue-types scratch on {target}: applied {type_name!r}, "
        f"observed {observed!r}",
        file=sys.stderr)
    sys.exit(1)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--create-in", metavar="TARGET", default=None,
                         help="opt into creating one throwaway issue in TARGET (owner/name)")
    args = parser.parse_args()
    target = args.create_in

    cfg = _load_config()
    github_cfg = cfg.get("github") or {}
    configured_repo = github_cfg.get("repo")
    repo_resolvable = bool(configured_repo) and "/" in str(configured_repo)
    repo = configured_repo if repo_resolvable else None
    tag = f" ({repo})" if repo else ""

    # Host gate: applies on EVERY invocation, opt-in or not.
    if shutil.which(GH) is None:
        _skip(f"gh not on PATH{tag}")
    if subprocess.run([GH, "auth", "status"], capture_output=True).returncode != 0:
        _skip(f"gh is not authenticated{tag}")

    if target is None:
        # Configured-repository availability gate: exempt when the opt-in was given.
        if not github_cfg.get("sync") or not repo_resolvable:
            _skip(f"github.sync is disabled or github.repo is not pinned{tag}")
        _report_or_skip(repo, lambda declared: _print_capability_present(repo, declared))
        return

    _report_or_skip(target, lambda declared: _live_pass(target, cfg, declared))


if __name__ == "__main__":
    main()
