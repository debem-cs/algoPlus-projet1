import itertools
import sys
import unittest
from pathlib import Path

import networkx as nx

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "solution"))
from algorithm import _Graph, _bfs, _quality, dominant as original_dominant, score
from improved_search import _balance_components, _bounded_repair, _priority, dominant


def valid(graph, pair):
    return all(
        v in chosen or any(w in chosen for w in graph[v])
        for chosen in map(set, pair) for v in graph
    )


class ImprovedSearchTests(unittest.TestCase):
    def test_all_atlas_graphs_preserve_validity_and_incumbent(self):
        for graph in nx.graph_atlas_g():
            with self.subTest(vertices=len(graph), edges=graph.number_of_edges()):
                before = graph.copy()
                pair = dominant(graph)
                self.assertTrue(valid(graph, pair))
                self.assertLessEqual(score(graph, pair), score(graph, original_dominant(graph)))
                self.assertTrue(nx.utils.graphs_equal(graph, before))
                for chosen in pair:
                    self.assertEqual(len(chosen), len(set(chosen)))
                    self.assertTrue(set(chosen) <= set(graph))

    def test_bounded_repair_against_exhaustive_optima(self):
        for graph in nx.graph_atlas_g():
            if len(graph) > 5:
                continue
            data = _Graph(graph)
            dominating = []
            for mask in range(data.full + 1):
                chosen = {v for v in graph if mask & (1 << v)}
                if all(v in chosen or any(w in chosen for w in graph[v]) for v in graph):
                    dominating.append(mask)
            optimum = min(_quality(pair)[0] for pair in itertools.product(dominating, repeat=2))
            pair = _bounded_repair(data, (0, 0), optimum, _priority(data.n, 0), node_limit=20000)
            self.assertIsNotNone(pair)
            self.assertTrue(valid(graph, data.export(pair)))
            self.assertEqual(_quality(pair)[0], optimum)
            self.assertIsNone(_bounded_repair(
                data, (0, 0), optimum - 1, _priority(data.n, 0), node_limit=20000,
            ))

    def test_component_balancing_against_exhaustive_orientations(self):
        graph = nx.disjoint_union_all([nx.star_graph(k) for k in range(1, 7)])
        data = _Graph(graph)
        pair = _bfs(data)
        balanced = _balance_components(data, pair)
        self.assertTrue(valid(graph, data.export(balanced)))
        self.assertEqual(pair[0] & pair[1], balanced[0] & balanced[1])
        candidates = []
        for flips in itertools.product([False, True], repeat=len(data.component_masks)):
            candidate = list(pair)
            for component, flip in zip(data.component_masks, flips):
                if flip:
                    first, second = candidate[0] & component, candidate[1] & component
                    candidate = [(candidate[0] & ~component) | second,
                                 (candidate[1] & ~component) | first]
            candidates.append(_quality(candidate)[0])
        self.assertEqual(_quality(balanced)[0], min(candidates))

    def test_regression_improves_greedy_local_optimum(self):
        graph = nx.gnm_random_graph(50, 250, seed=23)
        self.assertEqual(score(graph, original_dominant(graph)), 0.16)
        self.assertEqual(score(graph, dominant(graph)), 0.12)

    def test_determinism_mixed_labels_and_loops(self):
        graph = nx.Graph([('A', 1), (1, (2, 3)), ((2, 3), 'A'), ('loop', 'loop')])
        graph.add_node('isolated')
        pair = dominant(graph)
        self.assertEqual(pair, dominant(graph))
        self.assertTrue(valid(graph, pair))
        random_graph = nx.gnm_random_graph(100, 250, seed=59)
        self.assertEqual(dominant(random_graph), dominant(random_graph))


if __name__ == '__main__':
    unittest.main()
