// FEAT-1928: the ONE in-process provider adapter for the persona digest schemas.
//
// bin/digest-schemas/<persona>.json (+ common.json) are the single copy of the live digest
// contract; digest_schema.py validates a returned object against them in full. The task hook
// hands the SAME files to OMP as the dispatch's strict `outputSchema`, so the provider shapes
// the child's yield before the validator ever sees it. OMP needs one self-contained tree, so
// this module reads the files synchronously, inlines every external `$ref` (file + JSON
// pointer), and projects the result to the structural subset a provider schema can carry:
//
//   type (object, array, string, integer, number, boolean, null), properties, required,
//   additionalProperties: false, items, enum, and nested nullable anyOf.
//
// Every array declares its `items`, and every property and element schema declares a type,
// an enum or an anyOf: OpenAI strict mode rejects the whole tool on one untyped node or one
// array without items, so such a schema file is refused here, naming its file#pointer.
//
// What the projection DROPS only ever narrows a value the shape already admits — annotations,
// string/number/array bounds, and the if/then/else conditionals (with an allOf that holds only
// conditionals, and an anyOf whose branches only require keys). digest_schema.py still enforces
// every one of them on the yield. `const` is carried as a one-value `enum`. Anything else that
// survives is a keyword this projection does not understand, and loading refuses it rather
// than guessing: a provider schema looser in SHAPE than the contract is never produced.
//
// Every field and required set comes from the JSON files; nothing here restates them. The
// persona table below mirrors digest_schema.PERSONAS / ALIASES, and the owning unit test
// compares the two tables so they cannot drift.

import { readFileSync, realpathSync } from "node:fs";
import { dirname, isAbsolute, join, relative, resolve } from "node:path";

export const DIGEST_PERSONAS: readonly string[] = Object.freeze([
  "harness-ai-dev", "harness-backend-dev", "harness-code-reviewer",
  "harness-data-engineer", "harness-dev-ops", "harness-documentor", "harness-eng-lead",
  "harness-frontend-dev", "harness-orchestrator", "harness-pm", "harness-product-lead",
  "harness-qa", "harness-security-reviewer", "harness-ui-reviewer",
  "harness-validator-lead", "harness-visual-designer",
]);

export const DIGEST_PERSONA_ALIASES: Readonly<Record<string, string>> = Object.freeze({
  "main-session": "harness-backend-dev",
  dev: "harness-backend-dev",
  reviewer: "harness-code-reviewer",
  lead: "harness-eng-lead",
});

// Every failure a load can meet — unknown persona, unreadable or malformed file, unresolved,
// cyclic or escaping reference, unsupported keyword. The message names the file and the JSON
// pointer at fault. A programming defect is not wrapped and surfaces as itself.
export class DigestSchemaBundleError extends Error {
  constructor(message: string, options?: { cause?: unknown }) {
    super(message, options);
    this.name = "DigestSchemaBundleError";
  }
}

export type DigestSchema = { readonly [keyword: string]: unknown };

// digest_schema.canonical_persona, same order: a persona itself, an alias, `harness-<name>`.
export function canonicalDigestPersona(name: string): string {
  if (DIGEST_PERSONAS.includes(name)) return name;
  if (Object.hasOwn(DIGEST_PERSONA_ALIASES, name)) return DIGEST_PERSONA_ALIASES[name];
  const prefixed = `harness-${name}`;
  if (DIGEST_PERSONAS.includes(prefixed)) return prefixed;
  throw new DigestSchemaBundleError(
    `unknown persona ${JSON.stringify(name)} — no digest schema resolves it; expected one of `
      + `${DIGEST_PERSONAS.join(", ")} or an alias in ${Object.keys(DIGEST_PERSONA_ALIASES).sort().join(", ")}.`,
  );
}

