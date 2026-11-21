#!/usr/bin/env python3
"""PreToolUse guard for merges while a Build-entry mirror receipt is owed, and the one locked
executor for distill merges.

Registered in `.omp/extensions/harness-hooks.ts`. With no arguments it is the hook: it reads a
PreToolUse payload on stdin. A raw `git merge` / `gh pr merge` whose candidate changes
`.harness/expertise/*.md` or `.harness/*/expertise/*.md` is a DISTILL CANDIDATE and is refused
with the `merge-distill` command; unreadable changed-path evidence refuses rather than guessing.

`merge-gate.py merge-distill --root <feature-worktree> --feature <id> --pr <number>` (FEAT-2225
D-03) holds one owner-checkout harness_merge lock from start until the synchronous `gh pr merge`
completes or fails. Inside it: current main, the exact PR head, replay --check, check-expertise,
committed-blob equality, and the same owner/binding/mirror-receipt policy the hook enforces
(DEC-220); main and head are rechecked immediately before merging at the exact head commit. It
never rebases, applies, re-judges, opens or recovers mirrors.

WAS A .sh WRAPPER (issue #1674). This native entry point preserves the wrapper's
isolated root resolution, refusal behavior and hook stream contracts while
removing its extra interpreter launch.
"""
import contextlib as _bootstrap_contextlib
import io as _bootstrap_io
import os as _bootstrap_os
import site as _bootstrap_site
import sys as _bootstrap_sys

_bootstrap_bin = _bootstrap_os.path.dirname(
    _bootstrap_os.path.abspath(__file__))
_bootstrap_original_path = list(_bootstrap_sys.path)
_bootstrap_pythonpath = {
    _bootstrap_os.path.realpath(entry)
    for entry in (_bootstrap_os.environ.get("PYTHONPATH") or "").split(
        _bootstrap_os.pathsep)
    if entry
}
_bootstrap_user_sites = _bootstrap_site.getusersitepackages()
if isinstance(_bootstrap_user_sites, str):
    _bootstrap_user_sites = [_bootstrap_user_sites]
_bootstrap_unsafe = _bootstrap_pythonpath | {
    _bootstrap_os.path.realpath(_bootstrap_bin),
    _bootstrap_os.path.realpath(_bootstrap_os.getcwd()),
    *(_bootstrap_os.path.realpath(entry) for entry in _bootstrap_user_sites),
}
_bootstrap_sys.path[:] = [
    entry for entry in _bootstrap_sys.path
    if entry and _bootstrap_os.path.realpath(entry) not in _bootstrap_unsafe
]


# ACCEPTED DUPLICATION (FEAT-61 D-09, DEC-234). This prologue is copied, not shared, in
# branch-create-gate.py, gh-close-gate.py, plan-sign-gate.py, run-unit-tests.py: it runs BEFORE the
# trusted bin path is on sys.path, so no helper can be imported to hold it — the code below IS
# what creates the import seam. Change all five together; never replace one with an import.
def _resolve_root():
    """Resolve through the trusted sibling with isolated import semantics."""
    try:
        _bootstrap_sys.path.insert(0, _bootstrap_bin)
        with _bootstrap_contextlib.redirect_stderr(_bootstrap_io.StringIO()):
            import harness_boundary
            return harness_boundary.resolve_root(_bootstrap_bin)
    except (ModuleNotFoundError, ValueError):
        # FEAT-64: the module did not import (a missing first-party sibling), or resolve_root
        # refused (strict: no MARKER anywhere) -- the two shapes "no root" takes, matching
        # check-state.py's copy. The four gate copies narrow the same way in FEAT-65.
        return ""


ROOT = _resolve_root()
if not ROOT or not _bootstrap_os.path.isdir(ROOT):
    print(
        f"merge-gate.py: no harness root could be resolved from "
        f"{_bootstrap_bin} — refusing to run",
        file=_bootstrap_sys.stderr,
    )
    raise SystemExit(2)
_bootstrap_sys.path[:] = _bootstrap_original_path

import argparse
import hashlib
import json
import os
import re
import shlex
import subprocess
import sys

sys.path.insert(0, os.path.dirname(__file__))
import artifact_accessors
import feature_corpus
import harness_merge
BIN = os.path.dirname(os.path.abspath(__file__))
EXPERTISE_PATH_RE = re.compile(r"^\.harness/(?:[^/]+/)?expertise/[^/]+\.md$")
DISTILL_COMMAND = ("python3 .claude/skills/harness/bin/merge-gate.py merge-distill "
                   "--root {root} --feature {feature} --pr {pr}")
