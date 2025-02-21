#!/usr/bin/env python3
# page_rank.py
# Grains-coded PageRank in a single file

import random
from collections import defaultdict
from fractions import Fraction

def build_grains_transition(graph, capacity=10):
    """
    Build grains-coded outlink distributions for each node.

    graph: dict of the form { "A": ["B", "C"], "B": ["C"], "C": ["A", "B", "C"] }
    capacity: number of grains to assign uniformly among outlinks or to reflect link weight.

    Returns a dictionary of the form:
      { node: { outnode: grains_count, ... }, ... }
    """
    grains_transition = {}
    for node, outlinks in graph.items():
        grains_transition[node] = {}
        if len(outlinks) == 0:
            # No outlinks: assign a self-loop with all grains.
            grains_transition[node][node] = capacity
        else:
            # Distribute grains roughly uniformly among outlinks.
            grains_each = max(1, capacity // len(outlinks))
            leftover = capacity - grains_each * len(outlinks)
            for o in outlinks:
                grains_transition[node][o] = grains_each

            # For simplicity, add any leftover grains to the first outlink.
            if leftover > 0:
                first_o = outlinks[0]
                grains_transition[node][first_o] += leftover

    return grains_transition

def grains_draw_next_node(grains_dict):
    """
    grains_dict: { nextNode: grains_count, ... }
    Perform a grains-coded random draw from the distribution.
    Returns one nextNode based on the grains-coded counts.
    """
    total = sum(grains_dict.values())
    if total == 0:
        # Degenerate case: pick randomly from available keys.
        return random.choice(list(grains_dict.keys()))

    draw = random.randint(0, total - 1)
    running_sum = 0
    for node, grains in grains_dict.items():
        running_sum += grains
        if draw < running_sum:
            return node
    # Theoretically, this should never be reached.
    return None

def grains_coded_pagerank(graph, steps=10000, alpha=0.85, grains_capacity=10, verbose=True):
    """
    Compute PageRank using a grains-coded approach.

    graph: dict { node: [list of outlinked nodes] }
    steps: number of random-walk steps.
    alpha: damping factor in [0,1] (interpreted as a finite fraction).
    grains_capacity: number of grains to assign among outlinks for each node.

    Approach:
      1) Build grains-coded distributions over outlinks.
      2) Convert damping factor alpha into a grains-coded value: grains_alpha out of 100.
      3) Perform a random walk for the specified number of steps, tracking visit counts.
      4) Return an approximate PageRank by normalizing the final counts as exact fractions.
    """
    # 1) Build grains-coded outlink distributions.
    grains_transition = build_grains_transition(graph, capacity=grains_capacity)

    # 2) Convert damping factor: alpha is scaled into an integer out of 100.
    grains_alpha = int(alpha * 100)  # e.g. 0.85 -> 85
    grains_total = 100  # total grains for the damping decision.

    # 3) Initialize random walk.
    nodes = list(graph.keys())
    current = random.choice(nodes)
    visit_count = {n: 0 for n in nodes}

    for _ in range(steps):
        visit_count[current] += 1

        # Decide whether to follow an outlink (with probability alpha) or teleport (with probability 1 - alpha).
        draw = random.randint(0, grains_total - 1)
        if draw < grains_alpha:
            # Follow the grains-coded outlink from the current node.
            next_node = grains_draw_next_node(grains_transition[current])
        else:
            # Teleport: choose a random node.
            next_node = random.choice(nodes)

        current = next_node

    # 4) Normalize visit counts to compute PageRank.
    total_visits = sum(visit_count.values())
    # Use Fraction to represent the normalized value exactly.
    pagerank = {n: Fraction(visit_count[n], total_visits) for n in nodes}

    if verbose:
        print("Final visit counts:", visit_count)
        print("PageRank approximation (exact fractions):", pagerank)

    return pagerank

def main():
    # Example graph:
    graph = {
        "A": ["B", "C"],
        "B": ["C", "D"],
        "C": ["A"],
        "D": ["B", "C"]
    }

    # Compute grains-coded PageRank with grains_capacity=10, alpha=0.85, over 2000 steps.
    pagerank = grains_coded_pagerank(graph, steps=2000, alpha=0.85, grains_capacity=10, verbose=True)

if __name__ == "__main__":
    main()