# Public release audit - ASC v0.6

**Scope:** public data and code. No confidential v0.3 package was copied into this release.

## Reproducibility checks

- v0.6 Python tests: **45 passed**.
- Preserved v0.5 Python tests: **57 passed**.
- The v0.6 analysis generated seven CSV datasets, one JSON summary and seven PNG graphs from `config/scenarios.json`.
- `make_report.py` regenerated a **21-page** public English PDF including ASC-001, ASC-002 and corrected ASC-003.
- The 28-page architectural Preprint 0.2 is preserved independently.
- All three public concept drawings are encoded as actual PNG files (not JPEG data with a PNG extension).

## Explicit assumption checks

- The numerical 288 addresses are **an illustrative 24 x 12 subdivision**, not a documented actual transducer count.
- The two 100-kW budgets in historical v0.5 and current v0.6 are **not one common power ledger**. The v0.5 gross 4.65 kW recovery must not be added to the v0.6 0.93 kW sector-only return.
- The v0.6 58% jet efficiency is **assumed, not predicted or demonstrated**. The computational break-even value is approximately 55.85%.
- All propulsion calculations assume expelled external momentum. Internal wave control is assigned zero closed-system vacuum thrust.
- Rocket equation examples are **ideal delta-v illustrations, not ASC speeds or verified maxima**. Power source, radiator, storage and structural masses remain unknown.

## Publication and privacy

- No v0.3 CONFIDENTIAL archive, private 1000+ page dossier, unpublished CAD files, credentials or physical ASC control settings were deliberately included.
- This check does not certify that the disclosed high-level architecture is legally safe to publish or that it cannot affect patent novelty. The author must review the public disclosure and set licensing terms.
- The release is public and numerically inspectable but has no automatic open-source license.
