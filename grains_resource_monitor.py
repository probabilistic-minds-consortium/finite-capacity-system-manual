#!/usr/bin/env python3

"""
lumps_resource_monitor.py
Shows how to track system resources (memory, CPU time) when refining capacity N(a).
"""

import psutil, time

def refine_capacity(old_capacity, factor, max_capacity):
    """
    Attempt to refine capacity from old_capacity to old_capacity*factor,
    but check memory usage first. If too high, skip or revert to partial expansion.
    """
    mem_info = psutil.virtual_memory()
    if mem_info.percent > 80:
        print("[WARNING] Memory usage above 80%. Refinement might be risky.")
        # either skip, or do partial factor, e.g. factor=2 -> factor=1.2, etc.
    
    new_capacity = old_capacity * factor
    if new_capacity > max_capacity:
        print(f"[STOP] new_capacity={new_capacity} would exceed max_capacity={max_capacity}.")
        return old_capacity  # no change
    
    # measure time cost for demonstration
    start_t = time.perf_counter()
    # (Here you'd actually unify or rescale lumps-coded data.)
    time.sleep(0.01)  # simulate small overhead
    end_t = time.perf_counter()
    dt = end_t - start_t

    print(f"Refined from {old_capacity} to {new_capacity}. [Time spent ~ {dt:.4f}s]")
    return new_capacity

def main():
    N = 50
    MAX_CAP = 1000
    print(f"Initial capacity={N}, max_capacity={MAX_CAP}")
    for i in range(5):
        N = refine_capacity(N, factor=2, max_capacity=MAX_CAP)
        # do lumps-coded computations at new capacity ...
        if N >= MAX_CAP:
            break

if __name__=="__main__":
    main()