def grains_error(k, M, N):
    """
    Compute the grains-coded difference: |k^2 - N*(M^2)|.
    This measures the error for approximating sqrt(N) using x = k/M.
    That is, it evaluates |(k^2 / M^2) - N| in an integer-coded form.
    """
    return abs(k * k - N * (M * M))

def grains_decimal(k, M):
    """For display only: convert grains-coded (k, M) to a decimal approximation."""
    return float(k) / float(M) if M != 0 else 0.0

def try_step(k, M, step, N):
    """
    Attempt a small grains step: new_k = k + step.
    Return (new_k, new_err). Negative k values are disallowed.
    """
    new_k = k + step
    if new_k < 0:
        return (k, grains_error(k, M, N))
    new_err = grains_error(new_k, M, N)
    return (new_k, new_err)

def approx_sqrtN_grains(N=2,
                        INITIAL_K=14,
                        INITIAL_M=10,
                        MAX_CAPACITY=200_000,
                        EXPANSION_FACTOR=10,
                        ALLOWED_ITER=1000,
                        verbose=True):
    """
    Approximate sqrt(N) using a grains-coded integer approach:
      - Start with x = k/M.
      - Each iteration tries x +/- (1/M) if it reduces grains_error.
      - If no local improvement is found, expand capacity (M *= EXPANSION_FACTOR) until MAX_CAPACITY is reached.
    Returns final (k, M, err, expansions_used, iteration_count).
    """
    k = INITIAL_K
    M = INITIAL_M
    expansions_used = 0
    iteration_count = 0

    err = grains_error(k, M, N)
    if verbose:
        print(f"Iter=1, err={err}, x={k}/{M} ~ {grains_decimal(k, M):.9f}")

    while iteration_count < ALLOWED_ITER:
        iteration_count += 1

        # Test a step of +1 grains
        new_k_plus, err_plus = try_step(k, M, +1, N)
        # Test a step of -1 grains
        new_k_minus, err_minus = try_step(k, M, -1, N)

        best_err = err
        best_k = k
        step_chosen = "no improvement"

        if err_plus < best_err:
            best_err = err_plus
            best_k = new_k_plus
            step_chosen = "+1"

        if err_minus < best_err:
            best_err = err_minus
            best_k = new_k_minus
            step_chosen = "-1"

        if best_err >= err:
            # No local improvement; attempt to refine capacity
            if M >= MAX_CAPACITY:
                if verbose:
                    print(f"[STOP] Max capacity reached: M={M}, grains_error={err}, x={k}/{M} ~ {grains_decimal(k, M):.9f}")
                return (k, M, err, expansions_used, iteration_count)
            else:
                newM = M * EXPANSION_FACTOR
                if newM > MAX_CAPACITY:
                    newM = MAX_CAPACITY
                expansions_used += 1
                # Rescale k exactly as an integer.
                newK = int(round(k * newM / M))
                if verbose:
                    print(f"--- Expanding capacity to M={newM}, re-scaling k => {newK}, new x={newK}/{newM} ~ {float(newK)/float(newM):.9f} ---")
                k, M = newK, newM
                err = grains_error(k, M, N)
                continue
        else:
            k, err = best_k, best_err
            if verbose:
                print(f"Iter={iteration_count+1}, step={step_chosen}, err={err}, x={k}/{M}")

        if err == 0:
            if verbose:
                print(f"[STOP] Perfect approximation: x={k}/{M} ~ {grains_decimal(k, M):.9f}")
            return (k, M, err, expansions_used, iteration_count)

    if verbose:
        print(f"[STOP] Exceeded ALLOWED_ITER={ALLOWED_ITER}, grains_error={err}, x={k}/{M} ~ {grains_decimal(k, M):.9f}")
    return (k, M, err, expansions_used, iteration_count)

def main():
    print("Which integer do you want to approximate the square root for?")
    user_in = input().strip()
    try:
        target_number = int(user_in)
        if target_number < 2:
            print("Please enter an integer >= 2.")
            return
    except:
        print("Invalid input. Please enter an integer.")
        return

    (k, M, err, expansions, iters) = approx_sqrtN_grains(
        N=target_number,
        INITIAL_K=14,
        INITIAL_M=10,
        MAX_CAPACITY=200000,
        EXPANSION_FACTOR=10,
        ALLOWED_ITER=1000,
        verbose=True
    )

    final_approx = grains_decimal(k, M)
    print("\nFinal Approximation in grains-coded form:")
    print(f"  sqrt({target_number}) ~ {k}/{M} = {final_approx:.9f}, grains_error={err}")
    print(f"  Capacity expansions used: {expansions}, total iterations: {iters}")

if __name__ == "__main__":
    main()