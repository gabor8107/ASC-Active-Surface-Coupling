#!/usr/bin/env python3
"""Regenerate public 100-kW hypothetical hybrid-recovery results, figures and note.
The input is an arbitrary scenario, not a build or prediction of ASC.
"""
from __future__ import annotations
import csv
import json
import sys
import math
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

ROOT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT/'src'))
from hybrid_recovery import (recoverable_power, fixed_useful_comparison,
    fixed_external_comparison, radiator_area_vacuum, simple_mass_penalty_proxy,
    break_even_penalty_fraction, carnot_limit)


def csv_out(name, rows):
    with (ROOT/'results'/name).open('w',newline='',encoding='utf-8') as f:
        writer=csv.DictWriter(f,fieldnames=list(rows[0]))
        writer.writeheader();writer.writerows(rows)


def render_plot(name):
    plt.tight_layout()
    plt.savefig(ROOT/'figures'/name,dpi=160,bbox_inches='tight')
    plt.close()


def fmt(x,dec=2):return f'{x:,.{dec}f}'


def main():
    (ROOT/'results').mkdir(exist_ok=True)
    (ROOT/'figures').mkdir(exist_ok=True)
    cfg=json.loads((ROOT/'config'/'hybrid_recovery_scenarios.json').read_text(encoding='utf-8'))
    f=cfg['fractions'];cap=cfg['illustrative_capture'];therm=cfg['thermal_reservoirs_K'];tr=cfg['system_tradeoffs']
    gross=cfg['gross_electric_W']
    r=recoverable_power(gross,f['useful'],f['heat'],f['rf_reflection_or_other_uncaptured'],
           f['unwanted_mechanical'],cap['heat_electric'],cap['rf_electric'],
           cap['mechanical_electric'],cap['rf_available'],therm['hot'],therm['cold'])
    equaluse=fixed_useful_comparison(gross,f['useful'],r['recovery_frac'],tr['useful_process_penalty_fraction_of_gross'],tr['auxiliary_external_W'])
    equalext=fixed_external_comparison(gross,f['useful'],r['recovery_frac'],tr['useful_process_penalty_fraction_of_gross'],tr['auxiliary_external_W'])
    mass=simple_mass_penalty_proxy(tr['baseline_mass_proxy_kg'],tr['added_recovery_mass_kg'],equalext['base_useful_W'],equalext['hybrid_useful_W'])
    breakeven=break_even_penalty_fraction(f['useful'],r['recovery_frac'],tr['auxiliary_external_W'],gross)
    rad=cfg['radiator'];heat=r['heat_bin_W'];rec_heat=r['heat_recovered_W']
    area_table=[]
    for radiator_K in rad['temperatures_K']:
        area_table.append(dict(radiator_temperature_K=radiator_K,baseline_heat_only_m2=round(radiator_area_vacuum(heat,radiator_K,therm['space'],rad['emissivity']),3),
        heat_only_after_TEG_m2=round(radiator_area_vacuum(heat-rec_heat,radiator_K,therm['space'],rad['emissivity']),3),
        note='Radiative-only, one-sided effective area; cannot establish actual TEG cold-side and cooling design'))
    csv_out('hybrid_radiator.csv',area_table)
    flows=[dict(branch='Useful modelled process (not thrust)',baseline_W=r['useful_W'],capture_pct=0,electric_recovered_W=0),
           dict(branch='Thermal bin (not total thermal load)',baseline_W=heat,capture_pct=100*cap['heat_electric'],electric_recovered_W=r['heat_recovered_W']),
           dict(branch='RF reflection/loss bin (not already recirculated)',baseline_W=r['rf_bin_W'],capture_pct=100*cap['rf_electric']*cap['rf_available'],electric_recovered_W=r['rf_recovered_W']),
           dict(branch='Unwanted vibration bin (not useful waves)',baseline_W=r['vibration_bin_W'],capture_pct=100*cap['mechanical_electric'],electric_recovered_W=r['vibration_recovered_W'])]
    csv_out('hybrid_power_bins.csv',flows)
    op=[dict(comparison='baseline',external_supply_W=gross,internal_process_W=gross,modelled_useful_W=r['useful_W'],gross_recovered_W=0,aux_W=0,process_penalty_frac=0),
        dict(comparison='hybrid_equal_useful',external_supply_W=round(equaluse['hybrid_external_W'],4),internal_process_W=round(equaluse['hybrid_internal_W'],4),modelled_useful_W=round(equaluse['hybrid_useful_W'],4),gross_recovered_W=round(equaluse['hybrid_recovered_W'],4),aux_W=tr['auxiliary_external_W'],process_penalty_frac=tr['useful_process_penalty_fraction_of_gross']),
        dict(comparison='hybrid_equal_external',external_supply_W=gross,internal_process_W=round(equalext['hybrid_internal_W'],4),modelled_useful_W=round(equalext['hybrid_useful_W'],4),gross_recovered_W=round(equalext['hybrid_recovered_W'],4),aux_W=tr['auxiliary_external_W'],process_penalty_frac=tr['useful_process_penalty_fraction_of_gross'])]
    csv_out('hybrid_operating_points.csv',op)
    sweeps=[]
    for penalty_kW in np.linspace(0,4.0,81):
        pfrac=float(penalty_kW)*1e3/gross
        e=fixed_useful_comparison(gross,f['useful'],r['recovery_frac'],pfrac,tr['auxiliary_external_W'])
        s=fixed_external_comparison(gross,f['useful'],r['recovery_frac'],pfrac,tr['auxiliary_external_W'])
        sweeps.append(dict(useful_process_penalty_kW_at_100kW=round(float(penalty_kW),3),external_savings_at_equal_useful_kW=round(e['external_savings_W']/1e3,4),useful_gain_at_equal_external_kW=round(s['delta_useful_W']/1e3,4),gain_pct_equal_external=round(s['delta_useful_pct'],4)))
    csv_out('hybrid_penalty_sweep.csv',sweeps)

    # Assumption sweep: illustrative ranges are not calibrated probability distributions.
    sens=cfg['illustrative_sensitivity']; rng=np.random.default_rng(sens['seed']); n=sens['samples']
    def sample(key): return rng.uniform(*sens[key],n)
    hot=sample('hot_K');cold=sample('cold_K');eta_heat=(1-cold/hot)*sample('fraction_of_Carnot_realized')
    cap_rf=sample('rf_capture_frac');av_rf=sample('rf_available_frac'); cap_vib=sample('vibration_capture_frac')
    aux=sample('aux_W');pen=sample('process_penalty_frac');mass_extra=sample('extra_mass_kg')
    rfrac=f['heat']*eta_heat + f['rf_reflection_or_other_uncaptured']*cap_rf*av_rf + f['unwanted_mechanical']*cap_vib
    internal=gross*f['useful']/(f['useful']-pen)
    ext=internal*(1-rfrac)+aux
    saving_kW=(gross-ext)/1e3
    internal_fx=(gross-aux)/(1-rfrac)
    new_useful=internal_fx*(f['useful']-pen)
    accel_ratio=new_useful/(gross*f['useful'])*tr['baseline_mass_proxy_kg']/(tr['baseline_mass_proxy_kg']+mass_extra)
    def summary(a): return dict(p05=float(np.percentile(a,5)),median=float(np.percentile(a,50)),p95=float(np.percentile(a,95)),minimum=float(np.min(a)),maximum=float(np.max(a)))
    monte=dict(external_savings_kW=summary(saving_kW),recovery_fraction=summary(rfrac),
       mass_adjusted_acceleration_ratio=summary(accel_ratio),
       proportion_positive_electrical_saving=float(np.mean(saving_kW>0)),
       proportion_positive_mass_adjusted_acceleration=float(np.mean(accel_ratio>1)),
       interpretation='Arbitrary independent uniform parameter sweeps; neither probability forecasts nor experimental uncertainty intervals')
    csv_out('hybrid_assumption_sweep_summary.csv',[
        {'quantity':k,**v} for k,v in monte.items() if isinstance(v,dict)])

    # Figures: 5 additional diagnostic graphics, old v0.4 figures retained.
    fig,ax=plt.subplots(figsize=(9,4.4))
    labels=['Useful process','Heat bin','RF bin','Unwanted vibration']; vals=[r['useful_W']/1e3,heat/1e3,r['rf_bin_W']/1e3,r['vibration_bin_W']/1e3]
    ax.bar(labels,vals,label='Gross partition (kW)',color=['#436a7c','#cc8b5d','#7395a8','#7b8177'])
    ax.bar(labels,[0,r['heat_recovered_W']/1e3,r['rf_recovered_W']/1e3,r['vibration_recovered_W']/1e3],label='Electrical recovery (kW)',color='#26684d')
    ax.set_ylabel('Power [kW]');ax.set_title('Illustrative 100 kW partition; recovery is a SUBSET of each loss bin');ax.legend(loc='upper right');ax.tick_params(axis='x',labelrotation=10)
    render_plot('hybrid_100kW_power_ledger.png')

    fig,ax=plt.subplots(figsize=(8.8,4.5))
    ax.plot([x['useful_process_penalty_kW_at_100kW'] for x in sweeps],[x['external_savings_at_equal_useful_kW'] for x in sweeps],label='Source-power saving at equal useful output')
    ax.plot([x['useful_process_penalty_kW_at_100kW'] for x in sweeps],[x['useful_gain_at_equal_external_kW'] for x in sweeps],label='Useful-process gain at fixed external input')
    ax.axhline(0,c='#222222',lw=1);ax.axvline(gross*tr['useful_process_penalty_fraction_of_gross']/1e3,linestyle='--',c='#a9583b',label='Example process penalty')
    ax.set(xlabel='Reduction of useful-process power per 100 kW gross [kW]',ylabel='Difference from baseline [kW]',title='Recovery can lose its benefit when coupling/process performance degrades');ax.grid(alpha=.2);ax.legend(fontsize=8)
    render_plot('hybrid_penalty_break_even.png')

    fig,ax=plt.subplots(figsize=(8,4.5))
    temps=[row['radiator_temperature_K'] for row in area_table]
    ax.plot(temps,[row['baseline_heat_only_m2'] for row in area_table],'o-',label='Baseline 45 kW heat branch')
    ax.plot(temps,[row['heat_only_after_TEG_m2'] for row in area_table],'o-',label='TEG cold-side rejection 42.75 kW')
    ax.set(xlabel='Radiator surface temperature [K]',ylabel='Required effective single-sided area [m²]',title='Vacuum radiation-only area check (not a cooler design)');ax.grid(alpha=.2);ax.legend()
    render_plot('hybrid_thermal_radiator.png')

    fig,ax=plt.subplots(figsize=(8.5,4.6))
    ax.hist(saving_kW,bins=55,color='#4f8291',alpha=.9)
    ax.axvline(0,color='#a04737',lw=1.5,label='No net saving')
    ax.set(xlabel='External power saving at same useful output [kW]',ylabel='Count of synthetic input combinations',title='Hypothetical assumption sweep: not a probability distribution for ASC');ax.legend()
    render_plot('hybrid_assumption_sensitivity.png')

    mass_sweep=[]
    for kg in np.linspace(0,25,101):
        a=simple_mass_penalty_proxy(tr['baseline_mass_proxy_kg'],float(kg),equalext['base_useful_W'],equalext['hybrid_useful_W'])
        mass_sweep.append(dict(extra_mass_kg=round(float(kg),3),relative_acceleration=round(a['acceleration_ratio_hybrid_to_base'],6),change_pct=round(a['hypothetical_acceleration_change_pct'],4)))
    csv_out('hybrid_mass_tradeoff.csv',mass_sweep)
    fig,ax=plt.subplots(figsize=(8.5,4.6))
    ax.plot([m['extra_mass_kg'] for m in mass_sweep],[m['change_pct'] for m in mass_sweep],color='#506b87')
    ax.axhline(0,c='#9b4838',lw=1.3)
    ax.axvline(tr['added_recovery_mass_kg'],ls='--',color='#a9583b',label='Illustrative +8 kg')
    ax.set(xlabel='Added recovery-system mass [kg]',ylabel='Hypothetical acceleration change [%]',title='Only if thrust tracks useful process power; NOT an ASC thrust model');ax.grid(alpha=.2);ax.legend()
    render_plot('hybrid_mass_tradeoff.png')

    details=dict(name='ASC public 100 kW hybrid recovery benchmark',scenario='PUBLIC hypothetical; no ASC hardware',
      original_gross_W=gross,carnot_limit=r['carnot_limit'],raw=r,
      fixed_useful=equaluse,fixed_external=equalext,mass_proxy=mass,
      useful_penalty_break_even_fraction=breakeven,thermal_radiation=area_table,
      assumption_sweep=monte,settings=cfg)
    (ROOT/'results'/'hybrid_summary.json').write_text(json.dumps(details,indent=2,ensure_ascii=False),encoding='utf-8')
    save_report(details)
    print('Hybrid gross recovered kW =',fmt(r['raw_recovered_W']/1000,3))
    print('Fixed useful: external saving kW =',fmt(equaluse['external_savings_W']/1000,3))
    print('Fixed external: modelled useful process change =',fmt(equalext['delta_useful_pct'],3),'%')
    print('Added mass proxy: acceleration change =',fmt(mass['hypothetical_acceleration_change_pct'],3),'%')
    print('Synthetic sweep median source saving kW =',fmt(monte['external_savings_kW']['median'],3))


