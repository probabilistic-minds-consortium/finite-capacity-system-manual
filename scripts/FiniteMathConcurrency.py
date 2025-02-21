#!/usr/bin/env python3
"""
Grains-Coded Concurrency Manager:
An example script demonstrating how to manage concurrency in a microservices/tasks environment using
grains-coded (finite) increments, dynamic vantage refinement, and discrete scaling steps.

Key Points:
  - Concurrency is represented as a finite integer value.
  - Capacity refinements occur in discrete leaps (multiplying concurrency by an integer factor).
  - Load pressure is tracked as an integer ratio (grains_load / grains_n) with no floating-point arithmetic.
  - Concurrency expansion is strictly bounded.
  - All core operations use exact, finite integer arithmetic.
"""

import math
import random
import time

class GrainsConcurrencyManager:
    def __init__(self, 
                 initial_concurrency=5,
                 max_refine_factor=10,
                 refine_threshold_numer=7,  # numerator of threshold fraction (e.g., 7/10 for 0.7)
                 refine_threshold_denom=10,
                 grains_n=100):
        self.concurrency = initial_concurrency
        self.max_refine_factor = max_refine_factor
        self.refine_threshold_numer = refine_threshold_numer
        self.refine_threshold_denom = refine_threshold_denom
        self.grains_n = grains_n
        self.grains_load = 0

    def compute_load_fraction(self):
        # Return as (grains_load, grains_n)
        return self.grains_load, self.grains_n

    def adjust_load_pressure(self, fraction_numer, fraction_denom):
        # Compute new grains_load = round( (fraction_numer / fraction_denom) * grains_n )
        # Do this using integer arithmetic:
        new_load = (fraction_numer * self.grains_n + fraction_denom // 2) // fraction_denom
        new_load = max(0, min(new_load, self.grains_n))
        self.grains_load = new_load

    def maybe_refine_capacity(self):
        load, total = self.compute_load_fraction()
        # Compare load/total with refine_threshold_numer/refine_threshold_denom without floats:
        # i.e., check if load * refine_threshold_denom > refine_threshold_numer * total.
        if load * self.refine_threshold_denom > self.refine_threshold_numer * total:
            # Determine smallest factor such that (current_fraction / factor) <= threshold.
            # Since current_fraction is load/total, we want factor >= ceil((load * refine_threshold_denom) / (refine_threshold_numer * total))
            factor_guess = (load * self.refine_threshold_denom + self.refine_threshold_numer * total - 1) // (self.refine_threshold_numer * total)
            factor_guess = max(2, min(factor_guess, self.max_refine_factor))
            old_concurrency = self.concurrency
            self.concurrency *= factor_guess
            print(f"[REFINE] Concurrency refined: {old_concurrency} -> {self.concurrency} (factor = {factor_guess})")

    def run_tasks(self, tasks):
        i = 0
        total_tasks = len(tasks)
        while i < total_tasks:
            batch_size = min(self.concurrency, total_tasks - i)
            print(f"Running tasks {i} to {i+batch_size-1} with concurrency = {self.concurrency}")
            # Simulate load pressure as a fraction between 30/100 and 80/100 (i.e., 0.3 to 0.8) using integers.
            load_numer = 30 + random.randint(0, 50)  # value between 30 and 80
            self.adjust_load_pressure(load_numer, 100)
            print(f"   ...Simulated load: {self.grains_load}/{self.grains_n}")
            self.maybe_refine_capacity()
            time.sleep(1)  # simulate task execution (1 second, display only)
            i += batch_size
        print("All tasks completed with the grains-coded finite approach.")

def example_usage():
    tasks = [f"task_{n}" for n in range(25)]
    manager = GrainsConcurrencyManager(initial_concurrency=3, max_refine_factor=5, refine_threshold_numer=6, refine_threshold_denom=10, grains_n=20)
    manager.run_tasks(tasks)

if __name__ == "__main__":
    example_usage()