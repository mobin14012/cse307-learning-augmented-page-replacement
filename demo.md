# 3–5 minute walkthrough

1. **Problem (30 seconds):** Explain that FIFO/LRU rely on assumptions about access behavior, while deployed workloads can shift.
2. **Workload (45 seconds):** Open `src/experiment.py` and show `make_trace`: references 0–499 are locality-heavy; references 500–999 are broad random accesses. Mention seed 307.
3. **Algorithms (60 seconds):** Point out `simulate` and briefly explain FIFO, LRU, Optimal, and the learned policy.
4. **Learned component (45 seconds):** Show the three features and independent training trace. Explain that the tree predicts whether a candidate is a good eviction victim.
5. **Results (60 seconds):** Open `results/page_faults.png`, then `results/metrics.csv`. Compare the 8-frame locality and shifted phases, emphasizing how the larger working set creates more misses after the shift.
6. **Limitation (30 seconds):** State that Optimal is an offline oracle and the learned labels use a future horizon during training; future work would use online labels and multiple workload seeds.
