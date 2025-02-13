#!/usr/bin/env python3

"""
lumps_arithmetic.py

Demonstration of:
  1. A lumps-coded fraction class (ArithLump) with add, sub, mul, div
  2. "Circle" geometry (approx) by lumps-coded polygons -- no pi usage.

We define a lumps-coded approach to approximate a circle's perimeter
by an N-sided regular polygon with lumps-coded side lengths, 
never using real-number pi or trigonometry. We rely on a simplistic 
"chord approximation" if we want a bigger N => more accurate perimeter.
All operations remain purely integer-based at each vantage step.
"""

import math

###############################################################################
# 1. Lumps-Coded Fraction Class
###############################################################################

def gcd(a,b):
    """Greatest common divisor: naive version."""
    if b == 0:
        return a
    return gcd(b, a % b)

class ArithLump:
    """
    A lumps-coded fraction: integer numerator (num) and integer denominator (den).
    We do add, sub, mul, div without floating operations. No references to infinite sets.
    """
    def __init__(self, numerator, denominator=1):
        if denominator == 0:
            raise ValueError("Denominator cannot be zero in lumps-coded fraction.")
        # keep them integer
        if not (isinstance(numerator, int) and isinstance(denominator, int)):
            raise TypeError("ArithLump requires integer numerator and denominator.")
        # sign management
        sign = -1 if (numerator*denominator < 0) else 1
        num = abs(numerator)
        den = abs(denominator)
        g = gcd(num, den)
        self.num = sign*(num//g)
        self.den = den//g

    def __repr__(self):
        return f"ArithLump({self.num}/{self.den})"

    def to_float(self):
        """For demonstration only; we do not rely on this internally."""
        return self.num / self.den

    # Lumps-coded additions, subtractions, multiplications, divisions
    def __add__(self, other):
        if not isinstance(other, ArithLump):
            other = ArithLump(other, 1)
        new_num = self.num*other.den + other.num*self.den
        new_den = self.den*other.den
        return ArithLump(new_num, new_den)

    def __sub__(self, other):
        if not isinstance(other, ArithLump):
            other = ArithLump(other, 1)
        new_num = self.num*other.den - other.num*self.den
        new_den = self.den*other.den
        return ArithLump(new_num, new_den)

    def __mul__(self, other):
        if not isinstance(other, ArithLump):
            other = ArithLump(other, 1)
        return ArithLump(self.num*other.num, self.den*other.den)

    def __truediv__(self, other):
        if not isinstance(other, ArithLump):
            other = ArithLump(other, 1)
        if other.num == 0:
            raise ZeroDivisionError("Divide by lumps-coded zero not permitted.")
        return ArithLump(self.num*other.den, self.den*other.num)

###############################################################################
# 2. Lumps-Coded "Circle" Approximation (Polygon)
###############################################################################

def lumps_polygon_perimeter(n_sides, side_length):
    """
    For an n-sided regular polygon, lumps-coded side_length is 
    a lumps-coded fraction. The perimeter is n_sides * side_length.
    """
    # multiply integer n_sides by lumps-coded side_length => lumps-coded
    n_as_lump = ArithLump(n_sides, 1)
    return n_as_lump * side_length


def lumps_approx_circle_perimeter(radius, n_sides):
    """
    Approximate a circle's perimeter by an n-sided polygon with lumps-coded chord approach.
    We do NOT use sin, cos, or pi. 
    Instead, we pretend side_length ~ chord(2*pi/n) ... 
    but we'll do a lumps-coded simplified approach: 
       side_length = 2 * radius
    which is basically an extremely naive approximation for large n_sides 
    (like inscribing a circle with a polygon of half-chords). 
    If we want a better approach, we could do lumps-coded expansions for trig. 
    But let's show this as a demonstration of "no pi" usage.

    radius: lumps-coded fraction
    n_sides: integer
    returns lumps-coded fraction for perimeter
    """
    # For a real approach, we might do side_length ~ 2*r*sin(pi/n). 
    # But we skip actual sin for demonstration: lumps-coded has no pi or trig in pure form.
    # We'll do a (very naive) chord length = 2 * radius * lumps_approxFactor. 
    # Let's define lumps_approxFactor = some lumps-coded fraction for "small angle approx"
    # e.g. lumps_approxFactor ~ 0.0314*(n_sides) =>  since 2*pi*r => 2*pi => ~6.283 => /n_sides => side
    # But we want no pi at all. We'll do a simpler approach: side_length = (2*radius) / n_sides. 
    # That "n_sides" factor tries to keep total perimeter ~ 2*r*(n_sides / n_sides)=2*r => obviously an under-approx for large n. 
    # It's only to show lumps-coded arithmetic, not a real circle solution. 

    nL = ArithLump(n_sides, 1)
    two = ArithLump(2,1)
    # side_length = (2*radius) / n_sides
    side_length = (two * radius) / nL
    # perimeter = n_sides * side_length
    perimeter = lumps_polygon_perimeter(n_sides, side_length)
    return perimeter

###############################################################################
# 3. Demonstration
###############################################################################

def main():
    print("\n=== Lumps-Coded Basic Arithmetic Demo ===\n")
    a = ArithLump(3,4)  # 3/4
    b = ArithLump(5,6)  # 5/6

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

    print("\n=== Lumps-Coded 'Circle' Approximation ===")
    # Let's pick a lumps-coded radius r= (5/1), i.e. radius=5 lumps-coded units
    r = ArithLump(5,1)
    n_sides = 8

    perimeter_approx = lumps_approx_circle_perimeter(r, n_sides)
    print(f"For n_sides={n_sides}, lumps-coded perimeter approx: {perimeter_approx} ~ {perimeter_approx.to_float():.4f}")

    # Try bigger n_sides => see how it changes
    n_sides2 = 32
    perimeter_approx2 = lumps_approx_circle_perimeter(r, n_sides2)
    print(f"For n_sides={n_sides2}, lumps-coded perimeter approx: {perimeter_approx2} ~ {perimeter_approx2.to_float():.4f}")

    # Notice we never used pi or real trig => purely lumps-coded step.
    # This is definitely not accurate for a real circle, but demonstrates no pi usage.

if __name__ == "__main__":
    main()