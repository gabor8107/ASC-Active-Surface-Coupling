# ASC v0.6 - External-momentum and segmented-power bounds

A standalone, reproducible engineering screening model. All values are hypothetical, including the 24-sector/288-address numerical illustration. No ASC engine is simulated, built or measured.

Run `python -m pip install -r requirements.txt`, then `python run_v06.py`, then `python -m unittest discover -s tests -v`. Rebuild the report with `python -m pip install -r requirements-pdf.txt` and `python make_report.py`.

The source `src/asc_physics.py` contains independent calculations for photon recoil, propellant-jet energy and momentum, closed electrical bus allocation, efficiency break-even, array vector forces, ideal mission rocket mass, effective radiation area and power-source aperture. The model deliberately treats active-surface cell counts as a transparent numerical assumption, not actual ASC geometry.

`results/` contains the regenerated summary JSON and seven CSV datasets; `figures/` contains seven PNG plots. The full English note, `docs/ASC_Public_Engineering_Research_v0.6_EN.pdf`, includes the three public conceptual drawings in the appendix.

**Two separate accounting boundaries must not be combined:** v0.5 models a complete 100 kW hypothetical *process* recovery ledger; v0.6 models a 100 kW external supply split between a notional surface branch and a *separate* jet branch. In v0.6 the 4.65% return is applied to only the 20 kW surface branch, resulting in 0.93 kW recovery; the old 4.65 kW recovery must not be counted again.

A computed break-even efficiency is not evidence that the ASC improves thruster efficiency. The report makes no claim of novel hardware or achieved delta-v. No confidential technical dossier was used.
