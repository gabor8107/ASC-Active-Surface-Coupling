#!/usr/bin/env python3
"""Build the public ASC v0.6 engineering note from checked numerical outputs."""
from __future__ import annotations
import json,csv,math
from pathlib import Path
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_LEFT,TA_CENTER
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, PageBreak, KeepTogether, HRFlowable

ROOT=Path(__file__).resolve().parent
OUT=ROOT/'docs/ASC_Public_Engineering_Research_v0.6_EN.pdf'
S=json.loads((ROOT/'results/summary_v06.json').read_text())
from decimal import Decimal
fontbase='/usr/share/fonts/truetype/lato'
pdfmetrics.registerFont(TTFont('Lato',fontbase+'/Lato-Regular.ttf'))
pdfmetrics.registerFont(TTFont('LatoBold',fontbase+'/Lato-Bold.ttf'))
pdfmetrics.registerFont(TTFont('LatoItalic',fontbase+'/Lato-Italic.ttf'))
pdfmetrics.registerFontFamily('Lato',normal='Lato',bold='LatoBold',italic='LatoItalic',boldItalic='LatoBold')
pdfmetrics.registerFont(TTFont('DejaVu','/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'))
NAVY=colors.HexColor('#13233B'); INK=colors.HexColor('#253041'); MUTED=colors.HexColor('#5E6C7D'); TEAL=colors.HexColor('#196B74'); LIGHT=colors.HexColor('#E9F0F1'); RULE=colors.HexColor('#D1DCE1'); PALE=colors.HexColor('#F5F8F9')
W,H=A4
styles={
 'coverkicker':ParagraphStyle('coverkicker',fontName='LatoBold',fontSize=11,leading=15,textColor=TEAL,spaceAfter=16),
 'cover':ParagraphStyle('cover',fontName='LatoBold',fontSize=29,leading=35,textColor=NAVY,spaceAfter=13),
 'coversub':ParagraphStyle('coversub',fontName='Lato',fontSize=15,leading=22,textColor=MUTED,spaceAfter=28),
 'h1':ParagraphStyle('h1',fontName='LatoBold',fontSize=18,leading=23,textColor=NAVY,spaceAfter=14),
 'h2':ParagraphStyle('h2',fontName='LatoBold',fontSize=11,leading=15,textColor=TEAL,spaceBefore=10,spaceAfter=6),
 'body':ParagraphStyle('body',fontName='Lato',fontSize=9.5,leading=15,textColor=INK,spaceAfter=9),
 'small':ParagraphStyle('small',fontName='Lato',fontSize=8.5,leading=12.5,textColor=MUTED,spaceAfter=7),
 'tiny':ParagraphStyle('tiny',fontName='Lato',fontSize=7.6,leading=11.4,textColor=MUTED,spaceAfter=5),
 'formula':ParagraphStyle('formula',fontName='DejaVu',fontSize=10,leading=18,textColor=NAVY,spaceBefore=8,spaceAfter=12,leftIndent=12),
 'caption':ParagraphStyle('caption',fontName='LatoItalic',fontSize=8,leading=12,textColor=MUTED,spaceAfter=13),
 'table':ParagraphStyle('table',fontName='Lato',fontSize=8.1,leading=11.4,textColor=INK),
 'th':ParagraphStyle('th',fontName='LatoBold',fontSize=8.1,leading=11.4,textColor=colors.white),
 'smallbold':ParagraphStyle('smallbold',fontName='LatoBold',fontSize=8.7,leading=12,textColor=NAVY,spaceAfter=4),
}

def P(txt,style='body'):return Paragraph(txt,styles[style])
def H1(txt):return P(txt,'h1')
def H2(txt):return P(txt,'h2')
def B(txt):return P(txt,'body')
def SM(txt):return P(txt,'small')
def eq(txt):return P(txt,'formula')
def space(n=8):return Spacer(1,n)

