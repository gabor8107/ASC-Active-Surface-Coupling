# Integration into existing public GitHub repository

This ZIP is intended as **one new subdirectory**, not as a replacement for the existing repository.

Suggested destination:

```text
ASC-Active-Surface-Coupling/
├── README.md                       # existing: keep original
├── preprint/                        # existing: keep 28-page PDF
├── drawings/                        # existing: keep ASC-001, 002, 003
├── engineering_fem/                 # existing: keep public v0.2.2
├── synthetic_demo/                  # existing: keep public v0.2.2
├── numerical_verification_v0.3/     # if already present, leave untouched
└── numerical_envelope_v0.5/         # copy this folder here
```

Copy **the contents of this package** into `numerical_envelope_v0.5/` (not as one ZIP file in source view). Do not copy the separate v0.3 confidential ZIP.

Add this short paragraph to the top-level README (manually; not applied to remote):

> **New: Public Numerical Engineering Envelope v0.5** — A separately reproducible, assumption-driven comparison of construction proxies, air/water drag and buoyancy, ideal propulsion energy/momentum limits, RF/thermal bookkeeping, bare-beam and command-phase checks. These are illustrative calculations, **not** ASC system simulation, hardware verification, or proof of thrust. See [`numerical_envelope_v0.5/`](numerical_envelope_v0.5/).

For reproducibility:

```bash
cd numerical_envelope_v0.4
python -m pip install -r requirements.txt
python run_analysis.py
python run_hybrid_analysis.py
python -m unittest discover -s tests -v
```

If GitHub Actions is desired, copy `docs/github_actions_example.yml` **to** `.github/workflows/asc-numerical-envelope.yml` at repository root. A file under `docs/` alone does not activate CI.

Do not change the 28-page preprint DOI. The v0.5 extension does **not** supersede it. Prefer a new GitHub tag only after license, IP and source-integrity checks and external review.


The new v0.5 folder is a complete successor to the public v0.4 folder; copy it as a **separate new directory** if you want to preserve the old public release in Git history. It contains the seven old plots and the five new `hybrid_` plots. The 28-page ASC Preprint remains separate.

For the combined PDF, optionally install `requirements-pdf.txt`, then run `python make_pdf.py`.
