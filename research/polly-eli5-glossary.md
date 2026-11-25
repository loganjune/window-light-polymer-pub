# Polly, explained plainly

Polly is a small research prototype for thinking about polyurethane structure, heat, and additive movement. Today, Polly has one trained benchmark: it estimates **glass-transition temperature (Tg)** from 28 precomputed polymer descriptors and measures how well that estimate transfers to unusual polyurethane records. The website also draws a temperature-versus-opening chart, but that chart is currently an **illustrative scenario**, not a learned measurement of real openings.

Polly does **not** yet predict additive leaching. Its POLLY-MAP code is a trainable framework for a future geometric screen: given suitable experimental or simulation data, it can learn an opening-size curve and show when an additive-sized probe might fit through the uncertain opening band. Fitting through is only one requirement for migration. The additive must also move at a useful rate and prefer the receiving material enough to leave the polymer.

One important wording correction: this is not about “subatomic distances becoming too small during melting.” Subatomic means smaller than an atom. Bond lengths also do not normally collapse to release an additive. The useful scale is **nanoscale free-volume pathways between moving polymer segments**. As temperature rises, those pathways may become larger or connect more often.

## Polymer and temperature words

### Melting versus softening

**Softening** means parts of a material gain mobility and the material becomes easier to bend or deform. Crossing Tg can cause this without turning the whole material into a liquid.

**Melting** is a different transition: ordered crystalline regions lose their order. A TPU may soften around Tg and may also have a broad melting or hard-domain-disruption range. A covalently crosslinked thermoset does not melt into separate flowing chains; enough heat eventually damages or decomposes it. Polly must not treat Tg as a melting point.

### Polymer segment

A polymer is a very long molecule, like a cord made from repeating chemical pieces. A **segment** is a useful stretch of that cord. Polyurethanes often have flexible “soft segments” and more polar “hard segments.” Heating can let segments wiggle and rearrange more even though ordinary chemical bonds remain intact.

### Polyurethane

A family of polymers containing urethane linkages. The name does not specify one recipe or one architecture. Polyurethane behavior also depends on the reactants, segment chemistry, molecular weight, branching, crosslinks, additives, morphology, cure history, moisture, and test conditions.

### Tg, or glass-transition temperature

The temperature region where amorphous polymer segments change from relatively frozen, glass-like motion to greater cooperative motion. Tg is not a sharp “all bonds unlock” temperature, and it is not the same as melting. Polly’s first trained model targets experimental Tg in kelvin.

### Thermoset polyurethane

A polyurethane whose chains are joined into a permanent three-dimensional network by covalent bonds. Heating can increase motion between network junctions, but the junctions do not simply let go. A thermoset therefore cannot be remelted like a typical thermoplastic.

### TPU, or thermoplastic polyurethane

A mostly linear or lightly branched, segmented polyurethane. Its hard segments can gather into physical domains that act like temporary junctions. Heat can weaken or reorganize those associations, allowing more chain movement and, in suitable ranges, melt processing.

### Urethane linkage

The chemical connection commonly written `—NH—C(=O)—O—`. Both TPU and thermoset polyurethane can contain this same linkage. Their different large-scale behavior comes mainly from how many chains and junctions are connected, not from changing the definition of the linkage.

## Openings and migration words

### Accessible opening

An estimate of how wide a connected route through the polymer is for a probe of a given size. It is more useful for migration screening than one atom-to-atom distance. A local empty pocket is not enough if it does not connect to another pocket. POLLY-MAP’s proposed target is the **median connected, probe-accessible opening diameter** at a stated temperature and material condition.

### Additive diameter

A simplified effective size for the additive, expressed in ångströms. One ångström (Å) is `0.1` nanometre. A real molecule changes shape and interacts with its surroundings, so its effective kinetic or hydrodynamic diameter is more useful than the longest distance between two atoms. Size alone says nothing about chemical attraction.

### Crossing interval

The temperature range in which an additive-size line crosses Polly’s uncertain opening curve. POLLY-MAP reports:

- **earliest crossing:** the optimistic upper edge of the opening band reaches the additive size;
- **median crossing:** the middle prediction reaches it;
- **latest crossing:** the conservative lower edge reaches it.

A crossing means “geometric access may be plausible.” It does not mean “leaching starts here.” If a curve never reaches the additive size within the requested temperatures, a crossing can be absent.

### Diffusion

