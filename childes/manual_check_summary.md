# Manual check summary (CHILDES Eng-NA)

Date: 2026-01-31
Sample: childes/manual_check_samples.tsv (200 rows; 50 per stratum)
Seed: 20260131

Definition: "vocative" = direct address to interlocutor; "argument" = referential mention
(including lists/appositives and possessives).

Results (informal spot-check):
- parent_voc: 49/50 clear vocatives; 1 list/appositive false positive.
- parent_arg: 37/50 arguments; 13 appear to be vocatives without commas (false negatives).
- extended_voc: 33/50 clear vocatives; 2 ambiguous; 15 list/appositive false positives.
- extended_arg: 50/50 arguments; occasional kin+name vocatives (e.g., "Cousin Tom") suggest
  additional false negatives.

Interpretation: the heuristic is conservative for parent vocatives and overcounts extended-kin
vocatives in list/appositive contexts. Both biases reduce the parent vs extended contrast, so the
reported contrast is a lower bound.

Note: In uncertainty analysis, the two ambiguous extended-vocative cases are conservatively coded
as vocative to reduce the parent/extended contrast.
