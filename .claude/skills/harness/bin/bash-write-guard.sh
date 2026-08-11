#!/usr/bin/env bash
# PreToolUse Bash hook — close the CASUAL Bash write bypass (DEC-151).
#
# Field incident: qa, denied a source edit by check-domain, made the same edit
# via `perl -pi` from Bash — the domain hook only sees Write/Edit. This guard
# does not make Bash-write extraction "winnable" in general (DEC-85 stands);
# it parses the COMMON in-place editors and redirections, which is what an
# agent under pressure actually reaches for. Unparseable commands pass — the
# guard converts casual bypass into deliberate obfuscation, which the post-run
# tree audit then catches.
#
# Policy:
#   - reviewers (code/security/ui) — READ-ONLY: any detected write pattern is
#     denied outright, no path analysis. Their job is findings, never fixes.
#   - dev-ops — exempt (trusted by design, owns builds/deploy; DEC-85).
#   - every other harness agent — a detected write whose target path is
#     extractable and OUTSIDE the agent's domain (per team-config.yaml,
#     shared paths included) is denied; in-domain and unparseable pass.
#   - main session and non-harness agents — ungoverned, exit 0.
set -uo pipefail

payload=$(cat)

# BASH_SOURCE is the one question only bash can answer, which is why any bash remains.
_self="${BASH_SOURCE[0]:-$0}"
_selfdir="$(cd "$(dirname "$_self")" && pwd)"
_derived="$(cd "$_selfdir/../../../.." && pwd)"

# T-15: ONE interpreter launch, not two. Same reasoning as T-13 on the sibling hook —
# this fires on every Bash tool call, and a Python start-up per launch is the bulk of
# it. Behaviour is unchanged: the dev-ops exemption, the harness-* prefix filter, the
# absent-manifest fail-open and every exit-2 message are identical, and the unchanged
# test suite is the equivalence proof (D-10, REQ-07).
HOOK_PAYLOAD="$payload" PYTHONPATH="$_selfdir${PYTHONPATH:+:$PYTHONPATH}" \
  python3 - "$_derived" <<'PY'
import sys, os, re, json, shlex

# harness_yaml is imported LAZILY, after the manifest check — NOT here. Ordering is
# behaviour: the two-launch version reached the absent-manifest fail-open in BASH,
# before any interpreter needed the module, so a guard whose module is missing must
# still exit 0 there rather than crash. (T-13 shipped this bug on the sibling hook and
# a test caught it.)
_derived = sys.argv[1]

try:
    d = json.loads(os.environ.get("HOOK_PAYLOAD") or "")
except Exception:
    sys.exit(0)

agent = d.get("agent_type") or ""
if not agent:
    sys.exit(0)

# harness-dev-ops is EXEMPT: it owns the tooling this guard is made of, and blocking
# it would remove the one recovery path when the guard itself is broken.
if agent == "harness-dev-ops":
    sys.exit(0)
if not agent.startswith("harness-"):
    sys.exit(0)

root = os.environ.get("CLAUDE_PROJECT_DIR") or ""
if not root or not os.access(os.path.join(root, ".harness", "team-config.yaml"), os.R_OK):
    if os.access(os.path.join(_derived, ".harness", "team-config.yaml"), os.R_OK):
        root = _derived
    else:
        root = root or os.getcwd()
manifest = os.path.join(root, ".harness", "team-config.yaml")

# not onboarded — fail open like check-domain
if not os.access(manifest, os.R_OK):
    sys.exit(0)

import harness_yaml

# The RETURN VALUE IS THE DECISION — see check-domain.sh's note. A bare call leaves
# REQ-04's fail-closed and SC-09's expiry inert: the function prints, and the write
# proceeds anyway because only exit 2 blocks (DEC-100).
if not harness_yaml.require_or_bootstrap(root):
    sys.exit(2)

