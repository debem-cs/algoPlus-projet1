"""Compare V1 and V2 on held-out synthetic graph families."""

import argparse
import csv
import json
import random
import sys
from pathlib import Path
from time import perf_counter

import networkx as nx

sys.path.insert(0, str(Path(__file__).resolve().parent / "solution"))
from algorithm import _Graph, _quality, _strategies, score
from improved_search import _improve
from compare import CASES


def make_graph(n, m, seed, family):
    if family == "gnm":
        return nx.gnm_random_graph(n, m, seed=seed)
    if family == "tree_plus_edges":
        graph = nx.random_tree(n, seed=seed)
    elif family == "cycle_plus_edges":
        graph = nx.cycle_graph(n)
    else:
        raise ValueError(family)
    rng = random.Random(seed + 10000)
    while graph.number_of_edges() < m:
        u, v = rng.sample(range(n), 2)
        graph.add_edge(u, v)
    return graph


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--seeds", type=int, nargs="+", default=[11, 23, 47])
    parser.add_argument("--families", nargs="+", default=["gnm", "tree_plus_edges", "cycle_plus_edges"])
    parser.add_argument("--output-dir", type=Path, default=Path(__file__).resolve().parent / "results/improved")
    args = parser.parse_args()
    rows = []
    for family in args.families:
        for seed in args.seeds:
            for n, m in CASES:
                graph = make_graph(n, m, seed, family)
                data = _Graph(graph)
                start = perf_counter()
                baseline = _strategies(data)
                before = min(baseline.values(), key=_quality)
                old_seconds = perf_counter() - start
                start = perf_counter()
                after = _improve(data, baseline)
                new_seconds = perf_counter() - start + old_seconds
                assert _quality(after) <= _quality(before)
                pair = data.export(after)
                for chosen in map(set, pair):
                    assert all(v in chosen or any(w in chosen for w in graph[v]) for v in graph)
                old_score = score(graph, data.export(before))
                new_score = score(graph, pair)
                rows.append({"family": family, "seed": seed, "vertices": n, "edges": m,
                             "v1_score": old_score, "v2_score": new_score,
                             "v1_seconds": old_seconds, "v2_seconds": new_seconds})
                print("{} seed={} n={} m={}: {:.4f} -> {:.4f}, {:.3f}s".format(
                    family, seed, n, m, old_score, new_score, new_seconds), flush=True)
    summary = {
        "dataset": "held-out synthetic graphs; not official Codabench instances",
        "graphs": len(rows),
        "improved_graphs": sum(row["v2_score"] < row["v1_score"] for row in rows),
        "max_seconds_per_graph": max(row["v2_seconds"] for row in rows),
        "families": {},
    }
    for family in args.families:
        chosen = [row for row in rows if row["family"] == family]
        summary["families"][family] = {
            "v1_mean_total_13_graphs": sum(row["v1_score"] for row in chosen) / len(args.seeds),
            "v2_mean_total_13_graphs": sum(row["v2_score"] for row in chosen) / len(args.seeds),
        }
    args.output_dir.mkdir(parents=True, exist_ok=True)
    with (args.output_dir / "comparison.csv").open("w", newline="") as out:
        writer = csv.DictWriter(out, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    (args.output_dir / "summary.json").write_text(json.dumps(summary, indent=2) + "\n")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
