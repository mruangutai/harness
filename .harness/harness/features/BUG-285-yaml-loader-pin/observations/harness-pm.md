# Observations - harness-pm

- 2026-09-09: BUG-285. A dispatch-supplied insertion anchor ("around :1445") was off by two: the
  T-06 Part C cases end at test-gh-sync.py:1442 and the fix1 Part B comment opens at :1444. Writing
  a bare line number into intent would have pointed the builder inside a comment block; I wrote the
  line number PLUS the two literal strings to re-locate by, which is what survives a concurrent edit.
- 2026-09-09: BUG-285. plan-merge.py apply reads --proposal - from a bash heredoc without tripping
  bash-write-guard.sh (no redirect target), so a whole bootstrap proposal goes in one call with no
  temp file. Confirmed APPLIED, exit 0, on a plan that did not previously exist. The observations
  dir is NOT auto-created: observations-merge.py dies with FileNotFoundError on the .lock path.
- 2026-09-09: BUG-285. check-plan-routes.py prints "granted to" the FULL resolved agent set, not the
  one named in execution_agent, so it cannot catch a wrong-but-granted routing choice. consult-when
  in team-config.yaml is the only discriminator; the resolver output does not carry it.
- 2026-09-09: BUG-285 c1. Dispatch mandated `plan-merge.py apply` to REVISE tasks[T-01].intent; apply is add-only and exited 7 CONFLICT (plan-merge.py:1217-1218). The docstring header's verb list (lines 11-16) omits `amend`, which the BUG-1128 block at :1215 adds — so a dispatch written from the header names an impossible route. Used `amend --key tasks --id T-01 --field intent --expect-sha256 <from --show> --value-file <raw dedented body>`; `_render_field` reuses the `|` header verbatim and re-indents the body, so the value file holds the dedented block content exactly as `--show` printed it.
- 2026-09-09: BUG-285 c1. Derived the replacement value with a throwaway script that loaded the plan, string-replaced only step f, and asserted the reverse replacement restored the original intent byte for byte — cheaper and safer than retyping a 5.5 KB block scalar, and it proves "nothing else changed" rather than claiming it.
- 2026-09-09: BUG-285 c1. The goal-check report's replacement wording carried markdown backticks around a git command; the target intent block uses double quotes for every literal it names and no backticks anywhere. Kept the file's idiom and recorded the deviation in the artifact rather than importing decoration into a data value.
- 2026-09-09: BUG-285 c2 — a re-grade note cited team-config.yaml:259 for harness-qa's notes grant; the worktree copy has it at 258 and the OWNER manifest at 259, and check-plan-routes.py says the hook consults the owner copy. Cite the owner manifest's line when a worktree carries a divergent team-config.
- 2026-09-09: BUG-285 c2 — plan-merge amend --value-file preserves the literal block only if the value file ends in a newline; a file whose trailing newline was trimmed would have changed the scalar form. Checked the round-trip with safe_load before and after.
- 2026-09-09: BUG-285 panel transcription — the lead digest carried the SAME finding in two wordings (prose table vs appended DIGEST yaml block); since the PF- id is a content hash the two hash differently. Extracted the value with yaml.safe_load from the fenced block instead of retyping, so the em-dash survived and the post-merge re-derivation matched. set-panel re-emits a summary as a double-quoted scalar with \u2014 escaped — representation change only, hash unaffected.