const TYPES: Record<string, true> = {
  object: true, array: true, string: true, integer: true, number: true, boolean: true, null: true,
};
// Keywords the projection drops, by why dropping is safe: an annotation carries no
// constraint; a bound or a conditional only narrows a value the kept shape admits.
const DROPPED: Record<string, "annotation" | "bound" | "conditional"> = {
  $schema: "annotation", $id: "annotation", $comment: "annotation", $defs: "annotation",
  title: "annotation", description: "annotation", examples: "annotation", default: "annotation",
  deprecated: "annotation", readOnly: "annotation", writeOnly: "annotation",
  pattern: "bound", format: "bound", minLength: "bound", maxLength: "bound", minimum: "bound",
  maximum: "bound", exclusiveMinimum: "bound", exclusiveMaximum: "bound", multipleOf: "bound",
  minItems: "bound", maxItems: "bound", uniqueItems: "bound", minProperties: "bound",
  maxProperties: "bound",
  if: "conditional", then: "conditional", else: "conditional",
};

type Loc = { file: string; pointer: string };
type Json = unknown;

function isPlainObject(value: unknown): value is Record<string, Json> {
  return typeof value === "object" && value !== null && !Array.isArray(value);
}

function isErrno(error: unknown): error is NodeJS.ErrnoException {
  return error instanceof Error && typeof (error as NodeJS.ErrnoException).code === "string";
}

class BundleLoader {
  readonly #root: string;
  readonly #documents = new Map<string, Json>();

  constructor(root: string) {
    this.#root = root;
  }

