#!/usr/bin/env python3
"""gh_issue_types.py must get these mappings and this capability classifier right — no gh
call, no network, offline.

FEAT-55 REQ-02/REQ-03/REQ-04/REQ-09. Covers, one assertion per value, never a loop-wide count:

  1. type_for_change_type(ct, {}) for every one of the twelve change_types — D-18: feature
     resolves to "Task" (a TASK SUB-ISSUE's role is an implementation task whatever its diff
     shape), not to "Feature". A parent's type comes from type_for_parent, never from here.
  2. type_for_nature(n, {}) for the three backlog natures.
  3. type_for_parent({}) == "Feature".
  4. An unrecognised change_type/nature raises UnknownWorkNature, never returns None.
  5. Overrides are keyed by CANONICAL TYPE NAME (D-12: exactly "Bug", "Feature", "Task",
     "parent") — never by a change_type string or a nature string.
  6. overrides_from_config(cfg) loads the github.issue_types map, dropping any key outside
     the four legal names.
  7. classify_capability(returncode, stdout)'s four discriminator cases: absent, available,
     query_failed (an errors array), and query_failed (unparseable output — never read as
     absent).
  8-10. The three gh invocation-argument builders: capability_query_args, node_id_args,
     apply_type_args.
  11. missing_types: which of a repo's required type names have no declared id.
  12. refusal_text: the operator-facing message when a repo has no matching type, keyed by
     the CANONICAL override key that would repair it.

    ./test-issue-types.py    -> exit 0 all pass, 1 otherwise
"""
import unit_support  # noqa: F401  (puts bin/ and tests/ on sys.path)
import sys

import gh_issue_types
from check_support import Checks

C = Checks()
check = C.check


def f_values(args):
    """Every value that follows a "-f" flag in a gh argv."""
    return [v for f, v in zip(args, args[1:]) if f == "-f"]


def check_unknown(label, fn):
    """fn("hovercraft", {}) must raise UnknownWorkNature naming the value and the missing map."""
    name = f"{label}('hovercraft', {{}}) raises UnknownWorkNature"
    try:
        fn("hovercraft", {})
    except gh_issue_types.UnknownWorkNature as e:
        check(name, True)
        check("...message contains the offending value 'hovercraft'", "hovercraft" in str(e), str(e))
        check("...message contains 'no issue type is mapped'", "no issue type is mapped" in str(e),
              str(e))
    except Exception as e:
        check(name, False, f"raised {type(e).__name__} instead: {e}")
    else:
        check(name, False, "returned instead of raising")


# ---------------------------------------------------------------------------------------------
# 1. type_for_change_type(ct, {}) — twelve separate assertions. feature -> "Task" is D-18.
# ---------------------------------------------------------------------------------------------
for _ct, _want, _note in [
        ("bugfix", "Bug", ""),
        ("feature", "Task", " (D-18: a task sub-issue, whatever its diff shape)"),
        ("logic", "Task", ""), ("api", "Task", ""), ("cross_module", "Task", ""),
        ("frontend", "Task", ""), ("ai_behavior", "Task", ""), ("docs", "Task", ""),
        ("config", "Task", ""), ("scaffolding", "Task", ""), ("infra", "Task", ""),
        ("ci", "Task", "")]:
    check(f"type_for_change_type: {_ct} -> {_want}{_note}",
          gh_issue_types.type_for_change_type(_ct, {}) == _want)

# ---------------------------------------------------------------------------------------------
# 2. type_for_nature(n, {}) — three separate assertions.
# ---------------------------------------------------------------------------------------------
for _n, _want in [("bug", "Bug"), ("chore", "Task"), ("enhancement", "Feature")]:
    check(f"type_for_nature: {_n} -> {_want}", gh_issue_types.type_for_nature(_n, {}) == _want)

# ---------------------------------------------------------------------------------------------
# 3. type_for_parent({}) == "Feature".
# ---------------------------------------------------------------------------------------------
check("type_for_parent: {} -> Feature",
      gh_issue_types.type_for_parent({}) == "Feature")

