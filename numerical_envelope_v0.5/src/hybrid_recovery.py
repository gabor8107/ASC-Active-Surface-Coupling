"""ASC public *hypothetical* hybrid energy recovery / power-boundary calculations.

No measured ASC data, private design, hardware feasibility claim or propulsion inference.
The three loss bins must be mutually exclusive at a specified power boundary.
"""
from __future__ import annotations
import math

SIGMA = 5.670374419e-8
G0 = 9.80665


def _finite_nonnegative(**vals):
    for name, val in vals.items():
        if not math.isfinite(float(val)) or val < 0:
            raise ValueError(f'{name} must be finite and >= 0')


def _fraction(name, x):
    _finite_nonnegative(**{name: x})
    if x > 1: raise ValueError(f'{name} exceeds 1')


def carnot_limit(hot_K: float, cold_K: float) -> float:
    """Heat engine efficiency upper bound, never a predicted TEG efficiency."""
    if not (math.isfinite(hot_K) and math.isfinite(cold_K) and 0 < cold_K < hot_K):
        raise ValueError('need 0 < T_cold < T_hot')
    return 1.0 - cold_K/hot_K


def recoverable_power(gross_W:float, useful_frac:float, heat_frac:float,
                      rf_frac:float, vibration_frac:float, heat_capture_frac:float,
                      rf_capture_frac:float, vibration_capture_frac:float,
                      rf_availability_frac:float=1.0,
                      hot_K:float=400, cold_K:float=300):
    """Partition: gross = useful + heat + unrecovered RF + unwanted vibration.

    'Heat' EXCLUDES RF/vibration bins, even if those eventually heat elsewhere.
    `rf_availability_frac` excludes reflected energy already returned upstream.
    Recovered heat requires hot/cold reservoirs and residual heat rejection.
    Returns raw recovery BEFORE ancillary loads and process performance changes.
    """
    if not math.isfinite(gross_W) or gross_W <= 0: raise ValueError('gross_W must >0')
    for n,x in [('useful_frac',useful_frac),('heat_frac',heat_frac),('rf_frac',rf_frac),
                ('vibration_frac',vibration_frac),('heat_capture_frac',heat_capture_frac),
                ('rf_capture_frac',rf_capture_frac),('vibration_capture_frac',vibration_capture_frac),
                ('rf_availability_frac',rf_availability_frac)]: _fraction(n,x)
    total=useful_frac+heat_frac+rf_frac+vibration_frac
    if abs(total-1)>1e-10: raise ValueError('power fractions must sum to exactly 1')
    carnot=carnot_limit(hot_K,cold_K)
    if heat_capture_frac > carnot+1e-12:
        raise ValueError('heat electrical recovery cannot exceed Carnot limit')
    heat_W=gross_W*heat_frac
    rf_W=gross_W*rf_frac
    vib_W=gross_W*vibration_frac
    raw_heat=heat_W*heat_capture_frac
    raw_rf=rf_W*rf_capture_frac*rf_availability_frac
    raw_vib=vib_W*vibration_capture_frac
    total_rec=raw_heat+raw_rf+raw_vib
    return dict(gross_W=gross_W,useful_W=gross_W*useful_frac,
       heat_bin_W=heat_W,rf_bin_W=rf_W,vibration_bin_W=vib_W,
       heat_recovered_W=raw_heat,rf_recovered_W=raw_rf,
       vibration_recovered_W=raw_vib,raw_recovered_W=total_rec,
       recovery_frac=total_rec/gross_W,
       heat_to_reject_after_TEG_W=heat_W-raw_heat,
       # This is NOT full-system heat rejection if remaining RF/vibrational energy is dissipated later.
       carnot_limit=carnot,energy_balance_residual_W=gross_W-(gross_W*useful_frac+heat_W+rf_W+vib_W))


