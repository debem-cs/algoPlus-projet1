"""Four deterministic strategies for the corrected Codabench score.

Minimize max(len(D1), len(D2)) + len(D1 & D2). The denominator |V|
is constant for a given graph. Only the Python standard library is used.
"""

from collections import deque
from heapq import heapify, heappop, heappush, heapreplace


# Fixed operation limits keep the search deterministic, unlike a clock cutoff.
LOCAL_WORK_LIMIT = 2000000
LOCAL_PASS_LIMIT = 24


def _vertices(mask):
    """Iterate set bits in graph insertion order (also supports mixed labels)."""
    while mask:
        bit = mask & -mask
        yield bit.bit_length() - 1
        mask ^= bit


def _count(mask):
    # int.bit_count() is unavailable in the competition's Python 3.7 image.
    return bin(mask).count("1")


class _Graph:
    def __init__(self, graph):
        self.nodes = list(graph)
        self.n = len(self.nodes)
        self.full = (1 << self.n) - 1
        index = {node: i for i, node in enumerate(self.nodes)}
        self.neighbors = [
            tuple(index[v] for v in graph[u] if v != u)
            for u in self.nodes
        ]
        self.neighborhoods = [
            (i,) + neighbors for i, neighbors in enumerate(self.neighbors)
        ]
        # Each integer is a set: bit i represents vertex i.
        self.closed = [
            sum(1 << v for v in neighborhood)
            for neighborhood in self.neighborhoods
        ]

    def export(self, pair):
        return tuple(
            [self.nodes[v] for v in _vertices(chosen)] for chosen in pair
        )

    def import_pair(self, pair):
        index = {node: i for i, node in enumerate(self.nodes)}
        return tuple(sum(1 << index[v] for v in set(chosen)) for chosen in pair)


def _quality(pair):
    sizes = [_count(chosen) for chosen in pair]
    overlap = _count(pair[0] & pair[1])
    # The score is primary; secondary criteria only break score ties.
    return max(sizes) + overlap, sum(sizes), overlap


def score(graph, pair):
    """Corrected normalized score; define the empty graph's score as zero."""
    if not len(graph):
        return 0.0
    first, second = map(set, pair)
    return (max(len(first), len(second)) + len(first & second)) / len(graph)


def _bfs(data):
    """Strategy 1: alternate colors along each BFS spanning tree."""
    pair = [0, 0]
    color = [-1] * data.n
    for root in range(data.n):
        if color[root] != -1:
            continue
        color[root] = 0
        pair[0] |= 1 << root
        if not data.neighbors[root]:
            pair[1] |= 1 << root
            continue
        queue = deque([root])
        while queue:
            vertex = queue.popleft()
            for neighbor in data.neighbors[vertex]:
                if color[neighbor] == -1:
                    color[neighbor] = 1 - color[vertex]
                    pair[color[neighbor]] |= 1 << neighbor
                    queue.append(neighbor)
    return tuple(pair)


def _coverage_counts(data, chosen):
    counts = [0] * data.n
    for vertex in _vertices(chosen):
        for covered in data.neighborhoods[vertex]:
            counts[covered] += 1
    return counts


def _prune(data, chosen, other, protected=None):
    """Remove redundant vertices, prioritizing those shared with other.

    During a swap, try removing old vertices before the newly added one.
    Coverage counts guarantee that every accepted removal stays valid.
    """
    counts = _coverage_counts(data, chosen)
    order = sorted(
        _vertices(chosen),
        key=lambda v: (v == protected, not bool(other & (1 << v)), -v),
    )
    for vertex in order:
        if all(counts[w] > 1 for w in data.neighborhoods[vertex]):
            chosen &= ~(1 << vertex)
            for covered in data.neighborhoods[vertex]:
                counts[covered] -= 1
    return chosen


def _prune_pair(data, pair):
    first = _prune(data, pair[0], pair[1])
    second = _prune(data, pair[1], first)
    return first, second


def _duplicated_greedy(data):
    """Strategy 2: repeatedly maximize new coverage, then return (D, D)."""
    heap = [(-len(neighborhood), v)
            for v, neighborhood in enumerate(data.neighborhoods)]
    heapify(heap)
    uncovered = data.full
    chosen = 0
    while uncovered:
        _, vertex = heappop(heap)
        gain = _count(data.closed[vertex] & uncovered)
        if not gain:
            continue
        # Old gains are upper bounds. Refresh lazily until the best is exact.
        if heap and (-gain, vertex) > heap[0]:
            heappush(heap, (-gain, vertex))
            continue
        chosen |= 1 << vertex
        uncovered &= ~data.closed[vertex]
    chosen = _prune(data, chosen, chosen)
    return chosen, chosen


def _best_gain(data, heap, uncovered, chosen, other, shared):
    """Best unselected vertex of a category, using lazy coverage updates."""
    while heap:
        old_gain, vertex = heap[0]
        bit = 1 << vertex
        if chosen & bit or bool(other & bit) != shared:
            heappop(heap)
            continue
        gain = _count(data.closed[vertex] & uncovered)
        if old_gain != -gain:
            heapreplace(heap, (-gain, vertex))
            continue
        return (vertex, gain) if gain else None
    return None


