# Learning-Augmented Page Replacement

**CSE-307 Operating Systems · Term Paper · Track 1: Memory Management**

This project compares FIFO, LRU, Belady's Optimal, and a small decision-tree eviction heuristic under a controlled change in page-reference behavior. The same experimental design is repeated with three independent random seeds, making the reported averages less dependent on one generated trace.

## Research question

How do classical and learned page-replacement policies behave when a locality-heavy reference stream shifts to broad random access, and how does the number of available frames affect that behavior?

## Repository map

| Path | Description |
|---|---|
| `src/experiment.py` | Workload generator, policy implementations, repeated experiment runner |
| `src/build_pdf.py` | Builds the report PDF from the measured results |
| `results/run_metrics.csv` | Per-seed measurements for every policy, frame count, and phase |
| `results/metrics.csv` | Mean and sample standard deviation across the three seeds |
| `results/trace.json` | Exact generated traces keyed by seed |
| `results/run_metadata.json` | Experiment parameters and seeds |
| `results/page_faults.png` | 8-frame phase comparison; error bars show ±1 sample standard deviation |
| `report/term-paper.pdf` | Current two-page report |
| `report/term-paper.tex`, `report/references.bib` | Editable report source and references |
| `demo.md` | Suggested 3–5 minute class walkthrough |

## Reproduce the experiment

Requires Python 3.11 or newer.

```bash
python -m venv .venv
# Windows PowerShell: .venv\Scripts\Activate.ps1
# Linux/macOS: source .venv/bin/activate
python -m pip install -r requirements.txt
python src/experiment.py
python src/build_pdf.py
```

The experiment uses evaluation seeds **307, 308, and 309**. Each produces one 1,000-reference trace, with the distribution shift at reference 500. In the first half, 82% of accesses select from a small hot set and the remainder provide occasional sequential references. In the second half, references are uniformly selected from a larger page set. Each trace is replayed unchanged for all policies at 4, 8, and 12 frames. The learned decision tree is trained once on a separate trace (seed 308) and held fixed across these evaluation runs.

## Policies and measurements

- **FIFO:** evicts the page resident for the longest time.
- **LRU:** evicts the page with the oldest last reference.
- **Optimal:** evicts the page whose next reference is farthest in the future. This offline algorithm is a comparison bound, not a practical online policy.
- **Learned:** a depth-4 decision tree scores resident candidates using age, frequency in the preceding 64 references, and a recent-touch indicator. Its labels are generated from a 96-reference future horizon on the separate training trace.

The CSVs report phase-specific page faults and hit ratios. `metrics.csv` includes arithmetic means and sample standard deviations over the three runs. The learned method is a lightweight supervised heuristic: because training labels use future accesses, it should not be interpreted as a fully online predictor. The results also show that performance is workload- and seed-dependent.

## Report and interpretation

The generated PDF summarizes the implementation, workload, averaged 8-frame results, chart, limitations, and references. Rebuild it after regenerating the experiment data. Before submission, fill in the student name and ID fields, read the report, and confirm that its explanation matches your own understanding and the included measurements.

## AI assistance

An AI coding assistant helped with implementation and documentation. The student should verify the results, understand the code, and be prepared to explain the work, as required by the course brief.

## Submission

Submit the GitHub repository URL and `report/term-paper.pdf` through the course submission channel. Follow the course brief for the printed report and in-class walkthrough requirements.
