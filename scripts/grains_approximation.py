#!/usr/bin/env python3
"""
Grains-Coded Approximation for Square Roots with Random Steps.

This script approximates sqrt(N) using a grains-coded integer approach.
All calculations are performed using exact, finite integer arithmetic.
"""

import random

def grains_error(k, M, N):
    return abs(k * k - N * (M * M))

def try_step(k, M, step, N):
    new_k = k + step
    if new_k < 0:
        return (k, grains_error(k, M, N))
    new_err = grains_error(new_k, M, N)
    return (new_k, new_err)

def print_state(iteration, step, err, k, M):
    # Print as fraction string "k/M" (exact representation)
    print(f"Iter={iteration}, step={step}, err={err}, x = {k}/{M}")

def grains_random_step_sqrtN(N=2, 
                              INITIAL_K=14, 
                              INITIAL_M=10, 
                              MAX_CAPACITY=200_000, 
                              EXPANSION_FACTOR=10, 
                              ALLOWED_ITER=1000,
                              verbose=True):
    k = INITIAL_K
    M = INITIAL_M
    expansions_used = 0
    iteration_count = 0

    p_plus = 5
    p_minus = 5
    capacity_probs = 10

    err = grains_error(k, M, N)
    if verbose:
        print(f"Iter=1, err={err}, x = {k}/{M}")

    while iteration_count < ALLOWED_ITER:
        iteration_count += 1
        total_p = p_plus + p_minus
        if total_p == 0:
            p_plus, p_minus = 1, 1
            total_p = 2

        draw = random.randint(0, total_p - 1)
        step = +1 if draw < p_plus else -1
        new_k, new_err = try_step(k, M, step, N)

        if new_err < err:
            k, err = new_k, new_err
            if verbose:
                print_state(iteration_count, step, err, k, M)
            if step == +1:
                p_plus = min(p_plus + 1, capacity_probs)
            else:
                p_minus = min(p_minus + 1, capacity_probs)
        else:
            if step == +1 and p_plus > 0:
                p_plus -= 1
            elif step == -1 and p_minus > 0:
                p_minus -= 1

            if p_plus + p_minus < 2:
                if M >= MAX_CAPACITY:
                    if verbose:
                        print(f"[STOP] Max capacity reached: M={M}, err={err}, x = {k}/{M}")
                    return (k, M, err, expansions_used, iteration_count)
                else:
                    M_old = M
                    M *= EXPANSION_FACTOR
                    expansions_used += 1
                    k = (k * M + M_old // 2) // M_old  # exact rescaling (rounding)
                    err = grains_error(k, M, N)
                    p_plus, p_minus = 5, 5
                    if verbose:
                        print(f"--- Expanding capacity to M={M}, re-scaled k={k}, err={err}, x = {k}/{M} ---")
                    continue
            else:
                k, err = new_k, new_err
                if verbose:
                    print_state(iteration_count, step, err, k, M)

        if err == 0:
            if verbose:
                print(f"[STOP] Exact approximation reached: x = {k}/{M}")
            return (k, M, err, expansions_used, iteration_count)

    if verbose:
        print(f"[STOP] Exceeded ALLOWED_ITER={ALLOWED_ITER}, err={err}, x = {k}/{M}")
    return (k, M, err, expansions_used, iteration_count)

def approx_sqrtN_grains(N=2,
                        INITIAL_K=14,
                        INITIAL_M=10,
                        MAX_CAPACITY=200_000,
                        EXPANSION_FACTOR=10,
                        ALLOWED_ITER=1000,
                        verbose=True):
    # A wrapper that calls grains_random_step_sqrtN
    return grains_random_step_sqrtN(N, INITIAL_K, INITIAL_M, MAX_CAPACITY, EXPANSION_FACTOR, ALLOWED_ITER, verbose)

def main():
    print("Enter the target integer for square root approximation:")
    try:
        target_number = int(input().strip())
        if target_number < 2:
            print("Please enter an integer >= 2.")
            return
    except Exception as e:
        print("Invalid input. Please enter an integer.")
        return

    result = approx_sqrtN_grains(N=target_number, verbose=True)
    k, M, err, expansions, iters = result
    print("\nFinal Approximation in grains-coded form:")
    print(f"  sqrt({target_number}) ~ {k}/{M} (exact fraction), error = {err}")
    print(f"  Capacity expansions used: {expansions}, total iterations: {iters}")

if __name__ == "__main__":
    main()