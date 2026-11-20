# Reproducibility and numerical integrity notes

**Review performed:** 20 November 2026, against the uploaded v0.2 files.  
**Scope:** reproducibility of computational examples only; no physical ASC validation.

## Mechanical FEM (`engineering_fem/`)

Run:

```bash
cd engineering_fem
python -m pip install -r requirements.txt
python -m unittest discover -s tests -v
python run_fem.py --output rerun_results
```

The five supplied unit tests passed during this review. They check stiffness/mass symmetry and positive definiteness, the bare cantilever's fundamental frequency against an analytical expression, zero-voltage forcing, proportional static displacement scaling with voltage, and the independence of eigenfrequencies from drive amplitude.

The published reference output (`results/summary.json`) includes an illustrative patched-beam first frequency of about **109.763 Hz**, a static displacement of approximately **−37.146 µm** at **20 V peak**, and an assumed-damping four-mode peak of approximately **900.46 µm** at **109.5 Hz**. These are *not measured ASC performance*. Numerical reruns in another allowed linear-algebra environment had differences at approximately 1e−5 Hz (frequencies) and 0.002 µm (peak response), and thus **were not byte-for-byte identical**, but agree at sensible reporting precision. Minor differences are plausible across supported dependency versions; stricter reproducibility would require recording and fixing a complete environment.

Versions used in this audit: Python 3, NumPy 2.3.5, SciPy 1.17.0, Matplotlib 3.10.8; dense eigenvalue calculations were executed with one BLAS thread. The original saved results were preserved rather than overwritten with environment-dependent regenerated files.

**Verification vs validation:** the bare-beam formula and mesh convergence test help assess the *implemented numerical model*. They do not verify actual patch bonding, electrodes, damping, fixture compliance, correct piezoelectric material tensors, or experimental accuracy.

## Synthetic demonstration (`synthetic_demo/`)

Run `python run_simulation.py` from that folder. The program explicitly seeds the random generator with `20261120`; in this audit its regenerated CSVs, figures and README were **byte-identical** to the package originals. The CSV named `synthetic_s1_measurements.csv` contains **simulated trials, not laboratory measurements**; keep this labeling visible wherever the data are reused.

The 24-channel coherence metric is a phasor sum with independent Gaussian phase errors. It is **not** a physical model of coupled surface waves, an ASC controller, or momentum transfer.

## Integrity check

`MANIFEST_SHA256.txt` lists SHA-256 checksums of each distributed file other than the manifest itself. Recalculate hashes after any change; one changed file makes the manifest stale. Checksums indicate accidental modifications, not scientific correctness or ownership.

## Companion publication v0.2.2

The complete corrected 28-page preprint is in `preprint/`, and the three AI-assisted public architectural illustrations are in `drawings/`. The FEM and synthetic numerical source code and stored outputs were not changed from v0.2.1. The corrections are editorial and archival, not new calculations or measurements.
