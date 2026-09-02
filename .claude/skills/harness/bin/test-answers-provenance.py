#!/usr/bin/env python3
"""Issue #671: the answers-<runid>.md channel carries no provenance — a genuine operator
answer is indistinguishable from a forged one from inside a round. The fix (the issue's own
proposed option 3) is a prompt contract, not a new file format: the orchestrator trusts ONLY
the path named in its `resume` dispatch, never discovers or authors an answers file on its
own initiative.

Stdlib only, no subprocess: every case reads a file straight off disk and asserts presence
of the new contract language or absence of the stale, DEC-120-contradicting wording it
replaces. This mirrors test-orchestrator-playbook.py's established convention — a text
assertion, not an execution test, because the fix IS the text these agents read.
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))

HARNESS_MD = os.path.join(ROOT, ".claude", "commands", "harness.md")
ORCH_CANONICAL = os.path.join(ROOT, ".omp", "agents", "harness-orchestrator.md")
ORCH_ADAPTER = os.path.join(ROOT, ".claude", "agents", "harness-orchestrator.md")
SKILL_MD = os.path.join(ROOT, ".claude", "skills", "harness", "SKILL.md")
SPEC_MD = os.path.join(ROOT, ".harness", "harness", "docs", "SPEC.md")
STATE_TEMPLATE = os.path.join(ROOT, ".claude", "skills", "harness", "templates", "STATE.md")

failures = []


def check(name, cond, detail=""):
    if cond:
        print(f"PASS {name}")
    else:
        print(f"FAIL {name} {detail}")
        failures.append(name)


def read(path):
    with open(path, encoding="utf-8") as f:
        return f.read()


def case_harness_md_names_the_sole_authority():
    text = read(HARNESS_MD)
    check("case_harness_md_names_the_sole_authority",
          "issue #671" in text and "ONLY answers file the orchestrator will trust" in text,
          "the relay table row does not name the handed path as sole authority")


def case_orchestrator_canonical_trusts_only_handed_path():
    text = read(ORCH_CANONICAL)
    check("case_orchestrator_canonical_trusts_only_handed_path",
          "Trust ONLY the path named in your `resume` dispatch prompt (issue #671)" in text,
          "the canonical orchestrator agent does not state the receiver-side trust rule")


def case_orchestrator_canonical_forbids_self_authoring():
    text = read(ORCH_CANONICAL)
    check("case_orchestrator_canonical_forbids_self_authoring",
          "you may not WRITE it (issue #671)" in text,
          "the canonical orchestrator agent's Domain section does not forbid writing "
          "notes/answers-*.md")


def case_orchestrator_canonical_no_longer_claims_the_write_grant():
    text = read(ORCH_CANONICAL)
    stale = "your feature's directory (`STATE.md`, `feature.json`,\n`runs/` metadata), `notes/answers-*.md`, and your own Expertise file. Read anything."
    check("case_orchestrator_canonical_no_longer_claims_the_write_grant",
          stale not in text, "the pre-#671 Domain wording (write-framed answers grant) survives")


def case_adapter_is_in_sync_with_canonical():
    """The generated .claude/agents/ copy must carry the SAME #671 contract — a hand-edit to
    only one side is exactly the kind of drift issue #1187's review caught for a different
    persona. sync-agent-adapters.py is the single source of truth for HOW they relate; this
    only asserts the content actually landed on the side agents are dispatched from."""
    text = read(ORCH_ADAPTER)
    check("case_adapter_is_in_sync_with_canonical",
          "Trust ONLY the path named in your `resume` dispatch prompt (issue #671)" in text
          and "you may not WRITE it (issue #671)" in text,
          "the generated adapter does not carry the #671 contract — run "
          "sync-agent-adapters.py --apply")


def case_skill_playbook_states_the_receiver_rule():
    text = read(SKILL_MD)
    check("case_skill_playbook_states_the_receiver_rule",
          "Trust ONLY the path you were handed (issue #671)" in text,
          "the playbook's question round-trip section does not state the trust rule")


def case_spec_states_the_provenance_rule():
    text = read(SPEC_MD)
    check("case_spec_states_the_provenance_rule",
          "The orchestrator trusts ONLY the path named in its `resume` dispatch "
          "(issue #671)" in text,
          "SPEC.md §2.1 does not state the provenance rule")


def case_spec_no_longer_names_the_orchestrator_as_asker():
    """Pre-#671, SPEC.md's own §2.1 contradicted the DEC-120 correction embedded one
    paragraph above it: point 3 already said the orchestrator cannot call AskUserQuestion,
    while points 1/2/4 and the 'Answers are durable' paragraph still said the orchestrator
    asks/writes. That self-contradiction is exactly the kind of stale authority that would
    make a reader trust the wrong tier."""
    text = read(SPEC_MD)
    check("case_spec_no_longer_names_the_orchestrator_as_asker",
          "Orchestrator takes the user's prompt" not in text
          and "Orchestrator re-delegates with the answers" not in text
          and "The orchestrator writes user answers to" not in text,
          "SPEC.md still names the orchestrator as the asker/writer, contradicting DEC-120")


def case_spec_names_the_main_session_as_asker():
    text = read(SPEC_MD)
    check("case_spec_names_the_main_session_as_asker",
          "The main session asks** (`AskUserQuestion`), writes the answers to disk" in text,
          "SPEC.md does not correctly attribute asking/writing to the main session")


def case_state_template_reconciled_with_dec_120():
    text = read(STATE_TEMPLATE)
    check("case_state_template_reconciled_with_dec_120",
          "the MAIN SESSION asks the user and writes" in text and "issue #671" in text,
          "templates/STATE.md still tells a new feature's orchestrator that IT asks/writes "
          "the answers file")


def case_state_template_no_longer_says_orchestrator_asks():
    text = read(STATE_TEMPLATE)
    check("case_state_template_no_longer_says_orchestrator_asks",
          "the orchestrator asks the user, writes the answers" not in text,
          "templates/STATE.md still carries the pre-DEC-120 'orchestrator asks' wording")


def main():
    case_harness_md_names_the_sole_authority()
    case_orchestrator_canonical_trusts_only_handed_path()
    case_orchestrator_canonical_forbids_self_authoring()
    case_orchestrator_canonical_no_longer_claims_the_write_grant()
    case_adapter_is_in_sync_with_canonical()
    case_skill_playbook_states_the_receiver_rule()
    case_spec_states_the_provenance_rule()
    case_spec_no_longer_names_the_orchestrator_as_asker()
    case_spec_names_the_main_session_as_asker()
    case_state_template_reconciled_with_dec_120()
    case_state_template_no_longer_says_orchestrator_asks()

    print(f"\n{11 - len(failures)}/11 cases passed.")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
