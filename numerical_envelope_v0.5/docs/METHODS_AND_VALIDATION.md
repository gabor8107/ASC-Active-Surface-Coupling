# Methods and verification notes

## Validation terminology

- **Mathematical identity:** derived from conservation / idealized formula under stated boundary conditions.
- **Numerical verification:** equations coded consistently and reproducibly, with independent analytic comparisons and negative controls.
- **Experimental validation:** a built, instrumented specimen matches quantitative predictions with measured uncertainty. **None exists for ASC here**.
- **System qualification:** integrated safety, environmental, structural, functional and operational proof. **Not attempted**.

No result in this repository has experimental validation. The code's tests do not verify the proposal of net propulsion.

## Formula register

| ID | Equation / identity | Application | Key exclusion |
|---|---|---|---|
| G01 | `A≈2πr² + π D H`; `m≈ρ t A + allocated_mass` | proxy construction | not actual curved shell material accounting |
| D01 | `F_D=0.5 ρ V² C_D A` | air / water drag envelope | unknown coefficients and flow regime |
| A01 | `P_induced = W^(3/2)/sqrt(2ρA)` | ideal actuator disk | does not describe ASC air momentum transfer |
| H01 | `F_b=ρ g V_displaced`; `p_gauge=ρgz` | displacement / pressure | net buoyancy and differential pressure require geometry |
| W01 | `T≈ṁ Δu`, `P_jet≈0.5 ṁ Δu²` | ideal stationary-water jet | excludes nozzle/pump efficiencies and nonuniform flow |
| V01 | `T=2ηP/(g0 Isp)`; `ṁ=T/(g0 Isp)` | conditional kinetic jet bound | not a full electric thruster model |
| V02 | `Δv = g0 Isp ln(m0/mf)`; `F_photon = P/c` | independent reference checks | require mass accounting and external emission |
| T01 | `P_e= P_wave + P_losses` | electrical balance | converted wave power ultimately dissipates outside |
| T02 | `Q_net= εσA(T⁴-T_env⁴)` | no-convection radiation scenario | requires unknown emissivity, view factors, real A |
| B01 | `f1=(β1²/(2πL²)) √(EI/(ρA))` | Euler–Bernoulli bare beam | linear/small-deflection assumption |
| B02 | `δ=FL³/(3EI)`, `σroot=FL(h/2)/I` | static bare beam point load | not a composite shell / pressure vessel |
| P01 | `C_m=|mean(exp(i[φk-mθk]))|` | digital phase pattern score | not force, actual SAW or wavefield observation |
| P02 | `Δt=Δφ/(360f)` | phase clock tolerance | does not include real device delays |
| P03 | `U=Q P_loss/(2π f)` | resonator energy identity | no energy gain or thrust |
| S01 | `λ=v_ph/f`, `pitch≈λ/2` | heuristic channel scaling | actual element density depends on dispersion/aperture |
| R01 | `P_accepted/P_in=1-10^(-RL/10)` | RF reference plane mismatch | accepted ≠ useful output |
| R02 | `P_ohmic=N I² R` | generic equal-path wiring loss | ignores actual topology, temperature and parasitics |

## Tests and controls

1. Closed-form analytical baseline for the **public v0.3 bare beam** frequency, distinct from its full FEM.
2. Input invariants: nonnegative speed/force/propellant, valid efficiency, positive material/size values.
3. Limiting cases: drag at V=0 equals zero, no heat implies radiative equilibrium with environment, zero propellant implies zero rocket delta-v.
4. Scaling checks: drag ∝V², drag power ∝V³, ideal hover power ∝W^1.5/A^0.5.
5. Energy/power-balance identity and kinetic-exhaust energy closure.
6. Monte Carlo fixed-seed reproducibility, off-target adjacent azimuthal mode and randomized-phase null.
7. Wave-sampling heuristic backed by elementary λ and perimeter geometry.
8. No measured ASC values or confidential inputs. No positive thrust is derived from internal resonance.

## Known limitations of uncertainty envelopes

Input ranges are **arbitrary public scenario tests** and the independent-uniform sampling assumption may be unrealistic. The quantiles characterize sensitivity to this chosen test distribution only. They should never appear as probability intervals about a physical ASC article.

## What additional data is needed for useful integrated prediction?

Actual specimen geometry; measured dielectric/elastic/piezo constants; modal damping; electrical reference planes; actuator/transducer layout; material density/thickness tolerances; boundary conditions; validated model and measurements of wave velocity/attenuation; fluid flow/force calibration; safe voltage/thermal limits; 3-D structural models; thermal boundary conditions; and measured external momentum transfer. These inputs are not included, nor supplied by images.


## Added in v0.5 - hybrid energy-recovery methods

Power-flow fractions must sum to 1 at the same reference boundary and describe disjoint bins. Captured heat/RF/vibration are **subsets of the respective original loss bins** and cannot be double-counted with existing source recirculation. Thermal-to-electric conversion is bounded by Carnot efficiency and requires rejection of the remaining heat.

The fixed-useful comparison solves `P_internal = P_target / (eta_useful - eta_penalty)` and `P_external = P_internal * (1 - r_capture) + P_aux`, independently of any actual ASC actuator. The fixed-external comparison uses `P_internal = (P_external - P_aux)/(1 - r_capture)`. These are bookkeeping expressions, not claims about regenerative physical hardware.

The extra-mass acceleration ratio is an illustrative *conditional* scaling test **only if** actual thrust tracked the modelled useful output. It does not supply thrust, velocity, or a propulsive coupling mechanism. The 15,000-seed sweep is an uncalibrated assumptions sweep and has no probabilistic interpretation for an actual system.
