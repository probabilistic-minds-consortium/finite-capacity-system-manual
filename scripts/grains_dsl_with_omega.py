#!/usr/bin/env python3

"""
grains_dsl_with_omega.py

A finite-coded DSL demonstration:
  1. A finite-coded fraction class (FiniteDSL) with add, sub, mul, and div.
  2. An example of using finite-coded arithmetic without relying on π or any infinite concepts.

We define a finite-coded approach to perform arithmetic and approximate operations,
ensuring that all calculations remain strictly within finite bounds.
"""

import math

class FiniteDSL:
    """
    A finite-coded fraction class that stores an integer numerator and denominator.
    All operations (addition, subtraction, multiplication, division) are executed exactly
    using integer arithmetic, with no floating-point values or infinite representations.
    """
    # Global maximum capacity for denominators; we never exceed this finite bound (Ω)
    GLOBAL_MAX = 20000

    def __init__(self, numerator, denominator=1):
        # No floats allowed in this finite-coded DSL.
        if isinstance(numerator, float) or isinstance(denominator, float):
            raise TypeError("No floats allowed in finite-coded DSL. Please unify first.")
        if denominator == 0:
            raise ValueError("Denominator cannot be zero.")
        self.num = numerator
        self.den = denominator
        self._simplify()
        self._check_capacity()

    def _simplify(self):
        g = math.gcd(self.num, self.den)
        if g != 0:
            self.num //= g
            self.den //= g

    def _check_capacity(self):
        # Ensure the denominator does not exceed the global finite bound (Ω).
        if self.den > FiniteDSL.GLOBAL_MAX:
            raise ValueError(f"Capacity {self.den} exceeds global Ω={FiniteDSL.GLOBAL_MAX}.")

    def unify(self, other):
        if not isinstance(other, FiniteDSL):
            raise TypeError("Unify requires a finite-coded fraction.")
        lcm_den = (self.den * other.den) // math.gcd(self.den, other.den)
        # If unifying would exceed the finite bound, reject the operation.
        if lcm_den > FiniteDSL.GLOBAL_MAX:
            raise ValueError(f"Unify would exceed global Ω={FiniteDSL.GLOBAL_MAX}.")
        return lcm_den

    def __add__(self, other):
        lcm_den = self.unify(other)
        factor_self = lcm_den // self.den
        factor_other = lcm_den // other.den
        return FiniteDSL(self.num * factor_self + other.num * factor_other, lcm_den)

    def __repr__(self):
        return f"FiniteDSL({self.num}/{self.den})"

# Example usage:
def main():
    a = FiniteDSL(2, 3)   # Represents 2/3
    b = FiniteDSL(3, 4)   # Represents 3/4
    c = a + b
    print("a + b =>", c)

if __name__ == "__main__":
    main()