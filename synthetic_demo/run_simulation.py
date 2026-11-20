"""ASC — preliminary synthetic measurement demonstration (not physical validation).

Public-safe, generic numerical exercises inspired by the ASC Preprint 0.2:
  A. S1: damped single-mode coupon response, direct-drive vs hypothetical interface.
  B. An abstract 24-channel phase-coherence sensitivity exercise.

All numerical model parameters are illustrative, not ASC hardware specifications.
No forces, efficiencies, SAW dispersion, plasma behavior, or propulsion are modeled.

Dependencies: numpy, matplotlib; Python 3.10+.
Usage: python run_simulation.py
"""
from pathlib import Path
import csv
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

OUT = Path(__file__).resolve().parent
SEED = 20261120
rng = np.random.default_rng(SEED)

# A. Mechanical response, normalized frequency r=f/f_ref; no fabricated physical units.
r = np.linspace(0.72, 1.28, 281)
trials = 30
sigma_noise = 0.018  # measured displacement noise expressed in reference-peak units
sigma_session = 0.012  # between-run multiplicative amplitude drift


def h_single_mode(r, r0, zeta, gain):
    """Complex displacement transfer H = gain / ((r0^2-r^2) + j 2*zeta*r0*r)."""
    return gain / ((r0*r0-r*r) + 1j * 2*zeta*r0*r)

h_ref = h_single_mode(r, 1.0, 0.040, 1.0)
h_alt = h_single_mode(r, 1.020, 0.046, 0.95)
scale = np.max(np.abs(h_ref))
response = {}
rows = []
for label, h in [('Direct-drive reference', h_ref), ('Hypothetical interface', h_alt)]:
    true_amplitude = np.abs(h)/scale
    readings=[]
    for trial in range(trials):
        drift = rng.normal(0,sigma_session)
        noisy = np.clip(true_amplitude*(1+drift) + rng.normal(0,sigma_noise,len(r)), 0, None)
        readings.append(noisy)
        for ri, ai in zip(r,noisy):
            rows.append([label,trial+1,float(ri),float(ai)])
    obs = np.array(readings)
    response[label] = dict(true=true_amplitude,mean=obs.mean(0),ci=1.96*obs.std(0,ddof=1)/np.sqrt(trials))

with (OUT/'synthetic_s1_measurements.csv').open('w',newline='',encoding='utf8') as ff:
    w=csv.writer(ff)
    w.writerow(['case','trial_id','normalized_frequency_ratio','synthetic_normalized_response'])
    w.writerows(rows)

plt.figure(figsize=(10,5.5),dpi=165)
for label,dat in response.items():
    line=plt.plot(r,dat['mean'],lw=2,label=label)[0]
    plt.fill_between(r,dat['mean']-dat['ci'],dat['mean']+dat['ci'],alpha=.18,color=line.get_color())
plt.xlabel('Frequency / reference natural frequency (dimensionless)')
plt.ylabel('Normalized response amplitude (dimensionless)')
plt.title('S1 synthetic frequency sweep — 30 simulated repeats per condition')
plt.legend(loc='upper right')
plt.grid(alpha=.22)
plt.text(.02,.96,'SYNTHETIC DATA — NOT MEASURED ASC PERFORMANCE',transform=plt.gca().transAxes,
         va='top',fontsize=9,bbox=dict(facecolor='white',alpha=.8,edgecolor='none'))
plt.tight_layout()
plt.savefig(OUT/'figure_1_synthetic_frequency_response.png')
plt.close()

# B. Generic 24-channel phase sensitivity: coherence of intended aligned phasors.
# Independent normally distributed errors. This is only a timing/control toy model;
# it is NOT a model of physically coupled surface-wave modes or platform forces.
error_deg = np.arange(0,91,5)
mc_runs=6000
means=[]; lo=[]; hi=[]
phase_rows=[]
for stddeg in error_deg:
    err=np.deg2rad(rng.normal(0,stddeg,(mc_runs,24)))
    coh=np.abs(np.exp(1j*err).sum(axis=1))/24.0
    means.append(coh.mean()); lo.append(np.percentile(coh,2.5)); hi.append(np.percentile(coh,97.5))
    phase_rows.append([int(stddeg), float(coh.mean()),float(lo[-1]),float(hi[-1])])
with (OUT/'synthetic_24_channel_phase_sensitivity.csv').open('w',newline='',encoding='utf8') as ff:
    w=csv.writer(ff);w.writerow(['phase_error_std_deg','mean_normalized_coherence','p2_5','p97_5']);w.writerows(phase_rows)

