# GitHub feltöltés - ASC numerikus v0.5

1. A meglévő `preprint/`, `drawings/`, `engineering_fem/`, `synthetic_demo/` és a korábbi `numerical_envelope_v0.4/` maradjon meg.
2. Töltsd fel ezt a teljes `numerical_envelope_v0.5/` mappát (ne csak a ZIP-et), benne a Python-kóddal, `results/`, `figures/` és `docs/` almappákkal.
3. Futtatás: `python -m pip install -r requirements.txt`, majd `python run_analysis.py`, `python run_hybrid_analysis.py`, végül `python -m unittest discover -s tests -v`.
4. Az új PDF: `docs/ASC_Public_Numerical_Engineering_Envelope_v0.5_EN.pdf`. A 28 oldalas eredeti ASC Preprintet **nem** kell lecserélni.
5. Ha szeretnéd, a gyökér README-be egy új sort: "Added v0.5 public hybrid energy-recovery numerical extension; illustrative inputs, no measured ASC performance."
6. Minden bemenő szám feltételezés. A 4,65 kW nem nettó nyereség, az 100 kW nem bizonyított hajtóműteljesítmény.
7. A licencelési és szabadalmi kérdéseket tisztázd; bizalmas anyagokat továbbra se tölts fel.
