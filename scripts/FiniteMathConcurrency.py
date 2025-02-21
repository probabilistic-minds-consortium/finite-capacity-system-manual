#!/usr/bin/env python3

"""
Grains-Coded Concurrency Manager:
An example script demonstrating how to manage concurrency 
in a microservices or tasks environment using grains-coded (finite) increments,
dynamic vantage refinement, and discrete scaling steps.

Key Points:
  - Concurrency is stored as a grains-coded fraction or a vantage-based integer.
  - Capacity refinements occur in discrete leaps (multiplying concurrency by an integer factor).
  - We track 'load pressure' as a finite integer representing a fraction.
  - Concurrency expansion is strictly bounded – no reliance on any notion of infinity.
  - Each vantage step is validated to ensure stable, finite updates.
"""

import math
import random
import time

class GrainsConcurrencyManager:
    def __init__(self, 
                 initial_concurrency=5,   # starting concurrency vantage
                 max_refine_factor=10,     # maximum integer factor for concurrency expansion
                 refine_threshold=0.7,     # threshold (as a finite fraction) for load pressure triggering refinement
                 grains_n=100):
        """
        initial_concurrency: starting number of tasks that can run in parallel.
        max_refine_factor: the largest factor by which concurrency can be expanded.
        refine_threshold: finite fraction in [0,1]; if load pressure exceeds this, refine capacity.
        grains_n: the denominator used for expressing load pressure as a finite fraction.
        """
        self.concurrency = initial_concurrency
        self.max_refine_factor = max_refine_factor
        self.refine_threshold = refine_threshold
        self.grains_n = grains_n

        # Load pressure is stored as an integer from 0 to grains_n, representing a fraction.
        self.grains_load = 0

    def compute_load_fraction(self):
        """Return the finite load fraction as grains_load / grains_n (exact value stored as a fraction)."""
        # The computation is done in integers; conversion is only for display.
        return self.grains_load, self.grains_n

    def adjust_load_pressure(self, fraction):
        """
        Given a fraction in [0,1], set grains_load = int(round(fraction * grains_n)).
        This simulates load from real metrics (e.g. CPU usage, queue depth).
        """
        grains_val = int(round(fraction * self.grains_n))
        # Clamp to ensure the value remains between 0 and grains_n.
        grains_val = max(0, min(grains_val, self.grains_n))
        self.grains_load = grains_val

    def maybe_refine_capacity(self):
        """
        If the load fraction exceeds the refine_threshold, refine concurrency 
        by multiplying it by an integer factor (between 2 and max_refine_factor).
        """
        current_load, total = self.compute_load_fraction()
        current_fraction = current_load / total
        if current_fraction > self.refine_threshold:
            # Determine the smallest factor that brings the fraction under threshold.
            factor_guess = math.ceil(current_fraction / self.refine_threshold)
            factor_guess = max(2, min(factor_guess, self.max_refine_factor))
            
            old_concurrency = self.concurrency
            self.concurrency *= factor_guess
            print(f"[REFINE] Concurrency refined: {old_concurrency} -> {self.concurrency} (factor = {factor_guess})")

    def run_tasks(self, tasks):
        """
        Simulate running tasks with current finite concurrency vantage.
        Tasks are processed in batches equal to the current concurrency.
        Load pressure is simulated and used to decide whether to refine capacity.
        """
        i = 0
        total_tasks = len(tasks)
        while i < total_tasks:
            batch_size = min(self.concurrency, total_tasks - i)
            batch_tasks = tasks[i:i+batch_size]
            print(f"Running tasks {i} to {i+batch_size-1} with concurrency = {self.concurrency}")
            
            # Simulate load pressure as a finite fraction in [0.3, 0.8].
            load_fraction = 0.3 + 0.5 * random.random()
            self.adjust_load_pressure(load_fraction)
            print(f"   ...Simulated load fraction: {load_fraction:.2f}")

            # Check if refinement is needed.
            self.maybe_refine_capacity()

            # Simulate running tasks (sleep for demonstration).
            time.sleep(0.5)
            i += batch_size

        print("All tasks completed with the grains-coded finite approach.")


def example_usage():
    # Create example tasks.
    tasks = [f"task_{n}" for n in range(25)]
    manager = GrainsConcurrencyManager(
        initial_concurrency=3, 
        max_refine_factor=5,    
        refine_threshold=0.6,   
        grains_n=20
    )
    manager.run_tasks(tasks)

if __name__ == "__main__":
    example_usage()