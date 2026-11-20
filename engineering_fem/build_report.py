"""Create an English engineering note from executed simulation output."""
from pathlib import Path
import json
from reportlab.platypus import SimpleDocTemplate,Paragraph,Spacer,Image,Table,TableStyle,PageBreak,KeepTogether
from reportlab.lib.styles import getSampleStyleSheet,ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.units import mm

ROOT=Path(__file__).resolve().parent
r=json.loads((ROOT/'results/summary.json').read_text())
cfg=json.loads((ROOT/'public_config.json').read_text())
fn=ROOT/'ASC_S1_Engineering_FEM_Technical_Note_EN.pdf'
doc=SimpleDocTemplate(str(fn),pagesize=(210*mm,297*mm),rightMargin=20*mm,leftMargin=20*mm,topMargin=20*mm,bottomMargin=19*mm,
                      title='ASC S1 - Engineering finite-element benchmark',author='P. Gabor (ASC concept) | computational drafting AI-assisted')
ss=getSampleStyleSheet();ss.add(ParagraphStyle(name='H1x',parent=ss['Heading1'],fontSize=17,leading=22,textColor=colors.HexColor('#17334e'),spaceBefore=5,spaceAfter=10))
ss.add(ParagraphStyle(name='H2x',parent=ss['Heading2'],fontSize=12.5,leading=17,textColor=colors.HexColor('#17334e'),spaceBefore=12,spaceAfter=5))
ss.add(ParagraphStyle(name='Bodyx',parent=ss['BodyText'],fontSize=9.3,leading=14,spaceAfter=7))
ss.add(ParagraphStyle(name='Captionx',parent=ss['BodyText'],fontSize=8.2,leading=11,textColor=colors.HexColor('#4b5d6b'),spaceBefore=3,spaceAfter=8))
ss.add(ParagraphStyle(name='Alertx',parent=ss['BodyText'],fontSize=10,leading=15,textColor=colors.HexColor('#983b25'),spaceBefore=6,spaceAfter=9))
story=[]
def p(s,style='Bodyx'):story.append(Paragraph(s,ss[style]))
def h(s):p(s,'H1x')
def h2(s):p(s,'H2x')
def img(file,width=165*mm):
    from PIL import Image as PILImage
    im=PILImage.open(ROOT/'results'/file); w,h=im.size
    story.append(Image(str(ROOT/'results'/file),width=width,height=width*h/w))
def tab(rows,widths=None):
    t=Table([[Paragraph(str(c),ss['Bodyx']) for c in row] for row in rows],colWidths=widths,hAlign='LEFT',repeatRows=1)
    t.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),colors.HexColor('#e7edf2')),
          ('GRID',(0,0),(-1,-1),.4,colors.HexColor('#ced5da')),
          ('VALIGN',(0,0),(-1,-1),'TOP'),('LEFTPADDING',(0,0),(-1,-1),7),('RIGHTPADDING',(0,0),(-1,-1),7),
          ('TOPPADDING',(0,0),(-1,-1),6),('BOTTOMPADDING',(0,0),(-1,-1),4)]))
    story.append(t)

def page(canvas,doc):
    canvas.setStrokeColor(colors.HexColor('#b9cbd8'));canvas.line(20*mm,15*mm,190*mm,15*mm)
    canvas.setFont('Helvetica',8);canvas.setFillColor(colors.HexColor('#4b6172'))
    canvas.drawString(20*mm,10.8*mm,'ASC S1 · PUBLIC ENGINEERING BENCHMARK · 20 NOV 2026')
    canvas.drawRightString(190*mm,10.8*mm,f'{doc.page}')

