

"""
grains_probability.py

A grains-coded probability script matching the style in Section 1 of the manual.
We store discrete counts (k) out of a capacity N(a), under keys (a, e, x).
All operations are finite and exact.
"""

import random
from collections import defaultdict

# Global dictionary:
#   Mu[(a, e, x)] = grains_count (an integer k in [0, capacity])
Mu = defaultdict(int)

def set_probability(a, e, x, k, capacity):
    """
    Store a grains-coded measure for pattern x at joint state (a, e).
    k is an integer grains count, and capacity is the finite denominator N(a).
    """
    if k < 0:
        raise ValueError("Cannot have negative grains-coded probability.")
    if k > capacity:
        raise ValueError(f"k={k} exceeds capacity={capacity}.")
    Mu[(a, e, x)] = k

def get_probability(a, e, x, capacity):
    """
    Return the grains-coded fraction (k / capacity) as a decimal for display.
    (This conversion is for inspection only; core logic remains finite.)
    """
    k = Mu.get((a, e, x), 0)
    return k / capacity

def create_distribution(a, e, grains_map, capacity):
    """
    Build a grains-coded distribution for multiple patterns at joint state (a, e).
    grains_map is a dict: { x: grains_count }, with sum(grains_map.values()) <= capacity.
    Stores each value in Mu[(a, e, x)] and returns a distribution structure for sampling.
    """
    total_grains = 0
    for x, grains_count in grains_map.items():
        set_probability(a, e, x, grains_count, capacity)
        total_grains += grains_count

    partial_sums = []
    running_sum = 0
    # Build partial sums array for sampling.
    for x, grains_count in grains_map.items():
        running_sum += grains_count
        partial_sums.append((x, running_sum))

    dist_struct = {
        "obs": a,
        "env": e,
        "capacity": capacity,
        "partial_sums": partial_sums,
        "total_grains": total_grains
    }
    return dist_struct

def sample_from_distribution(dist_struct):
    """
    Perform a grains-coded random draw from the distribution built by create_distribution().
    We pick an integer in [0, total_grains - 1] and determine which pattern x it falls into.
    """
    total_grains = dist_struct["total_grains"]
    if total_grains <= 0:
        # Degenerate distribution: no grains assigned.
        return None
    draw = random.randint(0, total_grains - 1)
    for x, upper_bound in dist_struct["partial_sums"]:
        if draw < upper_bound:
            return x
    # Should not reach here if partial sums are constructed correctly.
    return None

def update_probability(a, e, x, delta, capacity):
    """
    Adjust the grains-coded probability for (a, e, x) by 'delta' grains.
    Clamps the value between 0 and capacity.
    """
    old_k = Mu.get((a, e, x), 0)
    new_k = max(0, min(old_k + delta, capacity))
    Mu[(a, e, x)] = new_k

def main():
    """
    A demonstration of grains-coded probabilities for patterns at joint state (a, e).
    """
    # Define observer state a="obs1", environment e="env1", capacity=40.
    a = "obs1"
    e = "env1"
    capacity = 40

    # Suppose we have 3 patterns: A, B, and C.
    grains_map = {"A": 5, "B": 15, "C": 5}  # total assigned grains = 25.
    dist = create_distribution(a, e, grains_map, capacity)
    print("Initial grains distribution (obs1, env1):", grains_map)
    print("Total grains assigned:", dist["total_grains"])
    print("Probabilities (for reference):")
    for x in grains_map:
        print(f"  {x}: {get_probability(a, e, x, capacity):.3f}")

    print("\nSampling a few draws:")
    results_count = {"A": 0, "B": 0, "C": 0}
    for _ in range(20):
        outcome = sample_from_distribution(dist)
        if outcome is not None:
            results_count[outcome] += 1
    print("Sampled distribution:", results_count)

    # Update probabilities: increase B by +5 grains and decrease C by -3 grains.
    update_probability(a, e, "B", +5, capacity)
    update_probability(a, e, "C", -3, capacity)

    # Rebuild distribution after updates.
    grains_map_updated = {}
    total_new = 0
    for x in ["A", "B", "C"]:
        grains_x = Mu.get((a, e, x), 0)
        grains_map_updated[x] = grains_x
        total_new += grains_x

    dist = {
        "obs": a,
        "env": e,
        "capacity": capacity,
        "partial_sums": [],
        "total_grains": total_new
    }
    running_sum = 0
    for x, grains_count in grains_map_updated.items():
        running_sum += grains_count
        dist["partial_sums"].append((x, running_sum))

    print("\nAfter updates (B +5, C -3):", grains_map_updated)
    print("Probabilities (for reference):")
    for x in grains_map_updated:
        print(f"  {x}: {get_probability(a, e, x, capacity):.3f}")

    # Another sampling round.
    results_count = {"A": 0, "B": 0, "C": 0}
    for _ in range(20):
        outcome = sample_from_distribution(dist)
        if outcome is not None:
            results_count[outcome] += 1
    print("\nRandom draws after update:", results_count)

if __name__ == "__main__":
    main()