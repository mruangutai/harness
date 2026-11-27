"""The provider projection of the persona digest schemas (BUG-2565 D-01).

schemas/digest/<persona>.json (+ common.json) are the one copy of the live digest contract;
digest_schema.py validates a returned object against them in full. Each harness agent's
frontmatter `output:` carries the provider projection built here (gen-agent-output.py writes
it, check-omp-port.py proves it current), so the provider shapes a child's yield before the
validator sees it. A provider needs one self-contained tree, so every external `$ref` (file +
JSON pointer) is inlined and the result is projected to the structural subset a provider
schema can carry:

  type (object, array, string, integer, number, boolean, null), properties, required,
  additionalProperties: false, items, enum, and nested nullable anyOf.

Every array declares its `items`, and every property and element schema declares a type, an
enum or an anyOf: OpenAI strict mode rejects the whole tool on one untyped node or one array
without items, so such a schema file is refused here, naming its file#pointer.

What the projection DROPS only ever narrows a value the shape already admits: annotations,
string/number/array bounds, and the if/then/else conditionals (with an allOf that holds only
conditionals, and an anyOf whose branches only require keys). digest_schema.py still enforces
every one of them on the yield. `const` is carried as a one-value `enum`. Any other keyword is
refused rather than guessed, so a provider schema looser in SHAPE than the contract is never
produced. This is a rule-for-rule port of the TypeScript loader it replaces
(`git show 104252db:.omp/extensions/digest-schema.ts`).
"""
import copy
import os
import re
from urllib.parse import unquote

import digest_schema
from artifact_accessors import ArtifactAccessError, load_json_mapping

TYPES = frozenset(("object", "array", "string", "integer", "number", "boolean", "null"))
ANNOTATIONS = frozenset(("$schema", "$id", "$comment", "$defs", "title", "description",
                         "examples", "default", "deprecated", "readOnly", "writeOnly"))
BOUNDS = frozenset(("pattern", "format", "minLength", "maxLength", "minimum", "maximum",
                    "exclusiveMinimum", "exclusiveMaximum", "multipleOf", "minItems", "maxItems",
                    "uniqueItems", "minProperties", "maxProperties"))
CONDITIONALS = frozenset(("if", "then", "else"))
DROPPED = ANNOTATIONS | BOUNDS | CONDITIONALS
SCHEME = re.compile(r"[A-Za-z][A-Za-z0-9+.-]*:")
INDEX = re.compile(r"0|[1-9][0-9]*")
# The schema directory relative to a checkout root, for callers that check a root other than
# this script's own (digest_schema.SCHEMA_DIR is that own checkout's absolute path).
SCHEMA_RELPATH = ".claude/skills/harness/schemas/digest"


class ProjectionError(Exception):
    """A persona schema that cannot be projected; the message names file and JSON pointer."""


