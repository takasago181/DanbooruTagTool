# Prototype QA

## Static checks
- Python syntax compile: PASS
- Verified 2026-09-02 canonical KB included: PASS
- Verified alias index included: PASS
- Verified special2788 linkage included: PASS

## Synthetic co-occurrence test
The engine was tested with a synthetic matrix where:
- `long_hair` strongly co-occurs with both `twintails` and `school_uniform`
- `blue_hair` strongly co-occurs with only one
- `sitting` moderately co-occurs with both

Expected common-mode ranking:
1. long_hair
2. sitting
3. blue_hair

Result:

```text
PASS
{'tag_count': 5, 'matrix_shape': (5, 5), 'matrix_dtype': 'float32', 'matrix_ram_gib': 9.313225746154785e-08}
long_hair 0.746666669845581 [0.800000011920929, 0.699999988079071]
sitting 0.5 [0.5, 0.5]
blue_hair 0.18095238506793976 [0.949999988079071, 0.10000000149011612]
```

## Not executed here
The 455,719,557-byte public production co-occurrence matrix could not be downloaded from the current execution container.
`DOWNLOAD_DATA.bat` downloads and SHA-256 verifies it on the user's Windows PC before the real run.
