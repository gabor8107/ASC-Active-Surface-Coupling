#!/usr/bin/env python3
"""Generate deterministic public ASC v0.6 scenario results and figures."""
from __future__ import annotations
import json,csv,sys
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
ROOT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT/'src'))
from asc_physics import *
CFIG=ROOT/'figures'; RES=ROOT/'results'; CFIG.mkdir(exist_ok=True);RES.mkdir(exist_ok=True)
config=json.loads((ROOT/'config/scenarios.json').read_text())
p=config['external_power_W']; eta0=config['baseline_jet_efficiency'];eta1=config['illustrative_hybrid_jet_efficiency'];isp=config['specific_impulse_s']
sector=config['sector_gross_electric_W'];r=config['recovery_fraction_of_sector_input'];aux=config['auxiliary_W']
base=jet(p,isp,eta0);bud=split_budget(p,sector,r,aux)
hyb=jet(bud['jet_available_W'],isp,eta1)
breakeven=eta_to_break_even(eta0,p,bud['jet_available_W'])
rad_base=p-base['jet_kinetic_W']
rad_hyb=p-hyb['jet_kinetic_W']


def write_csv(fname, rows):
    if not rows:return
    with open(RES/fname,'w',newline='',encoding='utf-8') as f:
        writer=csv.DictWriter(f,list(rows[0].keys()));writer.writeheader();writer.writerows(rows)

# Power split: no sector, sector without recovery, sector with recovery.
power_rows=[]
for s in np.arange(0,40001,2500):
    for rec in (0.,r):
        b=split_budget(p,float(s),rec,aux if s>0 else 0.)
        required=eta_to_break_even(eta0,p,b['jet_available_W'])
        power_rows.append(dict(sector_kW=round(s/1000,3),recovery_pct=100*rec,
            jet_kW=b['jet_available_W']/1000, required_efficiency_pct=required*100,
            thrust_eta45_N=jet(b['jet_available_W'],isp,eta0)['thrust_axial_N'] if b['jet_available_W'] else 0,
            thrust_eta58_N=jet(b['jet_available_W'],isp,eta1)['thrust_axial_N'] if b['jet_available_W'] else 0,
            recovered_kW=b['sector_recovered_W']/1000))
write_csv('power_split_comparison.csv',power_rows)

align_rows=[]
for angle in (0,10,20,30,45,60,90):
    a=array_forces(power_W=bud['jet_available_W'],eta=eta1,isp_s=isp,tilt_deg=angle)
    align_rows.append(dict(tilt_deg=angle, axial_N=a['force_z_N'],lateral_N=np.hypot(a['force_x_N'],a['force_y_N']),
       torque_Nm=a['torque_norm_Nm'],effective_alignment=a['force_z_N']/hyb['thrust_magnitude_N']))
write_csv('alignment_scan.csv',align_rows)

fail_rows=[]
for label,dead in [('none',[]),('one_sector',[0]),('three_adjacent',[0,1,2]),('three_evenly_spaced',[0,8,16])]:
    a=array_forces(power_W=bud['jet_available_W'],eta=eta1,isp_s=isp,tilt_deg=10.,radius_m=config['illustrative_radius_m'],dead_sectors=dead)
    fail_rows.append(dict(fault=label,dead_sectors=len(dead),alive_cells=a['alive_cells'],axial_N=a['force_z_N'],
      lateral_N=np.hypot(a['force_x_N'],a['force_y_N']),torque_Nm=a['torque_norm_Nm']))
write_csv('sector_faults.csv',fail_rows)

rocket_rows=[]
for target_kmh in (100000,300000):
    for Isp in (1500,5000):
        x=rocket_budget(config['dry_mass_kg'],target_kmh/3.6,p,Isp,eta0,
            specific_battery_Wh_kg=config['battery_specific_energy_Wh_kg'])
        rocket_rows.append(dict(target_km_h=target_kmh,isp_s=Isp,mass_ratio=x['required_mass_ratio'],
          propellant_tonnes=x['required_propellant_kg']/1000,initial_wet_tonnes=x['wet_mass_kg']/1000,
          burn_days=x['constant_power_burn_days'],source_energy_MWh=x['source_energy_MWh'],
          illustrative_battery_mass_tonnes=x['battery_mass_if_200Wh_kg_kg']/1000,thrust_N=x['thrust_axial_N']))
