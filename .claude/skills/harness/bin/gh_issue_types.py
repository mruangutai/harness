"""Shared GitHub Issue Type primitives — mapping, response parsing, argv builders only
(FEAT-55, REQ-02/REQ-03/REQ-04). It EXECUTES NOTHING: no subprocess, no network. `gh-sync.py`
skips and exits 0 on an environmental failure, `factory_gh.py` raises `GhError` — two different
failure semantics a shared runner here would have to pick one of, so each caller keeps its own.

The mapping resolves an issue's TYPE from its ROLE (D-18), and there are three resolvers, each
answering for exactly one role: `type_for_change_type` for a task sub-issue (planned or
factory), `type_for_nature` for a backlog item, `type_for_parent` for a feature or factory
parent. No caller may resolve a parent through `type_for_change_type`.
"""
import json

DEFAULT_TYPE_BY_CHANGE_TYPE = {
    "bugfix": "Bug",
    "feature": "Task",
    "logic": "Task",
    "api": "Task",
    "cross_module": "Task",
    "frontend": "Task",
    "ai_behavior": "Task",
    "docs": "Task",
    "config": "Task",
    "scaffolding": "Task",
    "infra": "Task",
    "ci": "Task",
}

DEFAULT_TYPE_BY_NATURE = {"bug": "Bug", "chore": "Task", "enhancement": "Feature"}

PARENT_KEY = "parent"
DEFAULT_PARENT_TYPE = "Feature"

LEGAL_OVERRIDE_KEYS = ("Bug", "Feature", "Task", "parent")

CAPABILITY_QUERY = (
    "query($owner:String!,$name:String!){ repository(owner:$owner,name:$name){ "
    "issueTypes(first:10){ nodes { id name } } } }"
)

APPLY_TYPE_MUTATION = (
    "mutation($id:ID!,$type:ID!){ updateIssue(input:{id:$id,issueTypeId:$type}){ issue { id } } }"
)


class UnknownWorkNature(Exception):
    """Raised, never returned, when a change_type or nature has no mapped issue type."""


def _resolve(name, table, overrides):
    if name not in table:
        raise UnknownWorkNature(
            f"{name!r} is not a known change_type, so no issue type is mapped for it - "
            "add it to DEFAULT_TYPE_BY_CHANGE_TYPE or fix the plan"
        )
    default = table[name]
    override = overrides.get(default)
    if isinstance(override, str) and override:
        return override
    return default


def type_for_change_type(change_type, overrides):
    return _resolve(change_type, DEFAULT_TYPE_BY_CHANGE_TYPE, overrides)


def type_for_nature(nature, overrides):
    if nature not in DEFAULT_TYPE_BY_NATURE:
        raise UnknownWorkNature(
            f"{nature!r} is not a known change_type, so no issue type is mapped for it - "
            "add it to DEFAULT_TYPE_BY_CHANGE_TYPE or fix the plan"
        )
    default = DEFAULT_TYPE_BY_NATURE[nature]
    override = overrides.get(default)
    if isinstance(override, str) and override:
        return override
    return default


def type_for_parent(overrides):
    override = overrides.get(PARENT_KEY)
    if isinstance(override, str) and override:
        return override
    return DEFAULT_PARENT_TYPE


def overrides_from_config(cfg):
    block = cfg.get("github", {})
    if not isinstance(block, dict):
        return {}
    issue_types = block.get("issue_types")
    if not isinstance(issue_types, dict):
        return {}
    return {
        key: value
        for key, value in issue_types.items()
        if key in LEGAL_OVERRIDE_KEYS and isinstance(value, str) and value
    }


def capability_query_args(repo):
    owner, name = repo.split("/", 1)
    return [
        "api", "graphql",
        "-f", "query=" + CAPABILITY_QUERY,
        "-f", "owner=" + owner,
        "-f", "name=" + name,
    ]


def _capability_error(stdout):
    return ("query_failed", {}, stdout[:200])


def classify_capability(returncode, stdout):
    try:
        doc = json.loads(stdout)
    except (ValueError, TypeError) as exc:
        return ("query_failed", {}, str(exc))
    if not isinstance(doc, dict):
        return _capability_error(stdout)
    errors = doc.get("errors")
    if isinstance(errors, list) and errors:
        first = errors[0]
        message = first.get("message", "") if isinstance(first, dict) else str(first)
        return ("query_failed", {}, message)
    if returncode != 0:
        return _capability_error(stdout)
    repository = (doc.get("data") or {}).get("repository")
    if repository is None:
        return ("absent", {}, "")
    issue_types = repository.get("issueTypes")
    if issue_types is None:
        return ("absent", {}, "")
    if isinstance(issue_types, dict) and isinstance(issue_types.get("nodes"), list):
        nodes = issue_types["nodes"]
        declared = {
            node["name"]: node["id"]
            for node in nodes
            if isinstance(node, dict) and "name" in node and "id" in node
        }
        return ("available", declared, "")
    return _capability_error(stdout)


def node_id_args(repo, number):
    return ["api", f"repos/{repo}/issues/{number}", "--jq", ".node_id"]


def apply_type_args(node_id, type_id):
    return [
        "api", "graphql",
        "-f", "query=" + APPLY_TYPE_MUTATION,
        "-f", "id=" + node_id,
        "-f", "type=" + type_id,
    ]


def missing_types(required_names, declared):
    return sorted({name for name in required_names if name not in declared})


def refusal_text(repo, type_name, config_key):
    return (
        f"issue type {type_name!r} is not declared by {repo} - set "
        f"github.issue_types.{config_key} in .harness/harness.json to a type name this "
        "repository declares, or add the type to the repository"
    )
