#!/usr/bin/env python3
# simplified.py
# Grains-coded approach to approximate sqrt(N) using random steps.
#
# We maintain a grains-coded probability distribution over step directions:
#   p(+1) = p_plus / (p_plus + p_minus)
#   p(-1) = p_minus / (p_plus + p_minus)
#
# On each iteration, we sample a step. If that step improves our grains_error,
# we accept it and reward that step's count; otherwise, we penalize it.
# If too many iterations occur without improvement (STUCK_THRESHOLD),
# we expand capacity (up to MAX_CAPACITY) and rescale k—all using integer arithmetic.
#
# No floating-point operations are used in the core algorithm.

from fractions import Fraction
import random

def grains_error(k, M, N):
    """
    Compute the grains-coded error: |k^2 - N*(M^2)|.
    This represents |(k/M)^2 - N| exactly using integer arithmetic.
    """
    return abs(k * k - N * (M * M))

def grains_fraction_str(k, M):
    """
    For display only: represent the grains-coded value as an exact fraction.
    """
    return str(Fraction(k, M))

def grains_try_step(k, M, step, N):
    """
    Attempt a small grains step: new_k = k + step.
    Return (new_k, new_error). Negative k values are disallowed.
    """
    new_k = k + step
    if new_k < 0:
        return (k, grains_error(k, M, N))
    new_err = grains_error(new_k, M, N)
    return (new_k, new_err)

def grains_random_step_sqrtN(N=2, 
                              INITIAL_K=14, 
                              INITIAL_M=10, 
                              MAX_CAPACITY=200_000, 
                              EXPANSION_FACTOR=10, 
                              ALLOWED_ITER=1000,
                              STUCK_THRESHOLD=50,
                              verbose=True):
    """
    Approximate sqrt(N) using a grains-coded approach with random steps.
    
    We maintain a grains-coded probability distribution over step directions:
      p(+1) = p_plus / (p_plus + p_minus)
      p(-1) = p_minus / (p_plus + p_minus)
    
    If a step reduces the grains_error, we accept it and reward that direction;
    otherwise, we penalize it. If STUCK_THRESHOLD consecutive iterations occur
    without improvement, we expand capacity (up to MAX_CAPACITY) and rescale k.
    
    All operations are performed using strictly finite, integer-based arithmetic.
    """
    k = INITIAL_K
    M = INITIAL_M
    expansions_used = 0
    iteration_count = 0

    # Initialize grains-coded probability distribution over step directions.
    p_plus = 5
    p_minus = 5

    err = grains_error(k, M, N)
    best_err = err
    if verbose:
        print(f"Iter=1, err={err}, x = {k}/{M} ~ {grains_fraction_str(k, M)}")

    no_improvement_count = 0

    while iteration_count < ALLOWED_ITER:
        iteration_count += 1

        # Build the grains-coded distribution for step selection.
        p_total = p_plus + p_minus
        if p_total == 0:
            p_plus, p_minus = 5, 5
            p_total = 10

        draw = random.randint(0, p_total - 1)
        step = +1 if draw < p_plus else -1

        new_k = k + step
        if new_k < 0:
            new_k = 0  # Ensure non-negative.
        new_err = grains_error(new_k, M, N)

        if new_err < err:
            # Improvement: accept the step.
            k, err = new_k, new_err
            if step == +1:
                p_plus = min(p_plus + 1, 100)
            else:
                p_minus = min(p_minus + 1, 100)
            no_improvement_count = 0
            if verbose:
                print(f"Iter={iteration_count}: step={step}, err={err}, x = {k}/{M} ~ {grains_fraction_str(k, M)}")
        else:
            no_improvement_count += 1
            if step == +1 and p_plus > 1:
                p_plus -= 1
            elif step == -1 and p_minus > 1:
                p_minus -= 1

            if no_improvement_count >= STUCK_THRESHOLD:
                if M >= MAX_CAPACITY:
                    if verbose:
                        print(f"[STOP] Max capacity reached: M={M}, err={err}, x = {k}/{M} ~ {grains_fraction_str(k, M)}")
                    break
                old_M = M
                # Expand capacity
                M = min(M * EXPANSION_FACTOR, MAX_CAPACITY)
                expansions_used += 1
                # Rescale k properly with integer rounding:
                # k_new = (k * new_M + old_M // 2) // old_M
                k = (k * M + old_M // 2) // old_M
                err = grains_error(k, M, N)
                p_plus, p_minus = 5, 5  # Reset probability distribution.
                no_improvement_count = 0
                if verbose:
                    print(f"--- Capacity expanded: M={M}, k={k}, err={err}, x = {k}/{M} ~ {grains_fraction_str(k, M)} ---")

        if err == 0:
            if verbose:
                print(f"[STOP] Perfect grains-coded sqrt({N}): x = {k}/{M} ~ {grains_fraction_str(k, M)}")
            break

        if err < best_err:
            best_err = err

    return k, M, err, expansions_used, iteration_count

if __name__ == "__main__":
    result = grains_random_step_sqrtN(N=2, verbose=True)
    print("\nFinal Result:", result)