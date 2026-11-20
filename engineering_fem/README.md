# ASC S1 — public engineering finite-element benchmark

**Version:** 0.1 • **Date:** 2026-11-20 • **Author / ASC concept:** P. Gabor  
**Status:** mathematical simulation using illustrative material and geometry assumptions. **Not experimental validation, a confirmed physical ASC design, full piezoelectric FEM, surface acoustic wave (SAW) simulation, or a propulsion result.**

## Purpose

This release adds a physically interpretable, 1-D finite-element (FE) mechanical benchmark to the earlier *synthetic measurement workflow* (which used a generic normalized damped oscillator). It addresses the S1 flat-specimen stage in **ASC Preprint 0.2**. It asks: can a selected bonded, piezo-actuated *cantilever beam* be modeled, its first bending resonances calculated, and its model uncertainty and numerical convergence checked? 

The geometry is a **public numerical example invented for this benchmark**. It is **not** taken from the ASC private design dossier or any planned vehicle part.

## Model and configuration

- 100 mm long × 20 mm wide beam, clamped at the left, free at the right.
- 1.0 mm illustrative aluminum 6061-T6 substrate for the full length.
- 0.3 mm piezoceramic patch from x=0 to 60 mm (uniform, perfectly bonded).
- Linear Euler–Bernoulli composite-beam bending with modulus-weighted neutral axis, effective EI and mass per unit length.
- Cubic Hermite 2-node beam elements with 2 DOFs/node (transverse displacement and slope), **consistent mass matrix**, symmetric generalized eigenproblem `K phi = omega² M phi`.
- Simplified inverse-piezo mechanism: uniform free strain `epsilon_p=d31*V/t_p`, converted to an equivalent local section moment and a FE nodal load. There is **no electrostatic field solve**, no dielectric model and no feedback from structural strain to electrical response.
- Illustrative peak driving voltage 20 V; illustrative modal damping ratio 2%; no assertion that these are correct, efficient or safe for any particular device.
- Reference case: bare aluminum cantilever, for which an established closed-form Euler–Bernoulli first-frequency expression exists.

All selected numerical values and supporting links are in [`public_config.json`](public_config.json). Properties are typical/example assumptions and are **not** a qualified PZT datasheet or a multi-parameter sensitivity analysis.

## Governing equations

`EI(x) = b Sum_i E_i * integral_i (z-zbar)^2 dz`  
`mu(x) = b Sum_i rho_i * (z_i,upper-z_i,lower)`  
`zbar = Sum_i E_i b integral_i z dz / Sum_i E_i A_i`  
`M_act(x) = b Sum_i E_i * epsilon_i * integral_i (z-zbar) dz`  
`K u = f_act; K phi = omega^2 M phi`  
`u(omega) ≈ Sum_{j=1}^{4} phi_j * (phi_j^T f_act)/(omega_j^2-omega^2+2 i zeta omega_j omega)`

The harmonic response uses 4 modal terms. Near a strong peak the response can be particularly sensitive to the assumed damping and to unmodeled fixture, bond and nonlinear effects.

## Quick start

```bash
python -m pip install -r requirements.txt
python run_fem.py
python -m unittest discover -s tests -v
```

The script produces tables, a JSON summary and five PNG plots in `results/`.

## Numerical results (illustrative, not measured)

The model is designed to disclose its own verification details. Inspect `results/summary.json` and the CSV files for exact outputs. The script verifies the bare-beam first frequency against an analytical expression, and compares a 80-element mesh against a 160-element mesh on the composite specimen. It fails with an assertion if either of these checks goes outside the configured numerical tolerances.

**Important:** the frequency response is a 1-D *bending* response below 800 Hz, **not SAW dispersion, phased-array directivity, multi-sector synchronization or any form of propulsive momentum transfer**. No accepted power, RF transfer, electromechanical efficiency or thrust is computed.

## Limits and interpretation

1. 1-D beam approximation: no plate bending or 2-D/3-D stress, radial ring, shell, torsion or anisotropic phononic modes.
2. Linear, small-deflection, perfect-bond assumption; adhesive thickness, hysteresis, loss and substrate tolerances omitted.
3. PZT represented by **one elastic modulus and one d31 coefficient**, not a full material tensor or coupled electromechanical solve.
4. Mode-dependent physical damping is not determined; a constant modal damping ratio is assumed.
5. A clamped cantilever is not necessarily the appropriate fixture for later ASC coupons. Real conditions must be recorded and measured independently.
6. Eigenfrequencies and modal curves are generated from a hypothetical specimen; fitting them to real measurements is future work.
7. No route to vehicle-level performance can be inferred from a coupon bending-mode calculation.
8. All inputs are intended for unrestricted publication; no internal ASC control algorithm, switching scheme, actual operating set point, manufacturing tolerance or unreleased CAD is present.

## Relation to earlier synthetic demonstrations

The earlier `ASC_S1_Preliminary_Synthetic_Simulation` archive contains synthetic normalized second-order responses and a 24-channel phase-error Monte Carlo exercise. It does **not** use FE mechanics or physical material parameters. Do not mix its synthetic numbers with the mechanical FE results without explicitly labeling their separate models and units. The two packages can be stored in the same public GitHub repository under different folders.

## References (background, not ASC validation)

- 6061-T6 typical properties: ASM MatWeb, https://asm.matweb.com/search/SpecificMaterial.asp?bassnum=MA6061T6
- Illustrative PZT values and the need to qualify them: APC International, https://www.americanpiezo.com/apc-materials/physical-piezoelectric-properties/
- Piezoelectric transducer materials review: https://doi.org/10.3390/s20144051
- Example published PZT-5A data (values depend on sample and method): https://pmc.ncbi.nlm.nih.gov/articles/PMC12566301/
- Cantilever Euler–Bernoulli eigenvalues: https://lampz.tugraz.at/~hadley/memm/mechanics/cbeam.php

## Provenance and AI disclosure

The overall ASC concept belongs to P. Gabor's independent development work. Generative AI assisted with creation of **this example FE source code, editorial text and plots**. The numerical output was generated by executing the included Python source. All reported data are simulated, not measurements. No AI output constitutes independent scientific review.

**License:** none is granted in this draft package. The author must choose a public code license (e.g. MIT or BSD-3-Clause) separately before describing the repository as open-source; a public GitHub repository without a license is not automatically free to reuse.