h('ASC S1 — Engineering finite-element benchmark')
p('Low-frequency bending response of an illustrative bonded aluminum–piezoelectric coupon')
p('<b>Independent concept:</b> P. Gabor  |  <b>Release:</b> public numerical demonstration 0.1  |  <b>Date:</b> 20 November 2026')
p('<b>SIMULATION ONLY. NO MEASURED ASC RESPONSE, NO PHYSICAL VALIDATION.</b>','Alertx')
h2('Abstract')
p('This note documents an independently executable mechanical finite-element model prepared as a first engineering exercise alongside the ASC Preprint 0.2 measurement plan. A hypothetical aluminum cantilever carrying a partially bonded piezoceramic patch is represented by one-dimensional Euler–Bernoulli beam elements. The calculated outputs are low-frequency bending eigenmodes, static deflection from a simplified piezoelectric free-strain model, a damped harmonic tip response and sensitivity to a selected elastic modulus. These calculations do not reproduce an ASC control device, its surface-acoustic-wave field, its 24-sector network or propulsion.')
h2('Selected numerical outputs')
tab([['Computed item','Illustrative result'],
     ['Bare aluminum first bending frequency: analytical / FEM',f"{r['bare_analytical_f1_hz']:.3f} / {r['bare_FE_f1_hz']:.3f} Hz"],
     ['Bonded-patch first 2 bending frequencies',f"{r['composite_FE_frequencies_hz'][0]:.2f} / {r['composite_FE_frequencies_hz'][1]:.2f} Hz"],
     ['Static free-tip deflection at illustrative 20 V peak',f"{r['composite_static_tip_deflection_um_at_peak_voltage']:.2f} micrometres (signed)"],
     ['Four-mode predicted response peak in 10–800 Hz sweep',f"{r['composite_peak_FRF_amplitude_um']:.1f} micrometres at {r['composite_peak_FRF_frequency_hz']:.1f} Hz"],
     ['First mode convergence change: 80 vs 160 elements',f"{100*r['convergence_80_to_160_relative_f1']:.5f}%"]], [88*mm,82*mm])
