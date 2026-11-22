"""Unit tests for public conditional physics. Passing tests are NOT ASC validation."""
import math
from pathlib import Path
import sys
import unittest
import numpy as np
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
from models import *

class GeometryTests(unittest.TestCase):
    def test_proxy_area_mass(self):
        g=cylinder_proxy(1,.25,.001,2700,{'frame':4})
        self.assertAlmostEqual(g['skin_area_m2'], 0.5*math.pi + 0.25*math.pi)
        self.assertAlmostEqual(g['proxy_skin_mass_kg'], g['skin_area_m2']*2.7)
        self.assertAlmostEqual(g['total_proxy_mass_kg']-g['proxy_skin_mass_kg'], 4)
    def test_proxy_bad_input(self):
        with self.assertRaises(ValueError):cylinder_proxy(-1,.25,.001,2700,{})
    def test_proxy_no_negative_masses(self):
        with self.assertRaises(AssertionError):cylinder_proxy(1,.25,.001,2700,{'bad':-5})

class DynamicsTests(unittest.TestCase):
    def test_zero_drag(self):self.assertEqual(drag_force(1.225,0,.5,1),0)
    def test_drag_speed_square(self):self.assertAlmostEqual(drag_force(1,4,1,1)/drag_force(1,2,1,1),4)
    def test_drag_area_scale(self):self.assertAlmostEqual(drag_force(1,3,.5,2)/drag_force(1,3,.5,1),2)
    def test_drag_power_cubic(self):
        p1=drag_electrical_power(1.225,4,.6,.25,.5)
        p2=drag_electrical_power(1.225,8,.6,.25,.5)
        self.assertAlmostEqual(p2/p1,8)
    def test_drag_invalid_eff(self):
        with self.assertRaises(ValueError): drag_electrical_power(1,1,1,1,1.1)
    def test_hover_mass_three_halves(self):
        p1=ideal_hover_power(2,1,1)
        p2=ideal_hover_power(4,1,1)
        self.assertAlmostEqual(p2/p1,2**1.5)
    def test_hover_area_half(self):
        self.assertAlmostEqual(ideal_hover_power(3,1,4)/ideal_hover_power(3,1,1),.5)
    def test_hover_positive(self):
        with self.assertRaises(ValueError):ideal_hover_power(10,1,1,-.3)
    def test_hydro_zero_neutral(self):
        h=displaced_water(10,0.01,1000)
        self.assertAlmostEqual(h['net_upward_N'],0)
        self.assertAlmostEqual(h['neutral_ballast_kg'],0)
    def test_pressure_depth_linear(self):
        self.assertAlmostEqual(hydrostatic_pressure(20)/hydrostatic_pressure(10),2)
    def test_jet_momentum_energy(self):
        o=water_jet_ideal(40,2)
        self.assertAlmostEqual(o['mass_flux_kg_s'],20)
        self.assertAlmostEqual(o['jet_kinetic_W'],40)

class VacuumTests(unittest.TestCase):
    def test_electric_jet_power_balance(self):
        e=electric_thruster(1000,1500,.45)
        kinetic=.5*e['mass_flow_kg_s']*e['exhaust_velocity_m_s']**2
        self.assertAlmostEqual(kinetic,450)
        self.assertAlmostEqual(e['thrust_N'],e['mass_flow_kg_s']*e['exhaust_velocity_m_s'])
    def test_electric_thrust_inverse_isp(self):
        a=electric_thruster(1000,500)['thrust_N']
        b=electric_thruster(1000,1000)['thrust_N']
        self.assertAlmostEqual(a/b,2)
    def test_electric_invalid_fraction(self):
        with self.assertRaises(ValueError):electric_thruster(1000,500,2)
    def test_rocket_equation_zero_prop(self):self.assertEqual(rocket_delta_v(1000,10,0),0)
    def test_rocket_equation_mass(self):
        self.assertAlmostEqual(rocket_delta_v(1500,10,5),1500*G0*math.log(2))
    def test_rocket_equation_invalid_prop(self):
        with self.assertRaises(ValueError):rocket_delta_v(500,1,2)
    def test_photon_thrust(self):self.assertAlmostEqual(photon_thrust(1000)*C0,1000)

