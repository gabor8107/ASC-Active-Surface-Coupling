#!/usr/bin/env python3
"""Rebuild every result table, figure and technical report from public inputs.

Usage: python run_analysis.py [--output-dir results]
No private ASC parameters or measured ASC data are read.
"""
from __future__ import annotations
import argparse
import csv
import hashlib
import json
import math
import platform
import sys
from datetime import date
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

ROOT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT/'src'))
from models import (G0, cylinder_proxy, drag_force, drag_electrical_power, ideal_hover_power,
 displaced_water, hydrostatic_pressure, water_jet_ideal, electric_thruster, rocket_delta_v,
 photon_thrust, energy_chain, radiation_equilibrium, cantilever_analytic, jitter_s_for_phase_degrees,
 stored_energy_from_q_loss, mode_monte_carlo, uncertainty_envelope, wave_sampling_scale,
 delivered_fraction_from_return_loss, ohmic_heat)


def save_csv(path, rows):
    if not rows: return
    path.parent.mkdir(parents=True,exist_ok=True)
    with path.open('w',newline='',encoding='utf-8') as f:
        w=csv.DictWriter(f, fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)


def save_figure(name):
    plt.grid(alpha=.15);plt.tight_layout();plt.savefig(ROOT/'figures'/name,dpi=170);plt.close()


def rd(x,n=4):return round(float(x),n)


