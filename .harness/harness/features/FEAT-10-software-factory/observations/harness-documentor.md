- 2026-08-09 (T-09): I ran the dispatch's `verify:` chain with `gen-decisions-index.py &&`
  prepended, then reported it as the acceptance run. A prepended step is a different command:
  the regen guaranteed the freshness that `diff` was supposed to be testing. Run the string
  unmodified, and separately if you want the convenience version.
- 2026-08-09 (T-09): writing DEC-186 I twice drifted into supplying reasoning for a `refs:`
  target the intent only wanted MENTIONED (DEC-168, then DEC-179). When an intent says
  "reference DEC-NN so the index rows link them", the mention is navigational — a scope
  disclaimer naming the id (DEC-183's shape) satisfies the ref without asserting a governing
  relationship nobody signed.