class EnergyTests(unittest.TestCase):
    def test_chain_conserves(self):
        e=energy_chain(1000,.85,.35)
        self.assertAlmostEqual(e['mechanical_W']+e['non_mechanical_losses_W'],1000)
        self.assertAlmostEqual(e['energy_balance_residual_W'],0)
    def test_radiation_zero(self):
        self.assertAlmostEqual(radiation_equilibrium(0,1,.8),293.15)
    def test_radiation_increases(self):
        self.assertGreater(radiation_equilibrium(1000,1,.8),radiation_equilibrium(200,1,.8))
    def test_resonator_q(self):
        self.assertAlmostEqual(stored_energy_from_q_loss(100,3,1000),100*3/(2*math.pi*1000))
    def test_return_loss(self):
        self.assertAlmostEqual(delivered_fraction_from_return_loss(10),.9)
        self.assertAlmostEqual(delivered_fraction_from_return_loss(0),0)
    def test_cable_heat(self):self.assertAlmostEqual(ohmic_heat(2,.2,24),19.2)

class StructureTests(unittest.TestCase):
    def test_cantilever_frequency(self):
        b=cantilever_analytic(70e9,2700,.12,.015,.001,.01)
        self.assertAlmostEqual(b['first_frequency_hz'],57.119571,places=4)
        self.assertGreater(b['tip_deflection_m'],0)
    def test_cantilever_linear_tip_scaling(self):
        a=cantilever_analytic(70e9,2700,.12,.015,.001,.005)
        b=cantilever_analytic(70e9,2700,.12,.015,.001,.01)
        self.assertAlmostEqual(b['tip_deflection_m']/a['tip_deflection_m'],2)
        self.assertAlmostEqual(b['root_bending_stress_Pa']/a['root_bending_stress_Pa'],2)
    def test_cantilever_frequency_thickness(self):
        a=cantilever_analytic(70e9,2700,.12,.015,.001,.01)
        b=cantilever_analytic(70e9,2700,.12,.015,.002,.01)
        self.assertAlmostEqual(b['first_frequency_hz']/a['first_frequency_hz'],2)

class PhaseTests(unittest.TestCase):
    def test_perfect_mode(self):
        th=2*np.pi*np.arange(24)/24
        self.assertAlmostEqual(synthetic_mode_score(3*th,3),1)
        self.assertLess(synthetic_mode_score(3*th,4),1e-10)
    def test_uniform_null(self):
        a=mode_monte_carlo(24,3,.3,1000,22)
        self.assertGreater(a['mean'],a['random_null_mean'])
        self.assertGreater(a['mean'],a['wrong_mode_mean'])
    def test_reproducible(self):
        self.assertEqual(mode_monte_carlo(24,3,.3,1000,22),mode_monte_carlo(24,3,.3,1000,22))
    def test_phase_noise_degrades(self):
        a=mode_monte_carlo(24,3,.1,1000,22)
        b=mode_monte_carlo(24,3,1,1000,22)
        self.assertGreater(a['mean'],b['mean'])
    def test_clock_frequency(self):
        self.assertAlmostEqual(jitter_s_for_phase_degrees(1e5,5)*1e6,5/36,places=8)
    def test_wave_sampling_scale(self):
        a=wave_sampling_scale(3000,100000,math.pi)
        self.assertAlmostEqual(a['wavelength_m'],.03)
        self.assertEqual(a['minimum_points_around_ring'],210)
        self.assertLess(a['sampling_pitch_m'],a['wavelength_m'])
    def test_phase_invalid(self):
        with self.assertRaises(ValueError):mode_monte_carlo(24,3,-.1)

class EnvelopeTests(unittest.TestCase):
    def test_seeded_sensitivity(self):
        args=(1000,123,[12,25],[.7,1.3],[.45,.75],[.2,1],2,[.35,.7],1.225,1025,.25)
        self.assertEqual(uncertainty_envelope(*args),uncertainty_envelope(*args))
    def test_bounds(self):
        d=uncertainty_envelope(1000,23,[12,25],[.7,1.3],[.45,.75],[.2,1],2,[.35,.7],1.225,1025,.25)
        for k in ('hover_power_W','water_edge_motion_power_W'):
            self.assertLess(d[k]['p05'],d[k]['median'])
            self.assertLess(d[k]['median'],d[k]['p95'])

if __name__=='__main__':unittest.main()