def table(headers,rows,widths=None):
    data=[[P(str(h),'th') for h in headers]]+[[P(str(v),'table') for v in r] for r in rows]
    t=Table(data,colWidths=widths,hAlign='LEFT',repeatRows=1)
    t.setStyle(TableStyle([
       ('BACKGROUND',(0,0),(-1,0),NAVY),('ROWBACKGROUNDS',(0,1),(-1,-1),[colors.white,PALE]),
       ('LINEBELOW',(0,-1),(-1,-1),.5,RULE),('BOTTOMPADDING',(0,0),(-1,-1),7),
       ('TOPPADDING',(0,0),(-1,-1),7),('LEFTPADDING',(0,0),(-1,-1),8),
       ('RIGHTPADDING',(0,0),(-1,-1),8),('VALIGN',(0,0),(-1,-1),'TOP')
    ]))
    return t

def figure(file, caption, width=440, maxh=263):
    from PIL import Image as PILImage
    p=ROOT/'figures'/file
    im=PILImage.open(p); w,h=im.size
    scale=min(width/w,maxh/h)
    return [Image(str(p),width=w*scale,height=h*scale,hAlign='CENTER'),P(caption,'caption')]

story=[]
def add(*items):story.extend(items)
def page():story.append(PageBreak())
def section(title):add(H1(title))
def header_footer(c,doc):
    c.saveState()
    if doc.page>1:
        c.setStrokeColor(RULE);c.line(46,H-48,W-46,H-48)
        c.setFont('LatoBold',8);c.setFillColor(TEAL);c.drawString(46,H-38,'ASC / PUBLIC ENGINEERING RESEARCH / v0.6')
        c.setFont('Lato',8);c.setFillColor(MUTED);c.drawRightString(W-46,H-38,'P. GABOR  ·  22 NOV 2026')
    c.setStrokeColor(RULE);c.line(46,43,W-46,43)
    c.setFont('Lato',7.5);c.setFillColor(MUTED)
    c.drawString(46,29,'PUBLIC NUMERICAL BENCHMARK  ·  NO ASC PROPULSION VALIDATION')
    c.drawRightString(W-46,29,str(doc.page).zfill(2))
    c.restoreState()

doc=SimpleDocTemplate(str(OUT),pagesize=A4,leftMargin=46,rightMargin=46,topMargin=64,bottomMargin=58,title='ASC - Public Engineering Research v0.6',author='P. Gabor',subject='First-principles momentum, segmented power, energy recovery and mission constraints')
CW=W-92

# 1 Cover
add(space(65),P('ACTIVE SURFACE COUPLING  /  ENGINEERING NOTE','coverkicker'),
    P('A public numerical assessment of the ASC-V propulsion proposal','cover'),
    P('Momentum, sector control, energy recovery and the practical limits of electric propulsion','coversub'),
    HRFlowable(width='100%',thickness=1,color=TEAL),space(26),
    P('<b>Research concept:</b> P. Gabor  |  Independent researcher, Hungary'),
    P('<b>Edition:</b> v0.6, 22 November 2026  |  Public / unreviewed research supplement'),
    P('<b>Companion works:</b> ASC Preprint 0.2 and public numerical envelope v0.5'),
    space(20),P('<b>Scope.</b> This report tests ordinary physical constraints on a proposed segmented active-surface platform. The calculations use disclosed, deliberately hypothetical inputs. None is a prediction of a built ASC motor, a verified spacecraft design or an observed propulsion effect.'),
    space(20),SM('Source code, test cases, configurations and regenerated figures accompany the report in the public repository. No confidential drawings, controller parameters or unpublished hardware specifications are used.'))
page()

