# ASC — Public Numerical Engineering Envelope (v0.5)

**PUBLIC — HYPOTHETICAL SURROGATE ENGINEERING CALCULATIONS**  
**Research concept:** P. Gabor · Independent Researcher, Hungary  
**Published as a proposed supplement:** 22 November 2026

> **This repository is NOT a working propulsion simulation, device validation, manufacturing specification, or proof of propulsion.** It is a transparent, independently executable feasibility-screening framework with explicitly *illustrative* inputs. No ASC-specific confidential parameters are used.

## Why this supplement exists

The ASC Preprint 0.2 is an architectural and experimental plan. The earlier v0.2.2 S1 files include a **piezo-patch cantilever FEM** and an independent **synthetic response**. The public v0.3 benchmark adds a **bare cantilever FEM** and a **24-channel phase-noise study**. These are distinct experiments, with distinct equations and scopes.

This additive v0.5 package extends v0.4 and complements those materials with **first-principles constraint checks across the proposed application environments**. It asks: *even under an intentionally simplified model, what conventional forces, mass flows, power, heat and measurement tolerances would have to be accounted for before a real system could make a claim?*

## What is included

| Module | Reproduced outcome | Excluded inference |
|---|---|---|
| Geometry and mass proxy | public cylinder-equivalent skin, mass budget | ASC's actual mass, geometry or integrity |
| Air translation and actuator-disk hover | drag, required air momentum / ideal induced power | surface-wave lift, EHD performance or flight |
| Water | buoyancy, pressure resultant, drag, ideal jet mass flow | sealed hull strength, pump or underwater propulsion |
| Vacuum | propellant-jet kinetic power, mass flow, Isp, photon recoil | reactionless thrust or qualified plasma thruster |
| Electrical & thermal | conversion losses, toy RF return loss and resistive heating | RF design, true efficiencies, cooling qualification |
| Bare beam | analytic bending resonance, load/deflection/stress | ASC shell stress or electromechanical FEM |
| 24-channel synthetic phase | mode-selectivity Monte Carlo and null controls | SAW field, force or sector control hardware |
| Wave sampling scale | wavelength and very rough point-count heuristic | finalized actuator density or frequency |
| Sensitivity envelope | ranges under deliberately chosen uniform input sweeps | empirical uncertainty or statistical confidence in ASC |

All models are independently specified, not a coupled multiphysics vehicle simulation. An apparent match across two different tables must never be treated as integration validation.

## Run

Python 3.10+ recommended:

```bash
python -m pip install -r requirements.txt
python run_analysis.py
python run_hybrid_analysis.py
python -m unittest discover -s tests -v
# Optional PDF: python -m pip install -r requirements-pdf.txt && python make_pdf.py
```

The baseline script regenerates the original v0.4 CSV data, `results/summary.json`, its original Markdown technical report and its **seven original graphs**. The separately run `run_hybrid_analysis.py` regenerates the new v0.5 outputs. Both are required for the combined PDF. Execution is deterministic given the pinned scenario file and recorded seeds. It runs offline.

**New in v0.5:** an auditable 100 kW hybrid thermal/RF/vibration recovery exercise with mutually exclusive power bins, Carnot check, radiator-area lower-complexity estimate, closed-loop external-power comparison, process penalty break-even, optional mass penalty caution, seeded assumptions sweep, 6 CSVs, 5 figures and 18 new unit tests. A 4.65 kW gross capture produces only ~3.01 kW conditional source-power saving at the chosen assumptions; other assumptions produce negative savings. This is not an ASC energy recovery prediction. See [`docs/HYBRID_RECOVERY_TECHNICAL_NOTE_EN.md`](docs/HYBRID_RECOVERY_TECHNICAL_NOTE_EN.md) and [`results/hybrid_summary.json`](results/hybrid_summary.json).

**Start reading:** [`docs/TECHNICAL_REPORT_EN.md`](docs/TECHNICAL_REPORT_EN.md) → [`config/public_scenarios.json`](config/public_scenarios.json) → [`src/models.py`](src/models.py) → tests and numerical tables.

## Notable conditional findings (not real ASC capabilities)