def fixed_useful_comparison(gross_base_W, useful_frac, recovery_frac, useful_penalty_frac, aux_W):
    """Same target useful process output; compare source demand with/without recovery.

    Recovery hardware reduces useful output as 'penalty' in units of gross process input.
    Captured losses are looped back to supply bus. Aux draws from external supply.
    Assumes all fractions remain constant across the small internal power adjustment.
    """
    _finite_nonnegative(gross_base_W=gross_base_W,aux_W=aux_W)
    if gross_base_W<=0: raise ValueError('gross_base_W must >0')
    for k,v in [('useful_frac', useful_frac),('recovery_frac',recovery_frac),('useful_penalty_frac',useful_penalty_frac)]: _fraction(k,v)
    if useful_frac==0 or useful_penalty_frac>=useful_frac or recovery_frac>=1:
        raise ValueError('nonphysical useful or recovery fractions')
    target_useful=gross_base_W*useful_frac
    actual_internal=target_useful/(useful_frac-useful_penalty_frac)
    rec=actual_internal*recovery_frac
    net_external=actual_internal-rec+aux_W
    return dict(baseline_external_W=gross_base_W,baseline_useful_W=target_useful,
       hybrid_internal_W=actual_internal,hybrid_useful_W=target_useful,
       hybrid_recovered_W=rec,hybrid_aux_external_W=aux_W,
       hybrid_external_W=net_external,external_savings_W=gross_base_W-net_external,
       relative_savings_frac=(gross_base_W-net_external)/gross_base_W)


def fixed_external_comparison(external_W, useful_frac, recovery_frac, useful_penalty_frac, aux_W):
    """Same external power; compare hypothetical useful process power.

    Single-loop balance: Pext = Pint*(1-r) + Paux. No energy creation.
    """
    _finite_nonnegative(external_W=external_W,aux_W=aux_W)
    if external_W<=aux_W: raise ValueError('external supply must exceed aux power')
    for k,v in [('useful_frac',useful_frac),('recovery_frac',recovery_frac),('useful_penalty_frac',useful_penalty_frac)]:_fraction(k,v)
    if useful_penalty_frac>useful_frac or recovery_frac>=1:
        raise ValueError('nonphysical process')
    gross=(external_W-aux_W)/(1-recovery_frac)
    useful=gross*(useful_frac-useful_penalty_frac)
    base=external_W*useful_frac
    return dict(external_W=external_W,base_useful_W=base,
                hybrid_internal_W=gross,hybrid_recovered_W=gross*recovery_frac,
                hybrid_useful_W=useful,delta_useful_W=useful-base,
                delta_useful_pct=100*(useful/base-1))


def radiator_area_vacuum(rejected_W, radiator_K, space_K=3.0, emissivity=.85,
                         sides_factor=1.0):
    """Effective radiating area, does not design a thermal system or a TEG cold sink."""
    _finite_nonnegative(rejected_W=rejected_W)
    if not all(math.isfinite(x) for x in [radiator_K,space_K,emissivity,sides_factor]):raise ValueError('finite')
    if not (radiator_K>space_K>=0 and 0<emissivity<=1 and sides_factor>0):raise ValueError('invalid radiative boundary')
    return rejected_W/(emissivity*SIGMA*(radiator_K**4-space_K**4)*sides_factor)


def simple_mass_penalty_proxy(base_mass_kg, added_mass_kg, base_useful_W, hybrid_useful_W):
    """ONLY fixed-useful-power-to-thrust conversion hypothetical: acceleration ratio.

    If (and only if) thrust is proportional to these 'useful_W' values,
    ratio a_hyb/a_base = (P_hyb/P_base) * m_base/(m_base+m_extra).
    This cannot be interpreted as ASC lift, thrust or speed.
    """
    if not all(math.isfinite(x) and x>0 for x in [base_mass_kg,base_useful_W,hybrid_useful_W]):
        raise ValueError('base mass / useful powers must be positive')
    _finite_nonnegative(added_mass_kg=added_mass_kg)
    ratio=(hybrid_useful_W/base_useful_W)*(base_mass_kg/(base_mass_kg+added_mass_kg))
    return dict(acceleration_ratio_hybrid_to_base=ratio,
       mass_penalty_frac=added_mass_kg/base_mass_kg,
       hypothetical_acceleration_change_pct=100*(ratio-1))


def break_even_penalty_fraction(useful_frac,recovery_frac,aux_W,base_external_W):
    """Maximum process useful fraction penalty that preserves baseline useful power
    at fixed external supply. Clipped to nonnegative; negative indicates no margin.
    """
    for k,v in [('useful_frac',useful_frac),('recovery_frac',recovery_frac)]:_fraction(k,v)
    _finite_nonnegative(aux_W=aux_W,base_external_W=base_external_W)
    if base_external_W<=0 or recovery_frac>=1 or aux_W>=base_external_W:raise ValueError('invalid supply')
    return useful_frac*(1-(1-recovery_frac)*base_external_W/(base_external_W-aux_W))
