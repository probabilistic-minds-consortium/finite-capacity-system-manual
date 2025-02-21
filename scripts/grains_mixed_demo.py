
"""
grains_mixed_demo.py

Demonstration of a grains-coded approach combining:
    1) Gauss-Jordan elimination
    2) 2D Mesh geometry
    3) Trapezoidal rule integration
    4) Simple ODE/PDE discretization

All using a 'Grain' class for finite rational increments.

Additionally, a separate PDE file models 1D diffusion using grains-coded logic.
No floating-point arithmetic or infinite assumptions are used.
"""

import math
from math import gcd

###############################################################################
# 1. Grain Class (Rational-based)
###############################################################################

class Grain:
    """
    Grains-coded fraction:
      - Stored as an integer numerator (n) and integer denominator (d).
      - All operations remain in rational form, with no floating-point arithmetic.
    """
    def __init__(self, numerator: int, denominator: int = 1):
        if denominator == 0:
            raise ValueError("Denominator cannot be zero in grains-coded rational.")
        # Sign management and gcd-based simplification
        sign = -1 if (numerator * denominator < 0) else 1
        num = abs(numerator)
        den = abs(denominator)
        g = gcd(num, den)
        self.n = sign * (num // g)
        self.d = den // g

    def __repr__(self):
        return f"Grain({self.n}/{self.d})"

    # Basic arithmetic operations
    def __add__(self, other):
        if not isinstance(other, Grain):
            raise TypeError("Grain can only add with Grain.")
        new_num = self.n * other.d + other.n * self.d
        new_den = self.d * other.d
        return Grain(new_num, new_den)

    def __sub__(self, other):
        return self.__add__(Grain(-other.n, other.d))

    def __mul__(self, other):
        if not isinstance(other, Grain):
            raise TypeError("Grain can only multiply with Grain.")
        return Grain(self.n * other.n, self.d * other.d)

    def __truediv__(self, other):
        if not isinstance(other, Grain):
            raise TypeError("Grain can only divide by Grain.")
        if other.n == 0:
            raise ZeroDivisionError("Division by grains-coded zero is not permitted.")
        return Grain(self.n * other.d, self.d * other.n)

    # Comparison operators for pivot selection, etc.
    def __eq__(self, other):
        return (self.n * other.d) == (other.n * self.d)

    def __lt__(self, other):
        return (self.n * other.d) < (other.n * self.d)

    def __le__(self, other):
        return (self.n * other.d) <= (other.n * self.d)

    def __ne__(self, other):
        return not (self == other)

    def __gt__(self, other):
        return not (self <= other)

    def __ge__(self, other):
        return not (self < other)

###############################################################################
# 2. Gauss-Jordan Elimination
###############################################################################

def gauss_jordan_solve(A, b):
    """
    Solve the system A * x = b using grains-coded Gauss-Jordan elimination.
    A is an N x N matrix of Grain objects, and b is an N x 1 vector of Grain objects.
    Returns the solution vector (list of Grain) of length N.
    """
    n = len(A)
    # Build the augmented matrix
    mat = [row[:] + [bval] for row, bval in zip(A, b)]  # Each row: [A[i], b[i]]

    # Forward elimination with pivoting
    for i in range(n):
        # Pivot selection: if the diagonal element is zero, swap with a lower row.
        if mat[i][i] == Grain(0):
            for r in range(i + 1, n):
                if mat[r][i] != Grain(0):
                    mat[i], mat[r] = mat[r], mat[i]
                    break
        pivot = mat[i][i]
        if pivot == Grain(0):
            raise ValueError("Matrix is singular in grains-coded sense.")

        # Normalize row i by dividing each element by the pivot
        for c in range(i, n + 1):
            mat[i][c] = mat[i][c] / pivot

        # Eliminate all entries in column i for rows below
        for r in range(i + 1, n):
            factor = mat[r][i]
            if factor != Grain(0):
                for c in range(i, n + 1):
                    mat[r][c] = mat[r][c] - factor * mat[i][c]

    # Back substitution
    for i in reversed(range(n)):
        for r in range(i):
            factor = mat[r][i]
            if factor != Grain(0):
                for c in range(i, n + 1):
                    mat[r][c] = mat[r][c] - factor * mat[i][c]

    # Extract solution from the last column
    return [row[n] for row in mat]

def demo_gauss_jordan():
    print("\n===== Gauss-Jordan Demo =====")
    # Example system: 2x + y = -4, 3x + 4y = -7
    A = [
        [Grain(2), Grain(1)],
        [Grain(3), Grain(4)]
    ]
    b = [Grain(-4), Grain(-7)]
    sol = gauss_jordan_solve(A, b)
    print("Grains-coded solution:", sol)

###############################################################################
# 3. 2D Mesh (Discrete Geometry)
###############################################################################

class MeshNode:
    """
    A grains-coded geometry node storing (x, y) as grains-coded rationals.
    """
    def __init__(self, x: Grain, y: Grain):
        self.x = x
        self.y = y

    def __repr__(self):
        return f"MeshNode({self.x}, {self.y})"

def build_2d_mesh(width, height):
    """
    Build a grains-coded 2D mesh of size width x height using integer grains for coordinates.
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
    print("\n===== 2D Mesh Demo =====")
    mesh = build_2d_mesh(3, 2)
    for row in mesh:
        print(row)

###############################################################################
# 4. Grains-coded Trapezoidal Integration
###############################################################################

def grains_trap_func(x: Grain):
    # f(x)= x^2 + 1 (finite-coded)
    one = Grain(1)
    return x * x + one

def grains_trapezoid_integration(a: Grain, b: Grain, n_steps: int):
    """
    Perform grains-coded integration of f(x)= x^2 + 1 over [a, b] using the trapezoidal rule,
    with n_steps intervals.
    """
    if b < a:
        raise ValueError("b < a in grains-coded trapezoid integration?")
    # Compute step as a finite fraction: step = (b - a) / n_steps
    step = (b - a) / Grain(n_steps)
    total = grains_trap_func(a) + grains_trap_func(b)
    x = a
    for i in range(1, n_steps):
        x = x + step
        total = total + (Grain(2) * grains_trap_func(x))
    return (step / Grain(2)) * total

def demo_trapezoid():
    print("\n===== Grains-coded Trapezoidal Integration Demo =====")
    a = Grain(0)
    b = Grain(5)
    n = 5
    area_approx = grains_trapezoid_integration(a, b, n)
    print(f"Trapezoidal area ≈ {area_approx}")

###############################################################################
# 5. Simple ODE/PDE Discretization
###############################################################################

def grains_forward_diff(yvals, dx: Grain):
    """
    Compute forward difference derivative approximation:
    (y[i+1] - y[i]) / dx for an array of y-values.
    Returns a list of finite-coded derivatives.
    """
    derivs = []
    n = len(yvals)
    for i in range(n - 1):
        slope = (yvals[i + 1] - yvals[i]) / dx
        derivs.append(slope)
    return derivs

def grains_ode_demo():
    """
    Demonstrate finite-coded ODE: Let y(x)= x^2 + 1 for x=0..4 with dx=1,
    and approximate the derivative using forward differences.
    """
    print("\n===== Grains-coded ODE Demo =====")
    dx = Grain(1)
    y_vals = []
    for x_int in range(5):
        x_val = Grain(x_int)
        y_vals.append(x_val * x_val + Grain(1))
    deriv_approx = grains_forward_diff(y_vals, dx)
    print("y =", y_vals)
    print("dy/dx forward approximation =", deriv_approx)

def grains_heat_step(u, alpha: Grain):
    """
    Perform one finite-coded heat equation time step in 1D:
    u[i]^(n+1) = u[i]^n + alpha * (u[i+1] - 2*u[i] + u[i-1])
    Boundary conditions: u[0] and u[-1] are set to 0.
    """
    n = len(u)
    next_u = u[:]  # Copy current state
    for i in range(1, n - 1):
        mid = u[i + 1] - Grain(2) * u[i] + u[i - 1]
        next_u[i] = u[i] + alpha * mid
    next_u[0] = Grain(0)
    next_u[-1] = Grain(0)
    return next_u

def grains_pde_demo():
    """
    Demonstrate a finite-coded PDE heat equation step on a 1D domain [0, 4] with dx=1.
    alpha is set to 1/2.
    Two time steps are simulated.
    """
    print("\n===== Grains-coded PDE Heat Demo =====")
    u = [Grain(0), Grain(3), Grain(6), Grain(3), Grain(0)]
    alpha = Grain(1, 2)
    print("Initial u =", u)
    for step in range(2):
        u = grains_heat_step(u, alpha)
        print(f"u({step+1}) =", u)

###############################################################################
# 6. Putting It All Together
###############################################################################

def main():
    # 1) Gauss-Jordan Elimination
    demo_gauss_jordan()
    # 2) 2D Mesh Geometry
    demo_2d_mesh()
    # 3) Trapezoidal Integration
    demo_trapezoid()
    # 4) ODE Forward Difference
    grains_ode_demo()
    # 5) PDE Heat Equation Step
    grains_pde_demo()

if __name__ == "__main__":
    main()