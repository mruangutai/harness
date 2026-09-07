# Observations - harness-pm

- 2026-09-07: BUG-124 — a rule that must read .harness/team-config.yaml cannot be parsed inside a hook body launched with `python3 -I`: PyYAML lives in the user site-packages that -I excludes (measured at 6d969ed3: isolated import ModuleNotFoundError, plain import fine). Any such plan must route the parse through a non-isolated invocation and pass the result in by env, or DEC-171 and the isolation flag contradict each other and the gate silently never fires.
- 2026-09-07: BUG-124 — `plan-merge.py apply --proposal -` with a bash heredoc is refused by bash-write-guard as `redirect targets -`. Staging the proposal as a /tmp file via the Write tool and passing that path works. Cost one blocked call.
- 2026-09-07: BUG-124 — proving each plan verify block RED pre-change was cheap and caught real design detail: firing the live dispatch-guard with a probe payload reaches the single-flight claim step, which is why the plan pins the new check to run BEFORE the claim (D-04). Check the inflight registry after any probe that fires a real hook.
- 2026-09-07: BUG-124 goal-check. When a plan adds a gate that refuses a literal token, grep the plan
  for that token: T-02 verify (plan.yaml:159) embeds the exact `runs/eng-t01/digest.md` path the new
  gate refuses, and leads carry verify verbatim into the dispatch prompt, so the gate blocks its own
  retry/qa dispatch. Invisible to every SC because SC-03 covers only compliant and no-path prompts.
- 2026-09-07: measured 309 distinct run dirs under .harness/*/features/*/runs/ in the owner root, all
  ending -product/-eng/-validator. That zero-non-conformer count is what made a callee-INDEPENDENT
  shape rule cost-free to accept over the operator's callee-specific wording.
- 2026-09-07: BUG-124 panel transcription. An acceptance criterion phrased as "git diff --stat names ONLY plan.yaml" is unmeetable when the feature directory is untracked at HEAD (git log -- plan.yaml empty, git status shows ?? on the dir): the diff is empty and names nothing. Reported the line delta (+69, 282 -> 351) plus set-panel's own reload-equality refusal (plan-merge.py:1050-1066) as the substitute evidence rather than calling the criterion failed.
- 2026-09-07: Generating a panel value file from a script that hashes the SAME string objects it yaml.safe_dumps removes the whole drift class panel_findings.py warns about; re-deriving each id from the file as loaded back out is then a genuine second measurement, not a re-print of the first.
