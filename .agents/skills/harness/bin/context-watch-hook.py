#!/usr/bin/env python3
"""PostToolUse hook: tell a running orchestrator that its context crossed the threshold.

THIS FILE IS THIN ON PURPOSE, and the thinness is what keeps T-16 in the team lane
(D-24). It holds NO arithmetic, NO threshold comparison and NO message text — all three
live in context-watch.py's `warn_for_agent`, which knows nothing about a hook. What is
here is only the cutover: read a payload, decide whether this agent is in scope, and put
whatever text the library returns on stderr.

WHY PostToolUse AND exit 2. The tool has ALREADY RUN, so nothing is blocked and the
hook's stderr reaches the running agent. PreToolUse plus exit 2 is EXCLUDED by operator
ruling: in PRE, exit 2 IS the refusal, and this warning advises. Evidence for the channel
is in notes/probe-hook-delivery-channel.md, and the one thing that note left open — that
the text reaches the model rather than being swallowed — was settled by direct observation
and recorded in notes/settled-Q-HOOKCTX.md.

THE MATCHER IS Write|Edit|Bash, AND THAT IS MEASURED, not assumed. Across the 25
most-recently-modified harness-orchestrator transcripts on this machine, 2026-08-22:
3359 tool_use events, of which Bash 2949, Write 235, Agent 117, Read 56, SendMessage 2.
Write|Edit|Bash covers 3184 of 3359 = 94.8 percent; Bash alone covers 87.8 percent. `Edit`
appears ZERO times and the dispatch tool is named `Agent`, not `Task`. A matcher that never
fires for an orchestrator is the green-and-incapable-of-red failure in hook form, so this
count is the evidence that it does fire.

IT NEVER RAISES AND NEVER BLOCKS, and fail-SILENT is correct HERE and only here. A payload
that is not JSON, a missing field, an unreadable transcript, an import failure — every one
exits 0 saying nothing. This hook fires on nearly every orchestrator tool call (2949 Bash
events in the sample above), so a warning path that crashes takes a live orchestrator's
tool call down with it. The instrument is advisory and the operator's own reading of
`context-watch.py` is the backstop, which is what makes silence acceptable — everywhere
else in this codebase a checker that cannot run must SAY so.

SOURCE OF IDENTITY: session_id plus agent_id, NEVER transcript_path. That field holds the
PARENT session's transcript, so using it would measure the main session on every
orchestrator tool call. Established in notes/probe-hook-payload-identity.md.
"""
import json
import os
import sys

IN_SCOPE_AGENT_TYPE = "harness-orchestrator"


def main():
    try:
        payload = json.loads(sys.stdin.read() or "{}")
        if not isinstance(payload, dict):
            return 0

        # Exit IMMEDIATELY for every other agent, before any file is touched. A lead or a
        # member crossing 200k is not this instrument's subject, and the cheap check comes
        # first because this runs on nearly every orchestrator tool call.
        if payload.get("agent_type") != IN_SCOPE_AGENT_TYPE:
            return 0

        session_id = payload.get("session_id")
        agent_id = payload.get("agent_id")
        cwd = payload.get("cwd")
        if not (session_id and agent_id and cwd):
            return 0

        bin_dir = os.path.dirname(os.path.abspath(__file__))
        if bin_dir not in sys.path:
            sys.path.insert(0, bin_dir)
        # Imported by file path, not by name: the module is `context-watch.py` and a
        # hyphen is not a legal identifier, so `import context_watch` would fail.
        import importlib.util
        spec = importlib.util.spec_from_file_location(
            "harness_context_watch", os.path.join(bin_dir, "context-watch.py"))
        cw = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(cw)

        projects_root = os.environ.get("HARNESS_PROJECTS_ROOT") or cw.DEFAULT_PROJECTS_ROOT
        text = cw.warn_for_agent(projects_root, session_id, agent_id, cwd,
                                 config_path=os.environ.get("HARNESS_CONFIG_PATH"))
        if not text:
            return 0

        # STDERR is the channel and stdout stays EMPTY. Exit 2 is what carries stderr back
        # to the agent in POST mode; it stops nothing, because the tool already ran.
        sys.stderr.write(text + "\n")
        return 2
    except Exception:
        # Deliberately bare, and deliberately silent — see the module docstring. Nothing is
        # printed because a traceback on an orchestrator's every tool call is worse than a
        # missed warning, and the tool remains runnable by hand.
        return 0


if __name__ == "__main__":
    sys.exit(main())
