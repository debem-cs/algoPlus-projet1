import sys
import unittest
from pathlib import Path

import networkx as nx

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "solution"))
from algorithm import (
    all_strategies,
    bfs_dominants,
    dominant,
    duplicated_greedy,
    joint_greedy,
    local_search,
    score,
)


class DominantTests(unittest.TestCase):
    def check_solution(self, graph, result):
        self.assertEqual(len(result), 2)

        for nodes in result:
            self.assertIsInstance(nodes, list)
            chosen = set(nodes)
            self.assertEqual(len(nodes), len(chosen))
            self.assertTrue(chosen <= set(graph))
            for vertex in graph:
                self.assertTrue(
                    vertex in chosen
                    or any(neighbor in chosen for neighbor in graph[vertex]),
                    "A vertex is not dominated",
                )

        forced = {
            vertex for vertex in graph
            if not any(neighbor != vertex for neighbor in graph[vertex])
        }
        self.assertTrue(forced <= set(result[0]) & set(result[1]))

    def check_strategies(self, graph):
        before = graph.copy()
        results = all_strategies(graph)
        self.assertEqual(set(results), {
            "bfs", "duplicated_greedy", "joint_greedy", "local_search",
        })
        for name, result in results.items():
            with self.subTest(strategy=name):
                self.check_solution(graph, result)
                self.assertLessEqual(
                    score(graph, results["local_search"]), score(graph, result),
                )

        first, second = results["bfs"]
        forced = {
            vertex for vertex in graph
            if not any(neighbor != vertex for neighbor in graph[vertex])
        }
        self.assertEqual(set(first) & set(second), forced)
        self.assertEqual(*results["duplicated_greedy"])
        selected = dominant(graph)
        self.check_solution(graph, selected)
        self.assertEqual(
            score(graph, selected),
            min(score(graph, pair) for pair in results.values()),
        )
        self.assertTrue(nx.utils.graphs_equal(graph, before))

    def test_all_simple_graphs_up_to_seven_vertices(self):
        # Includes empty graphs, isolates, trees, odd cycles and cliques.
        for graph in nx.graph_atlas_g():
            with self.subTest(vertices=len(graph), edges=graph.number_of_edges()):
                self.check_strategies(graph)

    def test_star_rewards_overlap_under_corrected_score(self):
        graph = nx.star_graph(4)
        self.assertEqual(score(graph, bfs_dominants(graph)), 0.8)
        self.assertEqual(score(graph, duplicated_greedy(graph)), 0.4)
        self.assertEqual(score(graph, dominant(graph)), 0.4)

    def test_complete_graph_rewards_distinct_singletons(self):
        graph = nx.complete_graph(5)
        self.assertEqual(score(graph, duplicated_greedy(graph)), 0.4)
        self.assertEqual(score(graph, joint_greedy(graph)), 0.2)
        self.assertEqual(score(graph, dominant(graph)), 0.2)

    def test_local_search_improves_path(self):
        graph = nx.path_graph(5)
        initial = bfs_dominants(graph)
        improved = local_search(graph, initial)
        self.check_solution(graph, improved)
        self.assertEqual(score(graph, initial), 0.6)
        self.assertEqual(score(graph, improved), 0.4)

    def test_local_search_from_all_vertices(self):
        graph = nx.cycle_graph(7)
        initial = (list(graph), list(graph))
        improved = local_search(graph, initial)
        self.check_solution(graph, improved)
        self.assertLess(score(graph, improved), score(graph, initial))

    def test_determinism(self):
        graph = nx.gnm_random_graph(100, 250, seed=42)
        self.assertEqual(all_strategies(graph), all_strategies(graph))

    def test_empty_graph_score(self):
        graph = nx.Graph()
        self.assertEqual(dominant(graph), ([], []))
        self.assertEqual(score(graph, ([], [])), 0.0)

    def test_mixed_labels_and_self_loops(self):
        graph = nx.Graph()
        graph.add_edges_from([("A", 1), (1, (2, 3)), ((2, 3), "A")])
        graph.add_node("isolated")
        graph.add_edge("loop", "loop")
        self.check_strategies(graph)

    def test_large_graphs(self):
        for graph in [
            nx.path_graph(10000),
            nx.star_graph(10000),
            nx.gnm_random_graph(500, 1000, seed=42),
            nx.complete_graph(500),
        ]:
            before = graph.copy()
            result = dominant(graph)
            self.check_solution(graph, result)
            self.assertLessEqual(score(graph, result), score(graph, bfs_dominants(graph)))
            self.assertTrue(nx.utils.graphs_equal(graph, before))


if __name__ == "__main__":
    unittest.main()
