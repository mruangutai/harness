#!/usr/bin/env python3
"""The panel finding identity helper (FEAT-45 T-09, D-05).

The ONE place a panel finding's identity is computed, so the validator lead, pm and
check-state.sh cannot disagree about what a finding is called. python3 stdlib only, no
third-party import.

WHY A CONTENT HASH AND NOT A SEQUENTIAL ID. A sequential id is assigned per run, so a
re-run renumbers and a risk acceptance recorded against finding 2 silently starts covering
whatever is second next time. A content hash keeps an unchanged finding's id stable
across runs, so an acceptance survives a re-run, and gives a REWORDED finding a NEW id, so
the old ruling stops applying and check-state.sh reports it as a stale risk acceptance.
That failure direction is deliberate and it is closed, not open.
"""
import argparse
import hashlib
import re
import sys

_WHITESPACE_RUN = re.compile(r"\s+")


def normalize_summary(summary):
    """Lowercase, collapse every run of whitespace to one space, strip the ends."""
    return _WHITESPACE_RUN.sub(" ", summary.lower()).strip()


def finding_id(reader, summary):
    """PF- followed by the first 32 characters of sha256(reader + '\\n' + normalized). Length 35."""
    normalized = normalize_summary(summary)
    digest_input = f"{reader}\n{normalized}".encode("utf-8")
    digest = hashlib.sha256(digest_input).hexdigest()
    return f"PF-{digest[:32]}"


def _cli_id(reader, summary):
    if not reader:
        print("panel_findings.py: --reader must not be empty", file=sys.stderr)
        return 2
    if not normalize_summary(summary):
        print("panel_findings.py: --summary must not be empty or whitespace-only", file=sys.stderr)
        return 2
    print(finding_id(reader, summary))
    return 0


def main(argv=None):
    parser = argparse.ArgumentParser(prog="panel_findings.py")
    subparsers = parser.add_subparsers(dest="command", required=True)
    id_parser = subparsers.add_parser("id", help="print the identity of a panel finding")
    id_parser.add_argument("--reader", required=True)
    id_parser.add_argument("--summary", required=True)

    args = parser.parse_args(argv)
    if args.command == "id":
        return _cli_id(args.reader, args.summary)
    return 2


if __name__ == "__main__":
    sys.exit(main())