# 2
section('Executive assessment')
add(B('The central question is not whether a complicated surface can store energy or sustain a travelling wave. It is whether the complete platform can transfer momentum to something outside itself, and do so better than a simpler system operating at the same external power and total mass.'),
    B('For a closed vehicle in vacuum, internal RF fields, piezoelectric vibration and circulating mechanical waves cannot deliver sustained net thrust. Directed radiation produces photon recoil; a real electric thruster can produce much more force by accelerating and expelling propellant. The proposed ASC sectorization is assessed here as a possible power-distribution, diagnostic and control architecture around those established momentum channels.'),
    table(['Question','Public calculation','What remains unknown'],[
      ['Can internal waves accelerate the vehicle?', 'No net sustained vacuum impulse in a closed system.', 'Nothing about ASC hardware can change that constraint.'],
      ['What can a 100 kW radiation beam do?', 'At most 0.334 mN axial recoil if all 100 kW escapes directionally.', 'Radiation pattern, losses and source power.'],
      ['What does 100 kW of propellant-jet input imply?', '6.12 N for an ideal 45%-efficient 1500 s Isp case.', 'Any ASC-V jet geometry, propellant source and measured performance.'],
      ['Can 24 sectors improve the result?', 'Only if any improvement outweighs their electric, thermal and mass penalties.', 'Whether sectors physically alter jet efficiency, control or losses.']],[195,165,CW-360]),
    space(10),H2('The result to keep in view'),
    B('In the specific 100 kW comparison, reserving 20 kW for a segmented surface, returning a hypothetical 0.93 kW from that branch and spending 0.35 kW on auxiliary control leaves 80.58 kW for a separate electric jet. To match a 45%-efficient 100 kW reference thruster, that jet would have to reach at least <b>55.85% kinetic efficiency</b> with the same exhaust velocity and axial alignment.'),
    SM('The threshold is calculable; the claimed improvement is not. The v0.6 code allows the assumed efficiencies, power split, cell count and alignments to be changed without altering the equations.'))
page()

# 3
section('1  Physical accounting: what can produce thrust?')
add(B('This work adopts a control volume around the complete vehicle. A lasting change in its momentum requires momentum carried across that boundary. For the cases examined here, the relevant channels are expelled matter and emitted electromagnetic radiation.'),
    H2('Ideal propellant jet'),
    eq('vₑ = Isp · g₀    |    ηP = ½ ṁ vₑ²    |    F = ṁ vₑ = 2ηP / vₑ'),
    B('Here P is electrical power delivered to the thruster branch, η is the fraction converted into directed exhaust kinetic energy, and vₑ is effective exhaust speed. The relation is an idealized kinetic-energy model; real ionization, divergence, plume interaction, neutralization and equipment losses are not simulated.'),
    H2('Radiation recoil'),
    eq('Fγ,axial = ξ Pγ / c,     0 ≤ ξ ≤ 1'),
    B('The directional factor ξ represents the axial projection of the actual escaped photon momentum. Beam steering changes the direction of radiation; it cannot make the net recoil exceed total outward radiated power divided by c.'),
    H2('A distributed hypothetical array'),
    eq('F⃗ = −Σ [ṁᵢ vₑ,ᵢ n̂ᵢ + (Pγ,ᵢ/c) k̂ᵢ]'),
    B('The sum is over independent external emitters, if such emitters exist. It is <b>not</b> a force formula for ordinary passive piezo patches or RF fields confined to a closed shell. The code represents this relationship using classical point-force vectors.'),
    H2('Conservation check'),
    B('No calculation in this package assigns thrust to internal resonant circulation. The recovered electrical power is counted once at its source boundary, and an independent current of momentum must still leave the vehicle for a propulsive result to exist.'))
page()

