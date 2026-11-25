# Polly literature curation: selected polyurethane families

Status: curated evidence set v2. It contains 48 traceable records, including 24 numeric PALS temperature/cavity observations from 3 independent papers and 4 polymer series. It is suitable for source tracking, hypothesis design, and downstream transport checks. It is **not yet a defensible training set for connected opening diameter**.

## Scope chosen for Polly

| Polly family | Target topology | Best evidence in this pass | Current readiness |
| --- | --- | --- | --- |
| Polyether | Linear thermoplastic | PTMG-PU PALS/WVP study; two commercial polyether-PU NO diffusion datasets | Transport validation ready; numeric PALS curve still needs licensed figure extraction |
| Polyester | Linear thermoplastic | Independent amorphous polybutylene-adipate TPU PALS series with 17 digitized temperatures, plus reported endpoints for a second PBA-PU | Temperature-resolved PALS surrogate ready below the source's 300 K reliability boundary; not connected-opening ready |
| Polycaprolactone | Linear thermoplastic | PCL-PU PALS radius endpoints from 140-350 K; independent PCL-PU PALS/WVP study | Coarse PALS surrogate ready, not connected-opening ready |
| Polycarbonate | Linear/commercial PU | Bionate 80A NO diffusion at 298 and 310 K | Downstream transport check ready; no direct PCU PALS temperature curve found |
| Polyether | Crosslinked | PPO/PCL urethane/urea PALS series at 298, 310 and 324 K; qualitative plasticized crosslinked-polyether PALS study | Mixed-chemistry surrogate only; a neat crosslinked-polyether series is still required |

## What was curated

The machine-readable staging dataset is [`pu-free-volume-evidence.jsonl`](./pu-free-volume-evidence.jsonl), governed by [`pu-free-volume-evidence.schema.json`](./pu-free-volume-evidence.schema.json). Every observation records its source, chemistry family, topology, condition, extraction method, and whether it can be used as a POLLY-MAP opening label or only as transport validation.

Key numeric observations:

- Independent amorphous polybutylene-adipate TPU: 17 o-Ps lifetime observations were digitized from 200-328 K and converted with the paper's Tao-Eldrup spherical model. The 13 observations from 200-296 K are allowed into the live interpolation. Four observations above 300 K remain in the audit dataset but are excluded from the live curve because the authors warn that o-Ps may no longer reliably report host-cavity size there. The same paper reports Tg = 244 K and an anisotropic hole-growth exponent of about 2 ± 0.2.
- Linear polybutylene-adipate polyurethane: PALS spherical-equivalent mean hole radius increased from 1.92 Å at 140 K to 3.19 Å near 350 K; the paper reports 33% crystallinity and a 314 K soft-segment melting transition.
- Linear polycaprolactone polyurethane: the corresponding radius increased from 1.97 Å to 3.30 Å; the paper reports 18% crystallinity and a high-temperature transition around 310-311 K.
- Crosslinked polypropylene-oxide/PCL urethane/urea with 5 wt% PCL: the larger PALS hole mode was digitized as 3.63, 3.72, and 3.77 Å in radius at 298, 310, and 324 K. The curation assigns ±0.04 Å digitization tolerance.
- Polyether Tecoflex SG80A: measured NO diffusion coefficients were 1.2 ± 0.5 and 1.9 ± 0.5 × 10^-6 cm²/s at 298 and 310 K.
- Polyether Pellethane 80A: 0.5 ± 0.1 and 0.8 ± 0.3 × 10^-6 cm²/s.
- Polycarbonate-PU Bionate 80A: 0.3 ± 0.1 and 0.7 ± 0.1 × 10^-6 cm²/s.

## Important scientific boundary

PALS reports a local cavity-size distribution under an assumed geometry. It does not directly measure whether those cavities join into a sample-spanning path. The 2018 PMI study also shows that flattened or elongated holes fit the free-volume fraction better than spheres. Therefore:

- `spherical_equivalent_diameter_a` is retained as a **surrogate structural observable**;
- it is not renamed `opening_p50_a`;
- it is not fed into the current POLLY-MAP connected-opening trainer;
- transport measurements remain separate labels for validating whether a structural signal has downstream meaning.

This matters because the PPO/PCL study found only a weak relationship between total PALS free volume and CO2 permeability, and explicitly identified void connectivity, crystallinity, chain flexibility, and wall chemistry as additional controls.

## Source decisions

| Source | Families used | Decision |
| --- | --- | --- |
| Consolati et al. (2016), Journal of Polymer Science Part B, DOI 10.1002/polb.24119 | Polyester | Accepted as an independent, temperature-resolved amorphous TPU series; 17 Figure 4 lifetimes retained, with only the 13 points below 300 K enabled for interpolation under the authors' reliability warning |
| Ning et al. (2001), Acta Polymerica Sinica | Polyester, PCL | Accepted for reported endpoint radii, transitions, and crystallinity; spherical-hole surrogate only |
| Wang et al. (2004), Materials Chemistry and Physics, DOI 10.1016/j.matchemphys.2004.07.012 | Polyether, polyester, PCL | Accepted as highest-priority matched-family source; numeric figures not transcribed without full-text figure access |
| Ferreira Marques et al. (2008), Acta Physica Polonica A | Crosslinked polyether/PCL | Accepted with explicit mixed-chemistry tag and figure-digitization tolerance |
| Ferreira Marques et al. (2007), Radiation Physics and Chemistry, DOI 10.1016/j.radphyschem.2006.03.017 | Crosslinked PPO/PDMS polyether | Accepted as matched variable-temperature PALS/CO2-permeation coverage; numeric curves remain unavailable in the accessible abstract |
| Ren et al. (2016), ACS Biomaterials Science & Engineering, DOI 10.1021/acsbiomaterials.6b00215 | Polyether, polycarbonate | Accepted as direct downstream diffusion validation; not an opening label |
| Forsyth et al. (1995), Electrochimica Acta | Crosslinked polyether | Qualitative only because the accessible abstract lacks numeric values and the system is plasticized |
| Pas et al. (2005), Electrochimica Acta | Polyether | Transport/free-volume corroboration only because the material is a NaPF6 polymer electrolyte |
| Consolati et al. (2018), Polymer Testing | Mixed polyether/polyester | Geometry-warning and Tg metadata; not a pure-family label |
| Kluin et al. (1992), Macromolecules | Neat polycarbonate | Excluded from PU calibration; retained only as a chemistry prior and explicit negative control |

## What Polly can do next without pretending

1. Plot a **PALS spherical-equivalent cavity diameter** evidence layer for polyester, PCL, and the mixed crosslinked PPO/PCL material, with a visible surrogate label and source-specific reliability boundary.
2. Add the polyether and polycarbonate NO diffusion values as a separate downstream-validation panel.
3. Obtain the licensed figures from Wang et al. (2004), digitize all three 30 wt% hard-segment curves, and keep the raw pixel calibration plus uncertainty.
4. Commission or locate a neat crosslinked PPO/PPG polyurethane PALS temperature series with full formulation, crosslink density, and replicate uncertainty.
5. Generate MD probe-accessibility curves for the same formulations, then calibrate PALS local-hole measures against connected probe-accessible openings before training POLLY-MAP.

Until steps 3-5 are complete, the honest output is a literature evidence chart, not a calibrated additive-leaching predictor.
