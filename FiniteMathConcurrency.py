#!/usr/bin/env python3

"""
Lumps-Coded Concurrency Manager:
An example script demonstrating how to manage concurrency 
in a microservices or tasks environment using lumps-coded (finite) increments,
dynamic vantage refinement, and discrete scaling steps.

Key Points:
  - concurrency_limit is stored as a lumps-coded fraction k/N or a vantage-based integer.
  - capacity refinements occur in leaps (e.g., multiply concurrency by an integer factor).
  - we track 'load pressure' or 'error rate' lumps-coded as well.
  - we never let concurrency expansion be infinite—bounded steps only!
  - safe and stable: each vantage step is validated, no illusions of continuous scaling.
"""

import math
import random
import time

# We'll define a vantage: concurrency has a "current capacity" vantage_c
# which is an integer representing how many tasks we can run in parallel.
# If vantage_c is too small, we refine by an integer factor (like lumps-coded expansions).
# We'll also lumps-code the load pressure as an integer from 0..N.

class LumpsConcurrencyManager:
    def __init__(self, 
                 initial_concurrency=5,   # our vantage_c
                 max_refine_factor=10,     # how much we multiply vantage_c in extreme
                 refine_threshold=0.7,     # if load_pressure fraction > refine_threshold, we refine
                 lumps_n=100):
        """
        initial_concurrency: starting vantage concurrency
        max_refine_factor: largest factor for concurrency expansions
        refine_threshold: lumps-coded fraction in [0,1], if load pressure surpasses it, we refine
        lumps_n: the lumps denominator for load pressure
        """
        self.concurrency = initial_concurrency
        self.max_refine_factor = max_refine_factor
        self.refine_threshold = refine_threshold
        self.lumps_n = lumps_n

        # We store load pressure lumps as an integer 0..lumps_n
        # e.g. a fraction x in [0,1] => lumps_load = int(x * lumps_n)
        self.lumps_load = 0

    def compute_load_fraction(self):
        """Return the lumps-coded load as a fraction lumps_load / lumps_n."""
        return self.lumps_load / float(self.lumps_n)

    def adjust_load_pressure(self, fraction):
        """
        fraction in [0,1] => lumps_load = int(round(fraction * lumps_n)).
        This might come from actual metrics: CPU usage, queue depth, error rate, etc.
        """
        lumps_val = int(round(fraction * self.lumps_n))
        # clamp it
        lumps_val = max(0, min(lumps_val, self.lumps_n))
        self.lumps_load = lumps_val

    def maybe_refine_capacity(self):
        """
        If load fraction > refine_threshold, we consider refining concurrency
        by a discrete integer factor, up to max_refine_factor.
        We'll choose a minimal factor that keeps load below threshold, if possible.
        """
        current_fraction = self.compute_load_fraction()
        if current_fraction > self.refine_threshold:
            # we refine concurrency in lumps-coded step: concurrency *= factor
            # But factor is an integer from 2..max_refine_factor
            # We'll pick the smallest factor that (roughly) would bring load fraction under threshold
            # approximate needed factor = current_fraction / refine_threshold
            factor_guess = math.ceil(current_fraction / self.refine_threshold)
            factor_guess = max(2, min(factor_guess, self.max_refine_factor))
            
            old_concurrency = self.concurrency
            self.concurrency *= factor_guess
            print(f"[REFINE] Concurrency vantage refined: {old_concurrency} -> {self.concurrency} (factor={factor_guess})")

    def run_tasks(self, tasks):
        """
        Simulate running tasks with current concurrency vantage.
        We'll chunk tasks into lumps-coded concurrency batches.
        Meanwhile, we'll simulate random load pressure changes 
        and see if we refine in the process.
        """
        i = 0
        total_tasks = len(tasks)
        while i < total_tasks:
            # run a batch of tasks = concurrency
            batch_size = min(self.concurrency, total_tasks - i)
            batch_tasks = tasks[i:i+batch_size]
            print(f"Running batch {i}..{i+batch_size-1} with concurrency={self.concurrency}")
            
            # simulate load
            # e.g. fraction ~ random, or we check how "big" the tasks are
            # For demonstration, we'll do something naive:
            load_fraction = 0.3 + 0.5 * random.random()  # in [0.3..0.8]
            self.adjust_load_pressure(load_fraction)
            print(f"   ...Load fraction simulated => {load_fraction:.2f}")

            # maybe refine
            self.maybe_refine_capacity()

            # Fake "running" them
            time.sleep(0.5)
            i += batch_size

        print("All tasks completed with lumps-coded concurrency approach.")


def example_usage():
    # Example tasks
    tasks = [f"task_{n}" for n in range(25)]

    manager = LumpsConcurrencyManager(
        initial_concurrency=3, 
        max_refine_factor=5,    
        refine_threshold=0.6,   
        lumps_n=20
    )

    manager.run_tasks(tasks)

if __name__ == "__main__":
    example_usage()