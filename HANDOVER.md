# Polly reconnect handover

Updated: 2026-11-25

## Resume here

This is the sanitized public mirror of Polly, a polyurethane structure explorer and bounded research prototype.

- Public repository: <https://github.com/loganjune/window-light-polymer-pub>
- Local public checkout: `/Users/pjh/chat/chemical safety/window-light-polymer-pub`
- Local app URL while the server is running: <http://127.0.0.1:4175/>

The repository was clean, pushed, and passing the `quality` GitHub Actions workflow before this handover was written.

## Start after reconnecting

```bash
git pull --ff-only
python3 -m venv .venv
.venv/bin/python -m pip install -e .
.venv/bin/python -m unittest discover -s tests -v
.venv/bin/window-light-polymer
```

Then open <http://127.0.0.1:4175/>. The expected result is 20 passing tests.

## Current state

- Polly compares thermoplastic and crosslinked polyurethane structures.
- The soft-segment choices are polyether, polyester, polycaprolactone, and polycarbonate.
- The Tg baseline is reproducible and retains its negative fine-tuning transfer result.
- POLLY-MAP alpha implements the intended monotonic, topology-aware crossing model, but serious calibration still requires independent real opening records.
- The live chart uses a separate literature PALS local-cavity proxy where matched evidence exists.
- The additive effective-diameter control is a draggable 2–12 Å slider that updates the size line and crossing temperature.
- The curated evidence contains 63 records, 39 numeric observations, 4 independent papers, 7 polymer series, and 23 live interpolation points.

Polyether TPU now has a five-point matched PALS proxy curve from 268-338 K. Polycarbonate-PU still uses the generic Tg-anchored scenario because a matched numeric temperature-resolved PALS curve has not been found.

## Scientific boundary

PALS cavity diameter is a local free-volume proxy, not a connected transport opening. A size crossing does not establish diffusion, partitioning, migrated mass, leaching, or safety. Serious migration work requires independent polyurethane PALS or validated MD trajectories, held-out chemistry families, diffusion and partition measurements, and external migration or leaching validation.

## Best next task

Curate numeric temperature-resolved polycarbonate polyurethane PALS or validated MD data, and seek an independent non-PEG-blended replication of the current polyether series. Record precise figure/table provenance and source reliability boundaries. Keep papers, formulations, and polymer series separate, then regenerate `artifacts/polly-map-pals-proxy.json`, run all tests, and verify the browser provenance text.

The public mirror intentionally excludes confidential invention-disclosure material, raw training data, downloaded papers, extracted page images, virtual environments, credentials, and local configuration.
