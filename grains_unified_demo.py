#!/usr/bin/env python3

"""
Demonstration of lumps-coded approach combining:
    1) Gauss-Jordan elimination
    2) 2D Mesh geometry
    3) Trapezoidal rule integration
    4) Simple ODE/PDE discretization
All using a 'Lump' class for finite rational increments.
"""

from math import gcd

###############################################################################
# 1. Lump Class
###############################################################################

class Lump:
    """
    Lumps-coded fraction:
      - Stored as integer numerator and denominator
      - All operations remain in rational form, no floating point.
    """
    def __init__(self, numerator, denominator=1):
        if denominator == 0:
            raise ValueError("Denominator cannot be zero.")
        # Ensure everything is integer
        if not isinstance(numerator, int):
            raise TypeError("Numerator must be an integer in lumps-coded approach.")
        if not isinstance(denominator, int):
            raise TypeError("Denominator must be an integer in lumps-coded approach.")

        # Attempt to keep them reduced
        sign = -1 if (numerator*denominator < 0) else 1
        num = abs(numerator)
        den = abs(denominator)
        g = gcd(num, den)
        self.n = sign * (num // g)
        self.d = den // g

    def __repr__(self):
        return f"Lump({self.n}/{self.d})"

    # Basic arithmetic:

    def __add__(self, other):
        if not isinstance(other, Lump):
            raise TypeError("Can only add Lump to Lump.")
        new_num = self.n*other.d + other.n*self.d
        new_den = self.d * other.d
        return Lump(new_num, new_den)

    def __sub__(self, other):
        return self.__add__(Lump(-other.n, other.d))

    def __mul__(self, other):
        if not isinstance(other, Lump):
            raise TypeError("Can only multiply Lump by Lump.")
        return Lump(self.n*other.n, self.d*other.d)

    def __truediv__(self, other):
        if not isinstance(other, Lump):
            raise TypeError("Can only divide Lump by Lump.")
        if other.n == 0:
            raise ZeroDivisionError("Divide by Lump(0/1) is not allowed.")
        return Lump(self.n * other.d, self.d * other.n)

    # For Gauss-Jordan pivot comparisons, etc.
    def __eq__(self, other):
        if not isinstance(other, Lump):
            return False
        return self.n == other.n and self.d == other.d

    def __ne__(self, other):
        return not self.__eq__(other)

    def __lt__(self, other):
        # Compare self.n/self.d < other.n/other.d
        return self.n * other.d < other.n * self.d

    def __le__(self, other):
        return self.n * other.d <= other.n * self.d

    def __gt__(self, other):
        return self.n * other.d > other.n * self.d

    def __ge__(self, other):
        return self.n * other.d >= other.n * self.d


###############################################################################
# 2. Gauss-Jordan Elimination (lumps-coded)
###############################################################################

def gauss_jordan_solve(A, b):
    """
    Solve system A x = b using lumps-coded Gauss-Jordan elimination.
    A is a list of lists of Lump, dimension NxN
    b is a list of Lump, dimension N
    Return list of Lump as solution vector.
    """

    # Make a local copy so we don’t destroy original
    N = len(A)
    # Extended matrix [A | b]
    mat = [row[:] + [b_i] for row, b_i in zip(A, b)]  # Nx(N+1)

    # Forward elimination
    for i in range(N):
        # 1. Find pivot (row with nonzero pivot in col i)
        if mat[i][i] == Lump(0):
            # find a row below i to swap
            for r in range(i+1, N):
                if mat[r][i] != Lump(0):
                    mat[i], mat[r] = mat[r], mat[i]
                    break
        pivot = mat[i][i]
        if pivot == Lump(0):
            raise ValueError("Matrix is singular or near-singular in lumps-coded sense.")

        # 2. Normalize pivot row (divide entire row by pivot)
        for c in range(i, N+1):
            mat[i][c] = mat[i][c] / pivot

        # 3. Eliminate below pivot
        for r in range(i+1, N):
            factor = mat[r][i]
            if factor != Lump(0):
                for c in range(i, N+1):
                    mat[r][c] = mat[r][c] - factor * mat[i][c]

    # Back substitution
    for i in reversed(range(N)):
        for r in range(i):
            factor = mat[r][i]
            if factor != Lump(0):
                for c in range(i, N+1):
                    mat[r][c] = mat[r][c] - factor * mat[i][c]

    # Extract solution
    return [row[N] for row in mat]


def demo_gauss_jordan():
    # Example: Solve system:
    #   2x + 1y = -4
    #   3x + 4y = -7
    A = [
        [Lump(2), Lump(1)],  # 2x + 1y
        [Lump(3), Lump(4)]   # 3x + 4y
    ]
    b = [Lump(-4), Lump(-7)]
    sol = gauss_jordan_solve(A, b)
    print("Gauss-Jordan solution (lumps-coded):", sol)


###############################################################################
# 3. Simple 2D Mesh (Discrete Geometry)
###############################################################################

class MeshNode:
    """
    A discrete geometry node with lumps-coded x,y coordinates.
    """
    def __init__(self, x, y):
        # x, y are Lump
        self.x = x
        self.y = y

    def __repr__(self):
        return f"MeshNode({self.x},{self.y})"

def build_2d_mesh(width, height):
    """
    Build a lumps-coded 2D mesh: width x height nodes
    Using integer lumps-coded coordinates for demonstration.
    """
    mesh = []
    for j in range(height):
        row = []
        for i in range(width):
            node = MeshNode(Lump(i), Lump(j))
            row.append(node)
        mesh.append(row)
    return mesh

def demo_2d_mesh():
    mesh = build_2d_mesh(3, 2)  # 3 wide x 2 tall
    print("\n2D Mesh (3x2) with lumps-coded coordinates:")
    for row in mesh:
        print("   ", row)


###############################################################################
# 4. Trapezoidal Rule (Integration) in lumps-coded form
###############################################################################

def trapezoidal_integration(func, start, end, num_steps):
    """
    Approximate the integral of `func(Lump) -> Lump`
    from x = start to x = end using lumps-coded trapezoidal rule.
    (start, end, num_steps are all Lump or can be turned into Lump)

    For demonstration, we assume start < end and num_steps is a plain int
    (or lumps-coded integer).  If you want lumps-coded step counts, you
    could refine the approach further.
    """
    if not isinstance(start, Lump):
        start = Lump(start)
    if not isinstance(end, Lump):
        end = Lump(end)
    if not isinstance(num_steps, int):
        raise TypeError("num_steps must be an integer for simplicity in this demo.")

    # Step size h = (end - start) / num_steps
    h = (end - start) / Lump(num_steps)
    # Evaluate func at start, end
    s = func(start) + func(end)
    # Evaluate interior points
    x = start
    for _ in range(num_steps - 1):
        x = x + h
        s = s + Lump(2) * func(x)
    # Final lumps-coded result
    return (h / Lump(2)) * s

def demo_integration():
    # Example: integrate f(x) = x^2 from 0 to 4, with 4 trapezoids
    # True integral = (4^3)/3 = 64/3 = ~21.3333
    # We'll see lumps-coded approximation
    def f(x_lump):
        return x_lump * x_lump  # lumps-coded multiplication => x^2

    approx = trapezoidal_integration(f, 0, 4, 4)
    print("\nTrapezoidal integration lumps-coded (f(x)=x^2, 0..4, 4 steps):", approx)


###############################################################################
# 5. Simple ODE/PDE Discretization (Forward Difference Example)
###############################################################################

def lumps_forward_difference(ys, dx):
    """
    A simple forward-difference approximation for derivative:
        d/dx (y[i]) ~ (y[i+1] - y[i]) / dx
    ys: list of Lump (y-values)
    dx: Lump representing the step in x
    Return list of derivative approximations for i=0..len(ys)-2
    (last point omitted for simple forward difference).
    """
    derivs = []
    for i in range(len(ys) - 1):
        slope = (ys[i+1] - ys[i]) / dx
        derivs.append(slope)
    return derivs

def lumps_ode_demo():
    """
    Suppose we have y(x) ~ x^2 + 1 for x = 0..4, lumps-coded steps of size 1
    We'll approximate derivative using forward difference.
    True derivative of x^2+1 is 2x, so we expect 0..2..4..6..8
    Our lumps-coded result won't do continuity or any float. 
    """
    dx = Lump(1)
    # y-values = x^2 + 1 for x=0..4
    y_vals = []
    for x_int in range(5):
        x_l = Lump(x_int)
        y_vals.append(x_l*x_l + Lump(1))

    # derivative approximations
    deriv_approx = lumps_forward_difference(y_vals, dx)

    print("\nODE Forward-Difference Derivative (y=x^2+1, lumps-coded dx=1):")
    for i, d in enumerate(deriv_approx):
        print(f"  x={i} => derivative approx = {d}")

def lumps_pde_demo_1d_heat():
    """
    A trivial 1D heat equation step (discretized) for demonstration:
       u_{t+1}(i) = u_t(i) + alpha * [ u_t(i+1) - 2*u_t(i) + u_t(i-1) ]
    We'll do a single time step lumps-coded.

    For simplicity, boundary conditions are zero, alpha is lumps-coded fraction.
    """
    alpha = Lump(1, 2)  # lumps-coded alpha=0.5
    # initial data
    u = [Lump(0), Lump(2), Lump(4), Lump(2), Lump(0)]  # e.g. a small shape
    # new array after one step
    u_new = u[:]  # copy

    for i in range(1, len(u)-1):
        lap = (u[i+1] - Lump(2)*u[i] + u[i-1])
        u_new[i] = u[i] + alpha * lap

    print("\n1D Heat Equation Step (alpha=1/2, lumps-coded):")
    print("  old:", u)
    print("  new:", u_new)


###############################################################################
# Putting It All Together (Main)
###############################################################################

if __name__ == "__main__":

    # 1) Gauss-Jordan Solve
    demo_gauss_jordan()

    # 2) 2D Mesh
    demo_2d_mesh()

    # 3) Trapezoidal Integration
    demo_integration()

    # 4) ODE Forward Diff
    lumps_ode_demo()

    # 5) PDE Heat Step
    lumps_pde_demo_1d_heat()