# 4
section('2  The 24-sector / 288-cell public proxy')
add(B('The earlier ASC preprint proposes 24 supervisory sectors. This supplement subdivides each into 12 identical notional cells, for <b>288 numerical addresses</b>. That is a bookkeeping and fault-analysis choice, not a released ASC transducer count, a verified mechanical layout or evidence that the cells can emit exhaust.'),
    table(['Attribute','Value used here','Interpretation'],[
      ['Supervisory sectors','24','Functional control groups, not established SAW transducer count'],
      ['Addresses per sector','12','Illustrative subdivision selected for the calculation'],
      ['Total addresses','288','Numerical population, not prototype evidence'],
      ['Outer ring radius','0.50 m','Illustrative lever arm for torque sensitivity'],
      ['Exhaust directions','Configurable tilt','Applied only if cells are hypothetical external emitters'],
      ['Cell operation','Independent / equal-power','Failed channels are not automatically reallocated']],[146,96,CW-242]),
    space(11),H2('Why the distinction matters'),
    B('Twelve cells in a drawing do not specify an electrode pitch, acoustic wavelength, feed routing or plasma source. The relevant spatial resolution depends on frequency, materials, boundary conditions and transducer technology. The v0.5 wave-sampling calculations remain a separate heuristic and cannot be combined with the propulsion model as though a multiphysics design had been solved.'),
    H2('A useful model without pretending to have hardware'),
    B('The array model can test power allocation, vector cancellation and fault symmetry under transparent assumptions. It can also expose an unwanted side force or moment when one group stops contributing. What it cannot determine is the actual force density, the achievable thrust, an electromagnetic field configuration or the validity of any ASC coupling mechanism.'))
page()

# 5
section('3  Power distribution and break-even performance')
add(B('A 100 kW power source is divided between a conventional exhaust-producing branch and a hypothetical active-surface branch. For this comparison the gross sector load is 20 kW, recoverable electrical fraction 4.65%, and external auxiliary consumption 0.35 kW. These are thought-experiment inputs, not measured ASC values.'),
    eq('Pjet = Pext − Psector + Precovered − Paux'),
    table(['Bus quantity','Baseline jet','Illustrative ASC-hybrid'],[
      ['External supply','100.00 kW','100.00 kW'],
      ['Segmented-surface gross allocation','0','20.00 kW'],
      ['Captured sector power','0','0.93 kW'],
      ['Auxiliary electrical draw','0','0.35 kW'],
      ['Electric jet branch','100.00 kW','80.58 kW'],
      ['Assumed kinetic jet efficiency','45%','58% (not demonstrated)'],
      ['Calculated aligned thrust, Isp = 1500 s','6.118 N','6.354 N']],[CW*.46,CW*.25,CW*.29]),
    space(9),eq('ηbreak-even = 0.45 × (100 / 80.58) = 0.55845 ≈ 55.85%'),
    B('The hybrid case gives about 3.86% more thrust only because the user-selected jet efficiency has been raised from 45% to 58%. No simulation of the active surface establishes that increase. Keeping the jet efficiency at 45% would instead reduce thrust to about 4.93 N.'),
    B('An optional 8 kg recovery-system mass increases an illustrative dry mass from 300 to 308 kg. The dry-mass-only acceleration ratio for the favorable 58% scenario is 1.0116, a gain of about 1.16%. This ratio excludes propellant and is not a spacecraft acceleration forecast.'))
page()

# 6 figure power
section('Power-split sensitivity')
add(B('The sector load is a debit, not a source of free propulsion. Electrical recovery can partially offset it, but that saving is small unless the technology also produces a genuine, independently measured improvement to the thruster.'),
    *figure('01_power_split_thrust.png','Figure 1. Thrust bounds under different assumed surface allocations. Recovery on the surface branch is 4.65% of that branch alone.',maxh=320),
    SM('A decline in the jet branch at unchanged efficiency is the default outcome. A favorable curve requires additional efficiency assumptions that must be verified in hardware.'))
page()

#7
section('The efficiency threshold')
add(B('An efficiency gain is useful only if the system can maintain the same exhaust speed, operate within its power and thermal constraints, and carry the added mass. The chart below shows the threshold that the assumed segmented surface would have to cross.'),
    *figure('02_efficiency_break_even.png','Figure 2. Jet-efficiency sensitivity for the 80.58 kW branch. The second curve uses a highly simplified dry-mass adjustment, not a complete wet-mass mission model.',maxh=320),
    B('At 58% efficiency, the jet kinetic power is 46.736 kW, compared with 45.000 kW for the conventional 100 kW baseline. The 1.736 kW difference is a conditional useful-energy result; it is neither surplus energy nor a measured ASC benefit.'))