class _Loader:
    def __init__(self, root):
        self.root = root
        self.documents = {}

    def fail(self, loc, message):
        file, pointer = loc
        raise ProjectionError(f"digest schema {os.path.relpath(file, self.root)}#{pointer}: {message}")

    def inside(self, path):
        rel = os.path.relpath(path, self.root)
        return rel != "." and not rel.startswith("..") and not os.path.isabs(rel)

    def document(self, file, from_loc):
        if file in self.documents:
            return self.documents[file]
        at = from_loc or (file, "")
        if not self.inside(file):
            self.fail(at, f"reference escapes the schema directory: {file}")
        try:
            real = os.path.realpath(file, strict=True)
        except OSError as error:
            self.fail(at, f"cannot read {file}: {error.strerror}")
        if not self.inside(real):
            self.fail(at, f"reference escapes the schema directory: {file} -> {real}")
        try:
            parsed = load_json_mapping(real)
        except ArtifactAccessError as error:
            self.fail((file, ""), f"malformed JSON: {error}")
        self.documents[file] = parsed
        return parsed

    def resolve_ref(self, ref, loc):
        """One `$ref` to (node, its file#pointer location). Only relative file references and
        JSON-pointer fragments resolve; a URI with a scheme or an absolute path is refused."""
        if not isinstance(ref, str):
            self.fail(loc, f"$ref must be a string, got {ref!r}")
        file_part, _, fragment = ref.partition("#")
        if SCHEME.match(file_part) or os.path.isabs(file_part):
            self.fail(loc, f"unsupported reference {ref!r} — only relative file references resolve")
        if fragment and not fragment.startswith("/"):
            self.fail(loc, f"unsupported reference {ref!r} — the fragment must be a JSON pointer")
        file = os.path.normpath(os.path.join(os.path.dirname(loc[0]), file_part)) if file_part else loc[0]
        node = self.document(file, loc)
        for encoded in (fragment[1:].split("/") if fragment else []):
            try:
                token = unquote(encoded, errors="strict").replace("~1", "/").replace("~0", "~")
            except UnicodeDecodeError:
                self.fail(loc, f"unresolved reference {ref!r}: malformed pointer token")
            if isinstance(node, list) and INDEX.fullmatch(token) and int(token) < len(node):
                node = node[int(token)]
            elif isinstance(node, dict) and token in node:
                node = node[token]
            else:
                self.fail(loc, f"unresolved reference {ref!r}: no {token!r} in "
                               f"{os.path.relpath(file, self.root)}")
        return node, (file, fragment)

    def typed(self, child, child_loc, what, stack):
        """A property or array element must say what it is: OpenAI strict refuses an untyped
        node (`{}`, `true`, one that only carried dropped bounds), so one is never emitted."""
        if not isinstance(child, dict):
            self.fail(child_loc, f"{what} must be a typed schema, got {child!r}")
        projected = self.project(child, child_loc, stack)
        if not {"type", "enum", "anyOf"} & projected.keys():
            self.fail(child_loc, f"{what} admits any value — it must declare a type, an enum or an anyOf")
        return projected

    def project(self, node, loc, stack):
        if not isinstance(node, dict):
            self.fail(loc, f"a schema must be an object, got {node!r}")
        if "$ref" in node:
            siblings = [key for key in node if key != "$ref" and key not in ANNOTATIONS]
            if siblings:
                self.fail(loc, f"unsupported keyword(s) beside $ref: {', '.join(siblings)}")
            target, target_loc = self.resolve_ref(node["$ref"], loc)
            key = f"{target_loc[0]}#{target_loc[1]}"
            if key in stack:
                chain = " -> ".join(os.path.relpath(entry, self.root) for entry in [*stack, key])
                self.fail(loc, f"reference cycle: {chain}")
            return self.project(target, target_loc, [*stack, key])

        def at(*tokens):
            escaped = (token.replace("~", "~0").replace("/", "~1") for token in tokens)
            return loc[0], loc[1] + "".join("/" + token for token in escaped)

        out = {}
        for keyword, value in node.items():
            if keyword in DROPPED:
                continue
            if keyword == "type":
                names = value if isinstance(value, list) else [value]
                if not names or any(not isinstance(name, str) or name not in TYPES for name in names):
                    self.fail(at(keyword), f"unsupported type {value!r}")
                out["type"] = list(value) if isinstance(value, list) else value
            elif keyword == "properties":
                if not isinstance(value, dict):
                    self.fail(at(keyword), "properties must be an object")
                out["properties"] = {name: self.typed(child, at(keyword, name), "a property", stack)
                                     for name, child in value.items()}
            elif keyword == "required":
                if not isinstance(value, list) or any(not isinstance(name, str) for name in value):
                    self.fail(at(keyword), "required must be an array of strings")
                out["required"] = list(value)
            elif keyword == "additionalProperties":
                if value is not False:
                    self.fail(at(keyword), f"unsupported additionalProperties {value!r} — only false projects")
                out["additionalProperties"] = False
            elif keyword == "items":
                out["items"] = self.typed(value, at(keyword), "array items", stack)
            elif keyword == "enum":
                if not isinstance(value, list) or not value:
                    self.fail(at(keyword), "enum must be a non-empty array")
                if "const" in node:
                    self.fail(at(keyword), "enum and const together are unsupported")
                out["enum"] = copy.deepcopy(value)
            elif keyword == "const":
                out["enum"] = [copy.deepcopy(value)]
            elif keyword == "allOf":
                # Only a list of conditionals (if/then/else) is a pure value constraint to drop.
                if not isinstance(value, list) or any(
                        not isinstance(branch, dict) or any(key not in CONDITIONALS | ANNOTATIONS for key in branch)
                        for branch in value):
                    self.fail(at(keyword), "unsupported allOf — only a list of if/then/else conditionals is dropped")
            elif keyword == "anyOf":
                if not isinstance(value, list) or not value:
                    self.fail(at(keyword), "anyOf must be a non-empty array")
                if not loc[1] and not stack:
                    self.fail(at(keyword), "anyOf at the schema root is unsupported")
                branches = [self.project(branch, at(keyword, str(index)), stack)
                            for index, branch in enumerate(value)]
                # Branches that only require keys constrain the enclosing object; they are not
                # alternative shapes. Alternatives must each carry a type or an enum.
                if all(set(branch) <= {"required"} for branch in branches):
                    continue
                if any(not {"type", "enum"} & branch.keys() for branch in branches):
                    self.fail(at(keyword), "unsupported anyOf — every alternative must carry a type or an enum")
                out["anyOf"] = branches
            else:
                self.fail(at(keyword), f"unsupported keyword {keyword!r}")
        types = out.get("type", [])
        if "array" in (types if isinstance(types, list) else [types]) and "items" not in out:
            self.fail(loc, "array schema without items — every array must declare its element schema")
        return out


def provider_bundle(persona, directory=digest_schema.SCHEMA_DIR):
    """The ref-free, projected provider schema for `persona`, read from the schema files on
    every call. Nothing is cached across calls (#2328): a regenerated contract is read now."""
    try:
        canonical = digest_schema.canonical_persona(persona)
    except digest_schema.DigestSchemaError as error:
        raise ProjectionError(str(error)) from error
    try:
        root = os.path.realpath(directory, strict=True)
    except OSError as error:
        raise ProjectionError(f"digest schema directory {directory} cannot be resolved: {error.strerror}") from error
    loader = _Loader(root)
    file = os.path.join(root, f"{canonical}.json")
    return loader.project(loader.document(file, None), (file, ""), [])
