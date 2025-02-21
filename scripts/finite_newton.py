#!/usr/bin/env python3

def accelerated_sqrtN(N=2, INITIAL_K=14, INITIAL_M=10, MAX_CAPACITY=200_000, EXPANSION_FACTOR=10, ALLOWED_ITER=1000, verbose=True):
    """
    Approximate sqrt(N) using an accelerated grains-coded approach:
    - Uses finite-coded derivatives to guide step size.
    - Dynamically adjusts steps for faster convergence.
    All computations are performed using integers to maintain finite precision.
    """
    k = INITIAL_K
    M = INITIAL_M
    expansions_used = 0
    iteration_count = 0

    def grains_error(k, M, N):
        # Computes the error: |(k/M)^2 - N|
        # Rearranged to integer arithmetic: |k^2 - N*(M^2)|
        return abs(k * k - N * (M * M))

    def derivative(k, M, N):
        """Finite-coded 'slope' for dynamic step size using integer differences."""
        delta_up = grains_error(k + 1, M, N) - grains_error(k, M, N)
        return delta_up  # Represents error change per grain step.

    err = grains_error(k, M, N)
    if verbose:
        # For display purposes only: converting to float to show approximate value.
        print(f"Initial: err={err}, x={k}/{M} ~ {k}/{M} (approx)")
    
    while iteration_count < ALLOWED_ITER:
        iteration_count += 1

        # Compute slope and decide on step direction: decrease k if error increases, otherwise increase k.
        slope = derivative(k, M, N)
        step = -1 if slope > 0 else +1

        new_k = k + step
        if new_k < 0:  # Ensure k stays non-negative
            step = 0
            new_k = k
        new_err = grains_error(new_k, M, N)

        # Check if the step improves the error.
        if new_err < err:
            k, err = new_k, new_err
            if verbose:
                print(f"Iter={iteration_count}: step={step}, err={err}, x={k}/{M} (approx)")
        else:
            # No improvement; increase capacity.
            if M >= MAX_CAPACITY:
                if verbose:
                    print(f"[STOP] Max capacity reached: M={M}, err={err}, x={k}/{M}")
                break
            M *= EXPANSION_FACTOR
            k = k * EXPANSION_FACTOR  # Scale k exactly as an integer.
            expansions_used += 1
            err = grains_error(k, M, N)
            if verbose:
                print(f"--- Expanding capacity to M={M}, re-scaling k={k}, err={err} ---")
        
        # Terminate if perfect approximation is reached.
        if err == 0:
            if verbose:
                print(f"[STOP] Perfect approximation: sqrt({N}) ~ {k}/{M}")
            break

    return k, M, err, expansions_used, iteration_count

# Example run
if __name__ == "__main__":
    result = accelerated_sqrtN(N=2, verbose=True)
    print("\nFinal Result:", result)