The spreading of molecules through random thermal motion. In a polymer, an additive may wait in one free-volume pocket and occasionally hop to another. A diffusion coefficient, usually written `D`, summarizes how quickly that spreading occurs under particular conditions. Two additives with the same size can diffuse differently because their shape and chemistry differ.

### Free volume

The small, changing spaces not occupied by polymer atoms. These are not permanent round holes. Polymer motion continuously changes their size and connectivity. More segment mobility can make useful pathways appear more often, but crystallinity, crosslinking, pressure, and chemistry also matter.

### Leaching or migration

The movement of an additive from the polymer into another material, such as air, water, food, soil, or a test liquid. A product-scale prediction needs more than an opening size. It normally needs the additive concentration, diffusion coefficient, partition coefficient, sample thickness, contact area, receiving phase, temperature, and exposure time.

### Partition coefficient

A measure of where an additive prefers to be at equilibrium. For example, does it prefer the polyurethane or the contacting liquid? Even a fast-moving additive may remain mostly in the polymer if that environment is much more favorable. Partitioning is therefore a separate gate from geometric fit and diffusion.

## Measurement and simulation words

### DFT, or density functional theory

A quantum-mechanical calculation of electrons and atomic interactions in a relatively small chemical system. DFT can help estimate charges, torsional preferences, and polymer–additive interaction energies. It is usually too expensive and too small in scale to simulate the full melting, morphology, and long-time migration of a polymer product. In Polly’s research plan, DFT helps parameterize or check a force field; molecular dynamics handles the larger moving system.

### Molecular dynamics, or MD

A computer simulation that moves atoms or coarse-grained beads forward in small time steps using a force model. Running MD across temperatures can produce density, segment motion, free-volume geometry, and additive diffusion estimates. A credible MD dataset must record the formulation, topology, cure state, force field, temperature, pressure, simulation cell, coordinates, and validation checks. Polly has a schema for derived opening records, but no real MD calibration dataset yet.

### PALS, or positron annihilation lifetime spectroscopy

An experimental method that uses positrons to estimate tiny free-volume hole sizes in materials. PALS can provide valuable temperature-dependent evidence about free volume. It does not automatically prove that holes form a connected escape path, so connected probe accessibility still needs a justified analysis or supporting simulation.

## Model and evidence words

### Chemistry-group holdout

A tougher test in which all records from one chemistry family are left out together, the model learns from the other families, and then it is tested on the missing family. This is more honest than randomly mixing nearly related records between training and testing. POLLY-MAP requires at least three chemistry groups and repeats this leave-one-group-out process to build its uncertainty estimate.

### Conformal uncertainty

A data-driven error band. POLLY-MAP first predicts groups it was not trained on, collects the absolute misses, and chooses a miss size that corresponds to the requested coverage, such as 90%. It then places that radius above and below future opening predictions. This makes the interval auditable, but the coverage is only meaningful when the calibration groups are sufficiently independent and representative. It is not a guarantee for completely different materials.

### MAE, or mean absolute error

The average size of the model’s misses, ignoring whether each miss is high or low. An MAE of `26.8 K` means the predictions are about 26.8 kelvin away from the measured values on average for that test set. It does not mean every prediction is within 26.8 K.

### Model card

A structured report saved beside a model. Polly’s Tg model card records the dataset identity and checksum, split rules, candidate settings, selected settings, evaluation results, software versions, and limitations. The web server reads this card instead of hiding the benchmark numbers inside the page.

### OOD, or out of distribution

Data that differ from the examples used for fitting. Polly’s Tg benchmark makes a polyurethane OOD test by selecting the 20% of polyurethane records farthest from the polyurethane descriptor center, without using their Tg labels to choose them. That tests unusual descriptor combinations. It does **not** test real-world disorder, extreme temperatures, new laboratories, or thermoset stability.

## How the code moves information through Polly

### 1. Download and verify the Tg data

`src/window_light_polymer/data.py` downloads the published PolyMetriX CSV, checks its MD5 checksum, and reads 7,367 polymer records. Each record contains an experimental Tg label, polymer metadata, and 28 numeric full-polymer descriptors. There are 123 records labeled as polyurethanes. All 123 come from the `GREA` source and carry the dataset’s `black` reliability label, so this is a first benchmark rather than a broad formulation dataset.

### 2. Train and audit the Tg baseline

`src/window_light_polymer/model.py` trains a standardized ridge regression. In plain language, ridge regression fits a weighted straight-line relationship while discouraging extreme coefficients.

The code:

