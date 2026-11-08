#!/usr/bin/env python3
"""`gh-sync.py start-task` adds an issue that has no project item before setting its station (#2181).

The shared FAKE_GH_STATIONS is extended locally, and the shared helper is not edited:
- The by-issue item lookup answers "no item" for every number listed in ABSENT_ISSUES.
- `gh project item-add` returns `ADDED_<n>` for the issue its URL names.

Both GH_SYNC_GH and FACTORY_GH point at the same fake. No live GitHub is touched.

    ./test-gh-sync-board-add.py    -> exit 0 all pass, 1 otherwise
"""
import os as _anchor_os, sys as _anchor_sys
_anchor_tests = _anchor_os.path.dirname(_anchor_os.path.abspath(__file__))
_anchor_root = _anchor_os.path.abspath(_anchor_os.path.join(_anchor_tests, "..", ".."))
_anchor_bin = _anchor_os.path.join(_anchor_root, ".claude", "skills", "harness", "bin")
_anchor_sys.path.insert(0, _anchor_bin)
_anchor_sys.path.insert(0, _anchor_tests)
import os
import tempfile

from gh_sync_support import FAKE_GH_STATIONS, calls, check, install_gh, report, run, stage_station

_LOOKUP = '  *"projectItems(first: 100)"*)\n'
_ABSENT_AND_ADD = r'''  *"projectItems(first: 100)"*)
    num=$(echo "$*" | grep -oE 'number=[0-9]+' | tail -1 | grep -oE '[0-9]+')
    case " $ABSENT_ISSUES " in
      *" $num "*)
        printf '{"data":{"repository":{"issue":{"projectItems":{"totalCount":0,"nodes":[]}}}}}\n'
        exit 0 ;;
    esac
    printf '{"data":{"repository":{"issue":{"projectItems":{"totalCount":1,"nodes":[{"id":"ITEM_%s","project":{"number":3}}]}}}}}\n' "$num"
    exit 0 ;;
  *"project item-add"*)
    num=$(echo "$*" | grep -oE 'issues/[0-9]+' | head -1 | grep -oE '[0-9]+')
    printf '{"id":"ADDED_%s"}\n' "$num"
    exit 0 ;;
'''


def _absent_fake():
    """FAKE_GH_STATIONS with its by-issue lookup branch replaced, end to end, by the one above."""
    start = FAKE_GH_STATIONS.index(_LOOKUP)
    end = FAKE_GH_STATIONS.index("    exit 0 ;;\n", start) + len("    exit 0 ;;\n")
    return FAKE_GH_STATIONS[:start] + _ABSENT_AND_ADD + FAKE_GH_STATIONS[end:]


FAKE_GH_ABSENT = _absent_fake()


def _start_task(absent):
    """Run start-task T-02 (own #326, parent #40). Returns (exit, output, call log)."""
    with tempfile.TemporaryDirectory() as tmp:
        install_gh(tmp, FAKE_GH_ABSENT)
        feat = stage_station(tmp, "FEAT-89-board-add",
                             [("T-01", "done"), ("T-02", "building"), ("T-03", "ready")],
                             issues={"T-01": 41, "T-02": 326}, parent=40)
        gh = os.path.join(tmp, "gh")
        result = run(["start-task", feat, "T-02"], tmp,
                     {"FACTORY_GH": gh, "ABSENT_ISSUES": " ".join(map(str, absent))})
        return result.returncode, result.stdout + result.stderr, calls(tmp)


def _index(log, *needles):
    return next((i for i, line in enumerate(log) if all(n in line for n in needles)), None)


def case_absent_own_card_is_added_then_set():
    code, out, log = _start_task(absent=[326])
    adds = [line for line in log if "project item-add" in line]
    lookup = _index(log, "projectItems(first: 100)", "number=326")
    add = _index(log, "project item-add 3", "--owner mruangutai",
                 "--url https://github.com/implentio/fake/issues/326")
    edit = _index(log, "project item-edit", "--id ADDED_326", "OPT_BUILDING")
    check("a.1 start-task exits 0 for an issue with no project item", code == 0, out)
    check("a.2 the absent card is looked up, added exactly once, then set to Building with "
          "the returned item id",
          len(adds) == 1 and None not in (lookup, add, edit) and lookup < add < edit,
          f"lookup={lookup} add={add} edit={edit} adds={adds}")
    check("a.3 the present parent card is set with its own item id and never added",
          _index(log, "project item-edit", "--id ITEM_40", "OPT_BUILDING") is not None
          and not any("issues/40" in line for line in adds), str(adds))


def case_present_cards_are_never_added():
    code, out, log = _start_task(absent=[])
    edits = [line for line in log if "project item-edit" in line]
    check("p.1 with both cards on the board, start-task exits 0 and adds nothing",
          code == 0 and not any("project item-add" in line for line in log), out)
    check("p.2 both present cards are set to Building with their own item ids",
          _index(edits, "--id ITEM_326", "OPT_BUILDING") is not None
          and _index(edits, "--id ITEM_40", "OPT_BUILDING") is not None, str(edits))


def main():
    case_absent_own_card_is_added_then_set()
    case_present_cards_are_never_added()
    return report()


if __name__ == "__main__":
    raise SystemExit(main())
