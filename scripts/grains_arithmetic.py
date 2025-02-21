#!/usr/bin/env python3

"""
grains_arithmetic.py

Demonstration of:
  1. A finite-coded fraction class (FiniteFraction) with add, sub, mul, and div.
  2. "Circle" geometry (approximation) using a finite-coded polygon approach – without using π or trigonometry.

We define a finite-coded approach to approximate a circle's perimeter by using an N-sided regular polygon.
All operations remain purely integer-based at each finite step.
"""

# Helper: Euclidean algorithm for greatest common divisor (GCD)
def gcd(a, b):
    if b == 0:
        return a
    return gcd(b, a % b)

###############################################################################
# 1. Finite-Coded Fraction Class
###############################################################################

class FiniteFraction:
    """
    A finite-coded fraction: stores an integer numerator and denominator.
    All operations (add, sub, mul, div) are performed exactly using integer arithmetic.
    """
    def __init__(self, numerator, denominator=1):
        if denominator == 0:
            raise ValueError("Denominator cannot be zero in a finite-coded fraction.")
        if not (isinstance(numerator, int) and isinstance(denominator, int)):
            raise TypeError("FiniteFraction requires integer numerator and denominator.")
        # Manage sign and simplify
        sign = -1 if (numerator * denominator < 0) else 1
        num = abs(numerator)
        den = abs(denominator)
        g = gcd(num, den)
        self.num = sign * (num // g)
        self.den = den // g

    def __repr__(self):
        return f"FiniteFraction({self.num}/{self.den})"

    def to_float(self):
        """For display only: convert the fraction to a float."""
        return self.num / self.den

    def __add__(self, other):
        if not isinstance(other, FiniteFraction):
            other = FiniteFraction(other, 1)
        new_num = self.num * other.den + other.num * self.den
        new_den = self.den * other.den
        return FiniteFraction(new_num, new_den)

    def __sub__(self, other):
        if not isinstance(other, FiniteFraction):
            other = FiniteFraction(other, 1)
        new_num = self.num * other.den - other.num * self.den
        new_den = self.den * other.den
        return FiniteFraction(new_num, new_den)

    def __mul__(self, other):
        if not isinstance(other, FiniteFraction):
            other = FiniteFraction(other, 1)
        return FiniteFraction(self.num * other.num, self.den * other.den)

    def __truediv__(self, other):
        if not isinstance(other, FiniteFraction):
            other = FiniteFraction(other, 1)
        if other.num == 0:
            raise ZeroDivisionError("Division by zero is not permitted in finite-coded arithmetic.")
        return FiniteFraction(self.num * other.den, self.den * other.num)

###############################################################################
# 2. Finite-Coded "Circle" Approximation (Polygon)
###############################################################################

def finite_polygon_perimeter(n_sides, side_length):
    """
    Compute the perimeter of an n-sided regular polygon.
    n_sides is an integer, and side_length is a FiniteFraction.
    Returns a FiniteFraction representing the perimeter.
    """
    n_as_fraction = FiniteFraction(n_sides, 1)
    return n_as_fraction * side_length

def finite_approx_circle_perimeter(radius, n_sides):
    """
    Approximate a circle's perimeter using an n-sided polygon, with a finite-coded approach.
    This demonstration uses a simplistic chord approximation (no π or trigonometry).
    Note: This is a naive approximation for demonstration purposes only.
    
    radius: a FiniteFraction representing the circle's radius.
    n_sides: an integer representing the number of sides.
    
    Returns a FiniteFraction for the approximated perimeter.
    """
    n_fraction = FiniteFraction(n_sides, 1)
    two = FiniteFraction(2, 1)
    # Naively define side_length = (2 * radius) / n_sides.
    side_length = (two * radius) / n_fraction
    perimeter = finite_polygon_perimeter(n_sides, side_length)
    return perimeter

###############################################################################
# 3. Demonstration
###############################################################################

def main():
    print("\n=== Finite-Coded Basic Arithmetic Demo ===\n")
    a = FiniteFraction(3, 4)  # 3/4
    b = FiniteFraction(5, 6)  # 5/6

    print("a =", a, "~", a.to_float())
    print("b =", b, "~", b.to_float(), "\n")

    c_add = a + b
    c_sub = a - b
    c_mul = a * b
    c_div = a / b

    print("a + b =", c_add, "~", c_add.to_float())
    print("a - b =", c_sub, "~", c_sub.to_float())
    print("a * b =", c_mul, "~", c_mul.to_float())
    print("a / b =", c_div, "~", c_div.to_float())

    print("\n=== Finite-Coded 'Circle' Approximation ===")
    # Example: radius = 5 (finite-coded as 5/1)
    r = FiniteFraction(5, 1)
    n_sides = 8

    perimeter_approx = finite_approx_circle_perimeter(r, n_sides)
    print(f"For n_sides={n_sides}, finite-coded perimeter approx: {perimeter_approx} ~ {perimeter_approx.to_float():.4f}")

    n_sides2 = 32
    perimeter_approx2 = finite_approx_circle_perimeter(r, n_sides2)
    print(f"For n_sides={n_sides2}, finite-coded perimeter approx: {perimeter_approx2} ~ {perimeter_approx2.to_float():.4f}")

    print("\nNote: This is a demonstration of finite-coded arithmetic without using π or any infinite concepts.")

if __name__ == "__main__":
    main()