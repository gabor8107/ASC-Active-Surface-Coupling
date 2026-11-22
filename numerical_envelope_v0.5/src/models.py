"""Public first-principles *scenario* calculations; never ASC performance predictions.

All inputs are explicitly chosen for illustration. No confidential values are used.
No geometry/frequency/efficiency is asserted to represent a built ASC system.
"""
from __future__ import annotations
import math
import numpy as np

SIGMA = 5.670374419e-8
G0 = 9.80665
C0 = 299792458.0


def require_positive(**kwargs):
    if any(not math.isfinite(float(v)) or float(v) <= 0 for v in kwargs.values()):
        raise ValueError('All dimensions / positive physical quantities must be finite and > 0')


def cylinder_proxy(diameter, height, thickness, shell_density, additions):
    """Planar two-face+rim shell proxy. NOT true disc hull geometry or sizing."""
    require_positive(diameter=diameter, height=height, thickness=thickness, shell_density=shell_density)
    radius = diameter / 2.0
    face_area = math.pi * radius**2
    edge_area = diameter * height  # sideways silhouette, NOT rim shell area
    rim_skin_area = math.pi * diameter * height
    skin_area = 2.0*face_area + rim_skin_area
    mass_skin = skin_area * thickness * shell_density  # ignores overlaps, joints, curvature
    assert all(float(v) >= 0 for v in additions.values())
    mass = mass_skin + sum(additions.values())
    vol = face_area * height
    return dict(radius_m=radius, face_area_m2=face_area, side_projected_area_m2=edge_area,
                skin_area_m2=skin_area, ideal_cylindrical_envelope_m3=vol,
                proxy_skin_mass_kg=mass_skin, additions_mass_kg=sum(additions.values()),
                total_proxy_mass_kg=mass)


def drag_force(rho, speed, cd, projected_area):
    require_positive(rho=rho, cd=cd, projected_area=projected_area)
    if speed < 0: raise ValueError('speed must be nonnegative')
    return 0.5*rho*speed**2*cd*projected_area


def drag_electrical_power(rho, speed, cd, area, efficiency):
    require_positive(efficiency=efficiency)
    if efficiency > 1: raise ValueError('efficiency must be <= 1')
    force = drag_force(rho, speed, cd, area)
    return force * speed / efficiency


def ideal_hover_power(mass, rho, effective_disk_area, figure_of_merit=1.0, g=G0):
    """Ideal actuator-disc momentum-theory lower bound scaled by assumed FM.

    Not a model of EHD, surface waves, or a specific propulsor. Output is
    physically conditional upon air being accelerated in a rotor-like wake.
    """
    require_positive(mass=mass,rho=rho,effective_disk_area=effective_disk_area,figure_of_merit=figure_of_merit,g=g)
    if figure_of_merit > 1: raise ValueError('figure_of_merit must be <= 1')
    thrust=mass*g
    induced=thrust**1.5/math.sqrt(2*rho*effective_disk_area)
    return induced/figure_of_merit


def displaced_water(mass, displaced_volume, density, g=G0):
    require_positive(mass=mass,density=density,g=g)
    if displaced_volume < 0: raise ValueError('volume must be nonnegative')
    buoyancy=density*g*displaced_volume
    weight=mass*g
    return dict(weight_N=weight,buoyancy_N=buoyancy,net_upward_N=buoyancy-weight,
                neutral_ballast_kg=density*displaced_volume-mass)


def hydrostatic_pressure(depth, density=1025., g=G0):
    require_positive(density=density,g=g)
    if depth < 0: raise ValueError('depth must be nonnegative')
    return density*g*depth  # gauge; no strength assessment


def water_jet_ideal(force, delta_velocity):
    """Static-water control-volume jet: T=mdot * Δv, Pkin=0.5*mdot*Δv².

    Only useful to bound required water throughput, not a designed pump or nozzle.
    """
    require_positive(delta_velocity=delta_velocity)
    if force < 0: raise ValueError('force must be nonnegative')
    mdot=force/delta_velocity
    return dict(mass_flux_kg_s=mdot,jet_kinetic_W=0.5*mdot*delta_velocity**2)


def electric_thruster(power, isp, kinetic_fraction=0.45, g=G0):
    """Idealized jet kinetic-power equation: eta P = 1/2 mdot ve².

    Omits ionization, divergence, plasma and all thruster hardware; conceptual.
    """
    require_positive(power=power,isp=isp,kinetic_fraction=kinetic_fraction,g=g)
    if kinetic_fraction>1: raise ValueError('fraction must be <= 1')
    ve=isp*g
    thrust=2*kinetic_fraction*power/ve
    mdot=thrust/ve
    return dict(exhaust_velocity_m_s=ve,thrust_N=thrust,mass_flow_kg_s=mdot,
                propellant_kg_per_day=mdot*86400,thrust_per_kW_mN=thrust*1000/(power/1000))


def rocket_delta_v(isp, wet_mass, propellant_mass, g=G0):
    require_positive(isp=isp,wet_mass=wet_mass,g=g)
    if not 0 <= propellant_mass < wet_mass: raise ValueError('propellant must be < wet mass')
    return isp*g*math.log(wet_mass/(wet_mass-propellant_mass))


def photon_thrust(power):
    require_positive(power=power)
    return power/C0


