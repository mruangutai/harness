Task build verification is the static checks below, run from /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-2037-product-document-guidance after the four guidance edits.
Expected: exit 0, no structural errors or suite FAILs; preload-weight NOTE is advisory and recorded; static results are not behavioural proof.
python3 /Users/molchairuangutai/GitHub/harness/.agents/skills/harness/bin/check-skill-weight.py /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-2037-product-document-guidance
python3 /Users/molchairuangutai/GitHub/harness/.agents/skills/harness/bin/check-skill-refs.py /Users/molchairuangutai/GitHub/harness/.claude/worktrees/harness/FEAT-2037-product-document-guidance
python3 .agents/skills/harness/bin/check-instruction-paths.py
python3 .agents/skills/harness/bin/run-unit-tests.py --kind unit
python3 .agents/skills/harness/bin/run-unit-tests.py --kind integration
Independent reviewer reads all four files at review_sha (SC-04), and live notes/uat-product-document-guidance-c0.md U-01 through U-04 with all 27 assertions, operator alone recording passed, and not run at intake remain feature acceptance gates AFTER build and NOT prerequisites of task completion.
