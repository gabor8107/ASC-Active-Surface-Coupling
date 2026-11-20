"""Automated sanity checks (no physical validation claimed)."""
import sys, unittest, json
from pathlib import Path
import numpy as np
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
import run_fem as m
CFG=json.loads((ROOT/'public_config.json').read_text(encoding='utf-8'))

class TestPhysicsSanity(unittest.TestCase):
    def test_stiffness_mass_symmetric_positive_definite(self):
        K,M,f,x=m.make_model(CFG,20,True)
        self.assertTrue(np.allclose(K,K.T))
        self.assertTrue(np.allclose(M,M.T))
        self.assertGreater(np.linalg.eigvalsh(K).min(),0)
        self.assertGreater(np.linalg.eigvalsh(M).min(),0)
    def test_unpatched_beam_against_analytical_fundamental(self):
        K,M,f,x=m.make_model(CFG,40,False)
        freq,_=m.modal(K,M,4)
        self.assertLess(abs(freq[0]/m.analytical_f1(CFG)-1),0.001)
    def test_zero_voltage_zero_force(self):
        cc=json.loads(json.dumps(CFG))
        cc['excitation']['voltage_peak_V']=0.0
        _,_,f,_=m.make_model(cc,20,True)
        self.assertLess(np.max(np.abs(f)),1e-15)
    def test_voltage_scaling_static(self):
        a=m.solution(CFG,20,True)
        cc=json.loads(json.dumps(CFG))
        cc['excitation']['voltage_peak_V']*=2
        b=m.solution(cc,20,True)
        self.assertAlmostEqual(b['u'][-2]/a['u'][-2],2.0,places=8)
    def test_modes_independent_of_drive_amplitude(self):
        a=m.solution(CFG,20,True)
        cc=json.loads(json.dumps(CFG))
        cc['excitation']['voltage_peak_V']*=1.5
        b=m.solution(cc,20,True)
        self.assertTrue(np.allclose(a['freq'],b['freq'],rtol=1e-6))

if __name__=='__main__':unittest.main()