  #fail(loc: Loc, message: string, cause?: unknown): never {
    const where = `${relative(this.#root, loc.file) || loc.file}#${loc.pointer}`;
    throw new DigestSchemaBundleError(`digest schema ${where}: ${message}`, { cause });
  }

  #inside(path: string): boolean {
    const rel = relative(this.#root, path);
    return rel !== "" && !rel.startsWith("..") && !isAbsolute(rel);
  }

  document(file: string, from: Loc | undefined): Json {
    const cached = this.#documents.get(file);
    if (cached !== undefined) return cached;
    const at: Loc = from ?? { file, pointer: "" };
    if (!this.#inside(file)) this.#fail(at, `reference escapes the schema directory: ${file}`);
    let real: string;
    let raw: string;
    try {
      real = realpathSync(file);
      raw = readFileSync(real, "utf8");
    } catch (error) {
      if (!isErrno(error)) throw error;
      return this.#fail(at, `cannot read ${file} (${error.code}): ${error.message}`, error);
    }
    if (!this.#inside(real)) this.#fail(at, `reference escapes the schema directory: ${file} -> ${real}`);
    let parsed: Json;
    try {
      parsed = JSON.parse(raw);
    } catch (error) {
      if (!(error instanceof SyntaxError)) throw error;
      return this.#fail({ file, pointer: "" }, `malformed JSON: ${error.message}`, error);
    }
    this.#documents.set(file, parsed);
    return parsed;
  }

  // One `$ref` to (document, node). Only relative file references and JSON-pointer
  // fragments are supported; a URI with a scheme or an absolute path is refused.
  resolveRef(ref: unknown, loc: Loc): { node: Json; loc: Loc } {
    if (typeof ref !== "string") this.#fail(loc, `$ref must be a string, got ${JSON.stringify(ref)}`);
    const hash = ref.indexOf("#");
    const filePart = hash < 0 ? ref : ref.slice(0, hash);
    const fragment = hash < 0 ? "" : ref.slice(hash + 1);
    if (/^[A-Za-z][A-Za-z0-9+.-]*:/.test(filePart) || isAbsolute(filePart)) {
      this.#fail(loc, `unsupported reference ${JSON.stringify(ref)} — only relative file references resolve`);
    }
    if (fragment !== "" && !fragment.startsWith("/")) {
      this.#fail(loc, `unsupported reference ${JSON.stringify(ref)} — the fragment must be a JSON pointer`);
    }
    const file = filePart ? resolve(dirname(loc.file), filePart) : loc.file;
    let node = this.document(file, loc);
    const tokens = fragment === "" ? [] : fragment.slice(1).split("/");
    for (const encoded of tokens) {
      let token: string;
      try {
        token = decodeURIComponent(encoded).replace(/~1/g, "/").replace(/~0/g, "~");
      } catch (error) {
        if (!(error instanceof URIError)) throw error;
        return this.#fail(loc, `unresolved reference ${JSON.stringify(ref)}: malformed pointer token`, error);
      }
      if (Array.isArray(node) && /^(0|[1-9][0-9]*)$/.test(token) && Number(token) < node.length) {
        node = node[Number(token)];
      } else if (isPlainObject(node) && Object.hasOwn(node, token)) {
        node = node[token];
      } else {
        this.#fail(loc, `unresolved reference ${JSON.stringify(ref)}: no ${JSON.stringify(token)} in ${relative(this.#root, file)}`);
      }
    }
    return { node, loc: { file, pointer: fragment } };
  }

  project(node: Json, loc: Loc, stack: readonly string[]): Record<string, unknown> {
    if (!isPlainObject(node)) this.#fail(loc, `a schema must be an object, got ${JSON.stringify(node)}`);
    if (Object.hasOwn(node, "$ref")) {
      const siblings = Object.keys(node).filter((key) => key !== "$ref" && DROPPED[key] !== "annotation");
      if (siblings.length) {
        this.#fail(loc, `unsupported keyword(s) beside $ref: ${siblings.join(", ")}`);
      }
      const target = this.resolveRef(node.$ref, loc);
      const key = `${target.loc.file}#${target.loc.pointer}`;
      if (stack.includes(key)) {
        this.#fail(loc, `reference cycle: ${[...stack, key].map((entry) => relative(this.#root, entry)).join(" -> ")}`);
      }
      return this.project(target.node, target.loc, [...stack, key]);
    }
    const at = (...tokens: string[]): Loc => ({
      file: loc.file,
      pointer: `${loc.pointer}${tokens.map((token) => `/${token.replace(/~/g, "~0").replace(/\//g, "~1")}`).join("")}`,
    });
    // A property or an array element must say what it is. OpenAI strict refuses an untyped
    // node (`{}`, `true`, one that only carried dropped bounds), so one is never emitted.
    const typed = (child: Json, childLoc: Loc, what: string): Record<string, unknown> => {
      if (!isPlainObject(child)) this.#fail(childLoc, `${what} must be a typed schema, got ${JSON.stringify(child)}`);
      const projected = this.project(child, childLoc, stack);
      if (!("type" in projected || "enum" in projected || "anyOf" in projected)) {
        this.#fail(childLoc, `${what} admits any value — it must declare a type, an enum or an anyOf`);
      }
      return projected;
    };
    const out: Record<string, unknown> = {};
    for (const [keyword, value] of Object.entries(node)) {
      if (Object.hasOwn(DROPPED, keyword)) continue;
      switch (keyword) {
        case "type": {
          const names = Array.isArray(value) ? value : [value];
          if (!names.length || names.some((name) => typeof name !== "string" || !Object.hasOwn(TYPES, name))) {
            this.#fail(at(keyword), `unsupported type ${JSON.stringify(value)}`);
          }
          out.type = Array.isArray(value) ? [...value] : value;
          break;
        }
        case "properties": {
          if (!isPlainObject(value)) this.#fail(at(keyword), "properties must be an object");
          out.properties = Object.fromEntries(Object.entries(value).map(([name, child]) =>
            [name, typed(child, at(keyword, name), "a property")]));
          break;
        }
        case "required": {
          if (!Array.isArray(value) || value.some((name) => typeof name !== "string")) {
            this.#fail(at(keyword), "required must be an array of strings");
          }
          out.required = [...value];
          break;
        }
        case "additionalProperties": {
          if (value !== false) {
            this.#fail(at(keyword), `unsupported additionalProperties ${JSON.stringify(value)} — only false projects`);
          }
          out.additionalProperties = false;
          break;
        }
        case "items": {
          out.items = typed(value, at(keyword), "array items");
          break;
        }
        case "enum": {
          if (!Array.isArray(value) || !value.length) this.#fail(at(keyword), "enum must be a non-empty array");
          if (Object.hasOwn(node, "const")) this.#fail(at(keyword), "enum and const together are unsupported");
          out.enum = structuredClone(value);
          break;
        }
        case "const": {
          out.enum = [structuredClone(value)];
          break;
        }
        case "allOf": {
          // Only a list of conditionals (if/then/else) is a pure value constraint to drop.
          if (!Array.isArray(value)
            || value.some((branch) => !isPlainObject(branch)
              || Object.keys(branch).some((key) => DROPPED[key] !== "conditional" && DROPPED[key] !== "annotation"))) {
            this.#fail(at(keyword), "unsupported allOf — only a list of if/then/else conditionals is dropped");
          }
          break;
        }
        case "anyOf": {
          if (!Array.isArray(value) || !value.length) this.#fail(at(keyword), "anyOf must be a non-empty array");
          if (!loc.pointer && !stack.length) this.#fail(at(keyword), "anyOf at the schema root is unsupported");
          const branches = value.map((branch, index) => this.project(branch, at(keyword, String(index)), stack));
          // Branches that only require keys constrain the enclosing object; they are not
          // alternative shapes. Alternatives must each carry a type or an enum.
          const shaped = branches.filter((branch) => "type" in branch || "enum" in branch);
          const requireOnly = branches.every((branch) => Object.keys(branch).every((key) => key === "required"));
          if (requireOnly) break;
          if (shaped.length !== branches.length) {
            this.#fail(at(keyword), "unsupported anyOf — every alternative must carry a type or an enum");
          }
          out.anyOf = branches;
          break;
        }
        default:
          this.#fail(at(keyword), `unsupported keyword ${JSON.stringify(keyword)}`);
      }
    }
    const types = out.type === undefined ? [] : Array.isArray(out.type) ? out.type : [out.type];
    if (types.includes("array") && out.items === undefined) {
      this.#fail(loc, "array schema without items — every array must declare its element schema");
    }
    return out;
  }
}

function deepFreeze<T>(value: T): T {
  if (value && typeof value === "object") {
    Object.values(value as Record<string, unknown>).forEach(deepFreeze);
    Object.freeze(value);
  }
  return value;
}

const BUNDLES = new Map<string, DigestSchema>();

// The ref-free, projected strict schema for `persona`, loaded once per canonical schema
// directory and canonical persona for the life of the process. A failed load is not cached.
export function loadDigestSchemaBundle(schemaDir: string, persona: string): DigestSchema {
  const canonical = canonicalDigestPersona(persona);
  let root: string;
  try {
    root = realpathSync(schemaDir);
  } catch (error) {
    if (!isErrno(error)) throw error;
    throw new DigestSchemaBundleError(
      `digest schema directory ${schemaDir} cannot be resolved (${error.code}): ${error.message}`, { cause: error });
  }
  const key = `${root}\0${canonical}`;
  const cached = BUNDLES.get(key);
  if (cached) return cached;
  const loader = new BundleLoader(root);
  const file = join(root, `${canonical}.json`);
  const bundle = deepFreeze(loader.project(loader.document(file, undefined), { file, pointer: "" }, []));
  BUNDLES.set(key, bundle);
  return bundle;
}

// OMP loads every *.ts directly under .omp/extensions as an extension and reports one that
// exports no factory as a load error. This module is a library of harness-hooks.ts and
// registers nothing of its own.
export default function digestSchemaExtension(_pi: unknown): void {}