page()

# 8
section('4  Steering, sector failures and structural moments')
add(B('The model distributes the emitted exhaust momentum around 24 equally spaced azimuths. Every address receives the same electrical share, and a common notional exhaust tilt is applied away from the positive thrust axis. For a fully symmetric array, lateral components cancel. Axial impulse falls as the cosine of that tilt.'),
    eq('Fz = Ftotal cos(θ)       (symmetric array, equal power, no failures)'),
    *figure('03_vector_alignment.png','Figure 3. Axial projection of an externally expelled jet, if all 288 hypothetical emitters exist.',maxh=238),
    B('A nonzero phase command does not by itself provide steering force. The model assumes physical exhaust directions; without exhaust, these curves describe no propulsion.'))
page()

# 9
section('Sector fault bookkeeping')
add(B('Fault cases apply a nominal 10° radial tilt with no power rerouting. A missing sector reduces the total emitted impulse and breaks symmetry. The simplified 0.5 m lever arm can then produce a reaction moment, but it does not predict actual hardware loading.'),
    table(['Case','Alive cells','Axial thrust','Lateral reaction','Torque'],[
      ['All sectors operating','288','6.258 N','~0 N','~0 Nm'],
      ['One sector offline','276','5.997 N','0.046 N','0.130 Nm'],
      ['Three adjacent offline','252','5.476 N','0.135 N','0.382 Nm'],
      ['Three equally spaced offline','252','5.476 N','~0 N','~0 Nm']],[CW*.32,CW*.13,CW*.17,CW*.2,CW*.18]),
    space(9),*figure('04_sector_faults.png','Figure 4. Notional control-sector outages. No redistribution or load-dependent response is assumed.',maxh=248),
    SM('This exercise is a control-architecture diagnostic. A real design would require separate estimates of structural inertia, actuator authority, cell force limits and thermal behavior.'))
page()

#10
section('5  Photon recoil versus propellant thrust')
add(B('At 100 kW, the magnitude of directed photon recoil is capped by P/c. That is about 0.000334 N (0.334 mN), even under ideal directionality. By comparison, a conventional propellant jet with 1500 s specific impulse and 45% kinetic efficiency produces an ideal 6.118 N at the same electric input. The difference is explained by momentum carried per unit of energy by slowly moving matter, not by resonant multiplication.'),
    *figure('07_momentum_channel_limits.png','Figure 5. Physical momentum channels on a logarithmic scale. The favorable segmented case assumes an improved electric jet; it does not derive that jet from ASC hardware.',maxh=320),
    B('The numerical force values should not be used to label the ASC shell as an operational engine. The model is a comparison of boundary conditions and energy allocations.'))
page()

# 11
section('6  Recovery and thermal constraints')
add(B('The previous v0.5 public exercise divided a separate 100 kW internal process into 45 kW useful work, 45 kW heat, 7 kW uncaptured RF and 3 kW unwanted vibration. Its 4.65 kW gross electrical recovery is a conditional example at that process boundary, not an additional power source. It must not be added to the new 100 kW thruster ledger.'),
    B('For v0.6, the 4.65% recovery ratio is applied only to the <b>20 kW sector branch</b>, returning 0.93 kW. The two studies use different boundaries and must be kept distinct.'),
    H2('Heat-rejection envelope'),
    B('Suppose, conservatively, that every external watt not converted to departing jet kinetic energy ultimately becomes heat that must be rejected onboard. This is an illustrative upper-allocation, not a measured thermal map. It gives 55.0 kW for the conventional case and 53.264 kW for the favorable hybrid case.'),
    table(['Radiating temperature','Baseline ideal area','Hybrid ideal area'],[
        ['350 K','76.0 m²','73.6 m²'],['400 K','44.6 m²','43.2 m²'],['450 K','27.8 m²','26.9 m²']],[CW*.38,CW*.31,CW*.31]),
    space(7),B('These are effective single-sided emitting areas for emissivity 0.85 against a 3 K background. Radiator supports, piping, working fluid, view factors, thermal interfaces, internal temperature gradients and mass are omitted. Rejecting tens of kilowatts is a system-level challenge, not an incidental detail.'))
