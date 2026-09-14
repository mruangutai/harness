# Artifact paths — where each persona's durable artifact goes

Read this before your first feature-directory write of a run. The rule lives in `harness-handoff`:
your artifact goes to the per-feature path your persona already owns, never to a path a dispatch
invents for you. This is the table, the root-resolve step, and the receipt fallback. Evidence and
history: DEC-214, issue #216.

## Resolve the root first

Every feature-directory write is prefixed by `<HARNESS_FEATURE_TREE_ROOT>`. Before your first one,
resolve it:

```
python3 <HARNESS_CONTROL_PLANE_ROOT>/.agents/skills/harness/bin/inflight_registry.py feature-root --feature <FEAT>
```

If your persona holds no shell, do not run that command. Your dispatcher supplies
`HARNESS-FEATURE-TREE-ROOT: <absolute path>` in the dispatch; dispatch-guard.py refuses its absence
at exit 2. If it is absent anyway, return `VERDICT: BLOCKED`.

## Check your own domain FIRST, and use what you already own

| Persona | Owns, under `<HARNESS_FEATURE_TREE_ROOT>/.harness/<repo>/features/<FEAT>/` |
|---|---|
| pm | `notes/research-*.md`, `notes/uat-*.md` |
| qa | `notes/qa-*.md` |
| each reviewer (code, security, ui) | `notes/review-<self>-*.md` |
| visual designer | `notes/mockups/`, `notes/prototypes/` |
| lead | `runs/<run-id>/digest.md` — the durable digest `validate-digest.py` checks (DEC-156) |

**If you own such a path, your artifact goes there and you write no receipt.** A dispatch that names
a receipt path for you does not override this — check-domain.py will deny the write, correctly
(#216).

## The receipt — fallback for the six who own no other path

The five engineers (frontend, backend, ai, data, dev-ops) and the documentor hold no per-feature
notes path of their own. Only those six write
`<HARNESS_FEATURE_TREE_ROOT>/.harness/<repo>/features/<FEAT>/notes/receipt-<your-agent-name>-<runid>.md`,
and cite it as `artifact:`.

## Never your observations log

`<HARNESS_FEATURE_TREE_ROOT>/.harness/<repo>/features/<FEAT>/observations/<your-agent-name>.md` is
the Expertise hot layer (harness-expertise). It is never injected into any spawn, so anything a
successor must read is lost there. Use it only for lessons about *how you work*.
