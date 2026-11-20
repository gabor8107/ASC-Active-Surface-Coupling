#!/usr/bin/env python3
"""ASC S1 public 1-D Euler-Bernoulli composite beam finite-element benchmark.

Model limitations: low-frequency slender-beam bending only. The piezoelectric
actuation is represented as a prescribed free strain d31*V/t_p: no coupled
piezoelectric field, high-frequency SAW, thermal model, or ASC system physics.
All numerical dimensions and controls are PUBLIC ILLUSTRATIVE assumptions.
"""
from pathlib import Path
import argparse, csv, json
import numpy as np
from scipy.linalg import eigh
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

HERE = Path(__file__).resolve().parent


def section(x, cfg, active):
    """Cross-sectional EI, lineic mass mu, eigenstrain-generated moment.

    z=0 at aluminum bottom, z increasing upward. Neutral axis is E-weighted.
    This simple composite cross-section assumes perfect bonding, linear
    elasticity and a uniform transverse electric field in the PZT patch.
    """
    s = cfg['substrate']; p = cfg['piezo']
    b = cfg['specimen']['width_m']
    layers = [(0.0, s['thickness_m'], s['E_Pa'], s['rho_kg_m3'], 0.0)]
    has_patch = active and x <= cfg['specimen']['patch_end_m'] + 1e-12
    if has_patch:
        layers += [(s['thickness_m'], s['thickness_m'] + p['thickness_m'],
                    p['E_Pa'], p['rho_kg_m3'],
                    p['d31_m_V'] * cfg['excitation']['voltage_peak_V'] / p['thickness_m'])]
    EA = sum(b*E*(z1-z0) for z0,z1,E,rho,eps in layers)
    zbar = sum(b*E*(z1*z1-z0*z0)/2 for z0,z1,E,rho,eps in layers) / EA
    EI = sum(b*E*((z1-zbar)**3-(z0-zbar)**3)/3 for z0,z1,E,rho,eps in layers)
    mu = sum(b*rho*(z1-z0) for z0,z1,E,rho,eps in layers)
    M0 = sum(b*E*eps*((z1-zbar)**2-(z0-zbar)**2)/2
             for z0,z1,E,rho,eps in layers)
    return EI, mu, M0


def element_matrices(EI, mu, h):
    ke = (EI/h**3)*np.array([
        [12, 6*h, -12, 6*h],
        [6*h, 4*h*h, -6*h, 2*h*h],
        [-12, -6*h, 12, -6*h],
        [6*h, 2*h*h, -6*h, 4*h*h],
    ], dtype=float)
    me = (mu*h/420)*np.array([
        [156, 22*h, 54, -13*h],
        [22*h, 4*h*h, 13*h, -3*h*h],
        [54, 13*h, 156, -22*h],
        [-13*h, -3*h*h, -22*h, 4*h*h],
    ], dtype=float)
    return ke, me


def make_model(cfg, ne=80, active=True):
    L = cfg['specimen']['length_m']; patch = cfg['specimen']['patch_end_m']
    assert ne > 6 and 0.0 < patch < L
    # Keep the patch tip precisely at an element boundary.
    npatch = int(round(ne*patch/L))
    assert abs(npatch/ne-patch/L) < 1e-10, 'Choose ne divisible by 5 for 60% patch.'
    h = L/ne; nd=2*(ne+1)
    K=np.zeros((nd,nd)); M=np.zeros((nd,nd)); f=np.zeros(nd)
    for i in range(ne):
        x=(i+.5)*h
        EI,mu,M0 = section(x,cfg,active)
        ke,me=element_matrices(EI,mu,h)
        idx=np.array([2*i,2*i+1,2*i+2,2*i+3])
        K[np.ix_(idx,idx)]+=ke
        M[np.ix_(idx,idx)]+=me
        # Integral of Hermite second-derivative B over element:
        # ∫ B dx = [0,-1,0,+1] in DOFs (w1,theta1,w2,theta2).
        f[idx]+= M0*np.array([0.,-1.,0.,1.])
    free=np.arange(2,nd) # w(0)=theta(0)=0
    return K[np.ix_(free,free)],M[np.ix_(free,free)],f[free],np.linspace(0,L,ne+1)


def modal(K,M,k=4):
    # Dense symmetric generalized eigenanalysis works for these public meshes.
    lamb,vec=eigh(K,M,subset_by_index=(0,k-1),check_finite=True)
    freq=np.sqrt(lamb)/(2*np.pi)
    return freq,vec