def save_report(d):
    r=d['raw'];e=d['fixed_useful'];x=d['fixed_external'];m=d['mass_proxy'];mon=d['assumption_sweep'];areas=d['thermal_radiation'];s=d['settings']
    text=f'''# ASC - Public Numerical Engineering Envelope v0.5: Hybrid Recovery Extension

**Technical note | 22 November 2026 | Concept: P. Gabor**  
**PUBLIC, UNREVIEWED, SYNTHETIC ENGINEERING EXAMPLE. NOT ASC VALIDATION.**

## Purpose and relation to the public v0.4 package

This additive numerical study tests a hypothetical hybrid of thermal, reflected RF, and unwanted mechanical-vibration energy recovery. It preserves the earlier v0.4 constraint models, their limitations, and their outputs; it does not replace the 28-page ASC Preprint 0.2 or provide a confidential design. The parameters are arbitrarily chosen for transparent sensitivity testing. No integrated ASC vehicle or engine is modelled, and no actual recovery subsystem has been built or measured.

An energy-recovery subsystem does **not create energy or reactionless propulsion**. Its success criterion is a reduction in external power for the **same independently defined useful work**, or a verified improvement in physical propulsion performance **at equal external input and equal total system mass**. At a real test bench, sensor loading and thermal/mechanical interference can make the new system worse than a simpler baseline.

## 1. Electrical accounting boundary: no overlap among loss bins

One gross process input of **{fmt(s['gross_electric_W']/1000,1)} kW** is allocated to four *disjoint* hypothetical bins: useful process {fmt(r['useful_W']/1000)} kW, thermal {fmt(r['heat_bin_W']/1000)} kW, RF reflection/loss {fmt(r['rf_bin_W']/1000)} kW and unwanted vibration {fmt(r['vibration_bin_W']/1000)} kW. These bins do **not** prove that thermal, RF and vibration losses in a real system can be measured independently. Reflected RF that has already returned to the source is **not** available to be recovered again; the RF availability parameter must exclude it. Mechanical wave energy intended for the useful effect is **not** counted as available vibration waste.

In the example only, electric capture fractions are 5% of the heat bin, 30% of the available RF bin, and 10% of the vibration bin. The raw capture is **{fmt(r['heat_recovered_W']/1000)} + {fmt(r['rf_recovered_W']/1000)} + {fmt(r['vibration_recovered_W']/1000)} = {fmt(r['raw_recovered_W']/1000)} kW**, or {fmt(100*r['recovery_frac'],3)}% of gross process input. That is recovered output **before controller loads, process degradation, mass and additional thermal hardware**. Energy-balance residual: {fmt(r['energy_balance_residual_W'],9)} W.

## 2. Thermodynamic check and rejected heat

Chosen hot-side temperature: {fmt(s['thermal_reservoirs_K']['hot'],0)} K; cold-side temperature: {fmt(s['thermal_reservoirs_K']['cold'],0)} K. The Carnot upper bound is **{fmt(100*r['carnot_limit'])}%**, versus the example's assumed **5%** electricity from the isolated 45 kW thermal bin. This assumption is below the bound; that does **not** establish a practical thermoelectric conversion efficiency or a physically sustainable temperature gradient. TEG converters also require sustained hot- and cold-side heat exchange. Their electrical output is drawn from the heat stream, and the remaining **{fmt(r['heat_to_reject_after_TEG_W']/1000)} kW** still requires cooling, even before any RF/vibration losses dissipate elsewhere.

A simple vacuum-only Stefan-Boltzmann comparison uses emissivity 0.85, an approximately 3 K external background, one-sided effective radiating area, and radiative-only exchange. It neglects view factor, radiator structure, pump load, hot/cold interface design and real spacecraft conditions:

| Radiator T [K] | Baseline 45 kW [m²] | After 2.25 kW TEG: 42.75 kW [m²] |
|---:|---:|---:|
'''
    for row in areas:text+=f"| {row['radiator_temperature_K']} | {fmt(row['baseline_heat_only_m2'])} | {fmt(row['heat_only_after_TEG_m2'])} |\n"
    text+=f'''

These figures are **area requirements for that isolated heat stream**, not a viable thermal architecture. If a 300 K cold side is required, its rejection area at 300 K can be much larger than at 400 K. The 350 K and 400 K radiator rows are separate radiative *what-if* cases and must not be combined with the 300 K TEG cold-side assumption without additional thermal architecture and work.

## 3. Same useful output: how much external power is actually saved?

The baseline is 100.00 kW gross and 45.00 kW modelled useful process output. The example adds **{fmt(s['system_tradeoffs']['auxiliary_external_W']/1000,3)} kW** of external auxiliary/control power and assumes a **{fmt(100*s['system_tradeoffs']['useful_process_penalty_fraction_of_gross'],2)}-percentage-point** useful-process loss per unit gross input (0.60 kW per 100 kW). To restore the *same 45.00 kW* useful process output, the hypothetical hybrid must circulate **{fmt(e['hybrid_internal_W']/1000,3)} kW** internally, of which **{fmt(e['hybrid_recovered_W']/1000,3)} kW** is returned. External demand becomes **{fmt(e['hybrid_external_W']/1000,3)} kW**, a conditional saving of **{fmt(e['external_savings_W']/1000,3)} kW ({fmt(100*e['relative_savings_frac'],3)}%)**.

It would be misleading to label the raw 4.65 kW as this net saving. The external supply must cover the auxiliary controls and must compensate the loss of useful process output. The same-effort model assumes fractions stay constant across small operating point shifts; this is *not* shown for real piezoelectric, RF or thermoelectric hardware.

## 4. Same external supply: additional throughput and hypothetical mass penalty

With external supply fixed at 100.00 kW, the example yields a recirculating gross process flow of **{fmt(x['hybrid_internal_W']/1000,3)} kW** and a conditional useful-process output of **{fmt(x['hybrid_useful_W']/1000,3)} kW**, compared with 45.000 kW without recovery: a **{fmt(x['delta_useful_W']/1000,3)} kW ({fmt(x['delta_useful_pct'],3)}%)** improvement *in the abstract useful-power metric*. No ASC thrust coefficient, efficiency or velocity can be inferred from it.

Additional system mass **{fmt(s['system_tradeoffs']['added_recovery_mass_kg'],1)} kg** is examined against an unrelated **{fmt(s['system_tradeoffs']['baseline_mass_proxy_kg'],1)} kg** notional mass scale, purely as a caution. **If and only if** thrust scaled linearly with the abstract useful output while all other physical variables remained fixed, acceleration would change by **{fmt(m['hypothetical_acceleration_change_pct'],3)}%** rather than improve. This is **not** a propulsion calculation and cannot supply speed, acceleration or flight claims for ASC.

The illustrative useful-process penalty break-even is **{fmt(d['useful_penalty_break_even_fraction']*100,3)} percentage points of gross** at the given capture and auxiliary assumptions. Above this threshold, at fixed external input, the recovery system delivers less useful-process power than the direct baseline. Negative or poor sensitivity cases must be retained rather than selected out.

## 5. Sensitivity - unknown inputs, not calibrated confidence intervals

A seeded sweep of **{s['illustrative_sensitivity']['samples']:,}** synthetic combinations varies the thermal gradient, fraction of Carnot efficiency, available RF return, vibration capture, auxiliary power, useful-process penalty and added mass. Every range was selected for exploration, **not fitted to hardware**. Draws are independent uniforms; percentiles are NOT confidence intervals, probabilities of ASC success or material-property distributions.

- Equal-useful external saving [kW], arbitrary 5th / median / 95th percentiles: **{fmt(mon['external_savings_kW']['p05'],3)} / {fmt(mon['external_savings_kW']['median'],3)} / {fmt(mon['external_savings_kW']['p95'],3)}**.
- Share of synthetic input combinations yielding electrical saving: **{fmt(100*mon['proportion_positive_electrical_saving'],1)}%**. This is NOT a probability that the ASC works.
- Share of synthetic combinations yielding improved mass-adjusted acceleration **under the unsupported linear-thrust proxy assumption**: **{fmt(100*mon['proportion_positive_mass_adjusted_acceleration'],1)}%**.

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
'''
    (ROOT/'docs'/'HYBRID_RECOVERY_TECHNICAL_NOTE_EN.md').write_text(text,encoding='utf-8')


if __name__=='__main__':main()
