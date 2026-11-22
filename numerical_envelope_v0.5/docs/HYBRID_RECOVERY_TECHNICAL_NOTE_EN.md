# ASC - Public Numerical Engineering Envelope v0.5: Hybrid Recovery Extension

**Technical note | 22 November 2026 | Concept: P. Gabor**  
**PUBLIC, UNREVIEWED, SYNTHETIC ENGINEERING EXAMPLE. NOT ASC VALIDATION.**

## Purpose and relation to the public v0.4 package

This additive numerical study tests a hypothetical hybrid of thermal, reflected RF, and unwanted mechanical-vibration energy recovery. It preserves the earlier v0.4 constraint models, their limitations, and their outputs; it does not replace the 28-page ASC Preprint 0.2 or provide a confidential design. The parameters are arbitrarily chosen for transparent sensitivity testing. No integrated ASC vehicle or engine is modelled, and no actual recovery subsystem has been built or measured.

An energy-recovery subsystem does **not create energy or reactionless propulsion**. Its success criterion is a reduction in external power for the **same independently defined useful work**, or a verified improvement in physical propulsion performance **at equal external input and equal total system mass**. At a real test bench, sensor loading and thermal/mechanical interference can make the new system worse than a simpler baseline.

## 1. Electrical accounting boundary: no overlap among loss bins

One gross process input of **100.0 kW** is allocated to four *disjoint* hypothetical bins: useful process 45.00 kW, thermal 45.00 kW, RF reflection/loss 7.00 kW and unwanted vibration 3.00 kW. These bins do **not** prove that thermal, RF and vibration losses in a real system can be measured independently. Reflected RF that has already returned to the source is **not** available to be recovered again; the RF availability parameter must exclude it. Mechanical wave energy intended for the useful effect is **not** counted as available vibration waste.

In the example only, electric capture fractions are 5% of the heat bin, 30% of the available RF bin, and 10% of the vibration bin. The raw capture is **2.25 + 2.10 + 0.30 = 4.65 kW**, or 4.650% of gross process input. That is recovered output **before controller loads, process degradation, mass and additional thermal hardware**. Energy-balance residual: 0.000000000 W.

## 2. Thermodynamic check and rejected heat

Chosen hot-side temperature: 400 K; cold-side temperature: 300 K. The Carnot upper bound is **25.00%**, versus the example's assumed **5%** electricity from the isolated 45 kW thermal bin. This assumption is below the bound; that does **not** establish a practical thermoelectric conversion efficiency or a physically sustainable temperature gradient. TEG converters also require sustained hot- and cold-side heat exchange. Their electrical output is drawn from the heat stream, and the remaining **42.75 kW** still requires cooling, even before any RF/vibration losses dissipate elsewhere.

A simple vacuum-only Stefan-Boltzmann comparison uses emissivity 0.85, an approximately 3 K external background, one-sided effective radiating area, and radiative-only exchange. It neglects view factor, radiator structure, pump load, hot/cold interface design and real spacecraft conditions:

| Radiator T [K] | Baseline 45 kW [m²] | After 2.25 kW TEG: 42.75 kW [m²] |
|---:|---:|---:|
| 300 | 115.27 | 109.50 |
| 350 | 62.22 | 59.11 |
| 400 | 36.47 | 34.65 |


These figures are **area requirements for that isolated heat stream**, not a viable thermal architecture. If a 300 K cold side is required, its rejection area at 300 K can be much larger than at 400 K. The 350 K and 400 K radiator rows are separate radiative *what-if* cases and must not be combined with the 300 K TEG cold-side assumption without additional thermal architecture and work.

## 3. Same useful output: how much external power is actually saved?

The baseline is 100.00 kW gross and 45.00 kW modelled useful process output. The example adds **0.350 kW** of external auxiliary/control power and assumes a **0.60-percentage-point** useful-process loss per unit gross input (0.60 kW per 100 kW). To restore the *same 45.00 kW* useful process output, the hypothetical hybrid must circulate **101.351 kW** internally, of which **4.713 kW** is returned. External demand becomes **96.989 kW**, a conditional saving of **3.011 kW (3.011%)**.

It would be misleading to label the raw 4.65 kW as this net saving. The external supply must cover the auxiliary controls and must compensate the loss of useful process output. The same-effort model assumes fractions stay constant across small operating point shifts; this is *not* shown for real piezoelectric, RF or thermoelectric hardware.

