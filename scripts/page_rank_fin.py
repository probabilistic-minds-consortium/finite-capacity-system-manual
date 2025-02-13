#!/usr/bin/env python3
# page_rank.py
# Lumps-coded PageRank in a single file

import random

def build_lumps_transition(graph, capacity=10):
    """
    Build lumps-coded outlinks for each node.

    graph: dict of the form { "A": ["B","C"], "B": ["C"], "C": ["A","B","C"] }
    capacity: lumps for uniform distribution among outlinks or to reflect link weight.

    Returns lumps_transition: {
      node: { outnode: lumps_count, ... },
      ...
    }
    """
    lumps_transition = {}
    for node, outlinks in graph.items():
        lumps_transition[node] = {}
        if len(outlinks) == 0:
            # No outlinks => self-loop with all lumps
            lumps_transition[node][node] = capacity
        else:
            # Distribute lumps roughly uniformly among outlinks
            lumps_each = max(1, capacity // len(outlinks))
            leftover = capacity - lumps_each * len(outlinks)
            for o in outlinks:
                lumps_transition[node][o] = lumps_each

            # Put any leftover lumps into the first link for simplicity
            if leftover > 0:
                first_o = outlinks[0]
                lumps_transition[node][first_o] += leftover

    return lumps_transition

def lumps_draw_next_node(lumps_dict):
    """
    lumps_dict: { nextNode: lumps_count, ... }
    Return one nextNode based on lumps-coded distribution.
    """
    total = sum(lumps_dict.values())
    if total == 0:
        # Degenerate => pick randomly from lumps_dict keys
        return random.choice(list(lumps_dict.keys()))

    draw = random.randint(0, total - 1)
    running_sum = 0
    for node, lumps in lumps_dict.items():
        running_sum += lumps
        if draw < running_sum:
            return node

    # Theoretically never hits here if lumps_dict isn't empty
    return None

def lumps_coded_pagerank(graph, steps=10000, alpha=0.85, lumps_capacity=10, verbose=True):
    """
    graph: dict { node: [list of outlinked nodes] }
    steps: number of random-walk steps
    alpha: damping factor in [0,1], lumps-coded approach
    lumps_capacity: lumps to assign among outlinks for each node

    We'll do a lumps-coded approach:
    1) Build lumps-coded distribution over outlinks.
    2) Use integer lumps for alpha * 100 to decide between following outlinks vs. teleport.
    3) Perform a random walk of 'steps' iterations, tracking visit counts.
    4) Return approximate PageRank by normalizing final counts.
    """

    # 1) Build lumps-coded outlink distributions
    lumps_transition = build_lumps_transition(graph, capacity=lumps_capacity)

    # 2) Convert damping factor alpha -> lumps_alpha out of 100
    lumps_alpha = int(alpha * 100)  # e.g. alpha=0.85 => lumps_alpha=85
    lumps_total = 100  # leftover = lumps_total - lumps_alpha

    # 3) Choose a random start node
    nodes = list(graph.keys())
    current = random.choice(nodes)

    # Initialize visit counts
    visit_count = {n: 0 for n in nodes}

    # 4) Random walk
    for _ in range(steps):
        visit_count[current] += 1

        # Decide whether to follow outlink (alpha) or teleport (1-alpha)
        draw = random.randint(0, lumps_total - 1)
        if draw < lumps_alpha:
            # Follow lumps-coded outlink from current node
            next_node = lumps_draw_next_node(lumps_transition[current])
        else:
            # Teleport: pick random node from the graph
            next_node = random.choice(nodes)

        current = next_node

    # 5) Normalize to get PageRank
    total_visits = sum(visit_count.values())
    pagerank = {n: visit_count[n] / total_visits for n in nodes}

    if verbose:
        print("Final visit counts:", visit_count)
        print("Pagerank approximation:", pagerank)

    return pagerank

def main():
    # Example directed graph
    graph = {
        "A": ["B", "C"],
        "B": ["C", "D"],
        "C": ["A"],
        "D": ["B", "C"]
    }

    # Lumps-coded PageRank with capacity=10 lumps, alpha=0.85, and 2000 steps
    pagerank = lumps_coded_pagerank(graph, steps=2000, alpha=0.85,
                                    lumps_capacity=10, verbose=True)

if __name__ == "__main__":
    main()

