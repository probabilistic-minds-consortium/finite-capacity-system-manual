#!/usr/bin/env python3

class Grain:
    """Potentially storing an integer or a rational (numerator, denominator)."""
    def __init__(self, numerator, denominator=1):
        # naive rational approach
        if denominator == 0:
            raise ValueError("Denominator cannot be zero in a grains-coded fraction.")
        self.num = numerator
        self.den = denominator

    def __repr__(self):
        return f"Grain({self.num}/{self.den})"

# Helper: Euclidean algorithm for GCD
def gcd(a, b):
    if b == 0:
        return a
    return gcd(b, a % b)

def grains_add(g1, g2):
    """(n1/d1) + (n2/d2) => (n1*d2 + n2*d1)/(d1*d2)."""
    num = g1.num * g2.den + g2.num * g1.den
    den = g1.den * g2.den
    g = gcd(abs(num), abs(den))
    return Grain(num // g, den // g)

def grains_sub(g1, g2):
    """(n1/d1) - (n2/d2)."""
    num = g1.num * g2.den - g2.num * g1.den
    den = g1.den * g2.den
    g = gcd(abs(num), abs(den))
    return Grain(num // g, den // g)

def grains_mult(g1, g2):
    """(n1/d1) * (n2/d2)."""
    num = g1.num * g2.num
    den = g1.den * g2.den
    g = gcd(abs(num), abs(den))
    return Grain(num // g, den // g)

def grains_div(g1, g2):
    """(n1/d1) / (n2/d2) => (n1*d2)/(n2*d1)."""
    if g2.num == 0:
        raise ZeroDivisionError("grains_div: division by zero.")
    num = g1.num * g2.den
    den = g1.den * g2.num
    g = gcd(abs(num), abs(den))
    return Grain(num // g, den // g)

def grains_zero():
    return Grain(0, 1)

def grains_one():
    return Grain(1, 1)

def gauss_jordan_solve(A, b):
    """
    Solve A*x = b using grains-coded Gauss-Jordan.
    - A is a list of lists of Grain objects.
    - b is a list of Grain objects.
    Returns x as a list of Grain.
    """
    n = len(A)
    # Build augmented matrix
    aug = [row[:] + [bval] for row, bval in zip(A, b)]

    # Forward elimination with pivoting
    for i in range(n):
        # Pivot: find a non-zero element in column i
        pivot = aug[i][i]
        if pivot.num == 0:
            for r in range(i + 1, n):
                if aug[r][i].num != 0:
                    aug[i], aug[r] = aug[r], aug[i]
                    pivot = aug[i][i]
                    break
        
        # Normalize row i by dividing every element by the pivot
        div_factor = pivot
        for col in range(n + 1):
            aug[i][col] = grains_div(aug[i][col], div_factor)

        # Eliminate all other entries in column i
        for r in range(n):
            if r != i:
                factor = aug[r][i]
                for c in range(i, n + 1):
                    product = grains_mult(factor, aug[i][c])
                    aug[r][c] = grains_sub(aug[r][c], product)

    # Extract solution vector: last column of augmented matrix
    x = [row[n] for row in aug]
    return x

# Example usage:
A = [
  [Grain(2), Grain(1)],
  [Grain(1), Grain(-1)]
]
b = [Grain(5), Grain(-1)]

sol = gauss_jordan_solve(A, b)
print("Grains-coded Gauss-Jordan solution:", sol)