"""Deterministic multistart and destroy/repair search for Codabench."""

from heapq import heapify, heappop, heappush, heapreplace

from algorithm import (
    _Graph, _count, _local_search, _prune_pair, _quality, _strategies, _vertices,
)


MULTISTART_VARIANTS = 64
REPAIR_ROUNDS = 256
LOCAL_STARTS = 10
LOCAL_START_WORK = 750000
REPAIR_BRANCH_LIMIT = 1200


def _balance_components(data, pair):
    """Optimally orient independent components for the current memberships.

    Swapping the two colors in a whole component preserves both domination
    and intersection. A small subset-sum DP minimizes the size imbalance.
    """
    components = getattr(data, "component_masks", None)
    if components is None:
        components = []
        seen = [False] * data.n
        for root in range(data.n):
            if seen[root]:
                continue
            seen[root] = True
            queue = [root]
            mask = 0
            for vertex in queue:
                mask |= 1 << vertex
                for neighbor in data.neighbors[vertex]:
                    if not seen[neighbor]:
                        seen[neighbor] = True
                        queue.append(neighbor)
            components.append(mask)
        data.component_masks = components
    if len(components) <= 1:
        return pair
    differences = [
        _count(pair[0] & component) - _count(pair[1] & component)
        for component in components
    ]
    reachable = {0: 0}
    for index, difference in enumerate(differences):
        if difference:
            for subtotal, flips in list(reachable.items()):
                reachable.setdefault(subtotal + difference, flips | (1 << index))
    total = sum(differences)
    subtotal = min(reachable, key=lambda value: (
        abs(total - 2 * value), _count(reachable[value]), value,
    ))
    first, second = pair
    for index in _vertices(reachable[subtotal]):
        component = components[index]
        old_first, old_second = first & component, second & component
        first = (first & ~component) | old_second
        second = (second & ~component) | old_first
    return first, second


def _priority(n, variant):
    """Deterministic permutations used only to order equivalent choices."""
    if not n:
        return []
    offset = (variant * 37) % n
    if variant % 2:
        return [(offset - v) % n for v in range(n)]
    return [(v + offset) % n for v in range(n)]


def _best_repair_gain(data, heap, uncovered, chosen, other, shared):
    while heap:
        old_gain, rank, vertex = heap[0]
        bit = 1 << vertex
        if chosen & bit or bool(other & bit) != shared:
            heappop(heap)
            continue
        gain = _count(data.closed[vertex] & uncovered)
        if old_gain != -gain:
            heapreplace(heap, (-gain, rank, vertex))
            continue
        return (vertex, gain) if gain else None
    return None


def _repair(data, pair, priority, shared_weight=1.0, free_cost=0.5):
    """Complete two possibly incomplete sets and then remove redundancies.

    Different fixed cost proxies explore alternatives; final comparisons
    always use the actual competition score, not these construction costs.
    """
    pair = list(pair)
    sizes = [_count(mask) for mask in pair]
    uncovered = []
    heaps = []
    for side in range(2):
        covered = 0
        for vertex in _vertices(pair[side]):
            covered |= data.closed[vertex]
        uncovered.append(data.full & ~covered)
        categories = [[], []]
        for vertex, neighborhood in enumerate(data.neighborhoods):
            if pair[side] & (1 << vertex):
                continue
            shared = int(bool(pair[1 - side] & (1 << vertex)))
            categories[shared].append((-len(neighborhood), priority[vertex], vertex))
        for heap in categories:
            heapify(heap)
        heaps.append(categories)

    while uncovered[0] or uncovered[1]:
        best = None
        for side in range(2):
            if not uncovered[side]:
                continue
            other = 1 - side
            for shared in (False, True):
                candidate = _best_repair_gain(
                    data, heaps[side][int(shared)], uncovered[side],
                    pair[side], pair[other], shared,
                )
                if candidate is None:
                    continue
                vertex, gain = candidate
                growth = max(sizes[side] + 1, sizes[other]) - max(sizes)
                cost = growth + shared_weight * int(shared)
                if free_cost:
                    key = (0, gain / (cost or free_cost), gain,
                           -int(shared), -priority[vertex], -side)
                else:
                    key = (cost == 0, gain / (cost or 1), gain,
                           -int(shared), -priority[vertex], -side)
                if best is None or key > best[0]:
                    best = key, side, vertex
        _, side, vertex = best
        other = 1 - side
        pair[side] |= 1 << vertex
        sizes[side] += 1
        uncovered[side] &= ~data.closed[vertex]
        if not pair[other] & (1 << vertex):
            gain = _count(data.closed[vertex] & uncovered[other])
            heappush(heaps[other][1], (-gain, priority[vertex], vertex))
    return _balance_components(data, _prune_pair(data, pair))