DISTILL_LOCK = os.path.join(".harness", "merge-distill.lock")
SUBPROCESS_TIMEOUT_SECONDS = 60
OPS = {";", "&", "&&", "|", "||", "(", ")", "<", ">", ">>", "\n"}


def words(command):
    try:
        lexer = shlex.shlex(command, posix=True, punctuation_chars=True)
        lexer.whitespace_split = True
        return [word for word in lexer if word not in OPS]
    except ValueError:
        return command.split()


def is_bin(token, name):
    return os.path.basename(token.strip("\\'\"$()`")) == name


# GRADE-2 REASON: token scanning is the security boundary; splitting the gh and git forms
# would duplicate the ordered token walk and make command detection drift.
def direct_merge(tokens):
    for index, token in enumerate(tokens):
        rest = tokens[index + 1:]
        found = gh_merge(rest) if is_bin(token, "gh") else git_merge(rest) if is_bin(token, "git") else None
        if found:
            return found
    return None


def gh_merge(rest):
    if rest[:2] != ["pr", "merge"]:
        return None
    return "gh", next((word for word in rest[2:] if word.isdigit()), None)


def option_end(tokens, index, values):
    return index + 2 if tokens[index] in values else index + 1


def first_subcommand(tokens, values):
    index = 0
    while index < len(tokens):
        if tokens[index].startswith("-"):
            index = option_end(tokens, index, values)
            continue
        return index
    return None


def merge_target(tokens):
    values = {"-F", "--file", "--cleanup", "--into-name", "-m", "--message", "-s",
              "--strategy", "-X", "--strategy-option"}
    index = 0
    while index < len(tokens):
        token = tokens[index]
        if token in {"--abort", "--continue", "--quit"}:
            return False, None
        if token.startswith("-"):
            index = option_end(tokens, index, values)
            continue
        return True, token
    return True, None


def git_merge(rest):
    globals_with_values = {"-C", "-c", "--work-tree", "--git-dir", "--namespace",
                           "--config-env", "--super-prefix", "--attr-source"}
    index = first_subcommand(rest, globals_with_values)
    if index is None or rest[index] != "merge":
        return None
    is_merge, target = merge_target(rest[index + 1:])
    return ("git", target) if is_merge else None


def nested_merge(tokens, depth):
    if depth >= 3:
        return None
    for token in tokens:
        if len(token.split()) > 1:
            found = merge_ref(token, depth + 1)
            if found:
                return found
    return None


def merge_ref(command, depth=0):
    tokens = words(command)
    return direct_merge(tokens) or nested_merge(tokens, depth)


def local_branch(cwd):
    result = subprocess.run(["git", "-C", cwd, "rev-parse", "--abbrev-ref", "HEAD"],
                            capture_output=True, text=True)
    return result.stdout.strip() if result.returncode == 0 else "unknown"


def gh_head(number, repo):
    try:
        result = subprocess.run(
            [os.environ.get("GH_BIN", "gh"), "pr", "view", number, "--repo", repo,
             "--json", "headRefName", "-q", ".headRefName"],
            capture_output=True, text=True,
        )
    except OSError as exc:
        return "", str(exc)
    text = (result.stderr or result.stdout).strip()
    return result.stdout.strip(), text.splitlines()[0] if text else "gh pr view failed"


def head_branch(command, cwd, repo):
    kind, value = merge_ref(command)
    if kind == "git" and value:
        return value.removeprefix("origin/"), None
    if kind != "gh" or not value:
        return local_branch(cwd), None
    branch, failure = gh_head(value, repo)
    return (branch, None) if branch else (local_branch(cwd), failure)


