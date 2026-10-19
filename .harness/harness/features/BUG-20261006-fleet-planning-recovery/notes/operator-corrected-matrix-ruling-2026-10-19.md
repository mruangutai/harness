# Corrected-pin matrix ruling

On 2026-10-19 the operator selected **Authorize one corrected-pin rerun** in response to:

> Allow one additional full unit/integration matrix at corrected review pin f9a13cac, preserving the original failed receipt?

This explicitly overrides the approved EXACTLY ONCE limit for **one additional full active unit/integration matrix** at `f9a13cacb4c554605dc5fa339f12d609d15818e1`. It does not rewrite the signed plan, first failed matrix receipt, historical returns, verdicts, timestamps or cycle counts. It authorizes neither an automatic retry nor Kaya operations, installation, push or merge.

The operator's selected option description was: “Override the once-only limit for one additional matrix. No Kaya operations, installation, push or merge.”
