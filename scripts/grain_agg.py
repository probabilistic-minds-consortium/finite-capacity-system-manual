#!/usr/bin/env python3
import math

def lumps_error(k, M):
    """
    Compute the lumps-coded difference |k^2 - 2*M^2|.
    This is effectively |(k^2 / M^2) - 2| in 'integer-coded' form.
    """
    return abs(k*k - 2*(M*M))

def lumps_decimal(k, M):
    """
    For display only: convert lumps-coded (k, M) to float.
    """
    return float(k)/float(M) if M != 0 else 0.0

def try_step(k, M, step):
    """
    Attempt a small lumps step:  new_k = k + step
    Return (new_k, new_err).
    """
    new_k = k + step
    if new_k < 0: 
        # can't have negative k in this approach; skip
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
    Approximate sqrt(2) using lumps-coded integer approach:
      1) Start with x = K/M
      2) Each iteration tries x+1/M or x-1/M if it reduces lumps_error.
      3) If no improvement, expand capacity up to MAX_CAPACITY.
    
    Returns final (k, M, lumps_err, expansions, iterations).
    """
    k = INITIAL_K
    M = INITIAL_M
    expansions_used = 0
    iteration_count = 0

    # Calculate initial error
    err = lumps_error(k, M)

    if verbose:
        print(f"Iter=1 no improvement, err={err}, x={k}/{M} ~ {lumps_decimal(k, M):.9f}")

    while iteration_count < ALLOWED_ITER:
        iteration_count += 1
        # Attempt a +1 lumps step
        new_k_plus, err_plus = try_step(k, M, +1)
        # Attempt a -1 lumps step (only if k>1, so it doesn't go negative)
        new_k_minus, err_minus = try_step(k, M, -1)

        best_err = err
        best_k = k
        step_chosen = "no improvement"

        # See which direction helps
        if err_plus < best_err:
            best_err = err_plus
            best_k = new_k_plus
            step_chosen = "+1"

        if (err_minus < best_err) and (new_k_minus >= 0):
            best_err = err_minus
            best_k = new_k_minus
            step_chosen = "-1"

        # If we found no improvement, try capacity expansion
        if best_err >= err:
            # no local improvement
            if M >= MAX_CAPACITY:
                # can't expand further, we stop
                if verbose:
                    print(f"[STOP] Reached max capacity {M}, lumps_error={err}, x={k}/{M} ~ {lumps_decimal(k,M):.9f}\n")
                return (k, M, err, expansions_used, iteration_count)
            else:
                # Expand capacity
                newM = M * EXPANSION_FACTOR
                if newM > MAX_CAPACITY:
                    newM = MAX_CAPACITY
                expansions_used += 1

                # Rescale k
                newK = int(round(k * newM / M))

                if verbose:
                    print(f"--- Expanding capacity to M={newM}, re-scale k => {newK}, new x={newK}/{newM} ~ {float(newK)/float(newM):.9f} ---")

                k, M = newK, newM
                err = lumps_error(k, M)
                continue  # next iteration
        else:
            # We accepted either +1 or -1 lumps step
            k, err = best_k, best_err
            if verbose:
                print(f"Iter={iteration_count+1}  step={step_chosen} err:{err},  x:{k}/{M} -> {k}/{M}")
            
        # If the lumps error is extremely small, we might stop
        if err == 0:
            # We found an exact lumps-coded representation of sqrt(2)? Unlikely, but let's just break
            if verbose:
                print(f"[STOP] lumps_error=0 => x={k}/{M} ~ {lumps_decimal(k,M):.9f}")
            return (k, M, err, expansions_used, iteration_count)
    # If we exceed ALLOWED_ITER
    if verbose:
        print(f"[STOP] Exceeded ALLOWED_ITER={ALLOWED_ITER}, lumps_error={err}, x={k}/{M} ~ {lumps_decimal(k,M):.9f}")
    return (k, M, err, expansions_used, iteration_count)

def main():
    # Very basic "main" with some default or custom parameters
    # You can edit these or parse from sys.argv if you prefer
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