def energy_chain(power, distribution_eff, conversion_eff):
    require_positive(power=power,distribution_eff=distribution_eff,conversion_eff=conversion_eff)
    if distribution_eff>1 or conversion_eff>1: raise ValueError('efficiency <= 1')
    at_converter=power*distribution_eff
    mechanical=at_converter*conversion_eff
    local_losses=power-mechanical
    return dict(electrical_W=power,after_distribution_W=at_converter,
                mechanical_W=mechanical,non_mechanical_losses_W=local_losses,
                energy_balance_residual_W=power-mechanical-local_losses)


def radiation_equilibrium(local_heat, area, emissivity, env_temperature_K=293.15):
    """Simple net-radiation-only surface-temperature scenario; no conduction/convection."""
    require_positive(area=area,emissivity=emissivity,env_temperature_K=env_temperature_K)
    if not 0 < emissivity <= 1 or local_heat < 0: raise ValueError('invalid radiation inputs')
    return (env_temperature_K**4 + local_heat/(emissivity*SIGMA*area))**.25


def cantilever_analytic(E, rho, L, width, thickness, tip_force):
    require_positive(E=E,rho=rho,L=L,width=width,thickness=thickness)
    if tip_force < 0: raise ValueError('tip force must be nonnegative')
    A=width*thickness; I=width*thickness**3/12
    f1=1.875104068711961**2/(2*math.pi*L**2)*math.sqrt(E*I/(rho*A))
    deflection=tip_force*L**3/(3*E*I)
    root_bending_stress=tip_force*L*(thickness/2)/I
    return dict(first_frequency_hz=f1,tip_deflection_m=deflection,
                root_bending_stress_Pa=root_bending_stress)


def jitter_s_for_phase_degrees(freq, degrees):
    require_positive(freq=freq,degrees=degrees)
    return degrees/360/freq


def stored_energy_from_q_loss(q, loss_W, frequency_hz):
    require_positive(q=q,loss_W=loss_W,frequency_hz=frequency_hz)
    return q*loss_W/(2*math.pi*frequency_hz)


def synthetic_mode_score(phases, order):
    """Normalized command-space DFT phasor coherence, NOT propagated-wave field."""
    phases=np.asarray(phases, dtype=float)
    n=phases.shape[-1]
    if n < 2: raise ValueError('need >=2 channels')
    theta=2*np.pi*np.arange(n)/n
    return np.abs(np.exp(1j*(phases-order*theta)).mean(axis=-1))


def mode_monte_carlo(n=24, order=3, sigma=.3, trials=20000, seed=20261122):
    if n < 2 or trials < 10 or sigma < 0 or not math.isfinite(sigma): raise ValueError('invalid phase experiment')
    rng=np.random.default_rng(seed)
    theta=2*np.pi*np.arange(n)/n
    commands=order*theta
    samples=commands+rng.normal(0,sigma,(trials,n))
    target=synthetic_mode_score(samples,order)
    wrong=synthetic_mode_score(samples,(order+1)%n)
    # Equal size randomized-phase null, not necessarily a physical null.
    null=rng.uniform(-np.pi,np.pi,(trials,n))
    null_score=synthetic_mode_score(null,order)
    return dict(sigma_rad=sigma,mean=float(np.mean(target)),p05=float(np.quantile(target,.05)),
                p95=float(np.quantile(target,.95)),wrong_mode_mean=float(np.mean(wrong)),
                random_null_mean=float(np.mean(null_score)),
                analytic_large_n_approx=float(math.exp(-.5*sigma*sigma)))


def uncertainty_envelope(n, seed, mass_minmax, diameter_minmax, hover_eff_range,
                         water_cd_range, water_speed, water_eff_range, rho_air, rho_water, height):
    """Scenario sensitivity distributions, NOT empirical confidence intervals."""
    rng=np.random.default_rng(seed)
    mass=rng.uniform(*mass_minmax,n)
    D=rng.uniform(*diameter_minmax,n)
    FM=rng.uniform(*hover_eff_range,n)
    cd=rng.uniform(*water_cd_range,n)
    eta=rng.uniform(*water_eff_range,n)
    area=np.pi*(D/2)**2
    induced=(mass*G0)**1.5/np.sqrt(2*rho_air*area)/FM
    underwater=0.5*rho_water*water_speed**3*cd*(D*height)/eta
    def stats(a): return dict(p05=float(np.quantile(a,.05)),median=float(np.median(a)),p95=float(np.quantile(a,.95)))
    return dict(hover_power_W=stats(induced),water_edge_motion_power_W=stats(underwater),
                inputs='Independent uniform hypothetical parameter sweeps: not physical uncertainty distributions')


def wave_sampling_scale(phase_velocity, frequency, circumference, samples_per_wavelength=2):
    """Elementary spatial-sampling *heuristic*, not an actual SAW array design."""
    require_positive(phase_velocity=phase_velocity,frequency=frequency,circumference=circumference,samples_per_wavelength=samples_per_wavelength)
    wavelength=phase_velocity/frequency
    pitch=wavelength/samples_per_wavelength
    return dict(wavelength_m=wavelength,sampling_pitch_m=pitch,minimum_points_around_ring=math.ceil(circumference/pitch))

def delivered_fraction_from_return_loss(return_loss_db):
    """At a defined reference plane, accepted fraction = 1 - |Gamma|²; not efficiency."""
    if return_loss_db < 0: raise ValueError('return loss positive dB by convention')
    return 1-10**(-return_loss_db/10)

def ohmic_heat(channel_current, resistance, channels):
    require_positive(resistance=resistance,channels=channels)
    if channel_current < 0: raise ValueError('negative current magnitude')
    return channels*channel_current**2*resistance
