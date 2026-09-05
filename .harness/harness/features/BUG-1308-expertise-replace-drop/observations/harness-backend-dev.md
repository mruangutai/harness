# Observations - harness-backend-dev

- 2026-09-05: BUG-1308 T-01 — the plan's Step A "missing required key" refusal lines needed a
  concrete wire format not fully pinned by the intent prose (which key literal + which index
  spelling). Chose `MALFORMED OPS op index=<i>: <message>` naming the literal token `section` (or
  `target`/`entry`) inline; both unit test and implementation authored together so the format is
  self-consistent, but a sibling reading only the plan intent would need to re-derive it — worth
  flagging in T-02/T-03 if they independently assert on refusal line shape beyond code+prefix.
