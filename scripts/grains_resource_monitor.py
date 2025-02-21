#!/usr/bin/env python3
"""
grains_resource_monitor.py
Shows how to track system resources (memory, CPU time) when refining capacity N(a)
using a grains-coded approach.
All operations remain finite and use only integer arithmetic for core logic.
"""

import psutil, time
import math

def refine_capacity(old_capacity, factor, max_capacity):
    """
    Attempt to refine capacity from old_capacity to old_capacity * factor,
    but check memory usage first. If memory usage is too high (≥ 80%),
    print a warning and proceed with caution.
    The capacity is increased only if it does not exceed max_capacity.
    All calculations are done using integers.
    """
    mem_info = psutil.virtual_memory()
    mem_percent = int(mem_info.percent)  # already integer
    if mem_percent >= 80:
        print("[WARNING] Memory usage above 80%. Refinement might be risky.")

    new_capacity = old_capacity * factor
    if new_capacity > max_capacity:
        print(f"[STOP] new_capacity={new_capacity} would exceed max_capacity={max_capacity}.")
        return old_capacity  # no change

    # Measure time cost in nanoseconds using integer arithmetic.
    start_t = time.perf_counter_ns()
    time.sleep(10e-6)  # sleep for 10,000 ns (10 µs) as a fixed simulated overhead
    end_t = time.perf_counter_ns()
    dt = end_t - start_t  # dt in nanoseconds

    print(f"Refined from {old_capacity} to {new_capacity}. [Time spent ~ {dt} ns]")
    return new_capacity

def main():
    capacity = 50
    MAX_CAP = 1000
    print(f"Initial capacity = {capacity}, max_capacity = {MAX_CAP}")
    for i in range(5):
        capacity = refine_capacity(capacity, factor=2, max_capacity=MAX_CAP)
        if capacity >= MAX_CAP:
            break

if __name__ == "__main__":
    main()