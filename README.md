# ASC - Active Surface Coupling

**Public engineering research release v0.6** | 22 November 2026  
**Concept and research programme:** P. Gabor | Independent researcher, Hungary

ASC is an independent proposal to investigate distributed active surfaces, controlled wave patterns and modular systems engineering. Its long-term drawings use a disc-shaped platform as a visual reference. The actual research begins with small, measurable experiments, ordinary conservation laws and comparisons with simpler designs.

This repository contains the 28-page public architecture preprint, three conceptual drawings, the earlier v0.5 numerical benchmarks and a new v0.6 numerical study of external momentum transfer, power allocation, sector faults, thermal loads and ideal electric-propulsion missions.

**No ASC propulsion device has been constructed or validated. No net thrust, useful coupling gain or flight capability is claimed.** The calculations use disclosed hypothetical values, not confidential ASC design information. The public models do not reproduce a coupled active surface/plasma engine.

## Begin here

1. [Public engineering report v0.6](numerical_envelope_v0.6/docs/ASC_Public_Engineering_Research_v0.6_EN.pdf) - the complete current calculation note (21 pages, including ASC-001/002/003).
2. [ASC architecture preprint 0.2](preprint/ASC_Preprint_0.2_Public_Release_EN_ASC001-003.pdf) - the original 28-page public research programme.
3. [v0.6 assumptions](numerical_envelope_v0.6/config/scenarios.json), [physics source](numerical_envelope_v0.6/src/asc_physics.py), [results](numerical_envelope_v0.6/results/summary_v06.json) and [tests](numerical_envelope_v0.6/tests/test_v06.py).
4. [v0.5 numerical baseline](numerical_envelope_v0.5/) - preserved independently for comparison; it has a different energy boundary.

## The physical question

A segmented active surface cannot, by itself, generate net thrust in a closed system in vacuum. A spacecraft must expel matter or radiation to exchange momentum. This public supplement therefore separates:

- **Internal wave / piezo / RF control:** electrical and mechanical redistribution, with no assigned vacuum thrust.
- **Radiation leaving the vehicle:** photon recoil bounded by `P_out/c`.
- **An actual propellant jet:** conditional `F = 2 eta P_jet / (Isp g0)` after allowing for the electrical budget and emission direction.
- **Recovery of electrical power:** a reduction in source demand only when the recovered power is not counted twice, is available at the bus and exceeds the added losses.

The v0.6 calculation uses **24 conceptual supervisory sectors and 12 illustrative addresses per sector (288 total)**. This is an intentionally simplified counting model, **not** a release of ASC hardware cell density, electrode layout or an established engine architecture.

## Representative results (model assumptions, not measured ASC performance)

At 100 kW external input, 1500 s assumed Isp and 45% jet kinetic efficiency, a conventional ideal propellant-jet comparison gives **6.118 N**. If 20 kW of the same source is allocated to the active surface, with 4.65% recovery of that branch and 350 W auxiliary draw, **80.58 kW** remains for the jet. The integrated jet would need at least **55.85% efficiency** to break even on aligned thrust against the 45% conventional reference. An assumed 58%-efficient jet yields **6.354 N**, but the ASC surface is **not known** to produce such a gain.

At 100 kW of perfectly directed outward radiation, the recoil limit is about **0.334 mN**. The report also includes thrust-vector cancellations, lost-sector moments, heat rejection, the ideal rocket equation, and solar/battery sizing diagnostics. A theoretical delta-v scenario is not an ASC velocity rating or maximum.

For complete numerical values and caveats, see the PDF and CSV tables.

## Reproduce the new results

Python 3.10+ is recommended.

```bash
cd numerical_envelope_v0.6
python -m pip install -r requirements.txt
python run_v06.py
python -m unittest discover -s tests -v
# Optional, to rebuild the PDF:
python -m pip install -r requirements-pdf.txt
python make_report.py
```

To reproduce the preserved v0.5 baseline:

```bash
cd numerical_envelope_v0.5
python -m pip install -r requirements.txt
python run_analysis.py
python run_hybrid_analysis.py
python -m unittest discover -s tests -v
```

At preparation, **45 tests passed for v0.6 and 57 for v0.5**. These are consistency tests of equations and software, not independent experimental verification. The analysis runs locally; it makes no network requests.

## Repository layout

```text
ASC-Active-Surface-Coupling/
  README.md
  CITATION.cff
  CHANGELOG.md
  PUBLISHING_AND_PRIVACY_HU.md
  LICENSE_DECISION.md
  preprint/
    ASC_Preprint_0.2_Public_Release_EN_ASC001-003.pdf
  drawings/
    ASC-001_Full_Structure_Section.png
    ASC-002_General_Arrangement.png
    ASC-003_Exploded_Assembly.png
  numerical_envelope_v0.5/        # preserved previous public benchmark
  numerical_envelope_v0.6/
    config/scenarios.json
    src/asc_physics.py
    run_v06.py
    make_report.py
    tests/test_v06.py
    results/                     # seven data tables plus JSON summary
    figures/                     # seven analysis plots
    docs/ASC_Public_Engineering_Research_v0.6_EN.pdf
```

## Provenance and limits

The three concept illustrations were made with generative-AI assistance and are explanatory, not construction drawings. Computational and editorial assistance was also used to prepare the numerical supplement. All statements remain subject to independent engineering review; the calculations contain no actual measurements of ASC-V.

The project has broader unpublished documentation. **No confidential v0.3 archive, private implementation data, working frequencies, material-stack specification or manufacturing plan is included here.** Public disclosure is not patent protection: further intellectual-property review is advisable before sharing implementation detail.

Public source availability does not itself grant reuse rights; see [LICENSE_DECISION.md](LICENSE_DECISION.md). The author should choose and add a software license before calling the repository open-source.

ASC is separate from the QRUM and MRIT research programmes.

## Related publications

- Zenodo: https://doi.org/10.5281/zenodo.24406624
- Project repository: https://github.com/gabor8107/ASC-Active-Surface-Coupling
- Research page: https://gabor8107.github.io/