def _joint_greedy(data):
    """Strategy 3: maximize new coverage per marginal score cost.

    Adding to the smaller set can cost zero; sharing a vertex costs one
    extra unit. Each side has heaps for shared and unshared candidates.
    """
    initial = [(-len(neighborhood), v)
               for v, neighborhood in enumerate(data.neighborhoods)]
    heapify(initial)
    heaps = [[list(initial), []], [list(initial), []]]
    pair = [0, 0]
    sizes = [0, 0]
    uncovered = [data.full, data.full]
    while uncovered[0] or uncovered[1]:
        best = None
        for side in range(2):
            if not uncovered[side]:
                continue
            other = 1 - side
            for shared in (False, True):
                candidate = _best_gain(
                    data, heaps[side][int(shared)], uncovered[side],
                    pair[side], pair[other], shared,
                )
                if candidate is None:
                    continue
                vertex, gain = candidate
                cost = (max(sizes[side] + 1, sizes[other])
                        - max(sizes) + int(shared))
                key = (cost == 0, gain / (cost or 1), gain,
                       -int(shared), -side, -vertex)
                if best is None or key > best[0]:
                    best = key, side, vertex
        _, side, vertex = best
        other = 1 - side
        pair[side] |= 1 << vertex
        sizes[side] += 1
        uncovered[side] &= ~data.closed[vertex]
        # The other side can now choose this vertex as a shared candidate.
        if not pair[other] & (1 << vertex):
            gain = _count(data.closed[vertex] & uncovered[other])
            heappush(heaps[other][1], (-gain, vertex))
    return _prune_pair(data, pair)


def _local_search(data, pair, work_limit):
    """Strategy 4: delete redundancies and exchange one new vertex for old ones.

    Only accept valid solutions with better (score, total size, overlap).
    Fixed work/pass budgets bound the search without clock-based choices.
    """
    pair = _prune_pair(data, pair)
    remaining = work_limit
    for _ in range(LOCAL_PASS_LIMIT):
        improved = False
        sides = sorted(range(2), key=lambda s: (-_count(pair[s]), s))
        for side in sides:
            other = 1 - side
            chosen = pair[side]
            members = list(_vertices(chosen))
            coverage_work = sum(len(data.neighborhoods[v]) for v in members)
            if coverage_work > remaining:
                return pair
            remaining -= coverage_work
            counts = _coverage_counts(data, chosen)
            unique = sum(1 << v for v, count in enumerate(counts) if count == 1)
            # A private vertex is covered by exactly one selected vertex.
            private = [data.closed[v] & unique for v in members]
            candidates = []
            for vertex in _vertices(data.full & ~chosen):
                if len(private) > remaining:
                    break
                remaining -= len(private)
                outside = data.full & ~data.closed[vertex]
                removable = sum(not (needed & outside) for needed in private)
                if removable:
                    candidates.append((
                        -removable, bool(pair[other] & (1 << vertex)),
                        -len(data.neighborhoods[vertex]), vertex,
                    ))
            for _, _, _, vertex in sorted(candidates):
                # Account for building counts and scanning the neighborhoods.
                work = 2 * (coverage_work + len(data.neighborhoods[vertex]))
                if work > remaining:
                    continue
                remaining -= work
                replacement = _prune(
                    data, chosen | (1 << vertex), pair[other], protected=vertex,
                )
                trial = list(pair)
                trial[side] = replacement
                trial = tuple(trial)
                if _quality(trial) < _quality(pair):
                    pair = trial
                    improved = True
                    break
            if improved:
                break
        if not improved:
            break
    return pair


def _strategies(data):
    results = {
        "bfs": _bfs(data),
        "duplicated_greedy": _duplicated_greedy(data),
        "joint_greedy": _joint_greedy(data),
    }
    # Improve each distinct starting solution, sharing a fixed work budget.
    starts = list(dict.fromkeys(results.values()))
    budget = LOCAL_WORK_LIMIT // len(starts)
    results["local_search"] = min(
        (_local_search(data, pair, budget) for pair in starts), key=_quality,
    )
    return results


def bfs_dominants(g):
    """Two dominating sets with minimum intersection (baseline)."""
    data = _Graph(g)
    return data.export(_bfs(data))


def duplicated_greedy(g):
    """A small greedy dominating set used twice."""
    data = _Graph(g)
    return data.export(_duplicated_greedy(data))


def joint_greedy(g):
    """Build both dominating sets with the corrected score in mind."""
    data = _Graph(g)
    return data.export(_joint_greedy(data))


def local_search(g, pair=None):
    """Improve a supplied valid pair, or start from all three constructors."""
    data = _Graph(g)
    if pair is None:
        result = _strategies(data)["local_search"]
    else:
        result = _local_search(data, data.import_pair(pair), LOCAL_WORK_LIMIT)
    return data.export(result)


def all_strategies(g):
    """Expose all four results for local comparisons."""
    data = _Graph(g)
    return {name: data.export(pair) for name, pair in _strategies(data).items()}


def dominant(g):
    """Codabench entry point: return the best of the four strategies.

    Every candidate is valid; the winner is never worse than the BFS
    baseline under the corrected score. No global optimality is claimed.
    """
    data = _Graph(g)
    return data.export(min(_strategies(data).values(), key=_quality))
