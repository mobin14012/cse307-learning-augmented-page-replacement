# CSE-307 Term Paper: Learning-Augmented Page Replacement

This repository implements **Track 1 — Learned Page Replacement** from the CSE-307 Section B brief. It compares FIFO, LRU, Belady's optimal replacement, and a small decision-tree heuristic on one reproducible trace containing a deliberate workload shift.

## Research question

How does a learned eviction heuristic compare with classical page-replacement policies when a locality-heavy workload changes to a broad random workload?

## Repository contents

```text
src/experiment.py          implementation, workload, experiment runner
results/metrics.csv        raw per-policy measurements
results/trace.json         exact seeded access trace
results/run_metadata.json  seed and experiment configuration
results/page_faults.png    generated comparison figure
report/term-paper.tex      report source
report/references.bib      references used in the report
demo.md                    3–5 minute walkthrough script
requirements.txt           pinned Python dependencies
```

## Reproduce the results

Python 3.11+ is recommended.

```bash
python -m venv .venv
# Windows: .venv\Scripts\activate
# Linux/macOS: source .venv/bin/activate
python -m pip install -r requirements.txt
python src/experiment.py
```

The script uses seed `307`, creates 1,000 references, and shifts at reference 500. The first phase is locality-heavy over a small hot set; the second phase is uniform random access over a larger page set. Results are split into 4, 8, and 12 frame configurations. The report focuses on the 8-frame case.

## Methods

- **FIFO:** evicts the page that has been resident longest.
- **LRU:** evicts the page with the oldest last-reference time.
- **Optimal:** evicts the page whose next reference is farthest in the future; this is an offline lower-bound baseline.
- **Learned:** trains a depth-4 decision tree on an independent seeded trace. Candidate features are recency age, recent-window frequency, and a recent-touch indicator. The training label is the candidate with the farthest next use in the training trace.

The learned policy is intentionally presented as an experimental heuristic, not as a deployable online predictor: its labels use a future horizon during training, while evaluation uses only current/history features. This limitation is discussed in the paper.

## AI assistance disclosure

An AI coding assistant was used to help structure the Python implementation, documentation, and report template. The student must inspect the code, rerun the experiment, verify the numbers, and rewrite or personalize the analysis before submission. The workload seed, measurements, interpretation, and final claims should be understood by the student and presented honestly.

## Submission checklist

1. Run `python src/experiment.py` and confirm the files in `results/` are current.
2. Read `report/term-paper.tex`, fill in your name, student ID, and institution, then compile it with a LaTeX installation or an online LaTeX editor.
3. Review the generated CSV and figure against the report tables.
4. Create your own GitHub repository, commit this project, and submit its URL plus the compiled PDF.

## References

The report cites Belady's optimal replacement work, the LRU paper, the scikit-learn decision-tree documentation, and the course brief. Full entries are in `report/references.bib`.
