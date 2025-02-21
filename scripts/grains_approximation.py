#!/usr/bin/env python3

import random

def grains_error(k, M, N):
    """
    Compute the grains-coded difference: |k^2 - N*(M^2)|.
    This is equivalent to measuring |(k^2 / M^2) - N| in a purely integer-coded form.
    """
    return abs(k * k - N * (M * M))

def grains_decimal(k, M):
    """
    For display only: convert the grains-coded (k, M) representation to a decimal approximation.
    """
    return float(k) / float(M) if M != 0 else 0.0

def grains_try_step(k, M, step, N):
    """
    Attempt a small grains step: new_k = k + step.
    Return (new_k, new_err). Negative k values are disallowed.
    """
    new_k = k + step
    if new_k < 0:
        # Cannot have negative grains; return current state.
        return (k, grains_error(k, M, N))
    new_err = grains_error(new_k, M, N)
    return (new_k, new_err)

def grains_random_step_sqrtN(N=2, 
                              INITIAL_K=14, 
                              INITIAL_M=10, 
                              MAX_CAPACITY=200_000, 
                              EXPANSION_FACTOR=10, 
                              ALLOWED_ITER=1000,
                              verbose=True):
    """
    Approximate sqrt(N) using a grains-coded approach with random steps.
    
    This function uses a grains-coded probability distribution over steps (+1 or -1).
    Each iteration samples a step, applies it, evaluates improvement via grains_error,
    and adjusts the grains-coded probabilities accordingly.
    
    Key points:
      - All operations use exact, finite integer arithmetic.
      - The probability distribution for the step is stored as grains (e.g., p(+1) and p(-1))
        out of a finite capacity.
      - If no local improvement is found, the system expands capacity by an integer factor,
        up to MAX_CAPACITY.
    
    Returns a tuple: (k, M, grains_error, expansions_used, iteration_count).
    """
    k = INITIAL_K
    M = INITIAL_M
    expansions_used = 0
    iteration_count = 0

    # Initialize probability distribution for steps:
    # p( step = +1 ) = p_plus / (p_plus + p_minus)
    # Start with an even distribution: 5 grains for +1, 5 grains for -1.
    p_plus = 5
    p_minus = 5
    capacity_probs = 10  # Total grains for the probability distribution.

    err = grains_error(k, M, N)
    if verbose:
        print(f"Initial: err={err}, x={k}/{M} ~ {grains_decimal(k, M):.9f}")

    while iteration_count < ALLOWED_ITER:
        iteration_count += 1

        # 1) Convert the grains-coded distribution to a random step.
        total_p = p_plus + p_minus
        if total_p == 0:
            # Reset in degenerate case.
            p_plus = 1
            p_minus = 1
            total_p = 2

        draw = random.randint(0, total_p - 1)
        step = +1 if draw < p_plus else -1

        # 2) Attempt the step.
        new_k, new_err = grains_try_step(k, M, step, N)

        # 3) Evaluate improvement.
        if new_err < err:
            # Accept the step.
            k, err = new_k, new_err
            if verbose:
                print(f"Iter={iteration_count}: step={step}, err={err}, x={k}/{M} ~ {grains_decimal(k, M):.9f}")
            # Increase grains for the chosen step, up to capacity.
            if step == +1:
                p_plus = min(p_plus + 1, capacity_probs)
            else:
                p_minus = min(p_minus + 1, capacity_probs)
        else:
            # No improvement: reduce grains for that step.
            if step == +1 and p_plus > 0:
                p_plus -= 1
            elif step == -1 and p_minus > 0:
                p_minus -= 1

            # If the probability distribution collapses, attempt capacity expansion.
            if p_plus + p_minus < 2:
                if M < MAX_CAPACITY:
                    M_old = M
                    M *= EXPANSION_FACTOR
                    expansions_used += 1
                    k = int(round(k * M / M_old))
                    err = grains_error(k, M, N)
                    p_plus, p_minus = 5, 5  # Reset probabilities.
                    if verbose:
                        print(f"--- Expanding capacity: M={M}, re-scaled k={k}, err={err}, new x={k}/{M} ~ {float(k)/float(M):.9f} ---")
                else:
                    if verbose:
                        print(f"[STOP] Max capacity reached: M={M}, err={err}, x={k}/{M} ~ {grains_decimal(k, M):.9f}")
                    break

        if err == 0:
            if verbose:
                print(f"[STOP] Exact grains-coded approximation: x={k}/{M} ~ {grains_decimal(k, M):.9f}")
            break

    if verbose:
        print(f"[STOP] Exceeded ALLOWED_ITER={ALLOWED_ITER}, err={err}, x={k}/{M} ~ {grains_decimal(k, M):.9f}")
    return k, M, err, expansions_used, iteration_count

# Quick test:
if __name__ == "__main__":
    result = grains_random_step_sqrtN(N=2, verbose=True)
    print("Final Result:", result)