page()

#12
section('Thermal design is part of propulsion design')
add(*figure('05_radiator_envelope.png','Figure 6. Stefan-Boltzmann radiating-area envelopes. The temperatures are hypothetical and do not define a physical thermal architecture.',maxh=315),
    H2('A recoverer can worsen the result'),
    B('A piezoelectric scavenger can damp the wave the surface was meant to produce. A thermoelectric stage requires a sustainable hot- and cold-side temperature difference. Recovering reflected RF may compete with source matching or recapture energy that has already been returned. Each addition has a mass, heat-leak and electrical cost. The correct metric is the net change of thrust, external power, mass and lifetime against a matched conventional reference.'),
    B('The public package intentionally includes configurations in which sectorization makes the result worse. Those cases are essential to a useful feasibility analysis.'))
page()

#13
section('7  Mission limits: Δv is not a maximum speed')
add(B('The rocket equation describes an ideal velocity increment in free space. It does not tell us the maximum speed of ASC. A mission also needs a real power source, thermal control, propellant storage, trajectory and a qualified propulsion system.'),
    eq('Δv = vₑ ln(m₀ / mf),     mprop = mf [exp(Δv / vₑ) − 1]'),
    B('With constant electric input, constant exhaust speed and efficiency, mass flow can be estimated from exhaust kinetic power. The required burn time follows by dividing required propellant by the mass flow. The examples below assume <b>300 kg dry mass already includes every piece of non-propellant hardware</b>; this requirement has not been demonstrated.'),
    table(['Ideal target Δv','Isp','Propellant','Burn time','Source energy'],[
       ['100,000 km/h','1500 s','1.683 t','46.8 days','112.4 MWh'],
       ['100,000 km/h','5000 s','0.229 t','70.7 days','169.7 MWh'],
       ['300,000 km/h','1500 s','86.28 t','2401 days','5762 MWh'],
       ['300,000 km/h','5000 s','1.341 t','414.7 days','995.4 MWh'],
    ],[CW*.29,CW*.12,CW*.18,CW*.2,CW*.21]),
    space(9),B('All four scenarios use 100 kW of continuous thruster electricity and 45% kinetic efficiency. Their speed changes follow from selected mass ratios and operating times; none is a validated or upper-limit ASC performance claim.'),
    H2('The often-overlooked power-source mass'),
    B('At a hypothetical battery specific energy of 200 Wh/kg, storing just the 112.4 MWh needed for the first scenario would require roughly <b>562 tonnes of batteries</b>, before conversion, packaging or degradation. That alone is incompatible with the assumed 300 kg dry vehicle. A continuously supplied source, such as solar or a separately qualified reactor, changes the problem but does not remove its mass and thermal requirements.'))
page()

#14
section('Mission mass and energy constraints')
add(*figure('06_propellant_mass_ratio.png','Figure 7. Two standard ideal-rocket cases. High specific impulse reduces propellant demand but increases the time needed to deliver an assumed fixed power.',maxh=310),
    H2('A solar-power aperture is not a spacecraft power system'),
    B('At 1 AU, using 1361 W/m² incident solar flux and a favorable 25% photovoltaic conversion assumption, continuous 100 kW electric output requires about <b>294 m² of fully illuminated collection area</b>, before incidence angle, degradation, eclipse time, conversion losses or structural mass. Solar availability also declines with distance from the Sun.'),
    B('The current public ASC materials contain no integrated power-system mass, no storage sizing and no qualifying radiator design. Until those exist, a dry-mass figure used in a rocket calculation is only a placeholder.'))
page()