p('The dynamic peak depends strongly on the chosen 2% damping ratio, perfect adhesion, electrical free-strain assumption and ideal clamp. It must not be interpreted as a prediction for a manufactured ASC device.')
h2('Connection to the public ASC research plan')
p('ASC Preprint 0.2 distinguishes a preliminary S1 flat-specimen experiment from subsequent curved-panel and system-scale hypotheses. This report supplies a reproducible low-frequency mechanical benchmark only. A real S1 trial would need sensor-calibrated displacement, temperature, boundary-condition and electrical-power data. No such data are included.')
story.append(PageBreak())
h('1. Public example, materials and boundary conditions')
img('fig_01_public_coupon_schematic.png',165*mm)
p('Figure 1. A generic, illustrative coupon. Schematic proportions are visualized for clarity; these are not withheld ASC dimensions or released manufacturing specifications.','Captionx')
tab([['Property','Public illustrative value'],['Beam length × width','100 mm × 20 mm'],['Substrate','1.0 mm aluminum; E = 69 GPa; density = 2700 kg/m³'],['Bonded patch','0.3 mm piezoceramic, first 60 mm of span'],['PZT-like properties','E = 56 GPa; density = 7600 kg/m³; d31 = −175 pm/V'],['Boundary condition','Left end ideal clamp; other end free'],['Drive model','Uniform free strain under 20 V peak sinusoid; zero feedback'],['Damping assumption','2% modal damping (not measured)']], [63*mm,107*mm])
h2('Finite-element formulation')
p('For each uniform beam segment, a transformed neutral axis is calculated by weighting each material layer by elastic modulus. The effective bending rigidity EI is the sum of E times the second moment of each layer about that neutral axis; the distributed mass is the sum of density times area. Each cubic-Hermite beam element contributes standard 4-by-4 bending-stiffness and consistent-mass matrices.')
p('The equations are <b>K u = f</b> for static response and <b>K φ = ω² M φ</b> for free vibration. An illustrative inverse-piezo free strain ε<sub>p</sub> = d<sub>31</sub>V/t<sub>p</sub> is converted to a section bending moment and equivalent nodal forces. A four-mode superposition with an assumed damping ratio gives the harmonic response. The full piezoelectric constitutive tensors and electrical circuit equations are deliberately not modeled.')
story.append(PageBreak())
h('2. Mode shapes and vibration response')
img('fig_02_fem_mode_shapes.png',160*mm)
p('Figure 2. Computed normalized transverse bending-mode shapes for the hypothetical composite beam; modal amplitudes are normalized, not measured.','Captionx')
p('Modes 1–4 occur at approximately '+', '.join(f'{x:.1f}' for x in r['composite_FE_frequencies_hz'])+' Hz. The first two are within or near the 10–800 Hz sweep. The plotted shapes describe bending of a slender beam rather than high-frequency wave propagation along a surface. Internal ASC resonator modes or shell modes cannot be inferred.')
story.append(PageBreak())
h('3. Forced response and the resonance caveat')
img('fig_03_fem_frequency_response.png',162*mm)
p('Figure 3. Idealized, four-mode tip displacement amplitude and phase produced by the equivalent piezoceramic strain; 2% modal damping, 20 V peak amplitude assumed.','Captionx')
p(f"The largest modeled tip response within the sweep is {r['composite_peak_FRF_amplitude_um']:.1f} µm around {r['composite_peak_FRF_frequency_hz']:.1f} Hz. This is a model-dependent, resonance-amplified displacement. It is not a measured value, proof of a coupling gain, an efficiency claim, or a safe drive recommendation. The high response illustrates the importance of independently identifying fixture compliance, hysteresis and damping before interpreting peaks.")
p('This simplified drive representation imposes a prescribed free strain. It does not compute capacitor charging, real and reactive electrical power, impedance matching, dielectric losses, electromechanical feedback, or temperature rise. A comparison against direct drive would require equal-power experimental conditions and measurements not supplied here.')
story.append(PageBreak())
h('4. Verification and sensitivity')
img('fig_04_mesh_convergence.png',157*mm)
p('Figure 4. Fundamental-mode mesh refinement for the piezoelectric-patch model: 20, 40, 80 and 160 one-dimensional elements.','Captionx')
p(f"A uniform, unpatched aluminum cantilever was first checked against the Euler–Bernoulli analytic first frequency: {r['bare_analytical_f1_hz']:.5f} Hz analytically versus {r['bare_FE_f1_hz']:.5f} Hz by FEM (80 elements). The patched beam changes by {100*r['convergence_80_to_160_relative_f1']:.5f}% in its first mode between the 80- and 160-element meshes. This verifies numerical consistency within the chosen *beam model*, not experimental accuracy.")
img('fig_05_modulus_sensitivity.png',157*mm)
p('Figure 5. Effect of changing the illustrative piezoceramic elastic modulus by −20% to +20%; other inputs are fixed. This is one sensitivity dimension, not a complete tolerance or uncertainty budget.','Captionx')
story.append(PageBreak())
h('5. Limitations, next tests and reproducibility')
h2('What this engineering simulation does not demonstrate')
p('The model contains no two-dimensional plate or three-dimensional shell, no anisotropic guided-wave dispersion, no layered phononic band structure, no LiNbO3 material tensor, no RF phase-distribution analysis, no measured power or heat balance, no 24-sector controller, no water or vacuum environment and no external momentum exchange. Therefore it makes no prediction of ASC propulsion, thrust, system-level efficiency, or technical novelty.')
h2('What a genuine S1 validation would require')
p('Before describing the model as validated, an actual coupon should be manufactured and characterized. Document the as-built geometry, electrode/patch placement, elastic and piezoelectric material characterization, fixture compliance, drive circuitry, environmental conditions and calibrated displacement instrumentation. Compare measured bending resonances and deflection against independent predictions, including a bare-substrate reference. Publish null results, model discrepancies and raw data as well as successful comparisons.')
h2('Reproducibility package')
p('Required files: run_fem.py, public_config.json, requirements.txt, tests/, results/, README.md. Execute with Python 3 and NumPy/SciPy/Matplotlib: <b>python run_fem.py</b>. Then run <b>python -m unittest discover -s tests -v</b>. Five checks cover matrix symmetry/positivity, analytic bare-beam frequency, zero-voltage force, linear voltage scaling and excitation-independent frequencies. The package does not contain the non-public ASC development dossier.')
h2('Provenance and responsible disclosure')
p('ASC is an independently developed research concept attributed to P. Gabor. Generative AI assisted with coding, figure layout and editorial preparation of this reproducible benchmark. The actual computations were executed using the included Python source. The model is an illustrative public testbed, not an independent scientific review, and its values are not measured or drawn from confidential ASC implementation data.')
h2('Selected public references')
for s in ['ASM MatWeb: aluminum 6061-T6, https://asm.matweb.com/search/SpecificMaterial.asp?bassnum=MA6061T6',
          'APC International: piezoelectric material property tables, https://www.americanpiezo.com/apc-materials/physical-piezoelectric-properties/',
          'Piezoelectric acoustic impedance review, https://doi.org/10.3390/s20144051',
          'Cantilever analytical eigenvalues and formula, https://lampz.tugraz.at/~hadley/memm/mechanics/cbeam.php']:
    p('• '+s,'Captionx')
doc.build(story,onFirstPage=page,onLaterPages=page)
print(fn)
