# lumps_dsl_with_omega.py

import math

class LumpsDSL:
    # A global max capacity for denominators
    # so we never exceed Ω
    GLOBAL_MAX = 20000

    def __init__(self, numerator, denominator=1):
        # no floats allowed
        if isinstance(numerator, float) or isinstance(denominator, float):
            raise TypeError("No floats in lumps-coded DSL. Please unify first.")
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
        # If denominator > GLOBAL_MAX => skip or revert
        if self.den > LumpsDSL.GLOBAL_MAX:
            raise ValueError(f"Capacity {self.den} exceeds global Ω={LumpsDSL.GLOBAL_MAX}.")

    def unify(self, other):
        if not isinstance(other, LumpsDSL):
            raise TypeError("Unify requires lumps-coded fraction.")
        lcm_den = (self.den*other.den)//math.gcd(self.den, other.den)
        # if unifying would exceed Ω => partial unify or fail
        if lcm_den > LumpsDSL.GLOBAL_MAX:
            raise ValueError(f"Unify would exceed global Ω={LumpsDSL.GLOBAL_MAX}.")
        return lcm_den

    def __add__(self, other):
        lcm_den = self.unify(other)
        factor_self  = lcm_den//self.den
        factor_other = lcm_den//other.den
        return LumpsDSL(self.num*factor_self + other.num*factor_other, lcm_den)

    def __repr__(self):
        return f"LumpsDSL({self.num}/{self.den})"

# Example usage:
def main():
    a = LumpsDSL(2, 3)   # 2/3
    b = LumpsDSL(3, 4)   # 3/4
    c = a + b
    print("a+b =>", c)

if __name__=="__main__":
    main()