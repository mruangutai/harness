# Fail-first receipt — BUG-1716 T-02 (amendments digest field)

New harness-eng-lead cases run against validate-digest.py at cb26ae9e (pre-change). Captured 2026-09-16T05:40Z by Main.

```
FAIL  amendments: the three BUG-285 recommendations are accepted eng-lead amendments
ok    amendments: absent is legal
FAIL  amendments: empty list is legal
FAIL  amendments: inline mappings for all three fields
FAIL  amendments: block mapping entry
ok    amendments: unknown key is refused naming index and key
FAIL  amendments: missing key is refused
ok    amendments: not a list is refused
FAIL  amendments: entry that is not a mapping is refused
FAIL  amendments: SC id as task is refused
FAIL  amendments: decision id as task is refused
ok    amendments: field outside intent/files/verify is refused
FAIL  amendments: empty reason is refused
FAIL  amendments: reason over 240 is refused
FAIL  amendments: intent with a list value is refused
FAIL  amendments: files with a string value is refused
FAIL  amendments: files with a line-number anchor is refused
FAIL  amendments: files with a bad mapping entry is refused
FAIL  amendments: second entry's fault is reported at its index
ok    amendments: a product lead may not carry the field
ok    amendments: a validator lead may not carry the field
```

The negative cases that already pass do so because `amendments` is an undeclared key today (the closed-contract gate); they must stay red-then-green for the RIGHT reason, which the must_mention tokens (task/field/reason/was/now/index) pin once the key is declared.
