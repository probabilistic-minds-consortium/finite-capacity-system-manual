import random

def lumps_random_step_sqrtN(N=2, 
                            INITIAL_K=14, 
                            INITIAL_M=10, 
                            MAX_CAPACITY=200_000, 
                            EXPANSION_FACTOR=10, 
                            ALLOWED_ITER=1000,
                            verbose=True):
    """
    Approximate sqrt(N) with a lumps-coded approach that uses random steps.
    We'll keep a lumps-coded distribution over {step=-1, step=+1} or bigger steps,
    then sample from it each iteration, check improvement, and adjust probabilities.
    """

    k = INITIAL_K
    M = INITIAL_M
    expansions_used = 0
    iteration_count = 0

    def lumps_error(k, M, N):
        return abs(k*k - N*(M*M))

    # Probability distribution in lumps form: p( step = +1 ) = p_plus / (p_plus + p_minus)
    # We'll start with an even distribution => 5 lumps for +1, 5 lumps for -1 => total 10 lumps
    p_plus = 5
    p_minus = 5
    capacity_probs = 10  # lumps for probability distribution

    err = lumps_error(k, M, N)
    if verbose:
        print(f"Initial: err={err}, x={k}/{M} ~ {float(k)/float(M):.9f}")

    while iteration_count < ALLOWED_ITER:
        iteration_count += 1

        # 1) Convert lumps-coded distribution to a random step
        total_p = p_plus + p_minus
        if total_p == 0:
            # degenerate case
            p_plus = 1
            p_minus = 1
            total_p = 2

        # Sample an integer in [0, total_p-1]
        draw = random.randint(0, total_p - 1)
        step = +1 if draw < p_plus else -1

        # 2) Attempt step
        new_k = k + step
        if new_k < 0:
            new_k = 0  # avoid negative lumps
        new_err = lumps_error(new_k, M, N)

        # 3) Evaluate improvement
        if new_err < err:
            # success => keep the step
            k, err = new_k, new_err
            if verbose:
                print(f"Iter={iteration_count}: step={step}, err={err}, x={k}/{M} ~ {float(k)/float(M):.9f}")
            # Possibly increase lumps for that step
            if step == +1:
                p_plus = min(p_plus + 1, capacity_probs)  # or some bigger increment
            else:
                p_minus = min(p_minus + 1, capacity_probs)
        else:
            # no improvement => reduce lumps for that step
            if step == +1 and p_plus > 0:
                p_plus -= 1
            elif step == -1 and p_minus > 0:
                p_minus -= 1

            # If we are stuck or distribution collapses, consider capacity expansion
            if p_plus + p_minus < 2:
                if M < MAX_CAPACITY:
                    M_old = M
                    M *= EXPANSION_FACTOR
                    expansions_used += 1
                    k = int(round(k * M / M_old))
                    err = lumps_error(k, M, N)
                    p_plus, p_minus = 5, 5  # reset probability lumps
                    if verbose:
                        print(f"--- Expanding capacity => M={M}, k={k}, err={err} ---")
                else:
                    # max capacity reached
                    if verbose:
                        print(f"[STOP] Max capacity={M}, err={err}, x={k}/{M}")
                    break

        if err == 0:
            if verbose:
                print(f"[STOP] Perfect lumps-coded sqrt({N}): x={k}/{M} ~ {float(k)/float(M):.9f}")
            break

    return k, M, err, expansions_used, iteration_count

# Quick test
if __name__ == "__main__":
    out = lumps_random_step_sqrtN(N=2, verbose=True)
    print("Final Result:", out)