"""ASC public v0.6. Physics bounds and *illustrative* sector allocation.

No ASC flight hardware, plasma source, 288-cell physical layout or propulsion
performance is established. All values are configurable screening assumptions.
"""
from __future__ import annotations
import math
from typing import Iterable
import numpy as np

C = 299_792_458.0
G0 = 9.80665
SIGMA = 5.670374419e-8


def positive(**values):
    for key, value in values.items():
        if not math.isfinite(float(value)) or float(value) <= 0:
            raise ValueError(f'{key} must be positive and finite')


def frac(**values):
    for key, value in values.items():
        if not math.isfinite(float(value)) or not 0 <= float(value) <= 1:
            raise ValueError(f'{key} must be within [0,1]')


def jet(power_W, isp_s, eta, projection=1.0):
    """Conventional idealized propellant exhaust. F=2 eta P/ve.

    projection is vector alignment of an emitted jet, not phase enhancement.
    """
    positive(power_W=power_W, isp_s=isp_s)
    frac(eta=eta, projection=projection)
    ve = isp_s * G0
    f_magnitude = 2*eta*power_W/ve
    mdot = f_magnitude/ve
    return dict(ve_m_s=ve, jet_kinetic_W=eta*power_W,
                thrust_magnitude_N=f_magnitude, thrust_axial_N=f_magnitude*projection,
                mass_flow_kg_s=mdot, isp_s=isp_s)


def photon(power_W, directionality=1.0):
    positive(power_W=power_W)
    frac(directionality=directionality)
    return power_W/C*directionality


def split_budget(external_W, sector_W, recovery_frac=0., auxiliary_W=0.):
    """P_ext = P_jet + P_sector - P_recovered + P_aux.

    Sector electrical recovery is a fraction of the *same* sector gross load,
    not the unrelated 100-kW v0.5 process ledger. It creates no extra energy.
    """
    positive(external_W=external_W)
    if not all(math.isfinite(x) and x >= 0 for x in (sector_W, auxiliary_W)):
        raise ValueError('sector and auxiliary loads must be finite and nonnegative')
    frac(recovery_frac=recovery_frac)
    rec=sector_W*recovery_frac
    jet_W=external_W-sector_W+rec-auxiliary_W
    if jet_W < 0: raise ValueError('budget exceeds source')
    residual=external_W-(jet_W+sector_W-rec+auxiliary_W)
    return dict(external_W=external_W, sector_gross_W=sector_W,
                sector_recovered_W=rec, auxiliary_W=auxiliary_W,
                jet_available_W=jet_W, balance_residual_W=residual)


def eta_to_break_even(baseline_eta, baseline_jet_W, hybrid_jet_W,
                      baseline_alignment=1., hybrid_alignment=1.):
    positive(baseline_jet_W=baseline_jet_W,hybrid_jet_W=hybrid_jet_W)
    frac(baseline_eta=baseline_eta,baseline_alignment=baseline_alignment,
         hybrid_alignment=hybrid_alignment)
    if hybrid_alignment == 0: return math.inf
    return baseline_eta*baseline_jet_W*baseline_alignment/(hybrid_jet_W*hybrid_alignment)


def rocket_budget(dry_mass_kg, target_delta_v_m_s, power_W, isp_s,
                  eta, axial_factor=1., specific_battery_Wh_kg=200.):
    """Ideal continuous vacuum burn with constant power, ve and alignment.

    Initial wet mass is solved from ideal rocket equation. Fixed dry mass must
    already include full source, radiator, tanks, structure and ancillary gear.
    Battery mass is a diagnostic constraint, NOT added to the assumed dry mass.
    """
    positive(dry_mass_kg=dry_mass_kg,target_delta_v_m_s=target_delta_v_m_s,
             power_W=power_W,isp_s=isp_s,specific_battery_Wh_kg=specific_battery_Wh_kg)
    frac(eta=eta,axial_factor=axial_factor)
    if axial_factor == 0 or eta == 0: raise ValueError('cannot accelerate without kinetic jet and axial impulse')
    j=jet(power_W,isp_s,eta,axial_factor)
    ratio=math.exp(target_delta_v_m_s/(j['ve_m_s']*axial_factor))
    prop=dry_mass_kg*(ratio-1)
    burn_s=prop/j['mass_flow_kg_s']
    energy_kWh=power_W*burn_s/3.6e6
    return dict(target_delta_v_km_h=target_delta_v_m_s*3.6,
        required_mass_ratio=ratio, required_propellant_kg=prop,
        wet_mass_kg=dry_mass_kg+prop,dry_mass_kg=dry_mass_kg,
        constant_power_burn_days=burn_s/86400,
        source_energy_MWh=energy_kWh/1000,
        battery_mass_if_200Wh_kg_kg=energy_kWh*1000/specific_battery_Wh_kg,
        thrust_axial_N=j['thrust_axial_N'], mass_flow_kg_s=j['mass_flow_kg_s'])


