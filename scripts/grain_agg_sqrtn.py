#!/usr/bin/env python3

def lumps_error(k, M, N):
    """
    Compute the lumps-coded difference: |k^2 - N*M^2|.
    Interprets x = k/M; we want to measure |x^2 - N|.
    That is effectively |(k^2 / M^2) - N| in integer-coded form => |k^2 - N*M^2|.
    """
    return abs(k*k - N*(M*M))

def lumps_decimal(k, M):
    """For display only: convert lumps-coded (k, M) to float if M != 0."""
    return float(k)/float(M) if M != 0 else 0.0

def try_step(k, M, step, N):
    """
    Attempt a small lumps step: new_k = k + step
    Return (new_k, new_err).
    We don't allow negative k.
    """
    new_k = k + step
    if new_k < 0:
        # skip negative
        return (k, lumps_error(k, M, N))
    new_err = lumps_error(new_k, M, N)
    return (new_k, new_err)

def approx_sqrtN_lumps(N=2,
                       INITIAL_K=14,
                       INITIAL_M=10,
                       MAX_CAPACITY=200_000,
                       EXPANSION_FACTOR=10,
                       ALLOWED_ITER=1000,
                       verbose=True):
    """
    Approximate sqrt(N) using lumps-coded integer approach:
      - Start with x = K/M.
      - Each iteration tries x +/- (1/M) if it reduces lumps_error.
      - If no improvement, we expand capacity (M *= EXPANSION_FACTOR) until MAX_CAPACITY or we converge.
    Returns final (k, M, err, expansions, iteration_count).
    """
    k = INITIAL_K
    M = INITIAL_M
    expansions_used = 0
    iteration_count = 0

    err = lumps_error(k, M, N)
    if verbose:
        print(f"Iter=1 no improvement, err={err}, x={k}/{M} ~ {lumps_decimal(k,M):.9f}")

    while iteration_count < ALLOWED_ITER:
        iteration_count += 1

        # Test +1 lumps step
        new_k_plus, err_plus = try_step(k, M, +1, N)
        # Test -1 lumps step
        new_k_minus, err_minus = try_step(k, M, -1, N)

        best_err = err
        best_k = k
        step_chosen = "no improvement"

        # check if +1 lumps helps
        if err_plus < best_err:
            best_err = err_plus
            best_k = new_k_plus
            step_chosen = "+1"

        # check if -1 lumps helps
        if err_minus < best_err:
            best_err = err_minus
            best_k = new_k_minus
            step_chosen = "-1"

        if best_err >= err:
            # No local improvement => expand capacity if possible
            if M >= MAX_CAPACITY:
                # done
                if verbose:
                    print(f"[STOP] Reached max capacity {M}, lumps_error={err}, x={k}/{M} ~ {lumps_decimal(k,M):.9f}")
                return (k, M, err, expansions_used, iteration_count)
            else:
                # expand capacity
                newM = M * EXPANSION_FACTOR
                if newM > MAX_CAPACITY:
                    newM = MAX_CAPACITY
                expansions_used += 1
                newK = int(round(k * newM / M))
                if verbose:
                    print(f"--- Expanding capacity to M={newM}, re-scale k => {newK}, new x={newK}/{newM} ~ {float(newK)/float(newM):.9f} ---")
                k, M = newK, newM
                err = lumps_error(k, M, N)
                continue
        else:
            # we do the best step
            k, err = best_k, best_err
            if verbose:
                # iteration_count+1 => next iteration # for printing
                print(f"Iter={iteration_count+1}  step={step_chosen} err:{err},  x:{k}/{M} -> {k}/{M}")

        if err == 0:
            # Perfect lumps-coded representation found? 
            if verbose:
                print(f"[STOP] lumps_error=0 => x={k}/{M} ~ {lumps_decimal(k,M):.9f}")
            return (k, M, err, expansions_used, iteration_count)

    # Exceeded ALLOWED_ITER
    if verbose:
        print(f"[STOP] Exceeded ALLOWED_ITER={ALLOWED_ITER}, lumps_error={err}, x={k}/{M} ~ {lumps_decimal(k,M):.9f}")
    return (k, M, err, expansions_used, iteration_count)

def main():
    print("Which integer do you want to approximate the square root for? ")
    user_in = input().strip()
    try:
        target_number = int(user_in)
        if target_number < 2:
            print("Please enter an integer >= 2.")
            return
    except:
        print("Invalid input. Please enter an integer.")
        return

    (k, M, err, expansions, iters) = approx_sqrtN_lumps(
        N=target_number,
        INITIAL_K=14,
        INITIAL_M=10,
        MAX_CAPACITY=200000,
        EXPANSION_FACTOR=10,
        ALLOWED_ITER=1000,
        verbose=True
    )

    final_approx = lumps_decimal(k, M)
    print("\nFinal Approximation in lumps-coded form:")
    print(f"  sqrt({target_number}) ~ {k}/{M} = {final_approx:.9f}, lumps_error={err}")
    print(f"  capacity expansions used: {expansions}, total iterations: {iters}")

if __name__ == "__main__":
    main()