# Only readable JSON objects with the matching branch can own a merge. Unattributable records are
# ignored; duplicate owners must be surfaced rather than allowing glob iteration to choose one.
#
# THE POPULATION IS THE MAIN CORPUS, NEVER A GLOB OF ROOT (FEAT-1559, FEAT-58 D-01). ROOT is the
# caller's checkout; in a sparse worktree it holds one feature directory, so the more-than-one
# owner deny below could never fire there. Landed records come from the owner root and this
# checkout's own directory replaces its landed copy. A population that cannot be established —
# a broken layout, an unreadable owner, a missing landed directory — raises; it never falls back.
def feature_for(branch, root):
    refusal = feature_corpus.layout_refusal(root)
    if refusal:
        raise feature_corpus.CorpusError(refusal)
    owners = []
    for entry in feature_corpus.population(root):
        document = entry["document"]
        if isinstance(document, dict) and document.get("branch") == branch:
            owners.append((entry["path"], document))
    return owners

def deny(reason):
    print(json.dumps({"hookSpecificOutput": {"hookEventName": "PreToolUse", "permissionDecision": "deny", "permissionDecisionReason": reason}}))


def repo_pinned(repo):
    return isinstance(repo, str) and "/" in repo and bool(repo)


def _github_config(root):
    """The `github` mapping of root's harness.json; an unreadable configuration reads as empty."""
    try:
        config_path = os.path.join(root, ".harness", "harness.json")
        return artifact_accessors.load_harness_json(config_path).get("github") or {}
    except artifact_accessors.ArtifactAccessError:
        return {}


def _read_request():
    """Read configuration and the hook payload, preserving silent parse failure."""
    github = _github_config(ROOT)
    try:
        payload = artifact_accessors.read_hook_payload(
            sys.stdin.read(), "merge-gate hook payload")
        command = (payload.get("tool_input") or {}).get("command") or ""
    except artifact_accessors.ArtifactAccessError:
        return None
    return github, command


def _print_unverified(branch, failure):
    """Explain an allowed merge whose GitHub head could not be resolved."""
    if failure:
        print(f"merge-gate: could not verify this merge - the head branch could not be resolved through gh ({failure}) and the local branch {branch} owes no build-entry receipt; allowing it, because GitHub is a mirror and never a gate (DEC-138).", file=sys.stderr)


def _enforce_receipt(feature_schema, github, feat_dir, document, root):
    """The receipt policy's refusal for one unambiguous feature owner, or None when it allows."""
    feat = os.path.basename(feat_dir)
    bound = feature_schema.has_repository_binding(document)
    if not bound and not github.get("sync"):
        problem = feature_schema.mirror_provenance_problem(document, github.get("repo"))
        if not problem:
            problem = "; ".join(feature_schema.mirror_evidence_problems(feat_dir, document))
        if not problem:
            return None
        return (f"merge-gate: {feat}: {problem}. Run: "
                f"{feature_schema.recovery_command_line(feat_dir, document, github.get('repo'))}")
    if not bound and not repo_pinned(github.get("repo")):
        return f"merge-gate: {feat} has github.sync true with github.repo NOT pinned, so the mirror records nothing here and no receipt can ever be written for it (D-09). NO COMMAND CLEARS THIS BY ITSELF. Pin github.repo in {root}/.harness/harness.json to the value of gh repo view --json nameWithOwner -q .nameWithOwner, or set github.sync to false, and then re-run the Build entry."
    try:
        repo, _board, _types = feature_schema.resolve_binding(document, root)
    except artifact_accessors.FleetError as error:
        return f"merge-gate: {feat} has an invalid authoritative repository binding: {error}"
    problems = feature_schema.mirror_evidence_problems(feat_dir, document)
    if not problems and feature_schema.receipt_allows_merge(document, repo):
        return None
    detail = "; ".join(problems) or feature_schema.mirror_provenance_problem(document, repo) or "receipt absent or incomplete"
    return (f"merge-gate: {feat} needs its GitHub mirror recovery completed before this merge can continue "
            f"({detail}). Run: {feature_schema.recovery_command_line(feat_dir, document, repo)}")


def _handle_owners(feature_schema, github, branch, owners, root):
    """The refusal for zero, duplicate or single-owner merge outcomes, or None when it allows."""
    if not owners:
        return None
    if len(owners) > 1:
        names = ", ".join(sorted(os.path.basename(path) for path, _ in owners))
        return f'merge-gate: {branch} is claimed by more than one feature record ({names}), so this merge cannot be attributed to one feature. Correct the duplicated top-level "branch" field in those feature.json records before merging; no receipt command clears this.'
    feat_dir, document = owners[0]
    # No local catch (FEAT-65): the receipt policy reads records already validated at the
    # load boundary; a defect in it reaches hook_guard's CLOSED form, which still denies.
    return _enforce_receipt(feature_schema, github, feat_dir, document, root)


