# ASC S1: Preliminary Synthetic Measurement Demonstration

**Status:** computational teaching/reference model, **not** experimental evidence, not a material-specific FEM model, not a validated ASC design.

## Objective
Rehearse two tests specified as future objectives in ASC Preprint 0.2 (20 November 2026): (A) S1 flat-coupon comparison against direct drive with repeat trials; (B) sensitivity of a 24-addressable-channel architecture to phase error.
The numbers below are deliberately **illustrative**, not obtained from an ASC specimen or the withheld private engineering dossier.

## Model A — normalized S1 transfer function
A generic damped second-order mode is used:

`H(r) = G / [(r0^2 - r^2) + i*2*zeta*r0*r]`

where `r` is normalized frequency, `r0` the normalized natural frequency, `zeta` the damping ratio, and `G` an arbitrary response scale.
Direct-drive reference: r0=1.00, zeta=0.040, G=1.00.
Hypothetical interface: r0=1.02, zeta=0.046, G=0.95. These settings *do not encode a claimed ASC improvement*; they deliberately make the candidate different to test the comparison pipeline.
Thirty independent synthetic acquisitions are created at each condition using amplitude noise sigma=0.018 and run-to-run gain drift sigma=0.012, both normalized. Error ribbon is approximate 95% confidence interval for the **mean** of simulated repeats, not a real metrology uncertainty budget.

## Model B — 24-channel phase coherence
For independent phase errors `epsilon_i` normally distributed with standard deviation `sigma_phi`, coherence is computed as

`C = |sum(exp(i * epsilon_i))| / 24`.

Six thousand Monte Carlo realizations are evaluated at each phase-error standard deviation from 0 to 90 degrees. The plotted band is the 2.5th–97.5th percentile over simulated realizations.
No actuator coupling, geometry, elastic-wave dispersion, multiphysics model, vehicle motion, or thrust is calculated.

## Illustrative numerical output
- Direct-drive reference: synthetic mean peak 0.996 at normalized frequency 1.000.
- Hypothetical interface: synthetic mean peak 0.794 at normalized frequency 1.014.
- Phase-error SD 0 degrees: coherence 1.000 (simulated 95% range 1.000–1.000).
- Phase-error SD 15 degrees: coherence 0.968 (simulated 95% range 0.947–0.984).
- Phase-error SD 30 degrees: coherence 0.877 (simulated 95% range 0.802–0.935).
- Phase-error SD 60 degrees: coherence 0.593 (simulated 95% range 0.396–0.763).
- Phase-error SD 90 degrees: coherence 0.328 (simulated 95% range 0.097–0.561).

## What this can and cannot answer
It checks that a reproducible sweep, reference comparison, repeated-trial variability, and phase-error sensitivity can be computed and documented. It can help plan sample rates, sensor placement, calibration, acceptance metrics, and negative controls once real hardware parameters exist.
It **cannot** establish an ASC operating frequency, power conversion efficiency, coupling gain, useful surface-wave mode, force generation, novelty, or technical feasibility. It is not evidence for a patent or a Zenodo performance claim.

## Next real-world inputs required
A chosen specimen geometry, verified material properties, mounting conditions, actuator and sensor locations, excitation limits, instrumentation response, calibration, and independent reference measurements. Once available, use a measured FRF and FEM/multiphysics model rather than this toy oscillator.

## Files
`run_simulation.py` (reproducible source), `synthetic_s1_measurements.csv`, `synthetic_24_channel_phase_sensitivity.csv`, two PNG plots. Re-run with Python 3.10+, NumPy, Matplotlib. Random seed 20261120.
