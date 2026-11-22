import math
import unittest
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
from hybrid_recovery import *

class HybridRecoveryTests(unittest.TestCase):
    def setUp(self):
        self.r=recoverable_power(100_000,.45,.45,.07,.03,.05,.3,.1,1,400,300)

    def test_carnot(self):
        self.assertAlmostEqual(carnot_limit(400,300),.25)

    def test_no_heat_engine_above_carnot(self):
        with self.assertRaises(ValueError):recoverable_power(100000,.45,.45,.07,.03,.30,.3,.1,1,400,300)

    def test_invalid_reservoir(self):
        with self.assertRaises(ValueError):carnot_limit(300,300)
        with self.assertRaises(ValueError):carnot_limit(250,300)

    def test_exact_100kw_recovery(self):
        self.assertAlmostEqual(self.r['raw_recovered_W'],4650)
        self.assertAlmostEqual(self.r['heat_recovered_W'],2250)
        self.assertAlmostEqual(self.r['rf_recovered_W'],2100)
        self.assertAlmostEqual(self.r['vibration_recovered_W'],300)
        self.assertAlmostEqual(self.r['heat_to_reject_after_TEG_W'],42750)

    def test_partition_must_be_exclusive(self):
        with self.assertRaises(ValueError):recoverable_power(100000,.45,.5,.07,.03,.05,.3,.1,1,400,300)

    def test_rf_availability_zero(self):
        r=recoverable_power(100000,.45,.45,.07,.03,.05,.3,.1,0,400,300)
        self.assertAlmostEqual(r['raw_recovered_W'],2550)

    def test_no_recovery_boundary(self):
        e=fixed_useful_comparison(100000,.45,0,0,0)
        self.assertAlmostEqual(e['external_savings_W'],0)
        x=fixed_external_comparison(100000,.45,0,0,0)
        self.assertAlmostEqual(x['delta_useful_W'],0)

    def test_fixed_useful_closure(self):
        e=fixed_useful_comparison(100000,.45,.0465,.006,350)
        self.assertAlmostEqual(e['hybrid_useful_W'],45000)
        self.assertAlmostEqual(e['hybrid_internal_W']*(1-.0465)+350,e['hybrid_external_W'])
        self.assertTrue(2000<e['external_savings_W']<4000)

    def test_fixed_external_closure(self):
        x=fixed_external_comparison(100000,.45,.0465,.006,350)
        self.assertAlmostEqual(x['hybrid_internal_W']*(1-.0465)+350,100000)
        self.assertTrue(x['delta_useful_W']>0)

    def test_too_large_penalty(self):
        e=fixed_useful_comparison(100000,.45,.0465,.04,350)
        self.assertLess(e['external_savings_W'],0)

    def test_rf_capture_not_a_source(self):
        r=recoverable_power(100000,.45,.45,.07,.03,0,0,0,0,400,300)
        self.assertEqual(r['raw_recovered_W'],0)

    def test_radiator_area_monotonicity(self):
        a=radiator_area_vacuum(45000,300)
        b=radiator_area_vacuum(45000,400)
        self.assertGreater(a,b)
        self.assertGreater(a,radiator_area_vacuum(42750,300))

    def test_mass_penalty(self):
        r=simple_mass_penalty_proxy(100,8,45000,46300)
        self.assertLess(r['acceleration_ratio_hybrid_to_base'],1)

    def test_mass_zero(self):
        r=simple_mass_penalty_proxy(100,0,45000,45000)
        self.assertAlmostEqual(r['acceleration_ratio_hybrid_to_base'],1)

    def test_no_negative_source(self):
        with self.assertRaises(ValueError):fixed_external_comparison(100000,.45,.0465,.006,110000)

    def test_no_recovery_over_100_percent(self):
        with self.assertRaises(ValueError):fixed_useful_comparison(100000,.45,1.0,0,0)

    def test_break_even_identity(self):
        p=break_even_penalty_fraction(.45,.0465,350,100000)
        x=fixed_external_comparison(100000,.45,.0465,p,350)
        self.assertAlmostEqual(x['delta_useful_W'],0,places=5)

    def test_conservation_ledger(self):
        self.assertAlmostEqual(self.r['energy_balance_residual_W'],0,places=8)
        self.assertLess(self.r['raw_recovered_W'],self.r['heat_bin_W']+self.r['rf_bin_W']+self.r['vibration_bin_W'])

if __name__=='__main__':unittest.main()