def solution(cfg,ne,active=True):
    K,M,f,x=make_model(cfg,ne,active)
    freq,modes=modal(K,M,4)
    u=np.linalg.solve(K,f)
    # Modal-projection frequency response with assumed modal damping.
    zeta=cfg['excitation']['modal_damping_ratio']
    freq_drive=np.linspace(10,800,1581)
    w_drive=2*np.pi*freq_drive
    # M-normal modes: phi^T M phi = 1
    # Modal truncation (first 4) is suitable for low-frequency range only.
    ff=modes.T@f
    mode_tip=modes[-2,:]
    q=np.zeros(freq_drive.shape,dtype=complex)
    for j,w0 in enumerate(2*np.pi*freq):
        q+=(mode_tip[j]*ff[j])/(w0*w0 - w_drive*w_drive+2j*zeta*w0*w_drive)
    return {'K':K,'M':M,'f':f,'x':x,'freq':freq,'modes':modes,'u':u,
            'drive_hz':freq_drive,'response_m':q,'active':active,'ne':ne}


def analytical_f1(cfg):
    s=cfg['substrate']; L=cfg['specimen']['length_m']; t=s['thickness_m']
    beta=1.875104068711961
    return beta**2/(2*np.pi*L**2)*np.sqrt(s['E_Pa']*t*t/(12*s['rho_kg_m3']))


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--config',default='public_config.json')
    parser.add_argument('--output',default='results')
    args=parser.parse_args()
    cfg=json.loads((HERE/args.config).read_text(encoding='utf-8'))
    out=HERE/args.output; out.mkdir(parents=True,exist_ok=True)
    ne=80; act=solution(cfg,ne,True); bare=solution(cfg,ne,False)
    fref=analytical_f1(cfg)
    # Verification: closed-form first frequency for uniform bare cantilever
    assert abs(bare['freq'][0]-fref)/fref < .001, 'Bare beam FE fails analytical benchmark'
    # Mesh verification on patch structure; modal and static convergence.
    convergence=[]
    for n in [20,40,80,160]:
        obj=solution(cfg,n,True)
        convergence.append({'elements':n,'f1_hz':float(obj['freq'][0]),
                            'tip_static_um':float(obj['u'][-2]*1e6)})
    ref_c=convergence[-1]
    rel_f=abs(convergence[-2]['f1_hz']/ref_c['f1_hz']-1)
    rel_tip=abs(convergence[-2]['tip_static_um']/ref_c['tip_static_um']-1)
    # 80 vs 160 elements should yield <2% modal convergence, <1% static.
    assert rel_f < .02 and rel_tip < .01, f'Mesh convergence failed: {rel_f},{rel_tip}'
    # Parameter sensitivity: vary PZT E (illustrative ±20%)
    sweep=[]
    for fac in [.8,.9,1.,1.1,1.2]:
        cc=json.loads(json.dumps(cfg));cc['piezo']['E_Pa']*=fac
        so=solution(cc,80,True)
        sweep.append({'E_pzt_factor':fac,'f1_hz':float(so['freq'][0]),
                      'tip_static_um':float(so['u'][-2]*1e6)})
    # Output data
    with open(out/'modal_frequencies.csv','w',newline='') as g:
        wr=csv.writer(g);wr.writerow(['mode','bare_aluminum_hz','aluminum_with_pzt_patch_hz'])
        for i in range(4):wr.writerow([i+1,format(bare['freq'][i],'.9g'),format(act['freq'][i],'.9g')])
    with open(out/'mesh_convergence.csv','w',newline='') as g:
        wr=csv.DictWriter(g,fieldnames=convergence[0].keys());wr.writeheader();wr.writerows(convergence)
    with open(out/'pzt_modulus_sensitivity.csv','w',newline='') as g:
        wr=csv.DictWriter(g,fieldnames=sweep[0].keys());wr.writeheader();wr.writerows(sweep)
    with open(out/'piezo_voltage_response.csv','w',newline='') as g:
        wr=csv.writer(g);wr.writerow(['frequency_hz','tip_displacement_amplitude_um','tip_phase_deg'])
        for fr,q in zip(act['drive_hz'],act['response_m']):
            wr.writerow([format(fr,'.7g'),format(abs(q)*1e6,'.9g'),format(np.angle(q,deg=True),'.9g')])
    summary={
       'status':'SIMULATED — ILLUSTRATIVE INPUTS — NO EXPERIMENTAL VALIDATION',
       'model':'1-D composite Euler-Bernoulli beam finite elements, Hermite cubic, consistent mass',
       'n_elements_final':ne,
       'bare_analytical_f1_hz':float(fref),'bare_FE_f1_hz':float(bare['freq'][0]),
       'composite_FE_frequencies_hz':[float(v) for v in act['freq']],
       'composite_static_tip_deflection_um_at_peak_voltage':float(act['u'][-2]*1e6),
       'composite_peak_FRF_frequency_hz':float(act['drive_hz'][np.argmax(abs(act['response_m']))]),
       'composite_peak_FRF_amplitude_um':float(max(abs(act['response_m']))*1e6),
       'convergence_80_to_160_relative_f1':float(rel_f),
       'convergence_80_to_160_relative_static_tip':float(rel_tip),
       'contains_no_real_ASC_dimensions_or_control_settings':True,
       'model_is_not_SAW_piezo_multiphysics':True,
    }
    (out/'summary.json').write_text(json.dumps(summary,indent=2),encoding='utf-8')
    plt.rcParams.update({'font.size':10,'axes.spines.top':False,'axes.spines.right':False,'figure.dpi':155})
    fig,ax=plt.subplots(figsize=(10.4,3.5))
    L=cfg['specimen']['length_m'];patch=cfg['specimen']['patch_end_m'];
    ts=cfg['substrate']['thickness_m'];tp=cfg['piezo']['thickness_m']
    from matplotlib.patches import Rectangle
    ax.add_patch(Rectangle((0,0),L*1000,ts*1000,facecolor='#aebcc9',edgecolor='#2f4057',label='Aluminum substrate'))
    ax.add_patch(Rectangle((0,ts*1000),patch*1000,tp*1000,facecolor='#e7ba70',edgecolor='#744c17',label='PZT patch (equivalent strain)'))
    ax.axvline(0,color='#c0392b',lw=5,alpha=.7)
    ax.annotate('Clamped end',xy=(0,.4),xytext=(10,3.2),arrowprops={'arrowstyle':'->'})
    ax.annotate('Free end, tip displacement',xy=(100,0.5),xytext=(57,3.2),arrowprops={'arrowstyle':'->'})
    ax.set(xlim=(-3,109),ylim=(-.4,4.1),xlabel='Axial position (mm)',ylabel='Section height (mm)',title='S1 public benchmark specimen | not ASC design dimensions')
    ax.legend(loc='lower center',ncol=2,frameon=False)
    fig.tight_layout();fig.savefig(out/'fig_01_public_coupon_schematic.png');plt.close(fig)
    # Normalize eigenfunctions to +/-1, interpolate sampled nodes
    fig,axs=plt.subplots(2,2,figsize=(10.5,7.1),sharex=True)
    for j,ax in enumerate(axs.flat):
        w=np.r_[0.0,act['modes'][::2,j]]
        w=w/max(abs(w))
        ax.plot(act['x']*1e3,w,lw=2)
        ax.axhline(0,color='gray',lw=.7)
        ax.set_title(f'Mode {j+1}: {act["freq"][j]:.2f} Hz')
        ax.set_ylabel('Normalized transverse mode shape')
        ax.grid(alpha=.2)
    for ax in axs[-1]:ax.set_xlabel('Distance from clamped end (mm)')
    fig.suptitle('Predicted bending eigenmodes | composite beam FEM',weight='bold')
    fig.tight_layout();fig.savefig(out/'fig_02_fem_mode_shapes.png');plt.close(fig)
    fig,axs=plt.subplots(2,1,figsize=(10.6,7.1),sharex=True)
    axs[0].semilogy(act['drive_hz'],np.maximum(abs(act['response_m'])*1e6,1e-7),lw=1.7)
    axs[0].set_ylabel('Tip amplitude (µm peak)')
    axs[1].plot(act['drive_hz'],np.angle(act['response_m'],deg=True),lw=1)
    axs[1].set(ylabel='Phase (degrees)',xlabel='Sinusoidal voltage drive frequency (Hz)')
    for ax in axs:
        for fr in act['freq']:
            if fr <= 800:ax.axvline(fr,ls='--',alpha=.23,color='grey')
        ax.grid(alpha=.2)
    fig.suptitle('Predicted low-frequency response | four-mode truncation, assumed damping',weight='bold')
    fig.tight_layout();fig.savefig(out/'fig_03_fem_frequency_response.png');plt.close(fig)
    fig,ax=plt.subplots(figsize=(9.8,4.6))
    ax.plot([a['elements'] for a in convergence],[a['f1_hz'] for a in convergence],'o-',label='Fundamental frequency')
    ax.set(xlabel='Number of beam elements',ylabel='First bending frequency (Hz)',title='Mesh convergence check | composite specimen')
    ax.grid(alpha=.2)
    fig.tight_layout();fig.savefig(out/'fig_04_mesh_convergence.png');plt.close(fig)
    fig,ax1=plt.subplots(figsize=(9.8,4.6))
    ax1.plot([a['E_pzt_factor'] for a in sweep],[a['f1_hz'] for a in sweep],'o-',label='f1')
    ax1.set(xlabel='PZT Young modulus multiplier (illustrative)',ylabel='First bending frequency (Hz)',title='Illustrative material-parameter sensitivity')
    ax1.grid(alpha=.2)
    fig.tight_layout();fig.savefig(out/'fig_05_modulus_sensitivity.png');plt.close(fig)
    print(json.dumps(summary,indent=2))

if __name__=='__main__':main()