plt.figure(figsize=(10,5.5),dpi=165)
plt.plot(error_deg,means,lw=2,label='Mean of 6,000 synthetic runs')
plt.fill_between(error_deg,lo,hi,alpha=.18,label='95% synthetic run interval')
plt.xlabel('Independent per-channel phase-error standard deviation (degrees)')
plt.ylabel('Normalized phasor coherence, 0–1 (dimensionless)')
plt.ylim(0,1.05)
plt.title('24-channel phase-error sensitivity — abstract control model')
plt.grid(alpha=.22);plt.legend()
plt.text(.03,.07,'NOT A SURFACE-WAVE OR PROPULSION PREDICTION',
         transform=plt.gca().transAxes,fontsize=9,
         bbox=dict(facecolor='white',alpha=.8,edgecolor='none'))
plt.tight_layout();plt.savefig(OUT/'figure_2_synthetic_phase_sensitivity.png');plt.close()

s=[]
s.append('# ASC S1: Preliminary Synthetic Measurement Demonstration')
s.append('')
s.append('**Status:** computational teaching/reference model, **not** experimental evidence, not a material-specific FEM model, not a validated ASC design.')
s.append('')
s.append('## Objective')
s.append('Rehearse two tests specified as future objectives in ASC Preprint 0.2 (20 November 2026): (A) S1 flat-coupon comparison against direct drive with repeat trials; (B) sensitivity of a 24-addressable-channel architecture to phase error.')
s.append('The numbers below are deliberately **illustrative**, not obtained from an ASC specimen or the withheld private engineering dossier.')
s.append('')
s.append('## Model A — normalized S1 transfer function')
s.append('A generic damped second-order mode is used:')
s.append('')
s.append('`H(r) = G / [(r0^2 - r^2) + i*2*zeta*r0*r]`')
s.append('')
s.append('where `r` is normalized frequency, `r0` the normalized natural frequency, `zeta` the damping ratio, and `G` an arbitrary response scale.')
s.append('Direct-drive reference: r0=1.00, zeta=0.040, G=1.00.')
s.append('Hypothetical interface: r0=1.02, zeta=0.046, G=0.95. These settings *do not encode a claimed ASC improvement*; they deliberately make the candidate different to test the comparison pipeline.')
s.append('Thirty independent synthetic acquisitions are created at each condition using amplitude noise sigma=0.018 and run-to-run gain drift sigma=0.012, both normalized. Error ribbon is approximate 95% confidence interval for the **mean** of simulated repeats, not a real metrology uncertainty budget.')
s.append('')
s.append('## Model B — 24-channel phase coherence')
s.append('For independent phase errors `epsilon_i` normally distributed with standard deviation `sigma_phi`, coherence is computed as')
s.append('')
s.append('`C = |sum(exp(i * epsilon_i))| / 24`.')
s.append('')
s.append('Six thousand Monte Carlo realizations are evaluated at each phase-error standard deviation from 0 to 90 degrees. The plotted band is the 2.5th–97.5th percentile over simulated realizations.')
s.append('No actuator coupling, geometry, elastic-wave dispersion, multiphysics model, vehicle motion, or thrust is calculated.')
s.append('')
s.append('## Illustrative numerical output')
for label, data in response.items():
    idx=int(np.argmax(data['mean']))
    s.append(f'- {label}: synthetic mean peak {data["mean"][idx]:.3f} at normalized frequency {r[idx]:.3f}.')
for target in [0,15,30,60,90]:
    row=next(x for x in phase_rows if x[0]==target)
    s.append(f'- Phase-error SD {target} degrees: coherence {row[1]:.3f} (simulated 95% range {row[2]:.3f}–{row[3]:.3f}).')
s.append('')
s.append('## What this can and cannot answer')
s.append('It checks that a reproducible sweep, reference comparison, repeated-trial variability, and phase-error sensitivity can be computed and documented. It can help plan sample rates, sensor placement, calibration, acceptance metrics, and negative controls once real hardware parameters exist.')
s.append('It **cannot** establish an ASC operating frequency, power conversion efficiency, coupling gain, useful surface-wave mode, force generation, novelty, or technical feasibility. It is not evidence for a patent or a Zenodo performance claim.')
s.append('')
s.append('## Next real-world inputs required')
s.append('A chosen specimen geometry, verified material properties, mounting conditions, actuator and sensor locations, excitation limits, instrumentation response, calibration, and independent reference measurements. Once available, use a measured FRF and FEM/multiphysics model rather than this toy oscillator.')
s.append('')
s.append('## Files')
s.append('`run_simulation.py` (reproducible source), `synthetic_s1_measurements.csv`, `synthetic_24_channel_phase_sensitivity.csv`, two PNG plots. Re-run with Python 3.10+, NumPy, Matplotlib. Random seed 20261120.')
(OUT/'README.md').write_text('\n'.join(s)+'\n',encoding='utf8')
print('\n'.join(s[-27:-14]))