#15
section('8  Air, water and vacuum are separate designs')
add(B('The ASC platform was initially drawn as a common geometric concept. That is not a reason to treat the surrounding environments as interchangeable.'),
    H2('In air'),
    B('Any lift or net aerodynamic force requires a real exchange of momentum with surrounding air or another external agency. An actuator-disc comparison in the v0.5 code is only a conventional lower-bound benchmark if an actuator actually produces airflow. The present study does not demonstrate lift from piezoelectric surface waves or a functioning electrohydrodynamic propulsion unit.'),
    H2('In water'),
    B('Hydrostatic loads, buoyancy, added mass, sealing and electrical safety dominate. An illustrative pressure multiplied by a projected area is not a net force on a closed submerged body and cannot establish hull integrity. The v0.5 water calculations remain independent screening exercises.'),
    H2('In vacuum'),
    B('Surface waves can help instrumentation, damping or internal control, but cannot change the momentum of a closed spacecraft. A useful ASC-V case therefore requires an independent external momentum path: expelled propellant or outward radiation. That channel must be characterized before thrust, specific impulse or spacecraft Δv can be attributed to ASC.'),
    H2('Integration remains a hypothesis'),
    B('It is possible that a segmented surface improves diagnostics, thermal management or actuator reliability without improving propulsion. An honest research programme should report those outcomes as well as negative results.'))
page()

#16
section('9  Validation gates and stopping rules')
add(B('This report can be checked with a Python interpreter. A propulsion claim cannot. The minimum next steps are therefore defined as observable tests rather than another unverified full-platform rendering.'),
    table(['Stage','Minimum evidence','What would falsify the proposed advantage'],[
      ['Electrical boundary','Calibrated source input, reflected RF and auxiliary loads at fixed reference planes','Power allocated twice or losses unaccounted'],
      ['Wave control','Independent displacement / phase map with dummy, inactive and direct-drive controls','Pattern disappears after sensor, mounting or cable changes'],
      ['Recovery','Measured delivered electrical recovery, heat flow and parasitic demand','Net output no better than direct reference'],
      ['External thrust','Independent force balance and exhaust mass/velocity or outgoing radiation measurement','Observed signal tracks wiring, thermal drift or fixture force'],
      ['Fair system comparison','Equal input energy, full wet mass, propellant, thermal equipment and run time','Apparent benefit disappears at equal system boundary']],[CW*.19,CW*.39,CW*.42]),
    space(8),B('Any eventual efficiency claim must specify the exact boundaries of η, including whether power is measured before or after power-processing electronics. A test result is only compelling when a simpler reference system is subjected to the same measurement conditions.'),
    H2('No automatic patent or novelty claim'),
    B('The mathematics here is conventional. The drawings are conceptual and are not manufacturing instructions. This document does not claim exclusive rights, a novel force-generating principle, independently measured propulsion or fitness for construction.'))
page()

#17
section('10  Reproducibility and release scope')
add(B('The v0.6 extension contains a single scenario JSON file, Python source for physical limits and sector vectors, a deterministic analysis driver, seven generated CSV tables, a machine-readable summary and seven figures. Unit tests check numerical identities, boundary cases, power conservation, rocket mass accounting and array-symmetry behavior.'),
    H2('A clean reproduction from source'),
    eq('python -m pip install -r numerical_envelope_v0.6/requirements.txt'),
    eq('cd numerical_envelope_v0.6  &&  python run_v06.py'),
    eq('python -m unittest discover -s tests -v'),
    B('From the companion historical folder, run the two original analysis scripts and its separate test suite. The current public package passed 45 v0.6 tests and 57 v0.5 tests in this environment. Passing those tests verifies program behavior and internal accounting, not physical accuracy.'),
    H2('Public / private boundary'),
    B('No confidential ASC v0.3 archive, unpublished internal drawings, proprietary operating parameters or private hardware data are packaged. The numerical 12-cell subdivision is a disclosed test assumption. The broader ASC documentation remains private, and these public examples should not be read as a blueprint or a finished design.'),
    H2('Illustrations and authorship'),
    B('The three ASC architectural illustrations accompanying the earlier 28-page preprint were prepared with generative-AI assistance and remain conceptual. The engineering proposal is presented under the name P. Gabor. Computational and editorial assistance was used in preparing this supplement; none of it substitutes for independent scientific or engineering review.'),
    SM('The public code is available for examination and reproduction. No reuse license is presumed; the repository includes a license-decision notice pending the author’s selection.'))
