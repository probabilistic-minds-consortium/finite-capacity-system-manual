def accelerated_sqrtN(N=2, INITIAL_K=14, INITIAL_M=10, MAX_CAPACITY=200_000, EXPANSION_FACTOR=10, ALLOWED_ITER=1000, verbose=True):
    """
    Approximate sqrt(N) using an accelerated lumps-coded approach:
    - Uses finite-coded derivatives to guide step size.
    - Dynamically adjusts steps for faster convergence.
    """
    k = INITIAL_K
    M = INITIAL_M
    expansions_used = 0
    iteration_count = 0

    def lumps_error(k, M, N):
        return abs(k*k - N*(M*M))

    def derivative(k, M, N):
        """Finite-coded 'slope' for dynamic step size."""
        delta_up = lumps_error(k + 1, M, N) - lumps_error(k, M, N)
        return delta_up  # Represents error change per lump step.

    err = lumps_error(k, M, N)
    if verbose:
        print(f"Initial: err={err}, x={k}/{M} ~ {float(k)/float(M):.9f}")

    while iteration_count < ALLOWED_ITER:
        iteration_count += 1

        # Compute slope and decide on step direction
        slope = derivative(k, M, N)
        step = -1 if slope > 0 else +1  # If slope positive, decrease; otherwise increase.

        # Try the step
        new_k = k + step
        if new_k < 0:  # Ensure k stays non-negative
            step = 0
        new_err = lumps_error(new_k, M, N)

        # Check improvement
        if new_err < err:
            k, err = new_k, new_err
            if verbose:
                print(f"Iter={iteration_count}: step={step}, err={err}, x={k}/{M} ~ {float(k)/float(M):.9f}")
        else:
            # No improvement; expand capacity
            if M >= MAX_CAPACITY:
                if verbose:
                    print(f"[STOP] Max capacity reached: M={M}, err={err}, x={k}/{M}")
                break
            M *= EXPANSION_FACTOR
            k = int(round(k * EXPANSION_FACTOR))
            expansions_used += 1
            err = lumps_error(k, M, N)
            if verbose:
                print(f"--- Expanding capacity to M={M}, re-scaling k={k}, err={err} ---")

        if err == 0:
            if verbose:
                print(f"[STOP] Perfect approximation: sqrt({N}) ~ {k}/{M} = {float(k)/float(M):.9f}")
            break

    return k, M, err, expansions_used, iteration_count

# Example run
if __name__ == "__main__":
    result = accelerated_sqrtN(N=2, verbose=True)
    print("\nFinal Result:", result)