# ---------------------------------------------------------------------------------------------
# 4. Unrecognised change_type/nature raises UnknownWorkNature, message names the value AND
#    says no type is mapped. Assert the raise, not a returned None.
# ---------------------------------------------------------------------------------------------
check_unknown("type_for_change_type", gh_issue_types.type_for_change_type)
check_unknown("type_for_nature", gh_issue_types.type_for_nature)

# ---------------------------------------------------------------------------------------------
# 5. Overrides keyed by CANONICAL TYPE NAME (D-12: "Bug", "Feature", "Task", "parent" — no
#    change_type key, no backlog-nature key is an override key).
# ---------------------------------------------------------------------------------------------
check("override renames Bug",
      gh_issue_types.type_for_change_type("bugfix", {"Bug": "Defect"}) == "Defect")
check("override renaming Bug leaves Task alone (fall-through)",
      gh_issue_types.type_for_change_type("logic", {"Bug": "Defect"}) == "Task")
check("override renaming Task renames every change_type resolving to Task, including feature",
      gh_issue_types.type_for_change_type("feature", {"Task": "Story"}) == "Story")
check("override renames parent",
      gh_issue_types.type_for_parent({"parent": "Epic"}) == "Epic")
check("override renames Task via a nature",
      gh_issue_types.type_for_nature("chore", {"Task": "Maintenance"}) == "Maintenance")
check("a change_type string is NOT an override key and must be ignored",
      gh_issue_types.type_for_change_type("bugfix", {"bugfix": "Defect"}) == "Bug")

# ---------------------------------------------------------------------------------------------
# 6. overrides_from_config(cfg) — loads github.issue_types, drops any key outside the four
#    legal names.
# ---------------------------------------------------------------------------------------------
check("overrides_from_config({}) == {}",
      gh_issue_types.overrides_from_config({}) == {})
check("overrides_from_config({'github': {}}) == {}",
      gh_issue_types.overrides_from_config({"github": {}}) == {})
check("overrides_from_config({'github': {'issue_types': 'not-a-map'}}) == {}",
      gh_issue_types.overrides_from_config({"github": {"issue_types": "not-a-map"}}) == {})
check("overrides_from_config({'github': {'issue_types': {'Bug': 'Defect'}}}) == {'Bug': 'Defect'}",
      gh_issue_types.overrides_from_config(
          {"github": {"issue_types": {"Bug": "Defect"}}}) == {"Bug": "Defect"})
check("a key outside the four legal keys is dropped by the loader",
      gh_issue_types.overrides_from_config(
          {"github": {"issue_types": {"bugfix": "Defect"}}}) == {})

# ---------------------------------------------------------------------------------------------
# 7. classify_capability(returncode, stdout) -> (state, declared, message). Four discriminator
#    cases: this is what the whole feature rests on.
# ---------------------------------------------------------------------------------------------
_state_absent, _declared_absent, _message_absent = gh_issue_types.classify_capability(
    0, '{"data":{"repository":{"issueTypes":null}}}')
check("classify_capability: exit 0, null issueTypes -> state absent",
      _state_absent == "absent", _state_absent)
check("classify_capability: exit 0, null issueTypes -> declared {}",
      _declared_absent == {}, _declared_absent)
check("classify_capability: exit 0, null issueTypes -> message ''",
      _message_absent == "", repr(_message_absent))

_avail_stdout = ('{"data":{"repository":{"issueTypes":{"nodes":['
                 '{"id":"IT_1","name":"Bug"},{"id":"IT_2","name":"Task"}]}}}}')
_state_avail, _declared_avail, _message_avail = gh_issue_types.classify_capability(0, _avail_stdout)
check("classify_capability: exit 0, populated nodes -> state available",
      _state_avail == "available", _state_avail)
check("classify_capability: exit 0, populated nodes -> declared maps NAME to id",
      _declared_avail == {"Bug": "IT_1", "Task": "IT_2"}, _declared_avail)

_fail_stdout = ('{"data":{"repository":null},"errors":[{"type":"NOT_FOUND",'
                '"message":"Could not resolve to a Repository with the name x."}]}')
