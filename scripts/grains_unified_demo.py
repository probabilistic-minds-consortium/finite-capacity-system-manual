#!/usr/bin/env python3

"""
Demonstration of grains-coded approach combining:
    1) Gauss-Jordan elimination
    2) 2D Mesh geometry
    3) Trapezoidal rule integration
    4) Simple ODE/PDE discretization
All using a 'Grain' class for finite rational increments.
"""

from math import gcd

###############################################################################
# 1. Grain Class
###############################################################################

class Grain:
    """
    Grains-coded fraction:
      - Stored as an integer numerator and integer denominator.
      - All operations remain in rational form with no floating-point arithmetic.
    """
    def __init__(self, numerator: int, denominator: int = 1):
        if denominator == 0:
            raise ValueError("Denominator cannot be zero in grains-coded rational.")
        # Ensure inputs are integers.
        if not isinstance(numerator, int):
            raise TypeError("Numerator must be an integer in grains-coded approach.")
        if not isinstance(denominator, int):
            raise TypeError("Denominator must be an integer in grains-coded approach.")
        # Simplify and manage sign.
        sign = -1 if (numerator * denominator < 0) else 1
        num = abs(numerator)
        den = abs(denominator)
        g = gcd(num, den)
        self.n = sign * (num // g)
        self.d = den // g

    def __repr__(self):
        return f"Grain({self.n}/{self.d})"

    # Basic arithmetic operations:
    def __add__(self, other):
        if not isinstance(other, Grain):
            raise TypeError("Can only add Grain to Grain.")
        new_num = self.n * other.d + other.n * self.d
        new_den = self.d * other.d
        return Grain(new_num, new_den)

    def __sub__(self, other):
        return self.__add__(Grain(-other.n, other.d))

    def __mul__(self, other):
        if not isinstance(other, Grain):
            raise TypeError("Can only multiply Grain by Grain.")
        return Grain(self.n * other.n, self.d * other.d)

    def __truediv__(self, other):
        if not isinstance(other, Grain):
            raise TypeError("Can only divide Grain by Grain.")
        if other.n == 0:
            raise ZeroDivisionError("Divide by Grain(0/1) is not allowed.")
        return Grain(self.n * other.d, self.d * other.n)

    # Comparison operators:
    def __eq__(self, other):
        if not isinstance(other, Grain):
            return False
        return self.n == other.n and self.d == other.d

    def __ne__(self, other):
        return not self.__eq__(other)

    def __lt__(self, other):
        return self.n * other.d < other.n * self.d

    def __le__(self, other):
        return self.n * other.d <= other.n * self.d

    def __gt__(self, other):
        return self.n * other.d > other.n * self.d

    def __ge__(self, other):
        return self.n * other.d >= other.n * self.d


###############################################################################
# 2. Gauss-Jordan Elimination (grains-coded)
###############################################################################

def gauss_jordan_solve(A, b):
    """
    Solve the system A * x = b using grains-coded Gauss-Jordan elimination.
    - A is an NxN matrix of Grain.
    - b is an N-element vector of Grain.
    Returns the solution vector as a list of Grain.
    """
    N_dim = len(A)
    # Build the augmented matrix [A | b]
    mat = [row[:] + [b_i] for row, b_i in zip(A, b)]

    # Forward elimination
    for i in range(N_dim):
        # Pivot selection: swap rows if pivot is zero.
        if mat[i][i] == Grain(0):
            for r in range(i + 1, N_dim):
                if mat[r][i] != Grain(0):
                    mat[i], mat[r] = mat[r], mat[i]
                    break
        pivot = mat[i][i]
        if pivot == Grain(0):
            raise ValueError("Matrix is singular or near-singular in grains-coded sense.")
        # Normalize pivot row (divide row by pivot)
        for c in range(i, N_dim + 1):
            mat[i][c] = mat[i][c] / pivot
        # Eliminate entries below pivot
        for r in range(i + 1, N_dim):
            factor = mat[r][i]
            if factor != Grain(0):
                for c in range(i, N_dim + 1):
                    mat[r][c] = mat[r][c] - factor * mat[i][c]

    # Back substitution
    for i in reversed(range(N_dim)):
        for r in range(i):
            factor = mat[r][i]
            if factor != Grain(0):
                for c in range(i, N_dim + 1):
                    mat[r][c] = mat[r][c] - factor * mat[i][c]

    # Extract solution (last column of augmented matrix)
    return [row[N_dim] for row in mat]

def demo_gauss_jordan():
    # Example: Solve the system:
    #   2x +  y = -4
    #   3x + 4y = -7
    A = [
        [Grain(2), Grain(1)],
        [Grain(3), Grain(4)]
    ]
    b = [Grain(-4), Grain(-7)]
    sol = gauss_jordan_solve(A, b)
    print("Gauss-Jordan solution (grains-coded):", sol)


###############################################################################
# 3. Simple 2D Mesh (Discrete Geometry)
###############################################################################

class MeshNode:
    """
    A discrete geometry node with grains-coded x, y coordinates.
    """
    def __init__(self, x: Grain, y: Grain):
        self.x = x
        self.y = y

    def __repr__(self):
        return f"MeshNode({self.x}, {self.y})"

def build_2d_mesh(width, height):
    """
    Build a 2D mesh of size width x height using grains-coded coordinates.
    """
    mesh = []
    for j in range(height):
        row = []
        for i in range(width):
            node = MeshNode(Grain(i), Grain(j))
            row.append(node)
        mesh.append(row)
    return mesh

def demo_2d_mesh():
    mesh = build_2d_mesh(3, 2)
    print("\n2D Mesh (3x2) with grains-coded coordinates:")
    for row in mesh:
        print("   ", row)


###############################################################################
# 4. Trapezoidal Rule Integration (grains-coded)
###############################################################################

def trapezoidal_integration(func, start, end, num_steps):
    """
    Approximate the integral of func (a function returning Grain) from x = start to x = end,
    using the trapezoidal rule with num_steps intervals.
    start and end are Grain, num_steps is an integer.
    """
    if not isinstance(start, Grain):
        start = Grain(start)
    if not isinstance(end, Grain):
        end = Grain(end)
    if not isinstance(num_steps, int):
        raise TypeError("num_steps must be an integer.")

    h = (end - start) / Grain(num_steps)
    total = func(start) + func(end)
    x = start
    for _ in range(num_steps - 1):
        x = x + h
        total = total + Grain(2) * func(x)
    return (h / Grain(2)) * total

def demo_integration():
    # Example: integrate f(x)=x^2 from 0 to 4 with 4 trapezoids.
    def f(x):
        return x * x
    approx = trapezoidal_integration(f, Grain(0), Grain(4), 4)
    print("\nTrapezoidal integration (f(x)=x^2, from 0 to 4, 4 steps):", approx)


###############################################################################
# 5. Simple ODE/PDE Discretization (Forward Difference)
###############################################################################

def grains_forward_difference(ys, dx):
    """
    Compute the forward-difference derivative approximation:
        (y[i+1] - y[i]) / dx for a list of Grain values.
    Returns a list of Grain representing the derivative approximations.
    """
    derivs = []
    for i in range(len(ys) - 1):
        derivs.append((ys[i+1] - ys[i]) / dx)
    return derivs

def grains_ode_demo():
    """
    Demonstrate an ODE: Let y(x)= x^2 + 1 for x = 0..4 (grains-coded steps of 1).
    Approximate the derivative using forward differences.
    Expected derivative of x^2+1 is 2x.
    """
    dx = Grain(1)
    y_vals = []
    for x_int in range(5):
        x_val = Grain(x_int)
        y_vals.append(x_val * x_val + Grain(1))
    deriv_approx = grains_forward_difference(y_vals, dx)
    print("\nODE Forward Difference Demo (y(x)=x^2+1, dx=1):")
    for i, d in enumerate(deriv_approx):
        print(f"  x={i} -> derivative approx = {d}")

def grains_pde_demo_1d_heat():
    """
    Perform one time-step of the 1D heat equation (discretized) using grains-coded arithmetic:
        u[i]^(n+1) = u[i]^n + alpha*(u[i+1] - 2*u[i] + u[i-1])
    Boundary conditions: u[0] and u[-1] are set to Grain(0).
    """
    alpha = Grain(1, 2)  # alpha = 0.5
    u = [Grain(0), Grain(2), Grain(4), Grain(2), Grain(0)]
    u_new = u[:]  # Copy current state.
    for i in range(1, len(u)-1):
        laplacian = u[i+1] - Grain(2)*u[i] + u[i-1]
        u_new[i] = u[i] + alpha * laplacian
    print("\n1D Heat Equation Demo (alpha = 1/2):")
    print("  u (old):", u)
    print("  u (new):", u_new)

###############################################################################
# 6. Putting It All Together (Main)
###############################################################################

def main():
    demo_gauss_jordan()
    demo_2d_mesh()
    demo_integration()
    grains_ode_demo()
    grains_pde_demo_1d_heat()

if __name__ == "__main__":
    main()