## 4. Same external supply: additional throughput and hypothetical mass penalty

With external supply fixed at 100.00 kW, the example yields a recirculating gross process flow of **104.510 kW** and a conditional useful-process output of **46.402 kW**, compared with 45.000 kW without recovery: a **1.402 kW (3.116%)** improvement *in the abstract useful-power metric*. No ASC thrust coefficient, efficiency or velocity can be inferred from it.

Additional system mass **8.0 kg** is examined against an unrelated **100.0 kg** notional mass scale, purely as a caution. **If and only if** thrust scaled linearly with the abstract useful output while all other physical variables remained fixed, acceleration would change by **-4.522%** rather than improve. This is **not** a propulsion calculation and cannot supply speed, acceleration or flight claims for ASC.

The illustrative useful-process penalty break-even is **1.942 percentage points of gross** at the given capture and auxiliary assumptions. Above this threshold, at fixed external input, the recovery system delivers less useful-process power than the direct baseline. Negative or poor sensitivity cases must be retained rather than selected out.

## 5. Sensitivity - unknown inputs, not calibrated confidence intervals

A seeded sweep of **15,000** synthetic combinations varies the thermal gradient, fraction of Carnot efficiency, available RF return, vibration capture, auxiliary power, useful-process penalty and added mass. Every range was selected for exploration, **not fitted to hardware**. Draws are independent uniforms; percentiles are NOT confidence intervals, probabilities of ASC success or material-property distributions.

- Equal-useful external saving [kW], arbitrary 5th / median / 95th percentiles: **-2.888 / 0.523 / 4.067**.
- Share of synthetic input combinations yielding electrical saving: **58.9%**. This is NOT a probability that the ASC works.
- Share of synthetic combinations yielding improved mass-adjusted acceleration **under the unsupported linear-thrust proxy assumption**: **2.0%**.

The penalty sweep demonstrates explicitly that larger recovery fractions need not give a system benefit if harvested wave power interferes with useful actuation, if RF return is already accounted for upstream, or if cooling/control adds losses and mass.

## 6. How it could relate to each ASC environment

- **Air:** a thermal or electrical energy saving helps only when compared at equal measured air momentum / static thrust or useful external flow. More available electrical power alone cannot establish lift from a passive or vibrating shell.
- **Water:** a wave-absorbing recovery layer may alter added mass, flow drag, sealing and modal response. The v0.4 hydrostatic one-face resultant is not a hull structural verification.
- **Vacuum:** internal recirculation does not generate net impulse. A real propellant jet or emitted photons must carry momentum away. Recovered energy might reduce prime electrical load for a separately verified electric thruster, but the added radiator and power-handling mass must be included. No 100,000 km/h performance follows from this work.

For any thrust comparison, measure externally transferred momentum and use identical **total system mass, thermal hardware boundary, input energy, initial conditions, propellant inventory, and operating time**. The 100 kW example gives neither working ASC thruster performance nor a means to bypass conservation laws.

## 7. Suggested falsification and hardware-gate measurements

1. Specify electrical reference planes and separately measure forward/reflected power, with proof no reflected watt is counted twice.
2. Calibrate heat flow and hot/cold temperature gradients; determine TEG net electrical delivery after its own pumps and controller consumption.
3. Independently map surface displacement/phase before and after a mechanical harvesting layer is installed; document the degradation in useful actuation.
4. Compare at *matched useful work and matched total system mass*; declare prior thresholds and null controls, including inactive harvesting and unchanged external load.
5. Measure power and uncertainty over repeated thermal cycles; include negative/neutral results and heat-sink limitations.
6. Claim no thrust or propulsive improvement without independent force, fluid momentum, or expelled-propellant diagnostics.

## 8. Reproducibility and publication boundary

Run `python run_analysis.py`, `python run_hybrid_analysis.py`, `python -m unittest discover -s tests -v`, and optionally `python make_pdf.py` after installing the separate PDF requirements. The calculations emit `hybrid_summary.json`, six CSV datasets and five additional PNG graphs. The earlier seven v0.4 graphs and their data remain in this combined release. All inputs are disclosed in `config/hybrid_recovery_scenarios.json`; none derive from private ASC documentation. License and patent questions require independent review before publication.

**Conclusion:** This is numerical bookkeeping and trade-off screening under assumptions, not measured energy recovery, proof of an innovative implementation, or a propulsive device. The only rigorous next step is a calibrated, directly comparable laboratory experiment.
