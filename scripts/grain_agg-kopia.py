def lumps_error(k, M):
    """
    Compute the lumps-coded difference |k^2 - 2*(M^2)|.
    This is equivalent to |(k^2 / M^2) - 2| in integer-coded form.
    All computations are strictly finite.
    """
    return abs(k * k - 2 * (M * M))

def lumps_decimal(k, M):
    """
    For display only: convert lumps-coded (k, M) to a decimal approximation.
    """
    return float(k) / float(M) if M != 0 else 0.0

def try_step(k, M, step):
    """
    Attempt a small lumps step: new_k = k + step.
    Return (new_k, new_err) using finite, integer arithmetic.
    Negative k values are not allowed.
    """
    new_k = k + step
    if new_k < 0:
        # Skip negative values; maintain finite, non-negative representation.
        return (k, lumps_error(k, M))
    new_err = lumps_error(new_k, M)
    return (new_k, new_err)

def approx_sqrt2_lumps(
    INITIAL_K=14,
    INITIAL_M=10,
    MAX_CAPACITY=200_000,
    EXPANSION_FACTOR=10,
    ALLOWED_ITER=1000,
    verbose=True
):
    """
    Approximate sqrt(2) using a lumps-coded integer approach:
      1) Start with x = k/M.
      2) Each iteration tries to adjust x by +/- (1/M) if it reduces the lumps_error.
      3) If no local improvement is found, expand capacity by multiplying M by an integer factor (EXPANSION_FACTOR),
         up to a maximum of MAX_CAPACITY.
    
    All calculations are performed using finite, integer arithmetic—no reference to infinity.
    
    Returns final (k, M, lumps_error, expansions_used, iteration_count).
    """
    k = INITIAL_K
    M = INITIAL_M
    expansions_used = 0
    iteration_count = 0

    err = lumps_error(k, M)
    if verbose:
        print(f"Iter=1, no improvement, err={err}, x={k}/{M} ~ {lumps_decimal(k, M):.9f}")

    while iteration_count < ALLOWED_ITER:
        iteration_count += 1

        # Try a +1 step
        new_k_plus, err_plus = try_step(k, M, +1)
        # Try a -1 step
        new_k_minus, err_minus = try_step(k, M, -1)

        best_err = err
        best_k = k
        step_chosen = "no improvement"

        if err_plus < best_err:
            best_err = err_plus
            best_k = new_k_plus
            step_chosen = "+1"

        if (err_minus < best_err) and (new_k_minus >= 0):
            best_err = err_minus
            best_k = new_k_minus
            step_chosen = "-1"

        if best_err >= err:
            # No local improvement; try capacity expansion
            if M >= MAX_CAPACITY:
                if verbose:
                    print(f"[STOP] Reached max capacity {M}, lumps_error={err}, x={k}/{M} ~ {lumps_decimal(k, M):.9f}\n")
                return (k, M, err, expansions_used, iteration_count)
            else:
                newM = M * EXPANSION_FACTOR
                if newM > MAX_CAPACITY:
                    newM = MAX_CAPACITY
                expansions_used += 1
                newK = int(round(k * newM / M))
                if verbose:
                    print(f"--- Expanding capacity to M={newM}, re-scaling k => {newK}, new x={newK}/{newM} ~ {float(newK)/float(newM):.9f} ---")
                k, M = newK, newM
                err = lumps_error(k, M)
                continue
        else:
            # Accept the best step found
            k, err = best_k, best_err
            if verbose:
                print(f"Iter={iteration_count+1}, step={step_chosen}, err={err}, x={k}/{M}")

        if err == 0:
            if verbose:
                print(f"[STOP] Exact approximation reached: x={k}/{M} ~ {lumps_decimal(k, M):.9f}")
            return (k, M, err, expansions_used, iteration_count)

    if verbose:
        print(f"[STOP] Exceeded ALLOWED_ITER={ALLOWED_ITER}, lumps_error={err}, x={k}/{M} ~ {lumps_decimal(k, M):.9f}")
    return (k, M, err, expansions_used, iteration_count)

def main():
    (k, M, err, expansions, iters) = approx_sqrt2_lumps(
        INITIAL_K=14,
        INITIAL_M=10,
        MAX_CAPACITY=200_000,
        EXPANSION_FACTOR=10,
        ALLOWED_ITER=1000,
        verbose=True
    )
    print("\nFinal Approximation in lumps-coded form:")
    print(f"x = {k}/{M} ~ {float(k)/float(M):.9f}, lumps_error={err}")
    print(f"Capacity expansions used: {expansions}, total iterations: {iters}")

if __name__ == "__main__":
    main()