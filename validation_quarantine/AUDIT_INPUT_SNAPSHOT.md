# Audit Input Snapshot

Issue: #32
Audit rule version at freeze: R1

## Frozen production reference
The quarantine branch was created from current `main` at audit setup time.

Recorded main tree SHA from setup inspection:
- `b95ea939c66b9929efdc8e4d32f59f09ed7edfac`

Primary input blob identities recorded from that tree:
- `data/generation/special2788_generation_profile.csv`
  - blob SHA: `ac6c1d24e1c6ce04b238cc0b16d788f9d0965a05`
- `data/generation/generation_family_rules.csv`
  - blob SHA: `400ae5abdd5d7ecb4c112ddb42f0ab610f33d78a`
- `data/generation/generation_model_observations.csv`
  - blob SHA: `b23a3b23438df4496102f042b3875a012d9db932`
- `data/semantic/semantic_support_profiles.csv`
  - blob SHA: `e666e4efd5c3aabf22410d75e04ff51d826c9b0e`
- `data/semantic/family_support_rules.csv`
  - blob SHA: `99ade8e98c5c62e112c55e2663ae98b2074c14dc`
- `docs/stages/STAGE_10_KNOWLEDGE_HANDOFF.md`
  - blob SHA: `49f8752557dee2409e086e1538961f240c219a27`

## Fixed ordering
The initial 2,788-row audit sequence is the row order of the frozen `special2788_generation_profile.csv` above. Sequence numbers in `results.csv` refer to that frozen order.

Do not silently switch to a later `main` revision during the first pass. New evidence or later production data may be compared separately, but any input revision change must be recorded as a new audit-input version and must not retroactively redefine completed rows.

## Protected source note
The Special2788 source corpus may be local/protected and is not treated as backed up by this quarantine branch. Source identity checks use the project's existing protected-data authority and integrity rules; no protected source is copied into Git by this audit.