For a **hypothetical** 1 m diameter × 0.25 m equivalent cylinder with arbitrary 1 mm aluminum skin and allocated subsystems (approx. 16.36 kg):

- Its weight is **160.45 N**. A conventional rotor-like actuator disk covering its planform would have an **ideal induced-power lower bound of 1.47 kW**; at an **assumed** figure of merit 0.6, about **2.44 kW** would be required. This does **not** establish that the ASC shell can impart that momentum to air.
- At 10 m seawater depth, gauge pressure multiplied by one horizontal projected face is **78.95 kN**. This is a one-face hydrostatic resultant, **not** a net resultant force on a sealed hull or an estimate of failure capacity.
- At 1 kW and hypothetical 1500 s Isp / 45% kinetic power fraction, an ideal electric propellant jet gives **61.18 mN thrust**, not a design for ASC-V. One day at that input draws **24 kWh** before overheads.
- A 24-channel synthetic command pattern with independent 0.3 rad phase noise gives mean target array factor **0.9577**, with separate adjacent-mode and random-phase nulls. This is a digital phasor exercise, not physical surface-wave coherence.
- A simple wave-scale heuristic predicts that **24 supervisory sectors are not synonymous with 24 physical transducers** at arbitrary high frequencies. No ASC frequency or wave velocity is disclosed or established.

The assumptions, all tables, diagnostics and explicit limitations are in the report.

## Structure

```text
numerical_envelope_v0.4/
├── README.md
├── LICENSE_DECISION.md
├── requirements.txt
├── run_analysis.py
├── run_hybrid_analysis.py
├── requirements-pdf.txt
├── config/hybrid_recovery_scenarios.json
├── src/hybrid_recovery.py
├── config/public_scenarios.json
├── src/models.py
├── tests/test_models.py
├── tests/test_hybrid_recovery.py
├── results/                   # generated tables and machine-readable summary
├── figures/                   # generated diagnostic charts
└── docs/                      # combined PDF, v0.4 core + v0.5 hybrid note
```

## Disclosure, reproducibility and provenance

- **No unpublished geometry, electrode designs, controller implementation, private coefficients, working parameters or private datasets were used.** The confidential v0.3 folder is deliberately absent.
- Numeric assumptions are **generic test examples**, not substitutions for actual missing ASC data. A synthetic input cannot prove that a design will work.
- Reported numerical sensitivity ranges result from hypothetical independent uniform sweeps, **not experimental error bars**.
- Independent test execution verifies code consistency only. External laboratory reproduction is still needed.
- This material neither discloses nor protects any later proprietary innovation or patentable detail. **Review potential prior disclosure and patents before releasing further work.**
- No open-source license is attached automatically; choose one based on intended reuse rights. Do not publish private source material. **Review patent/public disclosure questions before uploading a new revision.**

## Related public releases

- **ASC Preprint 0.2 (28 pages)**: https://doi.org/10.5281/zenodo.24406624
- **Public ASC project GitHub**: https://github.com/gabor8107/ASC-Active-Surface-Coupling
- **Research page**: https://gabor8107.github.io/

**Research status:** exploratory, independent, unreviewed, without an ASC physical prototype or demonstrated system-level thrust, efficiency gain, or environmental operation. ASC is separate from QRUM and MRIT.

## v0.5 publication integrity

- The combined PDF (`docs/ASC_Public_Numerical_Engineering_Envelope_v0.5_EN.pdf`) contains the previously released v0.4 numerical-envelope discussion **and** the independently rerunnable v0.5 hybrid extension. Do not claim that new model parameters come from experiments.
- The single gross-process ledger is explicitly hypothetical and cannot be added to a separate old v0.4 loss ledger as if they describe one physical machine.
- The thermal radiator estimates are independent isolated branches, not a qualified TEG/radiator co-design. Some nominal radiator temperatures cannot simultaneously be the selected 300 K TEG cold sink.
- The separate 28-page public ASC Preprint 0.2 remains the primary architectural reference. Neither that preprint nor the prior public v0.4 should be silently overwritten on Zenodo.
- Existing v0.4 results remain in this folder for reproducibility, while the new `hybrid_*` files make v0.5 additions identifiable.