write_csv('ideal_mission_budgets.csv',rocket_rows)

rads=[]
for temp in config['radiator_temperatures_K']:
    rads.append(dict(radiator_K=temp, baseline_radiator_m2=radiator_area(rad_base,temp),
    hybrid_radiator_m2=radiator_area(rad_hyb,temp)))
write_csv('thermal_radiator.csv',rads)

eta_rows=[]
for eff in np.arange(0.30,0.751,0.025):
    y=jet(bud['jet_available_W'],isp,float(eff))
    eta_rows.append(dict(jet_efficiency_pct=eff*100,hybrid_thrust_N=y['thrust_axial_N'],
    baseline_thrust_N=base['thrust_axial_N'],thrust_gain_pct=100*(y['thrust_axial_N']/base['thrust_axial_N']-1),
    mass_adjusted_acceleration_change_pct=100*((y['thrust_axial_N']/base['thrust_axial_N'])*
    (config['dry_mass_kg']/(config['dry_mass_kg']+config['illustrative_recovery_added_mass_kg']))-1)))
write_csv('efficiency_and_added_mass.csv',eta_rows)

cell_rows=[]
for label,a in [('baseline_photon',photon(p)),('sector_20kW_photon',photon(sector)),('hybrid_jet',hyb['thrust_axial_N'])]:
    cell_rows.append(dict(scenario=label,thrust_N=a))
write_csv('propulsion_bounds.csv',cell_rows)

solar=source_envelopes(p,config['solar_flux_1AU_W_m2'],config['solar_efficiency'])
summary={"identification":"PUBLIC HYPOTHETICAL v0.6; numerical bounds only; no physical ASC motor or flight test",
 "baseline":base,"hybrid_allocation":bud,"hybrid_jet_if_eta58":hyb,
 "efficiency_required_break_even":breakeven,
 "baseline_radiator_heat_if_all_nonjet_energy_is_onboard_W":rad_base,
 "hybrid_radiator_heat_if_all_nonjet_energy_is_onboard_W":rad_hyb,
 "ideal_photon_limit_100kW_N":photon(p),"source_envelope":solar,
 "mass_adjusted_dry_only_acceleration_ratio":(hyb['thrust_axial_N']/base['thrust_axial_N'])*
     config['dry_mass_kg']/(config['dry_mass_kg']+config['illustrative_recovery_added_mass_kg']),
 "caveats":["288 identical hypothetical emission cells are not a demonstrated ASC mechanism",
 "v0.5 4.65-kW recovery cannot be added again to this 100-kW external-power split",
 "external photovoltaic area and stored-battery figures are simplistic diagnostics, not viable spacecraft designs",
 "a velocity increment is not an ASC speed limit or prediction"]}
(RES/'summary_v06.json').write_text(json.dumps(summary,indent=2,ensure_ascii=False)+'\n')

plt.rcParams.update({'figure.figsize':(8.5,4.6),'font.size':10,'axes.spines.top':False,'axes.spines.right':False,'savefig.dpi':165})
def save(n):plt.tight_layout();plt.savefig(CFIG/n,bbox_inches='tight');plt.close()

x=np.arange(0,42.5,2.5)
y_no=[];y_rec=[]; y_rec58=[]
for sv in x:
    y_no.append(jet(split_budget(p,sv*1000,0,aux if sv>0 else 0)['jet_available_W'],isp,eta0)['thrust_axial_N'])
    pw=split_budget(p,sv*1000,r,aux if sv>0 else 0)['jet_available_W']
    y_rec.append(jet(pw,isp,eta0)['thrust_axial_N'])
    y_rec58.append(jet(pw,isp,eta1)['thrust_axial_N'])