# ---- distill candidates (FEAT-2225 T-04) ----------------------------------------------------
class DistillRefusal(Exception):
    """One refused distill step; its message is the reason shown to the caller."""


def _run(argv, text=True):
    try:
        return subprocess.run(argv, capture_output=True, text=text, timeout=SUBPROCESS_TIMEOUT_SECONDS)
    except (OSError, subprocess.TimeoutExpired) as exc:
        raise DistillRefusal(f"{os.path.basename(argv[0])} could not run: {exc}") from exc


def _output(argv, what):
    proc = _run(argv)
    if proc.returncode != 0:
        lines = (proc.stderr or proc.stdout).strip().splitlines()
        raise DistillRefusal(f"{what} failed ({lines[0] if lines else f'exit {proc.returncode}'})")
    return proc.stdout.strip()


def _git(root, *args):
    return _output(["git", "-C", root, "-c", "core.quotepath=off", *args], f"git {args[0]}")


def _gh(repo, *args):
    argv = [os.environ.get("GH_BIN", "gh"), *args]
    if repo_pinned(repo):
        argv += ["--repo", repo]
    return _output(argv, f"gh {' '.join(args[:2])}")


def expertise_paths(paths):
    return sorted(path for path in paths if EXPERTISE_PATH_RE.match(path))


def candidate_paths(kind, value, repo, cwd):
    """The changed paths of a raw merge candidate; DistillRefusal when they cannot be read."""
    if kind == "gh":
        return _gh(repo, "pr", "diff", *([value] if value else []), "--name-only").splitlines()
    if not value:
        raise DistillRefusal("git merge names no ref")
    return _git(cwd, "diff", "--name-only", f"HEAD...{value}", "--").splitlines()


def _distill_command(kind, value, owners):
    feature = os.path.basename(owners[0][0]) if len(owners) == 1 else "<feature-id>"
    pr = value if kind == "gh" and value else "<pr-number>"
    return DISTILL_COMMAND.format(root="<feature-worktree>", feature=feature, pr=pr)


def _distill_refusal(kind, value, github, owners):
    """The raw-merge refusal for a distill candidate, or None for an ordinary merge."""
    command = _distill_command(kind, value, owners)
    try:
        changed = expertise_paths(candidate_paths(kind, value, github.get("repo") or "", os.getcwd()))
    except DistillRefusal as exc:
        return (f"merge-gate: the changed paths of this {kind} merge could not be read ({exc}), so it "
                f"is denied rather than guessed to be an ordinary merge; a merge that changes "
                f"Expertise must run: {command}")
    if not changed:
        return None
    return (f"merge-gate: this raw {kind} merge changes Expertise ({', '.join(changed)}), so it is a "
            f"distill candidate; raw git merge and gh pr merge of a distill candidate are refused. "
            f"Run: {command}")


def _evaluate_merge(command, github):
    """Resolve the merge owner, then route its receipt and distill-candidate outcome."""
    import feature_schema
    kind, value = merge_ref(command)
    branch, failure = head_branch(
        command, os.getcwd(), github.get("repo") or "")
    try:
        owners = feature_for(branch, ROOT)
    except feature_corpus.CorpusError as exc:
        deny(f"merge-gate: cannot establish which feature owns {branch}, so this merge is "
             f"denied rather than attributed to a guess: {exc}")
        return
    reason = (_handle_owners(feature_schema, github, branch, owners, ROOT)
              or _distill_refusal(kind, value, github, owners))
    if reason:
        deny(reason)
        return
    _print_unverified(branch, failure)


# ---- merge-distill executor ------------------------------------------------------------------
def _parse_json(text, context):
    try:
        return artifact_accessors.parse_gh_json(text, context)
    except artifact_accessors.ArtifactAccessError as exc:
        raise DistillRefusal(str(exc)) from exc


def _pr_metadata(number, repo):
    """(head oid, head branch, base branch) of PR `number`; each is required."""
    meta = _parse_json(_gh(repo, "pr", "view", number, "--json", "headRefOid,headRefName,baseRefName"),
                       f"gh pr view {number}")
    fields = tuple(meta.get(key) if isinstance(meta, dict) else None
                   for key in ("headRefOid", "headRefName", "baseRefName"))
    if not all(isinstance(field, str) and field for field in fields):
        raise DistillRefusal(f"PR #{number} metadata lacks headRefOid, headRefName or baseRefName")
    return fields


