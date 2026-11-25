# Training data

Polly's first model uses **Curated Glass Transition Temperature for Polymers**, PolyMetriX version 2:

- DOI: <https://doi.org/10.5281/zenodo.15789599>
- License: CC BY 4.0
- File: `LAMALAB_CURATED_Tg_structured_polymerclass_with_embeddings.csv`
- Expected size: 43,615,282 bytes
- Expected MD5: `31400a5f499394e3a6e0658488a464bb`

The raw CSV is intentionally ignored by Git. Download and verify it with:

```bash
window-light-polymer-fetch
```

The model uses the 28 numeric `fullpolymerlevel.features.*` descriptors and the experimental `labels.Exp_Tg(K)` target. The source contains 7,367 polymer records, including 123 records classified as `Polyurethanes`. All 123 polyurethane records come from the same upstream source (`GREA`) and carry the dataset's `black` reliability label, so they are suitable for an initial benchmark but not for a production or formulation claim.

