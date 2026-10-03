"""Reproducible page-replacement experiment for CSE-307 Track 1."""
from __future__ import annotations

import csv
import json
import random
from collections import Counter
from pathlib import Path

import matplotlib.pyplot as plt
from sklearn.tree import DecisionTreeClassifier

ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results"
SEED = 307
SHIFT = 500
TRACE_LENGTH = 1000
FRAME_COUNTS = (4, 8, 12)


def make_trace(seed: int, training: bool = False) -> list[int]:
    """Locality-heavy phase then a broad, randomized phase."""
    rng = random.Random(seed)
    trace: list[int] = []
    hot_pages = list(range(8 if not training else 10))
    for i in range(TRACE_LENGTH):
        if i < SHIFT:
            # Mostly access a small working set, with occasional sequential scans.
            if rng.random() < 0.82:
                trace.append(rng.choice(hot_pages))
            else:
                trace.append((i // 5) % 24)
        else:
            # Distribution shift: uniform accesses to a much larger page set.
            trace.append(rng.randrange(32 if not training else 40))
    return trace


def simulate(trace: list[int], frames: int, policy: str) -> tuple[list[bool], int]:
    memory: list[int] = []
    fifo_order: list[int] = []
    last_seen: dict[int, int] = {}
    hits: list[bool] = []
    for i, page in enumerate(trace):
        hit = page in memory
        hits.append(hit)
        if not hit:
            if len(memory) == frames:
                if policy == "FIFO":
                    victim = fifo_order[0]
                elif policy == "LRU":
                    victim = min(memory, key=lambda p: last_seen[p])
                elif policy == "Optimal":
                    future = trace[i + 1:]
                    next_use = {p: (future.index(p) if p in future else len(future) + 1) for p in memory}
                    victim = max(memory, key=lambda p: next_use[p])
                elif policy == "Learned":
                    victim = learned_victim(memory, i, trace, last_seen)
                else:
                    raise ValueError(policy)
                memory.remove(victim)
                fifo_order.remove(victim)
            memory.append(page)
            fifo_order.append(page)
        last_seen[page] = i
    return hits, sum(not h for h in hits)


def learned_victim(memory: list[int], i: int, trace: list[int], last_seen: dict[int, int]) -> int:
    """Fit a small tree offline from an independent seeded labeled trace.

    Features are age, within-window access frequency, and whether the page was
    touched recently. Labels identify the page with the farthest next use.
    This is an oracle-supervised heuristic, not an online learner.
    """
    model = TRAINED_MODEL
    candidates = []
    start = max(0, i - 64)
    recent = trace[start:i]
    counts = Counter(recent)
    for p in memory:
        age = i - last_seen[p]
        candidates.append((p, [age, counts[p], int(age <= 8)]))
    # Select the candidate with the greatest estimated probability of being
    # the farthest-next-use victim. A deterministic age tie-break makes the
    # behavior stable when tree leaves have equal probabilities.
    return max(candidates, key=lambda item: (model.predict_proba([item[1]])[0][1], item[1][0]))[0]


def train_model() -> DecisionTreeClassifier:
    trace = make_trace(SEED + 1, training=True)
    model = DecisionTreeClassifier(max_depth=4, min_samples_leaf=4, random_state=SEED)
    features, labels = [], []
    for i in range(80, len(trace) - 64):
        window = trace[max(0, i - 64):i]
        candidates = list(dict.fromkeys(window[-12:]))
        if len(candidates) < 2:
            continue
        freq = Counter(window)
        horizon = trace[i:min(len(trace), i + 96)]
        future_positions = {p: (horizon.index(p) if p in horizon else len(horizon) + 1) for p in candidates}
        victim = max(candidates, key=lambda p: future_positions[p])
        for p in candidates:
            age = next((k for k, x in enumerate(reversed(window)) if x == p), len(window))
            features.append([age, freq[p], int(age <= 8)])
            labels.append(int(p == victim))
    model.fit(features, labels)
    return model


TRAINED_MODEL = train_model()


def main() -> None:
    RESULTS.mkdir(exist_ok=True)
    trace = make_trace(SEED)
    rows = []
    for frames in FRAME_COUNTS:
        for policy in ("FIFO", "LRU", "Optimal", "Learned"):
            hit_vector, faults = simulate(trace, frames, policy)
            for phase, lo, hi in (("locality", 0, SHIFT), ("shifted_random", SHIFT, len(trace))):
                segment = hit_vector[lo:hi]
                phase_faults = sum(not h for h in segment)
                rows.append({"policy": policy, "frames": frames, "phase": phase,
                             "accesses": len(segment), "hits": len(segment) - phase_faults,
                             "faults": phase_faults, "hit_ratio": (len(segment) - phase_faults) / len(segment)})
    with (RESULTS / "metrics.csv").open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=rows[0].keys())
        writer.writeheader(); writer.writerows(rows)
    with (RESULTS / "trace.json").open("w", encoding="utf-8") as f:
        json.dump({"seed": SEED, "shift_index": SHIFT, "pages": trace}, f)
    make_figure(rows)
    summary = {"seed": SEED, "trace_length": len(trace), "shift_index": SHIFT,
               "frame_counts": FRAME_COUNTS, "model": "DecisionTreeClassifier(max_depth=4)",
               "training_trace_seed": SEED + 1}
    (RESULTS / "run_metadata.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print("Generated results/metrics.csv, results/trace.json, results/run_metadata.json, results/page_faults.png")


def make_figure(rows: list[dict]) -> None:
    policies = ("FIFO", "LRU", "Optimal", "Learned")
    fig, axes = plt.subplots(1, 2, figsize=(10, 4.2), sharey=True)
    for ax, phase in zip(axes, ("locality", "shifted_random")):
        selected = [r for r in rows if r["phase"] == phase and r["frames"] == 8]
        ax.bar(policies, [r["faults"] for p in policies for r in selected if r["policy"] == p], color=["#5577aa", "#3a9d83", "#d28b36", "#9b6baa"])
        ax.set_title(f"{phase.replace('_', ' ').title()} (8 frames)")
        ax.set_ylabel("Page faults / 500 references")
        ax.tick_params(axis="x", rotation=20)
        ax.grid(axis="y", alpha=.25)
    fig.suptitle("Page replacement before and after the workload shift")
    fig.tight_layout()
    fig.savefig(RESULTS / "page_faults.png", dpi=180)


if __name__ == "__main__":
    main()
