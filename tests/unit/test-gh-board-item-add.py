#!/usr/bin/env python3
"""gh_board.set_station adds an absent issue to the board before setting its station (#2181).

Every call to `factory_gh` is recorded, so the tests can check:
- the order: lookup, then an add only when the item is absent, then the field set;
- the exact arguments, including the canonical issue URL and the board's owner and number;
- that the returned or existing item id reaches the field write;
- that a GhError at each step becomes a BoardError naming the issue and the lowercase station, with no call after the failing step.

    ./test-gh-board-item-add.py    -> exit 0 all pass, 1 otherwise
"""
import os as _anchor_os, sys as _anchor_sys
_anchor_tests = _anchor_os.path.dirname(_anchor_os.path.abspath(__file__))
_anchor_root = _anchor_os.path.abspath(_anchor_os.path.join(_anchor_tests, "..", ".."))
_anchor_bin = _anchor_os.path.join(_anchor_root, ".claude", "skills", "harness", "bin")
_anchor_sys.path.insert(0, _anchor_bin)

import factory_gh  # noqa: E402
import gh_board  # noqa: E402

FAILURES = []
BOARD = {"owner": "acme", "number": 9, "station_field": "Status"}
REPO = "acme/widgets"
URL = "https://github.com/acme/widgets/issues/17"
_NAMES = ("issue_board_item_id", "project_item_add", "project_field_set")


def check(name, cond, detail=""):
    if cond:
        print(f"PASS  {name}")
    else:
        print(f"FAIL  {name}{(' — ' + detail) if detail else ''}")
        FAILURES.append(name)


def _error():
    return factory_gh.GhError([], 1, "", "boom", "simulated failure", REPO, "fake")


def _run(existing=None, fail_at=None):
    """Call set_station(BOARD, REPO, 17, "ready") against recording fakes.

    Returns the recorded calls and whatever was raised; the real functions are restored."""
    log = []

    def lookup(repo, number, board_number):
        log.append(("lookup", repo, number, board_number))
        if fail_at == "lookup":
            raise _error()
        return existing

    def add(owner, number, url):
        log.append(("add", owner, number, url))
        if fail_at == "add":
            raise _error()
        return "ITEM_ADDED"

    def field_set(owner, number, item_id, field, value):
        log.append(("set", owner, number, item_id, field, value))
        if fail_at == "set":
            raise _error()

    real = {name: getattr(gh_board.factory_gh, name) for name in _NAMES}
    for name, fake in zip(_NAMES, (lookup, add, field_set)):
        setattr(gh_board.factory_gh, name, fake)
    raised = None
    try:
        gh_board.set_station(BOARD, REPO, 17, "ready")
    except Exception as exc:  # noqa: BLE001 — the type is asserted by the caller
        raised = exc
    finally:
        for name, fn in real.items():
            setattr(gh_board.factory_gh, name, fn)
    return log, raised


def case_absent_item_is_added_then_set():
    log, raised = _run(existing=None)
    check("u.1 an absent item is looked up, added once with the canonical URL, then set",
          raised is None and log == [
              ("lookup", REPO, 17, 9),
              ("add", "acme", 9, URL),
              ("set", "acme", 9, "ITEM_ADDED", "Status", "Ready")],
          f"raised={raised!r} log={log}")


def case_present_item_is_never_added():
    log, raised = _run(existing="ITEM_EXISTING")
    check("u.2 an existing item is set with its own id and never re-added",
          raised is None and log == [
              ("lookup", REPO, 17, 9),
              ("set", "acme", 9, "ITEM_EXISTING", "Status", "Ready")],
          f"raised={raised!r} log={log}")


def case_each_failure_is_a_board_error():
    for step, existing, calls in (("lookup", None, ["lookup"]),
                                  ("add", None, ["lookup", "add"]),
                                  ("set", None, ["lookup", "add", "set"]),
                                  ("set", "ITEM_EXISTING", ["lookup", "set"])):
        log, raised = _run(existing=existing, fail_at=step)
        text = str(raised)
        check(f"u.3 a GhError at {step} (existing={existing!r}) is a BoardError naming the "
              "issue and the lowercase station, with no later call",
              isinstance(raised, gh_board.BoardError) and "#17" in text and "ready" in text
              and "Ready" not in text and [entry[0] for entry in log] == calls,
              f"raised={raised!r} log={log}")


def main():
    case_absent_item_is_added_then_set()
    case_present_item_is_never_added()
    case_each_failure_is_a_board_error()
    if FAILURES:
        print(f"\n{len(FAILURES)} FAILURE(S): {FAILURES}")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
