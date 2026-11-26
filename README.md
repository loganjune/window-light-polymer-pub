# Window Light Polymer

Window Light Polymer is a source-available research and portfolio project. See [LICENSE](LICENSE) for reuse terms.

Meet **Polly**, an interactive, inspectable robot guide to the structural difference between **thermoplastic polyurethane (TPU)** and **thermoset polyurethane**. The project carries forward the visual language of `window-light-scientist` and now includes a deliberately narrow first scientific model: a reproducible polyurethane glass-transition-temperature transfer baseline.

## What the explorer shows

- Both material families contain urethane linkages, commonly written `—NH—C(=O)—O—`.
- TPU is typically a mostly linear, segmented polymer. Its hard segments can gather into reversible, hydrogen-bonded physical domains while soft segments provide flexibility.
- Thermoset polyurethane is a covalently crosslinked network made with multifunctional reactants. Those network junctions do not melt apart when heated.
- Heating therefore increases chain mobility in a TPU and can permit melt processing, while a thermoset retains its network until thermal damage begins.

The diagrams are deliberately schematic. Real behavior depends on monomer functionality, stoichiometry, segment chemistry, molecular weight, additives, morphology, cure history, moisture, and temperature. This is an educational comparison, not a formulation, processing window, or safety tool.

## First trainable model

The baseline uses the CC BY 4.0 PolyMetriX **Curated Glass Transition Temperature for Polymers** dataset (DOI `10.5281/zenodo.15789599`): 7,367 polymers with 28 full-polymer descriptors and experimental Tg labels. The dataset contains 123 polyurethane records.

The evaluation is designed to expose transfer failures:

1. Train a broad ridge-regression model on non-polyurethane polymers.
2. Select regularization on a general-polymer guard split.
3. Fine-tune by upweighting polyurethane training records, while limiting allowed damage on the guard split.
4. Evaluate once on 25 unusual polyurethane records selected by descriptor distance, with labels hidden during splitting.
5. Audit the same fine-tuned model on a sealed 663-record general-polymer split.

Current reproduced result:

| Sealed evaluation | Broad model MAE | PU-fine-tuned MAE | Change |
| --- | ---: | ---: | ---: |
| Unusual polyurethane Tg, 25 records | 26.75 K | 26.81 K | **+0.06 K** |
| General-polymer audit, 663 records | 44.41 K | 44.88 K | **+0.46 K** |

Fine-tuning improved the polyurethane validation split but **did not transfer to the sealed unusual-polyurethane test** and slightly damaged the general audit. That negative result is preserved rather than tuned away.

### Temperature response and distance boundary

The explorer now uses the polyurethane Tg distribution to anchor an interactive below/near/above-Tg softening regime. The changing segment separation is deliberately a visual cue without an Ångström scale. The current dataset has no 3D coordinates, temperature-indexed trajectories, interatomic-distance labels, density targets or radial-distribution functions, so it cannot train a defensible interatomic-distance predictor. Columns with `distance` in their names are graph/connectivity descriptors rather than Cartesian geometry.

A real distance model requires molecular-dynamics or experimental structural trajectories with temperature, pressure, cell, topology and per-frame coordinates. That requirement is captured in the serious-modeling roadmap.

For additive migration, the intended serious chart is temperature versus the **distribution of accessible free-volume opening diameters**, with the user's additive diameter drawn as a horizontal line. A crossing indicates that a geometrical hopping path may become accessible; it is not, by itself, a leaching prediction. Quantitative migration additionally requires a diffusion coefficient, polymer/additive-to-extractant partition coefficient, starting concentration, material thickness, contact area and exposure time.

### POLLY-MAP alpha

The repository now includes a trainable research method for a potentially differentiating contribution: topology-aware opening curves with **leave-one-chemistry-group-out cross-conformal crossing intervals**. It constrains thermal slopes to be nonnegative, uses different response bases for thermoplastics and thermosets, calibrates uncertainty by excluding entire polyurethane chemistry groups, and returns earliest/median/latest temperatures at which a user-supplied additive diameter crosses the opening band.

The algorithm is implemented and tested, but it is not yet calibrated: unit tests use synthetic records only. Real training data must follow [research/pu-migrate-opening.schema.json](research/pu-migrate-opening.schema.json). The public repository deliberately excludes confidential invention-disclosure material.

The browser also loads a separate, explicitly labeled **literature PALS proxy**. The v3 evidence set has 63 traceable records, including 39 numeric temperature/cavity observations from 4 independent papers and 7 polymer series. Polly keeps different polymers and papers separate instead of pretending repeated points are independent samples. Its live chart uses 23 accepted interpolation points: 5 from a PTMG/PEG polyether TPU series, 13 from an amorphous polyester TPU series below the authors' 300 K reliability boundary, 2 polycaprolactone-TPU endpoints, and 3 crosslinked PPO/PCL observations. Four higher-temperature polyester observations remain in the audit data but are excluded from interpolation. Polycarbonate-PU remains on the generic scenario because a matched numeric PALS curve has not been found. The proxy is deliberately not passed to the connected-opening trainer: local PALS cavities do not prove path connectivity.

```bash
window-light-polymer-literature-proxy

window-light-polymer-migration-train \
  --dataset path/to/temperature-indexed-opening-records.jsonl
```

All 123 polyurethane records come from the same upstream source (`GREA`) and have the dataset's `black` reliability label. This is enough for a first benchmark, not a formulation model. The next research phases are specified in [research/serious-modeling-roadmap.md](research/serious-modeling-roadmap.md).

## Run locally

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -e .
window-light-polymer-fetch
window-light-polymer-train
window-light-polymer
```

Open <http://127.0.0.1:4175>.

## Static research preview

The public site is built without a Python server. Its deployment validates and bundles the Tg model card and literature
PALS proxy alongside the browser assets:

```bash
window-light-polymer-static-build --output _site
python -m http.server 4176 --directory _site
```

The interface is explicitly labeled as an exploratory PALS/free-volume proxy, not a validated additive-migration,
leaching, exposure, or safety model. The site's research-feedback link opens a structured public issue so data
suggestions and scientific criticism remain reproducible and inspectable.

## Test

```bash
python -m unittest discover -s tests -v
```

## Repository layout

```text
src/window_light_polymer/server.py  standard-library static server and health endpoint
src/window_light_polymer/data.py    download, checksum and dataset parser
src/window_light_polymer/model.py   deterministic splits, transfer fit and audits
src/window_light_polymer/train.py   reproducible training command
src/window_light_polymer/migration.py topology-aware opening model and group-conformal crossing intervals
src/window_light_polymer/migration_train.py POLLY-MAP training command
src/window_light_polymer/literature_proxy.py curated PALS proxy artifact builder
src/window_light_polymer/static_site.py validated static-site packager
src/window_light_polymer/web/       interactive structure explorer
artifacts/                           model coefficients and complete model card
research/                            serious-modeling roadmap
tests/                               data, model, server and packaged-asset checks
```
