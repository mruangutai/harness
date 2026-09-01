# Expertise — harness-ai-dev
## Patterns (max 15)
## Gotchas (max 15)
- G-01: WHEN auditing this repo's Expertise injection DO note that `inject-expertise.sh` globs every `.harness/*/expertise/<agent>.md` with no per-dispatch segment filter, guarded only by prose (D-01, open, single-segment today) — an audit finding here is very likely already recorded under D-01.
- G-02: WHEN editing plan-panel.yaml's closing comment or harness-validator-lead.md's 'Hosting plan-panel' section DO update both — no test cross-checks their duplicated transcription mechanics (unrated-gating, PF- id ownership), so one can drift silently while the other stays authoritative.
## Outcomes (max 10)
## Open (max 5)
