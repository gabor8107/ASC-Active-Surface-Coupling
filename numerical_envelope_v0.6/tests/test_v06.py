import math, sys, unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
from asc_physics import *

class PhysicsBoundsTests(unittest.TestCase):
    def test_speed_of_light(self):self.assertEqual(C,299792458.)
    def test_jet_100kw(self):self.assertAlmostEqual(jet(100000,1500,.45)['thrust_axial_N'],6.11829727786757,10)
    def test_mdot_from_thrust(self):
        j=jet(100000,1500,.45)
        self.assertAlmostEqual(j['mass_flow_kg_s']*j['ve_m_s'],j['thrust_magnitude_N'],10)
    def test_jet_kinetic_power(self):
        j=jet(100000,1500,.45)
        self.assertAlmostEqual(.5*j['mass_flow_kg_s']*j['ve_m_s']**2,45000.)
    def test_jet_projection(self):self.assertAlmostEqual(jet(50000,1500,.45,.5)['thrust_axial_N'],jet(50000,1500,.45)['thrust_axial_N']*.5)
    def test_projection_zero(self):self.assertEqual(jet(10000,1000,.5,0)['thrust_axial_N'],0)
    def test_invalid_efficiency(self):
        with self.assertRaises(ValueError):jet(10,500,1.01)
    def test_invalid_isp(self):
        with self.assertRaises(ValueError):jet(10,0,.5)
    def test_invalid_negative_power(self):
        with self.assertRaises(ValueError):jet(-10,1500,.5)
    def test_photon_100kw(self):self.assertAlmostEqual(photon(100000),100000/C)
    def test_photon_angular(self):self.assertAlmostEqual(photon(100000,.4),photon(100000)*.4)
    def test_photon_invalid(self):
        with self.assertRaises(ValueError):photon(100,1.4)
    def test_budget_closes(self):
        b=split_budget(100000,20000,.0465,350)
        self.assertAlmostEqual(b['jet_available_W'],80580)
        self.assertAlmostEqual(b['balance_residual_W'],0)
    def test_budget_no_recovery(self):self.assertAlmostEqual(split_budget(100000,20000,0,350)['jet_available_W'],79650)
    def test_budget_recovery_0_sector(self):self.assertEqual(split_budget(100000,0,.1)['jet_available_W'],100000)
    def test_budget_no_free_energy(self):self.assertLessEqual(split_budget(100000,20000,1.)['jet_available_W'],100000)
    def test_budget_exceeds_source(self):
        with self.assertRaises(ValueError):split_budget(100000,150000,.1)
    def test_budget_negative_aux(self):
        with self.assertRaises(ValueError):split_budget(100000,10000,.1,-1)
    def test_efficiency_breakeven(self):
        b=split_budget(100000,20000,.0465,350)
        e=eta_to_break_even(.45,100000,b['jet_available_W'])
        self.assertAlmostEqual(jet(b['jet_available_W'],1500,e)['thrust_axial_N'],jet(100000,1500,.45)['thrust_axial_N'])
    def test_efficiency_less_power_requires_more_efficiency(self):self.assertGreater(eta_to_break_even(.45,100000,80000),.45)
    def test_efficiency_zero_alignment(self):self.assertTrue(math.isinf(eta_to_break_even(.45,100000,80000,1.,0)))
    def test_rocket_mass_ratio(self):
        r=rocket_budget(300,100000/3.6,100000,1500,.45)
        self.assertAlmostEqual(r['wet_mass_kg']/r['dry_mass_kg'],r['required_mass_ratio'])
    def test_rocket_100k_days(self):self.assertAlmostEqual(rocket_budget(300,100000/3.6,100000,1500,.45)['constant_power_burn_days'],46.8208187,places=4)
    def test_rocket_300k_days(self):self.assertAlmostEqual(rocket_budget(300,300000/3.6,100000,5000,.45)['constant_power_burn_days'],414.749525,places=4)
    def test_rocket_more_dv_more_propellant(self):self.assertGreater(rocket_budget(300,300000/3.6,100000,1500,.45)['required_propellant_kg'],rocket_budget(300,100000/3.6,100000,1500,.45)['required_propellant_kg'])
    def test_rocket_more_power_shorter_burn(self):self.assertAlmostEqual(rocket_budget(300,100000/3.6,200000,1500,.45)['constant_power_burn_days'],rocket_budget(300,100000/3.6,100000,1500,.45)['constant_power_burn_days']/2)
    def test_rocket_no_fuel_burn_model(self):
        with self.assertRaises(ValueError):rocket_budget(300,100,100000,1500,0)
    def test_rocket_more_alignment_cost(self):self.assertGreater(rocket_budget(300,100000/3.6,100000,1500,.45,.8)['required_propellant_kg'],rocket_budget(300,100000/3.6,100000,1500,.45,1.)['required_propellant_kg'])
    def test_energy_total(self):
        r=rocket_budget(300,100000/3.6,100000,1500,.45)
        self.assertAlmostEqual(r['source_energy_MWh'],r['constant_power_burn_days']*24*100/1000)
    def test_radiator_temp(self):self.assertLess(radiator_area(55000,400),radiator_area(55000,350))
    def test_radiator_zero(self):self.assertEqual(radiator_area(0,400),0)
    def test_radiator_bad_temp(self):
        with self.assertRaises(ValueError):radiator_area(100,300,ambient_K=301)
    def test_array_cell_count(self):self.assertEqual(array_forces()['installed_cells'],288)
    def test_array_axial_full(self):self.assertAlmostEqual(array_forces()['force_z_N'],jet(80000,1500,.45)['thrust_axial_N'])
    def test_array_lateral_cancellation(self):self.assertLess(abs(array_forces(tilt_deg=10)['force_x_N']),1e-10)
    def test_array_torque_cancellation(self):self.assertLess(array_forces(tilt_deg=10)['torque_norm_Nm'],1e-10)
    def test_array_one_dead_has_torque(self):self.assertGreater(array_forces(tilt_deg=10,dead_sectors=[0])['torque_norm_Nm'],0)
    def test_array_symmetric_three_dead_torque(self):self.assertLess(array_forces(tilt_deg=10,dead_sectors=[0,8,16])['torque_norm_Nm'],1e-10)
    def test_array_dead_reduces_axial(self):self.assertLess(array_forces(dead_sectors=[0])['force_z_N'],array_forces()['force_z_N'])
    def test_array_planar_no_axial(self):self.assertAlmostEqual(array_forces(tilt_deg=90)['force_z_N'],0,places=10)
    def test_array_bad_dead(self):
        with self.assertRaises(ValueError):array_forces(dead_sectors=[24])
    def test_array_bad_cell_count(self):
        with self.assertRaises(ValueError):array_forces(cells_per_sector=0)
    def test_array_bad_tilt(self):
        with self.assertRaises(ValueError):array_forces(tilt_deg=110)
    def test_source_area(self):self.assertAlmostEqual(source_envelopes(100000)['ideal_1AU_illuminated_solar_area_m2'],100000/(1361*.25))
    def test_source_more_power_more_area(self):self.assertGreater(source_envelopes(200000)['ideal_1AU_illuminated_solar_area_m2'],source_envelopes(100000)['ideal_1AU_illuminated_solar_area_m2'])

if __name__=='__main__': unittest.main()