# GRANTED, and there is no parser. Recorded, NOT acted on here — see below.
#
# This used to `sys.exit(0)` on the spot, which short-circuited the ENTIRE guard. But
# only the DOMAIN check needs the manifest: the reviewer read-only rule and the
# write-pattern detection need neither a manifest nor a parser. So a bootstrap-grant
# session let `harness-code-reviewer` run `rm -rf src/main.py` — reproduced live, exit 0
# where a PyYAML-present run exits 2. On `main` this guard had NO YAML dependency at
# all, so reviewer read-only was unconditional; the short-circuit was a regression
# introduced by this feature.
#
# It is also the exact defect the sibling hook was fixed for one commit earlier
# ("Skip only what actually needs the parser", check-domain.sh) — fixed there and not
# here, in a pair of files this same feature otherwise went to lengths to keep in step
# (D-03). Two guards, one rule, and I changed one of them.
_no_parser = harness_yaml.yaml is None

cmd = ((d.get("tool_input") or {}).get("command") or "")
if not cmd:
    sys.exit(0)

REVIEWERS = {"harness-code-reviewer", "harness-security-reviewer", "harness-ui-reviewer"}

# --- detect write patterns and extract candidate target paths where parseable ---
findings = []   # (pattern-name, [paths])

def mask_quoted(text):
    """Blank the CONTENTS of quoted spans, preserving length and the quotes.

    The redirect scan below is a regex over the raw command, so a `>` inside a
    quoted string was read as an operator. That blocked the MANDATED
    `Co-Authored-By: … <noreply@anthropic.com>` trailer on every agent commit, an
    arrow in a printed string, and an HTML comment in prose (Task #5).

    Masking rather than deleting keeps offsets and lengths intact, so a QUOTED
    redirect target still yields a capturable token: `> "src/x.py"` becomes
    `> "xxxxxxxxx"`, which still finds the redirect and still blocks. The guard
    fails safe — a masked span can only hide `>` characters that bash itself
    would treat as literal text, never an operator.
    """
    out, q = [], None
    for ch in text:
        if q:
            if ch == q:
                q = None; out.append(ch)
            else:
                out.append("x")
            continue
        if ch in "\"'":
            q = ch
        out.append(ch)
    return "".join(out)

SHELL_FEEDERS = {"bash", "sh", "zsh", "dash", "ksh"}


def strip_heredoc_bodies(text):
    """Drop heredoc BODIES, keeping the command line that opens them.

    A heredoc body is DATA, not shell syntax: `python3 - <<PY ... if a > b: ... PY`
    feeds a script to an interpreter, and reading that `>` as a redirect refused every
    inline script this repo runs (B-6). The `<<TAG` line itself is kept, so a real
    redirect on it — `cat <<EOF > src/main.py` — is still scanned and still blocks.

    EXCEPTION, and it is the whole reason this is safe: when the heredoc feeds a SHELL
    (`bash <<EOF`), the body IS code and its redirects are real. Those bodies are kept.
    An unrecognised feeder is treated as a shell too — the guard fails toward scanning.
    """
    lines, out, i = text.splitlines(), [], 0
    while i < len(lines):
        line = lines[i]
        out.append(line)
        # Only an UNQUOTED << opens a heredoc; mask first so `echo "a <<b"` does not.
        m = re.search(r"<<-?\s*([\"']?)([A-Za-z_][A-Za-z0-9_]*)\1", mask_quoted(line))
        i += 1
        if not m:
            continue
        tag, dash = m.group(2), "<<-" in line
        try:
            words = [os.path.basename(w) for w in shlex.split(line)]
        except ValueError:
            # An unbalanced quote must not raise: this is a PreToolUse hook, and only
            # exit 2 blocks (DEC-100), so an uncaught exception fails OPEN. Keep the body.
            words = []
            keep_body = True
        else:
            # A shell ANYWHERE in the pipeline means the body is code, not data:
            # `cat <<EOF | bash` routes it to a shell just as surely as `bash <<EOF`,
            # and looking only at the first word let that shape through (a fail-open
            # this function introduced and this line closes).
            keep_body = (any(w in SHELL_FEEDERS for w in words)
                         or not words
                         or words[0] not in KNOWN_DATA_FEEDERS)
        while i < len(lines):
            body = lines[i]
            i += 1
            if (body.strip() if dash else body) == tag:
                out.append(body)
                break
            if keep_body:
                out.append(body)
    return "\n".join(out)


