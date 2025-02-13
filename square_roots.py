#!/usr/bin/env python3
"""
Lumps-Based "Neural Net" for Approximating Roots via Discrete Steps.

This updated version includes a user-friendly interface to input:
  - Target number for approximation (e.g., sqrt(2), sqrt(5), etc.).
  - Initial numerator and denominator (k and M).
  - Tolerance for approximation.
  - Maximum number of iterations.

The system works entirely with rational approximations, avoiding floating-point arithmetic for updates.
"""

class EvalLayer:
    def __init__(self, target_num, target_den=1):
        self.tn = target_num
        self.td = target_den

    def square_x(self, k, M):
        return (k * k, M * M)

    def error_abs(self, k2, M2):
        left = k2 * self.td
        right = self.tn * M2
        diff = abs(left - right)
        denom = M2 * self.td
        return diff, denom

    def forward(self, k, M):
        k2, M2 = self.square_x(k, M)
        diff, denom = self.error_abs(k2, M2)
        return k2, M2, diff, denom


class UpdateLayer:
    def __init__(self, eval_layer):
        self.eval_layer = eval_layer

    def measure_error(self, k, M):
        k2, M2, diff, denom = self.eval_layer.forward(k, M)
        return diff, denom

    def forward(self, k, M):
        curr_diff, _ = self.measure_error(k, M)
        best_k = k
        best_diff = curr_diff
        changed = False

        up_k = k + 1
        up_diff, _ = self.measure_error(up_k, M)
        if up_diff < best_diff:
            best_k = up_k
            best_diff = up_diff
            changed = True

        if k > 0:
            dn_k = k - 1
            dn_diff, _ = self.measure_error(dn_k, M)
            if dn_diff < best_diff:
                best_k = dn_k
                best_diff = dn_diff
                changed = True

        return best_k, changed


class CapacityExpandLayer:
    def __init__(self, factor=10):
        self.factor = factor

    def forward(self, k, M):
        return k * self.factor, M * self.factor


def lumps_to_float(k, M):
    return k / M if M != 0 else 0.0


def main():
    print("=== Lumps-Based Approximation for Roots ===")
    target_num = int(input("Enter the target number for the square root (e.g., 2 for sqrt(2)): "))
    init_k = int(input("Enter the initial numerator (e.g., 14 for 1.4): "))
    init_M = int(input("Enter the initial denominator (e.g., 10 for 1.4): "))
    tolerance_num = int(input("Enter the tolerance denominator (e.g., 1000 for 0.001): "))
    max_iter = int(input("Enter the maximum number of iterations: "))

    eval_layer = EvalLayer(target_num=target_num)
    update_layer = UpdateLayer(eval_layer=eval_layer)
    expand_layer = CapacityExpandLayer(factor=10)

    k = init_k
    M = init_M

    for i in range(1, max_iter + 1):
        k2, M2, diff, denom = eval_layer.forward(k, M)
        err_val = diff / denom if denom > 0 else float('inf')
        x_float = lumps_to_float(k, M)

        print(f"Iter {i}: x= {k}/{M} = {x_float:.6f},  error= {err_val:.6e}")

        if diff * tolerance_num < denom:
            print("Converged within tolerance!")
            break

        k_new, changed = update_layer.forward(k, M)

        if changed:
            k = k_new
        else:
            old_x = lumps_to_float(k, M)
            k, M = expand_layer.forward(k, M)
            new_x = lumps_to_float(k, M)
            print(f"  No local improvement. Expanding capacity => x: {old_x:.6f} -> {new_x:.6f} (k={k}, M={M})")

    k2, M2, diff, denom = eval_layer.forward(k, M)
    final_err = diff / denom if denom > 0 else float('inf')
    final_x = lumps_to_float(k, M)

    print("\n=== Final result ===")
    print(f"x= {k}/{M} = {final_x:.8f}, error= {final_err:.6e}")
    print("Done.")


if __name__ == "__main__":
    main()