_state_fail, _declared_fail, _message_fail = gh_issue_types.classify_capability(1, _fail_stdout)
check("classify_capability: exit 1, top-level errors array -> state query_failed",
      _state_fail == "query_failed", _state_fail)
check("classify_capability: exit 1, top-level errors array -> declared {}",
      _declared_fail == {}, _declared_fail)
check("classify_capability: exit 1, top-level errors array -> message contains 'Could not resolve'",
      "Could not resolve" in _message_fail, repr(_message_fail))

_state_unparse = gh_issue_types.classify_capability(0, "")[0]
check("classify_capability: exit 0, unparseable stdout -> state query_failed, never absent",
      _state_unparse == "query_failed", _state_unparse)

# ---------------------------------------------------------------------------------------------
# 8. capability_query_args("owner/name")
# ---------------------------------------------------------------------------------------------
_cap_args = gh_issue_types.capability_query_args("owner/name")
check("capability_query_args: first two elements are api, graphql",
      _cap_args[:2] == ["api", "graphql"], _cap_args)
check("capability_query_args: contains -f owner=owner",
      "owner=owner" in f_values(_cap_args), _cap_args)
check("capability_query_args: contains -f name=name",
      "name=name" in f_values(_cap_args), _cap_args)
_cap_query = next((a for a in _cap_args if "issueTypes" in a), "")
check("capability_query_args: query element contains issueTypes(first:10)",
      "issueTypes(first:10)" in _cap_query, _cap_query)
check("capability_query_args: query element contains nodes",
      "nodes" in _cap_query, _cap_query)
check("capability_query_args: query element contains id",
      "id" in _cap_query, _cap_query)
check("capability_query_args: query element contains name",
      "name" in _cap_query, _cap_query)

# ---------------------------------------------------------------------------------------------
# 9. node_id_args("owner/name", 77)
# ---------------------------------------------------------------------------------------------
_node_args = gh_issue_types.node_id_args("owner/name", 77)
check("node_id_args: exact argv",
      _node_args == ["api", "repos/owner/name/issues/77", "--jq", ".node_id"], _node_args)

# ---------------------------------------------------------------------------------------------
# 10. apply_type_args("I_node", "IT_1")
# ---------------------------------------------------------------------------------------------
_apply_args = gh_issue_types.apply_type_args("I_node", "IT_1")
check("apply_type_args: starts api, graphql",
      _apply_args[:2] == ["api", "graphql"], _apply_args)
_apply_query = next((a for a in _apply_args if "updateIssue" in a), "")
check("apply_type_args: query element contains updateIssue",
      "updateIssue" in _apply_query, _apply_query)
check("apply_type_args: query element contains issueTypeId",
      "issueTypeId" in _apply_query, _apply_query)
check("apply_type_args: passes the node id as an -f value",
      any("I_node" in v for v in f_values(_apply_args)), _apply_args)
check("apply_type_args: passes the type id as an -f value",
      any("IT_1" in v for v in f_values(_apply_args)), _apply_args)

# ---------------------------------------------------------------------------------------------
# 11. missing_types(required, declared)
# ---------------------------------------------------------------------------------------------
check("missing_types(['Bug', 'Task'], {'Bug': 'IT_1'}) == ['Task']",
      gh_issue_types.missing_types(["Bug", "Task"], {"Bug": "IT_1"}) == ["Task"])
check("missing_types(['Bug'], {'Bug': 'IT_1'}) == []",
      gh_issue_types.missing_types(["Bug"], {"Bug": "IT_1"}) == [])

# ---------------------------------------------------------------------------------------------
# 12. refusal_text("owner/name", "Maintenance", "Task") — the third arg is the CANONICAL
#     override key that repairs it, never the change_type or nature that resolved to it.
# ---------------------------------------------------------------------------------------------
_refusal = gh_issue_types.refusal_text("owner/name", "Maintenance", "Task")
check("refusal_text: contains the type name 'Maintenance'",
      "Maintenance" in _refusal, _refusal)
check("refusal_text: contains 'github.issue_types.Task'",
      "github.issue_types.Task" in _refusal, _refusal)
check("refusal_text: contains the repo 'owner/name'",
      "owner/name" in _refusal, _refusal)

sys.exit(C.report())