# Feeders whose heredoc body is inert DATA. Anything not listed keeps its body scanned,
# so a novel or obfuscated feeder cannot smuggle a redirect past the guard.
KNOWN_DATA_FEEDERS = {"cat", "python", "python3", "git", "tee", "jq", "sed", "awk",
                      "grep", "node", "ruby", "perl", "psql", "sqlite3", "mail", "ssh"}


def segments(text):
    """Split a compound command into its parts at UNQUOTED shell separators.

    `shlex.split` leaves `;` attached to the preceding token ('docs/a.md;'), so the
    guard's `if a in (";", "&&", ...)` break never fired and the NEXT command's name was
    collected as an operand — `rm -f docs/a.md; echo ok` was refused for "rm targets
    echo" (B-6). Splitting first makes each command's operand list actually end.
    """
    parts, cur, q, i = [], [], None, 0
    while i < len(text):
        ch = text[i]
        if q:
            cur.append(ch)
            if ch == q:
                q = None
            i += 1
            continue
        if ch in "\"'":
            q = ch; cur.append(ch); i += 1; continue
        two = text[i:i + 2]
        if two in ("&&", "||"):
            parts.append("".join(cur)); cur = []; i += 2; continue
        if ch in ";\n|&":
            parts.append("".join(cur)); cur = []; i += 1; continue
        cur.append(ch)
        i += 1
    parts.append("".join(cur))
    return [p for p in (s.strip() for s in parts) if p]


scan_text = strip_heredoc_bodies(cmd)
SEGMENTS = segments(scan_text)

# redirections:  > path   >> path   (not 2>/dev/null, >&2, >(...) etc.)
# Scanned over the MASKED text so quoted text cannot pose as an operator.
for _seg in SEGMENTS:
    for m in re.finditer(r"(?<![0-9&<])>{1,2}\s*([^\s;&|)]+)", mask_quoted(_seg)):
        p = m.group(1)
        if p.startswith(("&", "(", "/dev/")):
            continue
        findings.append(("redirect", [p]))

# A redirection is not an operand. `shlex.split` hands back `2>/dev/null` as an ordinary
# token, so `cp docs/a.md docs/b.md 2>/dev/null` read its LAST token as the cp destination
# and denied a legal in-domain copy, naming "2>/dev/null" as the path (B-5, hit twice during
# FEAT-11). Two shapes exist and both must go: the operator glued to its target
# (`2>/dev/null`, `>out.md`) and the operator standing alone, whose target is the NEXT token
# (`> out.md`).
#
# THIS DOES NOT WEAKEN THE GUARD, and that is the whole reason it is safe to drop them: the
# redirect scan above (the `>{1,2}` finditer over the masked text) already reports every real
# redirect target as its own finding. `cp a b > src/evil.py` is still denied — by the finding
# that correctly calls it a redirect, instead of by one that mislabels it a cp destination.
REDIR = re.compile(r"^(?:[0-9]*(?:>{1,2}|<)|[0-9]*>&|&>{1,2})")


