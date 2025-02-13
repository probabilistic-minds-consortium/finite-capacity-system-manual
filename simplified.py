import random

def lumps_random_step_sqrtN(N=2, 
                            INITIAL_K=14, 
                            INITIAL_M=10, 
                            MAX_CAPACITY=200_000, 
                            EXPANSION_FACTOR=10, 
                            ALLOWED_ITER=1000,
                            STUCK_THRESHOLD=50,
                            verbose=True):
    """
    Approximate sqrt(N) with a lumps-coded approach that uses random steps.
    
    We keep a lumps-coded probability distribution over step directions:
      p(+1) = p_plus / (p_plus + p_minus)
      p(-1) = p_minus / (p_plus + p_minus)
    
    If a step improves the lumps_error, we do it, and reward that direction by 
    incrementing its lumps. If not, we penalize by decrementing lumps for that direction.
    
    STUCK_THRESHOLD: if we go too many iterations without improvement, 
    we forcibly expand capacity or break.
    """

    k = INITIAL_K
    M = INITIAL_M
    expansions_used = 0
    iteration_count = 0

    # lumps-coded distribution over step=+1 or step=-1
    p_plus = 5
    p_minus = 5

    def lumps_error(k, M, N):
        return abs(k*k - N*(M*M))

    err = lumps_error(k, M, N)
    best_err = err
    if verbose:
        print(f"Initial: err={err}, x={k}/{M} ~ {float(k)/float(M):.9f}")

    # for tracking "no improvement" consecutive
    no_improvement_count = 0

    while iteration_count < ALLOWED_ITER:
        iteration_count += 1

        # Construct the lumps-coded distribution for steps
        p_total = p_plus + p_minus
        if p_total == 0:  # degenerate, reset
            p_plus, p_minus = 5, 5
            p_total = 10

        draw = random.randint(0, p_total - 1)
        step = +1 if draw < p_plus else -1

        # Proposed next k
        new_k = k + step
        if new_k < 0:
            new_k = 0  # can't be negative lumps

        new_err = lumps_error(new_k, M, N)

        if new_err < err:
            # improvement => accept
            k, err = new_k, new_err
            if step == +1:
                p_plus = min(p_plus + 1, 100)   # clamp lumps for distribution
            else:
                p_minus = min(p_minus + 1, 100)
            no_improvement_count = 0

            if verbose:
                print(f"Iter={iteration_count}: step={step}, err={err}, x={k}/{M} ~ {float(k)/float(M):.9f}")
        else:
            # no improvement => penalize lumps for that step
            no_improvement_count += 1
            if step == +1 and p_plus > 1:
                p_plus -= 1
            elif step == -1 and p_minus > 1:
                p_minus -= 1

            # If we have repeatedly not improved, try capacity expansion or exit
            if no_improvement_count >= STUCK_THRESHOLD:
                if M >= MAX_CAPACITY:
                    if verbose:
                        print(f"[STOP] Max capacity reached => M={M}, err={err}, x={k}/{M}")
                    break
                oldM = M
                M = min(M * EXPANSION_FACTOR, MAX_CAPACITY)
                expansions_used += 1
                # rescale k
                k = int(round(k * M / oldM))
                err = lumps_error(k, M, N)
                p_plus, p_minus = 5, 5  # reset lumps distribution
                no_improvement_count = 0
                if verbose:
                    print(f"--- Expand capacity => M={M}, k={k}, err={err} ---")

        if err == 0:
            if verbose:
                print(f"[STOP] Perfect lumps-coded sqrt({N}): x={k}/{M} ~ {float(k)/float(M):.9f}")
            break

        # track best
        if err < best_err:
            best_err = err

    return k, M, err, expansions_used, iteration_count


if __name__ == "__main__":
    result = lumps_random_step_sqrtN(N=2, verbose=True)
    print("\nFinal Result:", result)