def main():
    p=argparse.ArgumentParser();p.add_argument('--output-dir', default='results');args=p.parse_args()
    out=ROOT/args.output_dir;out.mkdir(parents=True,exist_ok=True)
    (ROOT/'figures').mkdir(exist_ok=True)
    cfg=json.loads((ROOT/'config/public_scenarios.json').read_text(encoding='utf-8'))
    geo=cfg['geometry'];env=cfg['environment'];air=cfg['aerodynamics'];water=cfg['hydrodynamics'];ep=cfg['electric_propulsion'];th=cfg['thermal'];beam=cfg['beam_public_v03'];phase=cfg['phase']
    geometry=cylinder_proxy(geo['diameter_m'],geo['envelope_height_m'],geo['equivalent_shell_thickness_m'],geo['shell_density_kg_m3'],
                          {key:geo[key] for key in ('frame_mass_kg','controls_mass_kg','sensors_mass_kg','energy_storage_mass_kg')})
    mass=geometry['total_proxy_mass_kg']; gravity=env['gravity_m_s2'];rhoair=env['air_density_kg_m3'];rhow=env['seawater_density_kg_m3']
    rows={}

    # Geometry: geometric proxy intentionally lacks a manufacturing description.
    rows['geometry']=[{'quantity':key,'value_SI':rd(val,8)} for key,val in geometry.items()]
    rows['air_drag']=[]
    for view,area in (('edge',geometry['side_projected_area_m2']),('face',geometry['face_area_m2'])):
        for cd in air['air_cd_sweep']:
            for speed in air['air_speeds_m_s']:
                F=drag_force(rhoair,speed,cd,area)
                P=drag_electrical_power(rhoair,speed,cd,area,air['propulsive_efficiency_assumption'])
                rows['air_drag'].append({'orientation':view,'Cd_assumed':cd,'speed_m_s':speed,'drag_N':rd(F,4),'mechanical_power_W':rd(F*speed,3),'electrical_power_W':rd(P,3)})

    rows['air_hover']=[]
    Fgrav=mass*gravity
    Pideal=ideal_hover_power(mass,rhoair,geometry['face_area_m2'],1)
    Passumed=ideal_hover_power(mass,rhoair,geometry['face_area_m2'],air['ideal_actuator_disk_figure_of_merit'])
    for P in air['comparison_electrical_powers_W']:
        rows['air_hover'].append({'assumed_electric_input_W':P,'weight_N':rd(Fgrav),
           'required_thrust_to_power_N_per_W':rd(Fgrav/P,6),
           'ideal_actuator_disk_induced_power_W':rd(Pideal,3),
           'induced_power_with_assumed_FM_W':rd(Passumed,3),
           'power_sufficient_under_FM_scenario':bool(P>=Passumed)})

    rows['water_buoyancy']=[]
    for fraction in water['displaced_envelope_fractions']:
        displacement=geometry['ideal_cylindrical_envelope_m3']*fraction
        for density_name,density in [('freshwater',env['freshwater_density_kg_m3']),('seawater',rhow)]:
            d=displaced_water(mass,displacement,density)
            rows['water_buoyancy'].append({'sealed_displacement_fraction':fraction,'medium':density_name,
                 'displaced_m3':rd(displacement,6),**{k:rd(v,3) for k,v in d.items()}})

    rows['water_pressure']=[]
    for depth in water['depths_m']:
        pressure=hydrostatic_pressure(depth,rhow,gravity)
        rows['water_pressure'].append({'depth_m':depth,'gauge_pressure_kPa':rd(pressure/1e3,3),
             'one_face_resultant_N':rd(pressure*geometry['face_area_m2'],2),
             'note':'gross one-face pressure resultant only; not net closed-hull force or pressure capacity'})

    rows['water_drag']=[]
    for view,area in (('edge',geometry['side_projected_area_m2']),('face',geometry['face_area_m2'])):
        for cd in water['water_cd_sweep']:
            for speed in water['water_speeds_m_s']:
                F=drag_force(rhow,speed,cd,area)
                P=drag_electrical_power(rhow,speed,cd,area,water['total_propulsive_efficiency_assumption'])
                rows['water_drag'].append({'orientation':view,'Cd_assumed':cd,'speed_m_s':speed,'drag_N':rd(F,3),
                                         'effective_mechanical_power_W':rd(F*speed,3),'nominal_electric_power_W':rd(P,2)})
    rows['water_jet']=[]
    for F in [10,100,300]:
        for dv in water['illustrative_jet_velocity_change_m_s']:
            j=water_jet_ideal(F,dv)
            rows['water_jet'].append({'required_thrust_N':F,'jet_speed_increment_m_s':dv,
                                     'ideal_water_flow_kg_s':rd(j['mass_flux_kg_s'],4),'minimum_jet_kinetic_W':rd(j['jet_kinetic_W'],4)})

    rows['vacuum_electric']=[]
    for P in ep['electric_powers_W']:
        for isp in ep['specific_impulses_s']:
            electric=electric_thruster(P,isp,ep['power_to_jet_kinetic_fraction'])
            burn_h=1
            rows['vacuum_electric'].append({'input_W':P,'Isp_s':isp,'assumed_kinetic_fraction':ep['power_to_jet_kinetic_fraction'],
                     'thrust_mN':rd(electric['thrust_N']*1000,4),'mdot_mg_s':rd(electric['mass_flow_kg_s']*1e6,6),
                     'ideal_propellant_kg_day':rd(electric['propellant_kg_per_day'],5),
                     'approx_delta_v_1h_m_s_constant_mass':rd(electric['thrust_N']*3600/mass,4),
                     'photon_thrust_at_equal_power_uN':rd(photon_thrust(P)*1e6,5),
                     'ideal_battery_kg_for_24h':rd(24*P/ep['battery_specific_energy_Wh_kg'],2),
                     'ideal_solar_area_m2_at_1au':rd(P/(env['solar_flux_1au_W_m2']*ep['solar_cell_efficiency_1au']),3),
                     'ideal_rocket_delta_v_for_propellant_m_s':rd(rocket_delta_v(isp,mass,ep['illustrative_propellant_mass_kg']),2)})

    rows['thermal']=[]
    for P in th['electrical_input_W']:
        c=energy_chain(P,th['distribution_efficiency'],th['mechanical_conversion_efficiency'])
        surface=geometry['skin_area_m2']*th['effective_radiating_area_fraction']
        T=radiation_equilibrium(c['non_mechanical_losses_W'],surface,th['emissivity'],env['radiation_background_temperature_K'])
        rows['thermal'].append({'input_W':P,'useful_mechanical_or_wave_W':rd(c['mechanical_W'],2),
            'locally_dissipated_W':rd(c['non_mechanical_losses_W'],2),
            'net_radiation_only_surface_temperature_C':rd(T-273.15,2),
            'energy_balance_residual_W':rd(c['energy_balance_residual_W'],10)})

    rows['beam']=[]
    for F in beam['tip_force_N']:
        s=cantilever_analytic(beam['E_Pa'],beam['density_kg_m3'],beam['length_m'],beam['width_m'],beam['thickness_m'],F)
        rows['beam'].append({'tip_load_N':F,'bare_cantilever_first_mode_hz':rd(s['first_frequency_hz'],6),
            'tip_displacement_mm_linear_model':rd(s['tip_deflection_m']*1000,5),
            'max_root_bending_stress_MPa_linear_model':rd(s['root_bending_stress_Pa']/1e6,6),
            'relative_tip_displacement_to_length':rd(s['tip_deflection_m']/beam['length_m'],8)})

    rows['phase']=[]
    for sigma in phase['phase_std_rad']:
        z=mode_monte_carlo(phase['channels'],phase['azimuthal_order'],sigma,phase['randomized_trials'],phase['seed'])
        rows['phase'].append({k:rd(v,6) if isinstance(v,(int,float)) else v for k,v in z.items()})
    rows['phase_timing']=[]
    for f in phase['clock_frequencies_hz']:
        for limit in phase['phase_error_degree_limits']:
            rows['phase_timing'].append({'frequency_hz':f,'allowed_phase_degrees':limit,
                'max_time_offset_us':rd(jitter_s_for_phase_degrees(f,limit)*1e6,7)})
    rows['resonance_energy']=[]
    for f in [1000,10000,100000]:
        for Q in [10,100,1000]:
            U=stored_energy_from_q_loss(Q,5,f)
            rows['resonance_energy'].append({'frequency_hz':f,'Q_hypothetical':Q,'loss_W':5,
                                             'stored_resonator_energy_J':rd(U,9)})

    rows['wave_sampling']=[]
    ws=cfg['waves']
    for velocity in ws['hypothetical_phase_velocities_m_s']:
        for f in ws['frequency_sweep_hz']:
            val=wave_sampling_scale(velocity,f,math.pi*geo['diameter_m'],ws['illustrative_samples_per_wavelength'])
            rows['wave_sampling'].append({'assumed_phase_velocity_m_s':velocity,'frequency_hz':f,
               'wavelength_mm':rd(1000*val['wavelength_m'],4),
               'simple_two_samples_pitch_mm':rd(1000*val['sampling_pitch_m'],4),
               'perimeter_positions_heuristic':val['minimum_points_around_ring'],
               'note':'Not the number of control sectors or an actual transducer design'})

    rows['rf_bookkeeping']=[]
    rf=cfg['rf_bookkeeping']
    for rl in rf['hypothetical_return_loss_dB']:
        delivered=delivered_fraction_from_return_loss(rl)
        rows['rf_bookkeeping'].append({'calculation':'reflection_at_defined_reference_plane',
           'return_loss_positive_dB':rl,'accepted_power_fraction':rd(delivered,6),
           'accepted_power_W':rd(rf['input_W']*delivered,3),
           'reflected_power_W':rd(rf['input_W']*(1-delivered),3),
           'note':'Reflected power is not necessarily heat; cannot infer coupling efficiency'})
    rows['ohmic_heat']=[]
    for R in rf['wire_resistance_ohm_each']:
        for I in rf['channel_current_A']:
            rows['ohmic_heat'].append({'channels_hypothetical':rf['channel_count'],
               'current_per_channel_A':I,'equivalent_resistance_ohm_each':R,
               'total_ohmic_W':rd(ohmic_heat(I,R,rf['channel_count']),5),
               'note':'Assumes one equivalent resistive path per channel; not actual ASC wiring'})

    sweeps=cfg['uncertainty_envelope']
    uncertain=uncertainty_envelope(sweeps['sample_count'],sweeps['seed'],sweeps['mass_uniform_kg'],sweeps['diameter_uniform_m'],
                                   sweeps['hover_efficiency_uniform'],sweeps['water_Cd_uniform'],sweeps['water_speed_m_s'],
                                   sweeps['water_efficiency_uniform'],rhoair,rhow,geo['envelope_height_m'])
    for k,v in rows.items():save_csv(out/(k+'.csv'),v)
    # Repeatable summary with traceable assumptions / exact source hash.
    summary={'project':'ASC public computational envelope v0.4',
        'publication_status':'Numerical hypothetical scenarios only; NOT ASC device simulation or experimental validation',
        'configuration_sha256':hashlib.sha256((ROOT/'config/public_scenarios.json').read_bytes()).hexdigest(),
        'scenario':{'diameter_m':geo['diameter_m'],'height_m':geo['envelope_height_m'],'proxy_mass_kg':mass,
              'no_use_of_confidential_inputs':True},
        'results':{'shell_mass_kg':geometry['proxy_skin_mass_kg'],'weight_N':Fgrav,
            'minimum_ideal_air_hover_power_W':Pideal,'assumed_FM_air_hover_power_W':Passumed,
            'seawater_pressure_force_at_10m_one_face_N':next(r['one_face_resultant_N'] for r in rows['water_pressure'] if r['depth_m']==10),
            'electric_thruster_1000W_1500s_thrust_mN':next(r['thrust_mN'] for r in rows['vacuum_electric'] if r['input_W']==1000 and r['Isp_s']==1500),
            'phase_MC_sigma_0_3_mean':next(r['mean'] for r in rows['phase'] if r['sigma_rad']==0.3),
            'sensitivity_envelopes':uncertain},
        'validity':'All numerical outputs are conditional on public hypothetical input values. No propulsive performance is attributed to ASC.',
        'environment':{'python':platform.python_version(),'numpy':np.__version__,'matplotlib':matplotlib.__version__},
        'methodology_reference_links':[
          'https://www1.grc.nasa.gov/beginners-guide-to-aeronautics/drag-equation/',
          'https://www1.grc.nasa.gov/beginners-guide-to-aeronautics/rocket-thrust-equation/',
          'https://www1.grc.nasa.gov/beginners-guide-to-aeronautics/specific-impulse/',
          'https://www.nasa.gov/smallsat-institute/sst-soa/in-space_propulsion/']}
    (out/'summary.json').write_text(json.dumps(summary,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')

    # Figures use matplotlib default color cycle; no mock measurement data.
    for medium in ('air','water'):
        key='air_drag' if medium=='air' else 'water_drag'
        speeds=air['air_speeds_m_s'] if medium=='air' else water['water_speeds_m_s']
        cds=air['air_cd_sweep'] if medium=='air' else water['water_cd_sweep']
        plt.figure(figsize=(7.8,4.8))
        for cd in cds:
            sub=[r for r in rows[key] if r['orientation']=='edge' and r['Cd_assumed']==cd]
            vals=[r['drag_N'] for r in sub]
            plt.plot(speeds,vals,marker='o',label=f'Hypothetical Cd={cd}')
        plt.xlabel('Relative speed [m/s]');plt.ylabel('Estimated drag [N]')
        plt.title(f'{medium.title()}: edge-on silhouette / drag uncertainty (illustrative)')
        plt.legend();save_figure(f'{medium}_edge_drag.png')

    plt.figure(figsize=(7.8,4.8))
    for isp in ep['specific_impulses_s']:
        sub=[r for r in rows['vacuum_electric'] if r['Isp_s']==isp]
        plt.plot([r['input_W'] for r in sub],[r['thrust_mN'] for r in sub],marker='o',label=f'Isp {isp} s')
    plt.xlabel('Electrical input [W]');plt.ylabel('Idealized jet thrust [mN]')
    plt.title('Electric-propulsion energy/momentum boundary (not ASC prediction)')
    plt.legend();save_figure('vacuum_thrust_vs_power.png')

    plt.figure(figsize=(7.8,4.8))
    ss=[r['sigma_rad'] for r in rows['phase']]
    for k,label in [('mean','Requested azimuthal mode'),('wrong_mode_mean','Adjacent mode'),('random_null_mean','Uniform-random null')]:
        plt.plot(ss,[r[k] for r in rows['phase']],marker='o',label=label)
    plt.plot(ss,[r['analytic_large_n_approx'] for r in rows['phase']],linestyle='--',label='exp(-sigma²/2) approximation')
    plt.xlabel('Independent phase perturbation σ [rad]');plt.ylabel('Normalized array factor (0..1)')
    plt.title('Command-space phase pattern sensitivity / 24 channels')
    plt.ylim(0,1.05);plt.legend();save_figure('phase_mode_controls.png')

    plt.figure(figsize=(7.8,4.8))
    sample=[r for r in rows['water_buoyancy'] if r['medium']=='seawater']
    plt.plot([r['sealed_displacement_fraction'] for r in sample],[r['neutral_ballast_kg'] for r in sample],marker='o')
    plt.axhline(0,linestyle='--');plt.xlabel('Fraction of ideal cylinder displacement [-]')
    plt.ylabel('Extra mass for neutral buoyancy [kg] (+ ballast / - flotation)')
    plt.title('Seawater buoyancy sensitivity / cylindrical envelope proxy')
    save_figure('water_buoyancy.png')

    plt.figure(figsize=(7.8,4.8))
    x=[r['input_W'] for r in rows['thermal']]
    plt.plot(x,[r['non_mechanical_losses_W'] if 'non_mechanical_losses_W' in r else r['locally_dissipated_W'] for r in rows['thermal']],marker='o',label='Local non-mechanical heat [W]')
    plt.plot(x,[r['useful_mechanical_or_wave_W'] for r in rows['thermal']],marker='o',label='Converted work/wave [W]')
    plt.xlabel('Electrical input [W]');plt.ylabel('Power [W]')
    plt.title('Illustrative power partition, not ASC coupling efficiency')
    plt.legend();save_figure('energy_partition.png')

    plt.figure(figsize=(7.8,4.8))
    for v in ws['hypothetical_phase_velocities_m_s']:
        sub=[r for r in rows['wave_sampling'] if r['assumed_phase_velocity_m_s']==v]
        plt.plot([r['frequency_hz']/1e3 for r in sub],
                 [r['perimeter_positions_heuristic'] for r in sub],marker='o',label=f'Assumed phase speed {v} m/s')
    plt.xscale('log');plt.yscale('log')
    plt.xlabel('Illustrative frequency [kHz]');plt.ylabel('Simple perimeter sampling positions [-]')
    plt.title('Sampling-scale heuristic ≠ 24 independently supervised sectors')
    plt.legend();save_figure('wave_sampling_scale.png')

    write_report(cfg,geometry,rows,summary,ROOT/'docs'/'TECHNICAL_REPORT_EN.md')
    print(json.dumps({'status':'ok','output_tables':len(rows),'figures':len(list((ROOT/'figures').glob('*.png'))),
                      'summary':summary['results']},indent=2))


def write_report(cfg,g,rows,s,path):
    R=s['results'];unc=R['sensitivity_envelopes'];mass=g['total_proxy_mass_kg']
    def get(table,**kv):return next(row for row in rows[table] if all(row[k]==v for k,v in kv.items()))
    air=get('air_drag',orientation='edge',Cd_assumed=0.6,speed_m_s=20.0)
    water=get('water_drag',orientation='edge',Cd_assumed=0.6,speed_m_s=2)
    seawater=get('water_buoyancy',sealed_displacement_fraction=0.65,medium='seawater')
    thr=get('vacuum_electric',input_W=1000,Isp_s=1500)
    t=get('thermal',input_W=1000)
    b=get('beam',tip_load_N=0.01)
    p=get('phase',sigma_rad=0.3)
    text=f'''# ASC — Public Numerical Engineering Envelope, v0.4

**Report type:** Preliminary, independent calculations under *explicitly hypothetical public inputs*  
**Publication status:** Unreviewed computational supplement; no physical device or measured ASC performance  
**Author of underlying ASC concept:** P. Gabor  
**Release:** 22 November 2026  
**Relationship:** Additive GitHub supplement; it does **not** replace the 28-page ASC Preprint 0.2 or earlier S1 FEM and synthetic releases.

## Executive finding

The reproducible calculations quantify what a selected *generic* 1.0 m diameter, 0.25 m high cylindrical-envelope surrogate would demand under conventional physics. **These are feasibility-screening numbers, not a virtual prototype and not evidence of ASC propulsion.** Air, water, and vacuum require different external momentum paths. Surface-wave coherence alone cannot produce net force in a closed system.

## Headline output: one public surrogate

| Quantity | Computed value | Meaning / caution |
|---|---:|---|
| Planar-two-face-plus-rim proxy area | {g['skin_area_m2']:.3f} m² | Simplified skin area, not real shell geometry |
| Proxy aluminum skin mass | {g['proxy_skin_mass_kg']:.2f} kg | Assumes 1 mm equivalent skin thickness |
| Proxy total mass incl. arbitrary subsystems | {mass:.2f} kg | Not a mass estimate for ASC |
| Weight at sea level | {R['weight_N']:.1f} N | Conventional weight |
| Ideal momentum-theory hover power | {R['minimum_ideal_air_hover_power_W']:.1f} W | Actuator-disk lower bound, not a shell-wave thrust model |
| Hover power with hypothetical FM 0.6 | {R['assumed_FM_air_hover_power_W']:.1f} W | Requires a *real* air-accelerating propulsor |
| Air edge-on drag, 20 m/s, Cd 0.6 | {air['drag_N']:.1f} N | Not a measured disc aerodynamic coefficient |
| Air edge-on electrical power at 65% assumed efficiency | {air['electrical_power_W']:.1f} W | Steady-motion drag-work estimate |
| Seawater edge-on drag, 2 m/s, Cd 0.6 | {water['drag_N']:.1f} N | Not a CFD or wave-propulsion result |
| Water electrical power at assumed 50% efficiency | {water['nominal_electric_power_W']:.1f} W | Steady-moving vehicle estimate |
| Seawater 65% volume: extra neutral ballast mass | {seawater['neutral_ballast_kg']:.1f} kg | Depends strongly on actual water displacement |
| Depth 10 m: gauge pressure resultant on one face | {R['seawater_pressure_force_at_10m_one_face_N']:.0f} N | Does not imply equivalent net hull force or stress limit |
| Electric jet, 1 kW, 1500 s, kinetic fraction 0.45 | {thr['thrust_mN']:.1f} mN | Generic idealized propellant jet, not designed ASC-V |
| 1 kW, same jet: one-day propellant use | {thr['ideal_propellant_kg_day']:.3f} kg | Assumes continuous electric power is provided |
| 1 kW electric input, heat from efficiency chain | {t['locally_dissipated_W']:.1f} W | Conversion assumptions arbitrary; work may dissipate later |
| Bare cantilever, 0.01 N tip force: deflection | {b['tip_displacement_mm_linear_model']:.4f} mm | Reuses v0.3 public illustrative coupon properties |
| Bare cantilever first bending frequency | {b['bare_cantilever_first_mode_hz']:.5f} Hz | No piezo patch, no ASC shell modes |
| Command-space 24-ch coherence for σ=0.3 rad | {p['mean']:.4f} | Non-physical pattern-control toy experiment |

## 1. What has and has not been modeled

**Computed:** cylinder-envelope geometry and rough mass accounting; standard quadratic drag; actuator-disk induced-power benchmark; hydrostatics, buoyancy, water-jet mass flow; ideal electrical jet and photon momentum; energy partition and radiative-only thermal balance; bare-beam linear bending; abstract multi-channel phase robustness; clock timing tolerance; normalized resonator energy identity; illustrative parameter sensitivity.

**Not computed:** a feasible integrated hull; material/fastener sizing; structural safety factor; a coupled 3-D electromechanical solver; SAW/phononic/photonic energy transfer; full RF matching; air or water flow generated by ASC; EHD corona and ion drift; CFD; plasmas or magnetic coils; actual thrust; lift; underwater pressure integrity; flight stability; power generation; validated cooling; operating frequencies or manufacturing instructions. Those outputs require geometry, measured material constants, control implementation, hardware and calibration data *not released and not assumed here*.

## 2. Construction proxy, mass, buoyancy and hydrostatic loading

The deliberate surrogate is a cylinder with diameter **1.0 m**, height **0.25 m**, an imaginary uniform **1 mm** aluminum shell, and arbitrarily assigned frame/equipment masses. Skin area is `2 π r² + π D H`; envelope volume is `π r² H`. The real disc is not a cylinder, and a drawing cannot supply its structural stiffness or displaced volume.

The displacement assumptions sweep **30%, 65%, 100% of the cylindrical envelope**, not actual flood-state measurements. For 65% seawater displacement, the extra mass required for neutral buoyancy in the simplistic model is **{seawater['neutral_ballast_kg']:.1f} kg**; a true hull may instead be flooded, vented or have substantially less sealed volume. A 10 m hydrostatic gauge pressure produces **{R['seawater_pressure_force_at_10m_one_face_N']:.0f} N** when multiplied by the chosen horizontal face area; this is a **single-face pressure resultant**, *not* a calculated failure load or net force on the closed hull. Plate bending, attachments, seals, buckling, fatigue and margins require a full model.

## 3. Air: hover and translation

NASA's conventional drag relation is `D = 0.5 ρ V² Cd A` [1]. For the illustrative edge silhouette (D × H), assumed Cd 0.6 and 20 m/s, drag is **{air['drag_N']:.1f} N**; minimum mechanical work against drag is `D V`, and electrical input would be **{air['electrical_power_W']:.1f} W** if a real propulsor had an overall useful propulsive efficiency of 65%.

For stationary hover the selected rotor-like momentum-theory bound is `P_induced = T^(3/2)/sqrt(2ρA)`. For weight **{R['weight_N']:.1f} N**, effective disk area equal to the envelope face, ideal power is **{R['minimum_ideal_air_hover_power_W']:.1f} W**; with hypothetical figure of merit 0.6 it becomes **{R['assumed_FM_air_hover_power_W']:.1f} W**. **This is not a prediction that an ASC surface can hover:** there is no demonstrated mechanism that gives its active shell the role of an actuator disk. EHD, aerodynamic and acoustic-streaming alternatives need individually measured thrust/power values, material dimensions, safety tests and comparison against conventional propulsors. An effective disc area equal to hull planform is not an established performance parameter.

## 4. Water: drag, displacement and momentum transfer

Assuming seawater density 1025 kg/m³, the edge-on Cd=0.6 surrogate at 2 m/s demands **{water['drag_N']:.1f} N** to offset drag, before any current, acceleration, buoyancy correction or control force. The notional 50%-efficiency motion-power figure is **{water['nominal_electric_power_W']:.1f} W**. For an ideal stationary-water jet, `T=ṁ Δv` and `P_kin = 0.5 ṁ Δv²`; the `water_jet.csv` table gives the illustrative mass throughputs. Those numbers do not supply a validated pump or nozzle and cannot be assigned to a wave-coupling ring. Pressure-integrity testing is an entirely separate qualification problem.

## 5. Vacuum: conservation, jet power, mass flow and electrical supply

A closed system accelerating its own internal waves or parts **does not obtain sustained net thrust**. Only external momentum exchange (expelled propellant, emitted radiation, or an independently demonstrated environmental interaction) can change its momentum. NASA's thrust and specific-impulse definitions [2,3] support the generic idealized electric-jet bound `η P = 0.5 ṁ (g0 Isp)²`; hence `T = 2 η P / (g0 Isp)`. At **1 kW**, **Isp=1500 s** and hypothetical **η=0.45**, the bound is **{thr['thrust_mN']:.1f} mN** using **{thr['ideal_propellant_kg_day']:.3f} kg/day** of propellant. These values omit ionization, plume divergence, cathode operation and every concrete component of a thruster. They are not ASC-V hardware predictions. As a scale check, photon recoil is `P/c`: a perfectly collimated 1 kW photon beam supplies only about 3.34 μN of thrust.

A 1 kW continuous electric requirement for 24 h is 24 kWh, corresponding to **{thr['ideal_battery_kg_for_24h']:.0f} kg** at a hypothetical 200 Wh/kg battery (before wiring/thermal mass). An idealized 25%-efficient solar collector at 1 AU would require **{thr['ideal_solar_area_m2_at_1au']:.2f} m²** projected toward the Sun, ignoring packing, temperature, power conversion, shadowing and attitude constraints. These large infrastructure demands underline why thrust **cannot** be assessed separately from mass and energy supply.

## 6. Electrical and thermal budgets

An illustrative input power is split by `P_useful = P_elec × 0.85 × 0.35` and `P_local_loss = P_elec - P_useful`; at 1000 W this yields **{t['useful_mechanical_or_wave_W']:.1f} W** converted work/wave energy and **{t['locally_dissipated_W']:.1f} W** local non-mechanical losses. This is only a *power-flow accounting example*, not a measured ASC efficiency and not a thrust conversion. Mechanical work may later turn into heat in its environment. Radiative-only temperatures are computed from `Q = ε σ A (T⁴ - T_env⁴)` with an arbitrary effective radiating surface fraction; real cooling would include conduction, geometry, convection (in media), surface optics and hardware ratings. The table cannot justify a thermal design.

## 7. FEM and load response: validated mathematical baseline only

The public v0.3 source gives a bare Euler–Bernoulli cantilever (L=0.12 m, b=0.015 m, h=0.001 m, E=70 GPa, ρ=2700 kg/m³). Its analytic first-mode benchmark is **{b['bare_cantilever_first_mode_hz']:.5f} Hz**. Here we also calculate classical small-deflection tip displacement `δ=FL³/(3EI)` and bending root stress `σ=FL(h/2)/I` for **0.005–0.02 N** illustrative point loads. The source v0.3 verifies the first frequency by a separate FEM mesh convergence; the present add-on does not reproduce or replace its FE solver and supplies **no shell or piezoelectric assembly stresses**.

## 8. 24-channel command-phase study and timing

For θₖ=2πk/N and a synthetic commanded azimuthal order m=3, define `C_m=abs(mean(exp(i(φₖ-mθₖ))))`. This is a normalized **command phasor-array factor**, not a measured field or fluid impulse. Independent Gaussian phase perturbations are compared against an adjacent Fourier mode and an independent uniform-phase null with **20,000 seeded trials** per σ. At σ=0.3 rad the target average is **{p['mean']:.4f}**, while the random-phase null is **{p['random_null_mean']:.4f}**. That comparison establishes only that the chosen digital pattern is recoverable under its own synthetic noise assumptions.

A command phase tolerance Δφ degrees at frequency f maps to maximum time error `Δt=Δφ/(360 f)`. For 5° at 100 kHz, the ideal reference timing tolerance is **{jitter_s_for_phase_degrees(100000,5)*1e6:.4f} μs**. This is a mathematical timing requirement, not a feasible measured clock performance in ASC electronics. Harmonic mode and abstract phase model can be separated from the mechanical system entirely.

## 9. Wave-scale sampling and RF boundary checks

A basic scale check uses the illustrative relation `λ = v_phase / f`. For a generic phase speed **3000 m/s** and **100 kHz**, wavelength is **30 mm**; a crude `λ/2` perimeter sampling pitch would suggest **{get('wave_sampling',assumed_phase_velocity_m_s=3000,frequency_hz=100000)['perimeter_positions_heuristic']}** positions around the **1.0 m diameter** ring. At 1 MHz the same toy calculation gives **{get('wave_sampling',assumed_phase_velocity_m_s=3000,frequency_hz=1000000)['perimeter_positions_heuristic']}** positions. This is a heuristic rather than a transducer count: 24 supervisory sectors in the public design are not equivalent to 24 SAW actuators. The actual propagation speed, dispersion, material tensor and mode shapes are unknown. This is one reason not to infer a workable waveguide from a diagram.

At an electrical reference plane, positive return loss `RL` dB corresponds to reflected power fraction `10^(-RL/10)` and accepted fraction `1-10^(-RL/10)`. An assumed 10 dB return loss therefore accepts 90% at that plane but does **not** imply 90% electromechanical conversion; reflected power may return to the source or be dissipated elsewhere. Ohmic losses obey `N I² R` only for a documented topology and equivalent path resistance; public toy values are in `ohmic_heat.csv`.

## 10. Sensitivity, negative controls, and decision gates

The `uncertainty_envelope` Monte Carlo sweeps **independent uniform hypothetical inputs**, not calibrated manufacturing uncertainty. The 5–95% range of conditional hover power is **{unc['hover_power_W']['p05']:.0f}–{unc['hover_power_W']['p95']:.0f} W**; the same for seawater edge-on motion at 2 m/s is **{unc['water_edge_motion_power_W']['p05']:.0f}–{unc['water_edge_motion_power_W']['p95']:.0f} W**. They express *scenario sensitivity*, **not confidence intervals about a real vehicle**. Broader or correlated assumptions could move both envelopes substantially.

Null controls: randomized phase commands; adjacent Fourier orders; zero-input drag; analytical bare-cantilever frequency; energy-balance residual; negative/unphysical input validation; and an internal-momentum-exchange no-thrust statement. There is no experiment-based discrimination of surface waves, EHD, fluid thrust or plasma acceleration. In any actual experiment: define the matched-power baseline, observable, instrument calibration, blind controls, uncertainty and stopping rules before measurement; publish adverse/null results.

## 11. Interpretation and publication boundary

The outcome is **a reproducible table of conditional constraints**, not new propulsive capability. No private ASC geometries, electrode arrays, control laws, frequency selections, operating limits, materials or fabrication instructions have been used. Public figures in the preprint are AI-assisted architectural illustrations and are not a source of dimensions or verified mechanical geometry. Other models in the repository (v0.2.2 piezo-patch FEM, synthetic demonstration, public v0.3 beam/phase baseline) are different exercises and must not have their numeric outputs interchanged.

A useful future stage would connect **a measured small coupon** to an identified input-output transfer function, then compare a coupling interface against direct drive under equal power and conditions. Claims about propulsion demand independent thrust/force and flow momentum measurements. Until those exist, all modeled propulsion results remain conditional examples. Do not confuse a large quantity of computational outputs with physical validation.

## Sources

[1] NASA Glenn, **Drag Equation**: https://www1.grc.nasa.gov/beginners-guide-to-aeronautics/drag-equation/  
[2] NASA Glenn, **Rocket Thrust Equation**: https://www1.grc.nasa.gov/beginners-guide-to-aeronautics/rocket-thrust-equation/  
[3] NASA Glenn, **Specific Impulse**: https://www1.grc.nasa.gov/beginners-guide-to-aeronautics/specific-impulse/  
[4] NASA Small Spacecraft Technology, **In-Space Propulsion**: https://www.nasa.gov/smallsat-institute/sst-soa/in-space_propulsion/  
[5] Source project: **ASC Public Research Release v0.2.2**, 28-page preprint. DOI: https://doi.org/10.5281/zenodo.24406624.  
[6] User-supplied **ASC Computational Validation v0.3 — PUBLIC**, bare-beam benchmark and independent phase Monte Carlo. No private files are inputs.

**Scientific status:** publicly reproducible hypothetical scenario screening; **not** experimental or integrated computational validation of Active Surface Coupling hardware.
'''
    path.parent.mkdir(exist_ok=True);path.write_text(text,encoding='utf-8')

if __name__=='__main__':main()