def _fetch_main(root, base):
    _git(root, "fetch", "--quiet", "origin", f"+refs/heads/{base}:refs/remotes/origin/{base}")
    return _git(root, "rev-parse", "--verify", f"refs/remotes/origin/{base}^{{commit}}")


def _live_main(root, base):
    listed = _git(root, "ls-remote", "origin", f"refs/heads/{base}").split()
    if not listed:
        raise DistillRefusal(f"origin has no {base} branch")
    return listed[0]


def _require_checkout(root, head, main):
    actual = _git(root, "rev-parse", "HEAD")
    if actual != head:
        raise DistillRefusal(f"the worktree {root} is at {actual}, not PR head {head}; check out "
                             f"the PR head and retry")
    if _git(root, "status", "--porcelain", "--", ".harness"):
        raise DistillRefusal(f"the worktree {root} has uncommitted .harness changes; commit and "
                             f"push them, or discard them, and retry")
    if _run(["git", "-C", root, "merge-base", "--is-ancestor", main, head]).returncode != 0:
        raise DistillRefusal(f"PR head {head} does not contain current main {main}; rebase the "
                             f"distill onto main, replay its receipts, commit, push and retry")


def _changed_expertise(root, main, head):
    changed = expertise_paths(_git(root, "diff", "--name-only", f"{main}...{head}", "--").splitlines())
    if not changed:
        raise DistillRefusal(f"PR head {head} changes no Expertise file against main {main}, so it "
                             f"is not a distill candidate; merge it through the ordinary route")
    return changed


def _replay_check(root, feature, main):
    proc = _run([sys.executable, os.path.join(BIN, "expertise-merge.py"), "replay", "--root", root,
                 "--feature", feature, "--base", main, "--check"])
    report = _parse_json(proc.stdout, "expertise-merge.py replay --check") if proc.returncode == 0 else None
    if not (isinstance(report, dict) and report.get("replayed") is True):
        detail = " | ".join((proc.stdout + proc.stderr).strip().splitlines()[:6])
        raise DistillRefusal(f"expertise-merge.py replay --check refused (exit {proc.returncode}): {detail}")
    return report


def _blob_sha256(root, head, rel):
    proc = _run(["git", "-C", root, "cat-file", "blob", f"{head}:{rel}"], text=False)
    return hashlib.sha256(proc.stdout).hexdigest() if proc.returncode == 0 else None


def _replayed_hashes(report):
    return {item["destination"]: item.get("result_sha256") for item in report.get("files") or []
            if isinstance(item, dict) and isinstance(item.get("destination"), str)}


def _committed_replay(root, head, changed, report):
    """[{destination, sha256}] once every changed Expertise file is covered by the replay and each
    committed blob equals the replay of this PR's active receipts onto main."""
    replayed = _replayed_hashes(report)
    evidence = []
    for rel in sorted(set(changed) | set(replayed)):
        if rel not in replayed:
            raise DistillRefusal(f"{rel} changed with no active receipt in this PR's replay")
        committed = _blob_sha256(root, head, rel)
        if committed != replayed[rel]:
            raise DistillRefusal(f"committed {rel} ({committed}) differs from the replay of this PR's "
                                 f"receipts onto main ({replayed[rel]}); replay onto current main, "
                                 f"commit the result, push and retry")
        evidence.append({"destination": rel, "sha256": committed})
    return evidence


def _check_expertise(root, changed):
    proc = _run([sys.executable, os.path.join(BIN, "check-expertise.py"),
                 *(os.path.join(root, rel) for rel in changed)])
    if proc.returncode != 0:
        detail = " | ".join((proc.stdout + proc.stderr).strip().splitlines()[:6])
        raise DistillRefusal(f"check-expertise failed (exit {proc.returncode}): {detail}")


def _require_owner(root, feature, branch, github):
    """DEC-220 for distills: one owner, the requested feature, and the hook's receipt policy."""
    import feature_schema
    try:
        owners = feature_for(branch, root)
    except feature_corpus.CorpusError as exc:
        raise DistillRefusal(f"cannot establish which feature owns {branch}: {exc}") from exc
    names = sorted(os.path.basename(path) for path, _ in owners)
    if not names:
        raise DistillRefusal(f"no feature record claims {branch}, so this PR cannot be attributed to {feature}")
    if len(names) == 1 and names != [feature]:
        raise DistillRefusal(f"{branch} is owned by {names[0]}, not {feature}")
    refusal = _handle_owners(feature_schema, github, branch, owners, root)
    if refusal:
        raise DistillRefusal(refusal)