plt.plot(x,y_no,label='No recovery, jet efficiency 45%');plt.plot(x,y_rec,label='Recovery 4.65%, jet efficiency 45%');plt.plot(x,y_rec58,label='Recovery 4.65%, assumed jet efficiency 58%')
plt.axhline(base['thrust_axial_N'],color='grey',linestyle='--',lw=1,label='100 kW jet baseline')
plt.xlabel('Illustrative sector gross load (kW)');plt.ylabel('Axial thrust under hypothetical jet assumption (N)');plt.title('Sector power cost must be repaid by a measured improvement');plt.legend(fontsize=8,loc='best');save('01_power_split_thrust.png')

plt.plot([row['jet_efficiency_pct'] for row in eta_rows],[row['thrust_gain_pct'] for row in eta_rows],label='Thrust gain at equal external input')
plt.plot([row['jet_efficiency_pct'] for row in eta_rows],[row['mass_adjusted_acceleration_change_pct'] for row in eta_rows],label='Dry-mass-adjusted acceleration proxy')
plt.axvline(100*breakeven,color='grey',ls='--',label='Thrust break-even');plt.axhline(0,color='grey',lw=1)
plt.title('Efficiency is a required outcome, not a model prediction');plt.xlabel('Assumed hybrid jet efficiency (%)');plt.ylabel('Change versus conventional baseline (%)');plt.legend(fontsize=9);save('02_efficiency_break_even.png')

xx=np.array([r['tilt_deg'] for r in align_rows]);plt.plot(xx,[r['axial_N'] for r in align_rows],marker='o')
plt.ylabel('Axial thrust (N)');plt.xlabel('Hypothetical radial exhaust tilt from axis (degrees)');plt.title('Directional projection: symmetrical outward jets lose axial thrust');save('03_vector_alignment.png')

lab=[r['fault'] for r in fail_rows];yy=[r['axial_N'] for r in fail_rows];plt.bar(lab,yy)
plt.xticks(rotation=12,ha='right');plt.ylabel('Axial thrust (N)');plt.title('Lost sectors: no automatic rerouting of unused power');save('04_sector_faults.png')

rr=np.array([v['radiator_K'] for v in rads]);plt.plot(rr,[v['baseline_radiator_m2'] for v in rads],marker='o',label='Baseline 100-kW jet')
plt.plot(rr,[v['hybrid_radiator_m2'] for v in rads],marker='o',label='Illustrative hybrid')
plt.xlabel('Radiating temperature (K)');plt.ylabel('Ideal effective emitting area (m$^2$)')
plt.title('Conservative radiative heat-rejection envelope');plt.legend();save('05_radiator_envelope.png')

for Isp in (1500,5000):
    d=[v for v in rocket_rows if v['isp_s']==Isp]
    plt.plot([v['target_km_h']/1000 for v in d],[v['propellant_tonnes'] for v in d],marker='o',label=f'Isp {Isp} s')
plt.xlabel('Target ideal velocity increment (thousand km/h)');plt.ylabel('Propellant (tonnes), 300 kg dry mass')
plt.title('Rocket equation: propellant demand is not an ASC forecast');plt.legend();save('06_propellant_mass_ratio.png')

plt.bar(['Photons, 100 kW','Conventional jet\n100 kW, 45%','Sector allocation\n80.58 kW, 58%'],
        [photon(p),base['thrust_axial_N'],hyb['thrust_axial_N']])
plt.yscale('log');plt.ylabel('Thrust (N), logarithmic scale');plt.title('Only emitted momentum produces net vacuum thrust');save('07_momentum_channel_limits.png')
print('v0.6 regenerated:',len(list(RES.glob('*.csv'))),'CSV datasets,',len(list(CFIG.glob('*.png'))),'plots; baseline',base['thrust_axial_N'],'N; hybrid',hyb['thrust_axial_N'],'N; break-even eta',breakeven)
