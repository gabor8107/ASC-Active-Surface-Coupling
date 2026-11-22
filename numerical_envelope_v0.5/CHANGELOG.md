# Changelog

## v0.5.0 - 22 November 2026 - Hybrid energy-recovery constraint checks

- Added a stand-alone, explicitly hypothetical 100 kW thermal/RF/vibration recovery study; the four ledger categories must be mutually exclusive.
- Added heat-engine Carnot upper bound, vacuum radiative-only area screen, and RF return-availability accounting.
- Added fairer paired comparisons: same useful output / same external supply; both account for controller power and degradation of useful wave/process output.
- Added an illustrative extra-mass penalty sensitivity proxy and break-even conditions (not thrust prediction).
- Added seeded 15,000-parameter input-sweep control (not physical confidence intervals).
- Added six hybrid CSV datasets, a JSON output, five diagnostic PNG figures and 18 automated tests (57 in total).
- The report and PDF include baseline v0.4 content plus distinct hybrid-extension section; no private v0.3 material used.
- Preservation of preprint v0.2 and earlier publicly released code is required; not a replacement for the ASC preprint.

---

# Changelog

## v0.4.0 — 2026-11-22 (public computational add-on)

- New: transparent cylinder-envelope geometry/mass proxy, air drag and ideal momentum-theory hover comparisons.
- New: water buoyancy, hydrostatics, drag and ideal mass-flux studies.
- New: conditional propellant electric-jet momentum/energy, photon recoil, battery and ideal solar-area scale comparisons.
- New: electrical/thermal power-balance scenarios, RF reflection / illustrative ohmic heat.
- New: analytic bare-beam static load/deflection, clock phase tolerance, resonator energy, wavelength/sampling scale and commanded 24-channel phase Monte Carlo with nulls.
- New: explicit sensitivity-envelope simulations with stated distribution assumptions.
- New: 39 independent consistency and boundary tests; machine-readable summary, 16 result tables, 7 figures and 9-page English PDF note.
- Excluded: real ASC geometry, manufacturing detail, propulsor design parameters and all confidential v0.3 materials.

**Compatibility:** additive supplement to v0.2.2 and v0.3 public releases. Does not supersede the 28-page preprint or imply an integrated ASC solver.
