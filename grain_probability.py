
"""
lump_probability.py

A lumps-coded probability script matching the style in Section 1 of your manual.
We store discrete counts (k) out of a capacity N(a), under keys (a,e,x).
"""

import random
from collections import defaultdict

# Global dictionary:
#   Mu[(a,e,x)] = lumps_count  (an integer k in [0..capacity])
Mu = defaultdict(int)

def set_probability(a, e, x, k, capacity):
    """
    Store lumps-coded measure for pattern x at joint state (a,e).
    k is an integer lumps count, capacity is the denominator N(a).
    """
    if k < 0:
        raise ValueError("Cannot have negative lumps-coded probability.")
    if k > capacity:
        raise ValueError(f"k={k} exceeds capacity={capacity}.")
    Mu[(a,e,x)] = k

def get_probability(a, e, x, capacity):
    """
    Return lumps-coded fraction (k / capacity) as a float for inspection.
    Not recommended for critical logic (floating error risk),
    but useful for quick debugging or printing.
    """
    k = Mu.get((a,e,x), 0)
    return k / capacity

def create_distribution(a, e, lumps_map, capacity):
    """
    Build a lumps-coded distribution for multiple patterns at joint state (a,e).
    lumps_map is a dict: { x: lumps_count }, with sum(lumps_map.values()) <= capacity.
    We'll store them in Mu[(a,e,x)] for each x, then return a 'distribution structure'
    used by sample_from_distribution().

    Example usage:
       lumps_map = {"A":5, "B":10, "C":30}
       dist = create_distribution("obs1","env1", lumps_map, capacity=50)
    """
    total_lumps = 0
    for x, lumps_count in lumps_map.items():
        set_probability(a, e, x, lumps_count, capacity)
        total_lumps += lumps_count

    partial_sums = []
    running_sum = 0
    # Build partial sums array for sampling
    for x, lumps_count in lumps_map.items():
        running_sum += lumps_count
        partial_sums.append((x, running_sum))

    dist_struct = {
        "obs": a,
        "env": e,
        "capacity": capacity,
        "partial_sums": partial_sums,
        "total_lumps": total_lumps
    }
    return dist_struct

def sample_from_distribution(dist_struct):
    """
    lumps-coded random draw from the distribution built by create_distribution().
    We pick an integer in [0, total_lumps-1] and see which pattern x it falls into.
    """
    total_lumps = dist_struct["total_lumps"]
    if total_lumps <= 0:
        # Degenerate => no lumps => we can only pick something arbitrarily
        return None
    draw = random.randint(0, total_lumps - 1)

    for x, upper_bound in dist_struct["partial_sums"]:
        if draw < upper_bound:
            return x
    # Theoretically never get here if partial sums are correct
    return None

def update_probability(a, e, x, delta, capacity):
    """
    Increase/decrease lumps-coded probability for (a,e,x) by 'delta' lumps.
    If this goes below 0, we clamp to 0. If above capacity, clamp to capacity.
    """
    old_k = Mu.get((a,e,x), 0)
    new_k = max(0, min(old_k + delta, capacity))
    Mu[(a,e,x)] = new_k

def main():
    """
    A small demo showing lumps-coded probabilities at (a,e) for patterns (x).
    """
    # We'll define observer state a="obs1", environment e="env1", capacity=40
    a = "obs1"
    e = "env1"
    capacity = 40

    # Suppose we have 3 patterns: A, B, C
    lumps_map = {"A": 5, "B": 15, "C": 5}  # total=25 lumps
    dist = create_distribution(a, e, lumps_map, capacity)
    print("Initial lumps distribution (obs1, env1):", lumps_map)
    print("Total lumps assigned:", dist["total_lumps"])
    print("Probabilities as float (for reference):")
    for x in lumps_map:
        print(f"  {x}: {get_probability(a,e,x,capacity):.3f}")

    print("\nSampling a few draws:")
    results_count = {"A":0, "B":0, "C":0}
    for _ in range(20):
        outcome = sample_from_distribution(dist)
        if outcome is not None:
            results_count[outcome] += 1

    print(results_count)

    # Increase lumps for B by +5, up to capacity
    update_probability(a, e, "B", +5, capacity)
    # Decrease lumps for C by -3
    update_probability(a, e, "C", -3, capacity)

    # Rebuild distribution after changes
    lumps_map_updated = {}
    total_new = 0
    for x in ["A","B","C"]:
        lumps_x = Mu.get((a,e,x),0)
        lumps_map_updated[x] = lumps_x
        total_new += lumps_x

    dist = {
        "obs": a,
        "env": e,
        "capacity": capacity,
        "partial_sums": [],
        "total_lumps": total_new
    }
    # Build partial sums
    running_sum = 0
    for x, lumps_count in lumps_map_updated.items():
        running_sum += lumps_count
        dist["partial_sums"].append((x, running_sum))

    print("\nAfter updates (B +5 lumps, C -3 lumps):", lumps_map_updated)
    print("Probabilities as float (for reference):")
    for x in lumps_map_updated:
        print(f"  {x}: {get_probability(a,e,x,capacity):.3f}")

    # Another sample pass
    results_count = {"A":0, "B":0, "C":0}
    for _ in range(20):
        outcome = sample_from_distribution(dist)
        if outcome is not None:
            results_count[outcome] += 1
    print("\nRandom draws after update:", results_count)

if __name__ == "__main__":
    main()