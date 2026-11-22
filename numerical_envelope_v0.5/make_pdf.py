#!/usr/bin/env python3
"""Optional public report PDF from reproducible technical Markdown and figures."""
from pathlib import Path
import mistune
from weasyprint import HTML
from weasyprint.text.fonts import FontConfiguration
ROOT=Path(__file__).parent
core=(ROOT/'docs'/'TECHNICAL_REPORT_EN.md').read_text(encoding='utf-8')
core=core.replace('# ASC — Public Numerical Engineering Envelope, v0.4',
 '# ASC — Public Numerical Engineering Envelope, v0.5\n\n*Part I: v0.4 public numerical constraint models retained; Part II: v0.5 hybrid recovery extension.*',1)
report=core + '\n\n---\n\n' + (ROOT/'docs'/'HYBRID_RECOVERY_TECHNICAL_NOTE_EN.md').read_text(encoding='utf-8')
markdown=mistune.create_markdown(plugins=['table'])
body=markdown(report)
imgs=[
 ('air_edge_drag.png','Air drag — edge-facing orientation'),
 ('water_edge_drag.png','Water drag — edge-facing orientation'),
 ('water_buoyancy.png','Seawater buoyancy — displaced-volume assumption'),
 ('vacuum_thrust_vs_power.png','Generic electric jet — power/momentum envelope'),
 ('phase_mode_controls.png','24-channel command-phase experiment and controls'),
 ('wave_sampling_scale.png','Perimeter sampling heuristic'),
 ('energy_partition.png','Electrical power accounting exercise'),
 ('hybrid_100kW_power_ledger.png','Hybrid: mutually exclusive 100 kW process flow'),
 ('hybrid_penalty_break_even.png','Hybrid: coupling degradation and break-even'),
 ('hybrid_thermal_radiator.png','Hybrid: isolated radiation-area screening'),
 ('hybrid_assumption_sensitivity.png','Hybrid: synthetic scenario range'),
 ('hybrid_mass_tradeoff.png','Hybrid: hypothetical mass penalty screen')]
figures='\n'.join(f'<div class="figure"><img src="figures/{f}"/><p><b>Figure {i}.</b> {caption}. All inputs are hypothetical; none show measured ASC data.</p></div>' for i,(f,caption) in enumerate(imgs,1))
body+='\n<h2 class="figtitle">Appendix — reproducible computational figures</h2>'+figures
css='''
@page {size: A4; margin: 17mm 17mm 17mm 17mm; @bottom-left { content: "ASC Numerical Envelope v0.5 | 22 Nov 2026"; font: 8pt sans-serif; color: #63758c; } @bottom-right { content: "Page " counter(page) ; font: 8pt sans-serif; color: #63758c;} }
@page:first {margin-top:20mm}
body {font-family: "DejaVu Sans", sans-serif; color:#152739; font-size:9.3pt; line-height:1.5; }
h1:not(:first-child) {break-before:page;}
h1 {font-size:20pt; line-height:1.1; color:#142f48; margin:0 0 12pt; border-bottom:3px solid #197c8b; padding-bottom:11pt;}
h2 {font-size:13pt; color:#176c7b; margin:18pt 0 7pt; break-after:avoid; border-bottom:1px solid #d4e3e8; padding-bottom:3pt;}
h3 {font-size:11pt;color:#234c69}
p {margin:0 0 9pt;} strong {color:#152739;} em {color:#42526a;} code {font-family: "DejaVu Sans Mono",monospace; font-size:8pt; background: #f3f6f8; padding:1pt 2pt; overflow-wrap:anywhere}
table {border-collapse:collapse; width:100%; font-size:7.65pt; margin:10pt 0; break-inside:auto;}
th {background:#dbeef1; border:0.5pt solid #bfcfd6; padding:5pt; text-align:left;}
td {border:0.5pt solid #d7e0e5; padding:4.5pt; vertical-align:top;}
tr:nth-child(even) {background:#f7fafb;}
tr {break-inside:avoid;}
a {color:#086b88; text-decoration:none; overflow-wrap:anywhere}
.figure {margin:12pt 0 20pt; break-inside:avoid; text-align:center;}
.figure img {max-width: 100%; max-height: 117mm; object-fit:contain;}
.figure p {font-size:8pt; color:#51677a; font-style:italic;}
.figtitle {break-before:page;}
'''
html=f'<!DOCTYPE html><html lang="en"><head><meta charset="utf-8"/><style>{css}</style></head><body>{body}</body></html>'
out=ROOT/'docs'/'ASC_Public_Numerical_Engineering_Envelope_v0.5_EN.pdf'
HTML(string=html,base_url=str(ROOT)+'/').write_pdf(str(out),font_config=FontConfiguration())
print(str(out),out.stat().st_size)