def _destroy(data, pair, iteration):
    """Remove a small, deterministic cluster to allow coordinated changes."""
    pair = list(pair)
    side = iteration % 2
    members = list(_vertices(pair[side]))
    if not members:
        return tuple(pair)
    pivot = members[(iteration * 17) % len(members)]
    affected = data.closed[pivot]
    for neighbor in data.neighbors[pivot]:
        affected |= data.closed[neighbor]
    for current_side in range(2):
        selected = list(_vertices(pair[current_side]))
        selected.sort(key=lambda v: (
            not bool(data.closed[v] & affected),
            (v + iteration * 13) % max(data.n, 1),
        ))
        amount = 1 + (iteration // 2 + current_side) % 3
        for vertex in selected[:amount]:
            pair[current_side] &= ~(1 << vertex)
    return tuple(pair)


def _bounded_repair(data, pair, target, priority, node_limit=REPAIR_BRANCH_LIMIT):
    """Search a bounded repair neighborhood for a score numerator <= target.

    Branch on how to cover the uncovered vertex with the fewest neighbors.
    The current numerator and a mandatory-addition bound prune impossible
    branches. Exhausting the node limit proves nothing about global optimality.
    """
    uncovered = []
    for chosen in pair:
        covered = 0
        for vertex in _vertices(chosen):
            covered |= data.closed[vertex]
        uncovered.append(data.full & ~covered)
    seen = set()

    def visit(current, missing, sizes, overlap):
        if len(seen) >= node_limit or current in seen:
            return None
        seen.add(current)
        # Each unfinished side needs at least one additional selected vertex.
        bound = max(sizes[0] + bool(missing[0]), sizes[1] + bool(missing[1])) + overlap
        if bound > target:
            return None
        if not missing[0] and not missing[1]:
            return current
        pivot = min(
            (len(data.neighborhoods[v]), priority[v], side, v)
            for side in range(2) for v in _vertices(missing[side])
        )
        _, _, side, vertex = pivot
        other = 1 - side
        choices = []
        old_cost = max(sizes) + overlap
        for selected in data.neighborhoods[vertex]:
            shared = int(bool(current[other] & (1 << selected)))
            cost = max(sizes[side] + 1, sizes[other]) + overlap + shared
            if cost <= target:
                gain = _count(data.closed[selected] & missing[side])
                choices.append((cost - old_cost, -gain, priority[selected], selected, shared))
        for _, _, _, selected, shared in sorted(choices):
            if len(seen) >= node_limit:
                break
            new_pair = list(current)
            new_pair[side] |= 1 << selected
            new_missing = list(missing)
            new_missing[side] &= ~data.closed[selected]
            new_sizes = list(sizes)
            new_sizes[side] += 1
            result = visit(tuple(new_pair), tuple(new_missing), tuple(new_sizes), overlap + shared)
            if result is not None:
                return result
        return None

    result = visit(tuple(pair), tuple(uncovered), tuple(_count(mask) for mask in pair),
                   _count(pair[0] & pair[1]))
    if result is None:
        return None
    return _balance_components(data, _prune_pair(data, result))


def _improve(data, baseline=None):
    """Keep the old result as an incumbent, then explore more valid pairs."""
    baseline = baseline or _strategies(data)
    best = _balance_components(data, min(baseline.values(), key=_quality))
    if not data.n:
        return best
    # Huge graphs retain the fast validated baseline. Contest graphs have <=500 nodes.
    if data.n > 1000:
        return best
    variants = 6 if data.n <= 12 else MULTISTART_VARIANTS
    pool = {pair: _quality(pair) for pair in baseline.values()}
    for variant in range(variants):
        shared_weight = (0.5, 1.0, 2.0, 4.0)[variant % 4]
        free_cost = (0.0, 0.25, 0.5, 1.0)[(variant // 4) % 4]
        pair = _repair(data, (0, 0), _priority(data.n, variant), shared_weight, free_cost)
        pool[pair] = _quality(pair)
        if _quality(pair) < _quality(best):
            best = pair

    # Spending the fixed budget on promising, distinct starts is inexpensive.
    starts = sorted(pool, key=lambda pair: (pool[pair], pair))[:LOCAL_STARTS]
    for pair in starts:
        candidate = _balance_components(data, _local_search(data, pair, LOCAL_START_WORK))
        if _quality(candidate) < _quality(best):
            best = candidate

    current = best
    visited = {current}
    rounds = 12 if data.n <= 12 else REPAIR_ROUNDS
    for iteration in range(rounds):
        variant = iteration + variants
        damaged = _destroy(data, current, iteration)
        candidate = _repair(
            data, damaged, _priority(data.n, variant),
            shared_weight=(0.5, 1.0, 2.0, 4.0)[iteration % 4],
            free_cost=(0.25, 0.5, 1.0)[iteration % 3],
        )
        if iteration % 8 == 7:
            repaired = _bounded_repair(
                data, damaged, _quality(best)[0] - 1, _priority(data.n, variant),
            )
            if repaired is not None and _quality(repaired) < _quality(candidate):
                candidate = repaired
        if candidate not in visited:
            visited.add(candidate)
            if _quality(candidate) < _quality(best):
                best = candidate
            # A bounded uphill move can leave a local optimum; best is retained.
            if _quality(candidate)[0] <= _quality(best)[0] + (iteration % 8 == 0):
                current = candidate
        if iteration % 12 == 11:
            current = best
        if iteration % 64 == 63:
            candidate = _balance_components(data, _local_search(data, best, LOCAL_START_WORK))
            if _quality(candidate) < _quality(best):
                best = current = candidate
    return best


def dominant(g):
    """Improved submission; never worse than the previous four-strategy result."""
    data = _Graph(g)
    return data.export(_improve(data))
