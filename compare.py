"""Compare four strategies on synthetic graphs, not official Codabench data."""

import argparse
import csv
import json
import sys
from pathlib import Path
from time import perf_counter

import networkx as nx

sys.path.insert(0, str(Path(__file__).resolve().parent / "solution"))
from algorithm import all_strategies, score


CASES = [
    (50, 50), (50, 250), (50, 500), (50, 1000),
    (100, 100), (100, 250), (100, 500), (100, 1000),
    (250, 250), (250, 500), (250, 1000),
    (500, 500), (500, 1000),
]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--seeds", type=int, default=3)
    parser.add_argument("--output-dir", type=Path,
                        default=Path(__file__).resolve().parent / "results")
    args = parser.parse_args()
    if args.seeds < 1:
        parser.error("--seeds must be positive")

    rows = []
    totals = {}
    runtimes = []
    for seed in range(args.seeds):
        totals[seed] = {}
        for n, m in CASES:
            graph = nx.gnm_random_graph(n, m, seed=seed)
            start = perf_counter()
            results = all_strategies(graph)
            elapsed = perf_counter() - start
            runtimes.append(elapsed)
            for name, pair in results.items():
                first, second = map(set, pair)
                assert all(
                    v in chosen or any(w in chosen for w in graph[v])
                    for chosen in (first, second) for v in graph
                ), (seed, n, m, name)
                value = score(graph, pair)
                totals[seed][name] = totals[seed].get(name, 0.0) + value
                rows.append({
                    "vertices": n, "edges": m, "seed": seed,
                    "strategy": name, "size_1": len(first), "size_2": len(second),
                    "intersection": len(first & second), "score": value,
                    "all_strategies_seconds": elapsed,
                })
            assert score(graph, results["local_search"]) <= min(
                score(graph, pair) for pair in results.values()
            )
            print("seed={} n={} m={} bfs={:.4f} final={:.4f} time={:.3f}s".format(
                seed, n, m, score(graph, results["bfs"]),
                score(graph, results["local_search"]), elapsed,
            ), flush=True)

    names = list(totals[0])
    summary = {
        "dataset": "synthetic NetworkX gnm_random_graph; not official Codabench instances",
        "networkx_version": nx.__version__,
        "seeds": args.seeds,
        "graphs": len(runtimes),
        "max_seconds_per_graph": max(runtimes),
        "totals_by_seed": totals,
        "mean_total_score": {
            name: sum(total[name] for total in totals.values()) / args.seeds
            for name in names
        },
    }
    args.output_dir.mkdir(parents=True, exist_ok=True)
    with (args.output_dir / "comparison.csv").open("w", newline="") as out:
        writer = csv.DictWriter(out, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    (args.output_dir / "summary.json").write_text(
        json.dumps(summary, indent=2) + "\n", encoding="utf-8",
    )
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