page()

#18
section('11  Limitations and concluding position')
add(B('The calculations support a firm boundary and a useful practical question. Without matter or radiation leaving the spacecraft, internal waves and RF circulation cannot provide sustained vacuum propulsion. Once a conventional momentum channel is added, thrust and Δv can be estimated from established physics, but only under explicit assumptions about effective exhaust speed, power, efficiency, source mass and operating duration.'),
    B('The 24-sector, 288-address example provides a tractable engineering screening model. It identifies wasted power, directional cancellation and possible reaction moments after faults. It does not prove that the proposed physical ASC surface can improve an electric thruster or even that its cells are suitable exhaust emitters.'),
    B('The most useful numerical result is the <b>55.85% break-even efficiency threshold</b> for one carefully specified 100 kW scenario. If a real ASC-integrated architecture cannot surpass that measured threshold at matched system mass and thermal boundary, the segmented auxiliary branch would not be justified for thrust performance in that scenario. A negative result would still help determine which modules are worth retaining.'),
    H2('Selected references'),
    SM('[1] NASA Glenn Research Center, Ideal Rocket Equation. https://www1.grc.nasa.gov/beginners-guide-to-aeronautics/ideal-rocket-equation/'),
    SM('[2] NASA Glenn Research Center, Specific Impulse. https://www1.grc.nasa.gov/beginners-guide-to-aeronautics/specific-impulse/'),
    SM('[3] NASA Small Spacecraft Technology, In-Space Propulsion (technology trade space, accessed November 2026). https://www.nasa.gov/smallsat-institute/sst-soa/in-space_propulsion/'),
    SM('[4] NIST, The International System of Units; exact speed of light. https://www.nist.gov/pml/special-publication-330/sp-330-section-2'),
    SM('[5] ASC Preprint 0.2, P. Gabor (2026), public architecture and experimental plan. https://doi.org/10.5281/zenodo.24406624'),
    SM('[6] ASC Public Numerical Engineering Envelope v0.5, P. Gabor (2026), public numerical companion files. Repository: https://github.com/gabor8107/ASC-Active-Surface-Coupling'),
    H2('Publication note'),
    B('This is a public numerical research reference, not a completed propulsion design. It is intended to make assumptions testable and to identify the measurements needed before more ambitious claims can be made.'))
page()

# 19+ figures conceptual
for n,(fname,title,caption) in enumerate([
 ('ASC-001_Full_Structure_Section.png','Appendix A  /  ASC-001: Full-structure section','AI-assisted conceptual architectural drawing. Not to scale; no construction authority.'),
 ('ASC-002_General_Arrangement.png','Appendix B  /  ASC-002: General arrangement','AI-assisted conceptual architectural drawing. Dimensions and mechanical details are illustrative.'),
 ('ASC-003_Exploded_Assembly.png','Appendix C  /  ASC-003: Exploded assembly','AI-assisted conceptual exploded view. Not a validated assembly order or manufacturing drawing.')
]):
    section(title)
    from PIL import Image as PImg
    path=ROOT.parent/'drawings'/fname
    im=PImg.open(path)
    iw,ih=im.size
    factor=min(CW/iw,610/ih)
    add(Image(str(path),width=iw*factor,height=ih*factor,hAlign='CENTER'),space(8),P(caption,'caption'),SM('See the ASC Preprint 0.2 for the original architectural context and disclosure limits.'))
    if n<2:page()

doc.build(story,onFirstPage=header_footer,onLaterPages=header_footer)
print(OUT)