# WHICH COMMANDS ACTUALLY TAKE A SCRIPT ARGUMENT AFTER -f. This set is the whole fix for
# #241, and getting it wrong fails in one of two directions, so it is a set and not a
# blanket rule.
#
# `sed -f script.sed file`, `perl -f`, `awk -f prog.awk file` consume the token after -f,
# and skipping it is what keeps the SCRIPT out of the target list.
#
# `rm -f path` does NOT. There -f means force, and the token after it is the target. The
# skip was unconditional, so `rm -f <out-of-domain-path>` arrived with an EMPTY target
# list and no deny fired — measured at exit 0 while bare `rm <same path>` exited 2. The
# most common deletion idiom was the one that got through. `rm -rf dir` was never affected
# because -rf is a single token; `rm -r -f path` was.
#
# DO NOT "simplify" this by dropping -f from the flag list entirely: `sed -i -f script.sed
# <out-of-domain>` blocks correctly TODAY by skipping the script path and keeping the real
# target, and a blanket drop would report the script as the target instead.
SCRIPT_ARG_CMDS = ("sed", "perl", "awk")


def trailing_files(args, drop_first_script=False, script_flags=False):
    out, skip, saw_expr, skip_is_redir = [], False, False, False
    for a in args:
        if skip:
            # A skipped REDIRECT target is not an expression. Conflating the two would let
            # `sed -i 's/a/b/' f > out` look as if -e had been passed, and drop_first_script
            # would then keep the script `s/a/b/` in the file list.
            skip = False
            if not skip_is_redir:
                saw_expr = True
            skip_is_redir = False
            continue
        if script_flags and a in ("-e", "-E", "--expression", "-f", "--file"):
            skip = True; continue          # the next token is an expression/script, not a target
        m = REDIR.match(a) if a else None
        if m:
            # A bare operator takes the next token as its target; a glued one carries it.
            if m.end() == len(a):
                skip = True; skip_is_redir = True
            continue
        if not a or a.startswith("-") or a in (";", "&&", "||"):
            continue                       # empty covers BSD `sed -i ''`
        out.append(a)
    if drop_first_script and not saw_expr and out:
        out = out[1:]                      # bare `sed -i 's/a/b/' file`: first arg is the script
    return out

tokens = []
for _seg in SEGMENTS:
    try:
        tokens.append(shlex.split(_seg, posix=True))
    except ValueError:
        tokens.append(_seg.split())

# Each segment is one command, so its operand list ends at the segment boundary — no
# in-list separator hunting, which is what silently failed before (B-6).
for seg_tokens in tokens:
    for i, t in enumerate(seg_tokens):
        base = os.path.basename(t)
        args = seg_tokens[i + 1:]
        if base in ("sed", "perl") and any(a.startswith(("-i", "-pi", "-ni")) or a == "-p" and "-i" in args for a in args):
            findings.append((f"{base} in-place",
                             trailing_files(args, drop_first_script=(base == "sed"),
                                            script_flags=(base in SCRIPT_ARG_CMDS))))
        elif base == "tee":
            findings.append(("tee", [a for a in trailing_files(args) if a != "-"]))
        elif base in ("mv", "cp") and len(trailing_files(args)) >= 2:
            findings.append((base, trailing_files(args)[-1:]))
        elif base == "rm":
            findings.append(("rm", trailing_files(args)))
        elif base == "sponge":
            findings.append(("sponge", trailing_files(args)))
        elif base == "awk" and any(a == "-i" or a.startswith("inplace") for a in args):
            findings.append(("awk inplace", trailing_files(args, script_flags=True)))

if not findings:
    sys.exit(0)

def deny(reason):
    print(f"bash-write-guard: BLOCKED — {reason}", file=sys.stderr)
    print("  File changes go through the Write tool, where your domain is enforced. "
          "A path the domain hook denied does not become writable by switching tools — "
          "that is guardrail evasion (DEC-151). If the file should be yours, raise it "
          "as an open_question.", file=sys.stderr)
    sys.exit(2)

if agent in REVIEWERS:
    pats = ", ".join(sorted({f[0] for f in findings}))
    deny(f"{agent} is READ-ONLY and this command writes files ({pats}). "
         f"Report the finding; never fix.")

