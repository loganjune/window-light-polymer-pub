# Polly serious-modeling roadmap

The first Tg transfer baseline is intentionally narrow. It establishes a reproducible training and evaluation spine without claiming that repeat-unit descriptors capture polyurethane formulations or cured networks.

| Scientific question | First model | Serious-modeling requirement | Evidence needed before claiming success |
| --- | --- | --- | --- |
| Chemically meaningful downstream task | Held-out polyurethane Tg prediction | Add tensile strength, modulus, elongation, DMA, swelling/gel fraction, density and decomposition targets | Chemistry-family and laboratory-held-out results with uncertainty |
| Disorder and unusual conditions | Descriptor-distance OOD split only | Atomistic or coarse-grained ensembles across temperature, humidity, strain, morphology and cure states | Performance by condition and distance from training distribution |
| Physical stability | Not modeled | Energy/force model or validated MD with bond, density, clash, drift and long-trajectory checks | Stability audits and comparison with experimental observables |
| Fine-tuning helps one regime without harming another | PU validation plus sealed general-polymer audit | Matrix across TPU, foams, coatings, elastomers and thermosets | Before/after metrics and uncertainty for every regime |
| Reproducibility | DOI, checksum, deterministic splits, coefficients and commands | Versioned raw/processed schemas, container, hardware record, seeds and archived artifacts | Independent rerun reproducing splits and metrics within tolerance |

## Data representation required for thermosets

A repeat-unit SMILES is not enough. Each serious record should include:

- isocyanate, polyol, chain extender and crosslinker structures;
- reactant functionality, equivalent weights and molecular-weight distributions;
- NCO/OH index, hard/soft-segment ratio and stoichiometry;
- catalyst, surfactant, blowing agent, filler and other additives;
- mixing, cure, annealing, humidity and specimen history;
- network descriptors such as gel fraction and crosslink density;
- the measurement method and conditions attached to every target.

## Proposed phases

1. Curate a polyurethane formulation schema and 50–100 fully sourced pilot records.
2. Add RadonPy or another validated MD workflow for amorphous TPU disorder tests.
3. Build a reactant-graph plus process-condition model for formulations.
4. Add thermoset network construction and physical-stability audits.
5. Run laboratory- and chemistry-family-held-out evaluation, then archive the entire benchmark.

## Data contract for temperature-dependent distances

The Tg table cannot supervise atomic geometry. A trainable distance model needs a separate trajectory table:

| Required field | Why it is needed |
| --- | --- |
| Per-frame atomic coordinates and simulation cell | Defines real distances in Å and periodic neighbors |
| Atom identities, bonds and network topology | Distinguishes bonded geometry from nonbonded segment spacing |
| Temperature, pressure and ensemble | Attaches each geometry to a thermodynamic condition |
| Formulation, cure state and morphology | Separates TPU softening from a thermoset network response |
| Force field or electronic-structure method | Makes generated labels traceable and comparable |
| Density, energy, forces and radial-distribution functions | Supports physical-stability and structural validation |

Evaluation must hold out chemistry families and entire trajectories—not random frames from trajectories also present in training. Report bonded-distance errors, radial-distribution errors, density versus temperature, long-run stability and uncertainty separately.

## Additive-migration model

The useful geometric quantity is not one interatomic distance. It is the distribution of connected, probe-accessible free-volume openings at each temperature. The proposed chart is:

- **x-axis:** temperature, with Tg and any thermoplastic melting interval shown separately;
- **y-axis:** accessible-opening diameter in Å, reported as a distribution or uncertainty band;
- **overlay:** a user-supplied additive kinetic or hydrodynamic diameter;
- **geometric result:** the temperatures where an opening path becomes plausible;
- **migration result:** additive diffusion coefficient and predicted mass transfer versus time.

The size-line crossing must not be labeled “leaching.” It ignores chemical affinity, concentration, crystallinity, crosslink density and the receiving phase.

| Layer | Method | Output |
| --- | --- | --- |
| Local chemistry | DFT on representative urethane, soft-segment and additive fragments | Charges, torsions and polymer–additive interaction energies for force-field validation |
| Temperature-dependent morphology | All-atom MD, then validated coarse-grained MD for longer times and larger cells | Density, Tg/melting behavior, free-volume opening distribution and morphology |
| Additive motion | MD or enhanced sampling with additive probes spanning size and chemistry | Mean-square displacement, hopping barriers and diffusion coefficient D(T) |
| Leaching boundary | Experiment or free-energy/solvation calculation | Polymer/receiving-phase partition coefficient K |
| Product-scale transport | Fickian or validated non-Fickian continuum model | Migrated mass versus time, thickness, temperature and contact condition |

### What can be done when the additive identity is unknown

Size alone supports a conservative **geometric screen**, not a material-specific migration prediction. Use probe beads covering a size grid and at least a small interaction grid (repulsive, weakly polar, strongly polar). Report an envelope across those interaction classes. Once additive chemistry is known, replace the envelope with an interaction-specific DFT/MD calculation and a measured or calculated partition coefficient.