1. puts non-polyurethane records into a broad training split, a guard split, and a sealed audit split using repeatable SHA-256 buckets;
2. selects the ridge regularization strength on the guard split;
3. reserves 25 unusual polyurethane records as an OOD test using descriptor distance, then divides the remaining polyurethane records into training and validation sets;
4. tries different polyurethane training weights;
5. rejects a candidate if it worsens general guard MAE by more than 5%;
6. selects the allowed weight with the best polyurethane validation MAE; and
7. evaluates the broad and fine-tuned models on the sealed polyurethane OOD test and general-polymer audit.

`src/window_light_polymer/train.py` writes the learned coefficients to `artifacts/polly-tg-model.json` and the evidence report to `artifacts/polly-tg-model-card.json`. The current polyurethane OOD MAE is `26.75 K` for the broad model and `26.81 K` after polyurethane weighting. The general audit MAE also rises from `44.41 K` to `44.88 K`. In other words, the fine-tuning helped the validation set but did not improve the sealed unusual-polyurethane test.

### 3. Serve the evidence to the browser

`src/window_light_polymer/server.py` serves the HTML, CSS, and JavaScript. Its `/api/model-card` endpoint returns the Tg model card, and `/api/health` reports whether that card is available. This is a local educational server, not a production prediction service.

### 4. Draw the structure explorer and current chart

`src/window_light_polymer/web/app.js` draws schematic TPU chains or a thermoset network. The “Apply heat” control changes the drawing and explanatory text; it does not run molecular simulation.

The browser loads the model card, uses the observed polyurethane median Tg (`335.15 K`) as the chart’s bend, and draws a provisional opening curve. The current formula assumes a `5 Å` opening at Tg, a slope of `0.003 Å/K` below Tg, an above-Tg slope of `0.012 Å/K` for TPU or `0.006 Å/K` for thermoset, and a fixed `±0.8 Å` band. Those numbers are hand-set display assumptions, not values learned from the Tg data or POLLY-MAP. The user’s additive diameter becomes a horizontal line, and the page calculates where that scenario crosses the line.

### 5. Train POLLY-MAP when opening data exist

`research/pu-migrate-opening.schema.json` defines one temperature-indexed training record. It includes polymer and chemistry-group IDs, topology, temperature, Tg, hard-segment fraction, crosslink density, median opening diameter, and whether the value came from experiment or simulation.

`src/window_light_polymer/migration.py` implements the POLLY-MAP research model. It fits separate nonnegative temperature and above-Tg slopes for thermoplastic and thermoset records, while also using hard-segment fraction and crosslink density. It repeatedly leaves out a whole chemistry group to measure its errors, converts those errors into a conformal interval, and can calculate earliest, median, and latest size-line crossings.

`src/window_light_polymer/migration_train.py` reads newline-delimited records that follow the schema and writes a model artifact. The algorithm is implemented and unit-tested with synthetic data. There is no real calibrated POLLY-MAP artifact today, so its code is a research framework rather than evidence of migration accuracy.

## What is real today, and what is still planned?

| Part of Polly | Status today | Safe interpretation |
| --- | --- | --- |
| TPU and thermoset structure drawings | Implemented educational diagrams | Explains chain versus network topology; not a molecular simulation |
| PolyMetriX Tg dataset pipeline | Implemented and checksum-verified | Reproducible source for the Tg benchmark |
| Tg ridge-regression benchmark | Trained, audited, and saved | Measures descriptor-to-Tg transfer; not a formulation or safety predictor |
| Tg fine-tuning result | Measured negative transfer result | Validation improved, but sealed PU OOD performance did not |
| Website opening chart | Implemented as a labeled scenario | Useful for explaining a size-line crossing; not calibrated geometry |
| POLLY-MAP algorithm and data schema | Implemented; synthetic tests only | Ready to train when independent PALS/MD opening records exist |
| Temperature-dependent opening predictions | Research plan | Requires several independent chemistry groups and physical validation |
| Additive diffusion prediction | Research plan | Requires additives or probe classes, trajectories, and diffusion validation |
| Partitioning and product-scale leaching | Research plan | Requires receiving-phase data, transport conditions, and migration experiments |
| Patentability or novelty | Not established by the code | Requires a professional claim-level prior-art search and supporting evidence |

The practical rule is simple: **Tg tells Polly when segment mobility may change; opening data would tell Polly about geometric access; diffusion and partitioning are still needed before Polly can say anything quantitative about leaching.**