def radiator_area(heat_W, temperature_K, emissivity=.85, ambient_K=3.):
    positive(temperature_K=temperature_K,emissivity=emissivity)
    frac(emissivity=emissivity)
    if ambient_K<0 or not math.isfinite(ambient_K) or ambient_K>=temperature_K or heat_W<0:
        raise ValueError('invalid thermal boundary')
    return heat_W/(emissivity*SIGMA*(temperature_K**4-ambient_K**4))


def array_forces(n_sectors=24,cells_per_sector=12,power_W=80_000,
                 eta=.45, isp_s=1500, tilt_deg=0.,radius_m=.5,
                 dead_sectors: Iterable[int] = ()):
    """288 independent hypothetical exhaust elements, equally fed and at fixed radius.

    Angular vectors give only external exhaust momentum, not force generated by
    surface waves. Failed sector power is assumed *not* redistributed.
    """
    if not isinstance(n_sectors,int) or not isinstance(cells_per_sector,int) or n_sectors<2 or cells_per_sector<1:
        raise ValueError('invalid sector array')
    positive(power_W=power_W,isp_s=isp_s,radius_m=radius_m)
    frac(eta=eta)
    if not math.isfinite(tilt_deg) or not 0<=tilt_deg<=90:raise ValueError('tilt must be 0 to 90 degrees')
    dead=set(dead_sectors)
    if any((not isinstance(i,int) or i<0 or i>=n_sectors) for i in dead):raise ValueError('bad dead sector index')
    theta=math.radians(tilt_deg)
    f_one=2*eta*(power_W/(n_sectors*cells_per_sector))/(isp_s*G0)
    r=np.zeros(3)
    m=np.zeros(3)
    for s in range(n_sectors):
        angle=2*math.pi*s/n_sectors
        pos=np.array([radius_m*math.cos(angle),radius_m*math.sin(angle),0.])
        direction=np.array([math.sin(theta)*math.cos(angle),math.sin(theta)*math.sin(angle),math.cos(theta)])
        if s in dead:continue
        force=f_one*direction*cells_per_sector
        r+=force
        m+=np.cross(pos,force)
    theoretical=2*eta*power_W/(isp_s*G0)
    return dict(remaining_sectors=n_sectors-len(dead),total_sectors=n_sectors,
                cells_per_sector=cells_per_sector,installed_cells=n_sectors*cells_per_sector,
                alive_cells=(n_sectors-len(dead))*cells_per_sector,
                force_x_N=float(r[0]), force_y_N=float(r[1]),force_z_N=float(r[2]),
                force_norm_N=float(np.linalg.norm(r)), torque_x_Nm=float(m[0]),
                torque_y_Nm=float(m[1]),torque_z_Nm=float(m[2]),
                torque_norm_Nm=float(np.linalg.norm(m)),
                total_aligned_jet_limit_N=theoretical,
                per_cell_electrical_W=power_W/(n_sectors*cells_per_sector))


def source_envelopes(power_W, solar_flux_W_m2=1361.,solar_eff=.25):
    positive(power_W=power_W,solar_flux_W_m2=solar_flux_W_m2)
    frac(solar_eff=solar_eff)
    if solar_eff==0:raise ValueError('solar efficiency must >0')
    return dict(ideal_1AU_illuminated_solar_area_m2=power_W/(solar_flux_W_m2*solar_eff),
        battery_Wh_per_day=power_W*24)