def _recheck(root, base, main, number, repo, head):
    """Main is read last, immediately before the merge call."""
    moved = _pr_metadata(number, repo)[0]
    if moved != head:
        raise DistillRefusal(f"PR #{number} head moved from {head} to {moved} during verification; "
                             f"check out the new head and retry")
    live = _live_main(root, base)
    if live != main:
        raise DistillRefusal(f"main advanced from {main} to {live} during verification; rebase the "
                             f"distill onto the new main, replay, commit, push and retry")


def _verified_merge(root, feature, number):
    github = _github_config(root)
    repo = github.get("repo") or ""
    head, branch, base = _pr_metadata(number, repo)
    main = _fetch_main(root, base)
    _require_checkout(root, head, main)
    changed = _changed_expertise(root, main, head)
    report = _replay_check(root, feature, main)
    files = _committed_replay(root, head, changed, report)
    _check_expertise(root, changed)
    _require_owner(root, feature, branch, github)
    _recheck(root, base, main, number, repo, head)
    _gh(repo, "pr", "merge", number, "--squash", "--match-head-commit", head)
    return {"merged": True, "feature": feature, "pr": number, "branch": branch, "head": head,
            "main": main, "files": files, "receipts": report.get("receipts"),
            "batches": report.get("batches")}


def merge_distill(root, feature, number):
    """Verify and merge one distill PR, holding the owner-checkout lock throughout."""
    root = os.path.realpath(root)
    lock_path = os.path.join(feature_corpus.owner_root(root), DISTILL_LOCK)
    with harness_merge.acquire(lock_path):
        return _verified_merge(root, feature, number)


def _pr_number(text):
    if not re.fullmatch(r"[1-9][0-9]*", text):
        raise argparse.ArgumentTypeError(f"{text!r} is not a pull request number")
    return text


def distill_main(argv):
    parser = argparse.ArgumentParser(
        prog="merge-gate.py",
        description="With no arguments: the PreToolUse merge hook (payload on stdin).")
    sub = parser.add_subparsers(dest="cmd", required=True)
    command = sub.add_parser("merge-distill", help="verify and merge one distill PR under the owner lock")
    command.add_argument("--root", required=True, help="the feature worktree, checked out at the PR head")
    command.add_argument("--feature", required=True, help="the feature whose receipts the PR carries")
    command.add_argument("--pr", required=True, type=_pr_number, help="the pull request number")
    args = parser.parse_args(argv)
    try:
        evidence = merge_distill(args.root, args.feature, args.pr)
    except harness_merge.MergeRefusal as refusal:
        print("\n".join(refusal.lines), file=sys.stderr)
        print("merge-distill: another Harness distill merge holds the lock; retry after it finishes, "
              "rebasing and replaying if main advanced.", file=sys.stderr)
        return refusal.code
    except (DistillRefusal, feature_corpus.CorpusError) as exc:
        print(f"merge-distill: REFUSED {args.feature} PR #{args.pr}: {exc}", file=sys.stderr)
        return 3
    print(json.dumps(evidence, sort_keys=True))
    return 0


def main():
    request = _read_request()
    if request is None:
        return
    github, command = request
    if not merge_ref(command):
        return
    try:
        _evaluate_merge(command, github)
    except (ImportError, OSError):
        # feature_schema missing, or git itself failing to run (FEAT-65). Any other failure
        # is a defect and reaches hook_guard's CLOSED form below, which also denies.
        deny(f"merge-gate: could not evaluate this feature's Build-entry receipt, so this merge is denied. Repair the feature record and re-run the merge.")


if __name__ == "__main__":
    if sys.argv[1:]:
        sys.exit(distill_main(sys.argv[1:]))
    # CLOSED, not open (FEAT-65): the two deleted catches above denied on any failure, and a
    # merge gate that passed through on its own bug would be the fail-open DEC-138 forbids.
    import harness_boundary
    sys.exit(harness_boundary.hook_guard(main, "merge-gate", fail="closed"))