# NO PARSER: everything above this line ran — the write-pattern detection and the
# reviewer read-only denial, neither of which needs the manifest. Only the domain walk
# below does, so only it is skipped. The grant exists to let a broken machine be fixed,
# not to suspend the rules that do not depend on the thing that is broken.
if _no_parser:
    sys.exit(0)

# --- non-reviewers: check extractable paths against the agent's domain ---
# T-14, and this is the SECURITY-RELEVANT half of D-03. This file used to carry its
# own copy of check-domain.sh's manifest skimmer — two hand-maintained walks over the
# same rulebook, which is one edit away from the two write surfaces disagreeing about
# what an agent may write. That is not a theoretical risk here: this hook exists
# BECAUSE an agent routed around check-domain.sh (DEC-151), so a divergence between
# them is a bypass by construction. Both now call one function; they cannot drift.
try:
    mine, shared = harness_yaml.manifest_domains(manifest, agent)
except harness_yaml.DuplicateKeyError as e:
    print(f"bash-write-guard: BLOCKED — the manifest has a duplicate key {e.key!r}.",
          file=sys.stderr)
    print(f"  {manifest}", file=sys.stderr)
    print("  The second occurrence silently shadows the first, so which domain "
          "applies is ambiguous. Enforcement cannot be trusted until it is fixed.",
          file=sys.stderr)
    sys.exit(2)
except harness_yaml.YamlParseError as e:
    # FAIL CLOSED, matching check-domain.sh. Distinct from the absent-manifest case
    # at :46, which still exits 0: an unconfigured project has nothing to enforce,
    # whereas here the project IS configured and exactly one action fixes it.
    print("bash-write-guard: BLOCKED — the manifest does not parse, so no domain can "
          "be checked.", file=sys.stderr)
    print(f"  {e.original}", file=sys.stderr)
    print("  Enforcement is CLOSED rather than partial: a rulebook that cannot be "
          "read cannot be half-applied. Fix the file (the main session owns it), "
          "then retry.", file=sys.stderr)
    sys.exit(2)

def glob_to_re(pat):
    out, i = [], 0
    while i < len(pat):
        if pat.startswith("**", i):
            out.append(".*"); i += 2
            if pat.startswith("/", i):
                out.append("/?"); i += 1
        elif pat[i] == "*":
            out.append("[^/]*"); i += 1
        elif pat[i] == "?":
            out.append("[^/]"); i += 1
        else:
            out.append(re.escape(pat[i])); i += 1
    return re.compile("^" + "".join(out) + "$")

def matches(path, pat):
    pat = pat.rstrip("/")
    if pat in (".", ""):
        return False
    if pat.endswith("/**"):
        base = pat[:-3]
        return bool(glob_to_re(base).match(path) or glob_to_re(base + "/**").match(path))
    return bool(glob_to_re(pat).match(path) or glob_to_re(pat + "/**").match(path))

allowed = mine + shared
for name, paths in findings:
    for p in paths:
        ap = os.path.abspath(os.path.join(root, p)) if not os.path.isabs(p) else p
        rel = os.path.relpath(ap, os.path.abspath(root))
        # Worktree carve-out (DEC-153): disposable checkouts are where sanctioned
        # perturbation proofs live — qa mutates source there to prove a test
        # discriminates. The MAIN checkout stays hard-protected. Reviewers never
        # reach this branch (denied on any write pattern above).
        if re.match(r"^\.claude/worktrees/", rel):
            continue
        cands = [rel]
        if rel.startswith(".."):
            continue  # outside repo — not this hook's problem
        # tmp/cache noise is not a domain question
        # NB: no `^/` alternative -- relpath means an out-of-repo absolute target
        # already hit the `..` continue above, so it was dead (review of PR #4).
        if re.match(r"^(\.pytest_cache|node_modules|__pycache__|\.venv)", rel):
            continue
        if not any(matches(r, g) for r in cands for g in allowed):
            deny(f"{agent}: `{name}` targets {rel}, outside your domain.")

sys.exit(0)
PY
