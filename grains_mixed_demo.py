#!/usr/bin/env python3

"""
Demonstration of lumps-coded approach combining:
    1) Gauss-Jordan elimination
    2) 2D Mesh geometry
    3) Trapezoidal rule integration
    4) Simple ODE/PDE discretization
All using a 'Lump' class for finite rational increments.

Additionally, we show a separate PDE file modeling 1D diffusion
via lumps-coded logic. 
"""

import math

###############################################################################
# 1. Lump Class (Rational-based)
###############################################################################
from math import gcd

class Lump:
    """
    Lumps-coded fraction:
      - stored as integer numerator (n) and denominator (d)
      - all operations remain in rational form, no floating point
    """
    def __init__(self, numerator: int, denominator: int=1):
        if denominator == 0:
            raise ValueError("Denominator cannot be zero in lumps-coded rational.")
        # sign management + gcd
        sign = -1 if (numerator*denominator < 0) else 1
        num = abs(numerator)
        den = abs(denominator)
        g = gcd(num, den)
        self.n = sign*(num//g)
        self.d = den//g

    def __repr__(self):
        return f"Lump({self.n}/{self.d})"

    # Basic arithmetic ops
    def __add__(self, other):
        if not isinstance(other, Lump):
            raise TypeError("Lump can only add with Lump.")
        new_num = self.n*other.d + other.n*self.d
        new_den = self.d*other.d
        return Lump(new_num, new_den)

    def __sub__(self, other):
        return self.__add__(Lump(-other.n, other.d))

    def __mul__(self, other):
        if not isinstance(other, Lump):
            raise TypeError("Lump can only multiply with Lump.")
        return Lump(self.n*other.n, self.d*other.d)

    def __truediv__(self, other):
        if not isinstance(other, Lump):
            raise TypeError("Lump can only divide by Lump.")
        if other.n == 0:
            raise ZeroDivisionError("Divide by lumps-coded zero.")
        return Lump(self.n*other.d, self.d*other.n)

    # comparisons for pivot selection, etc.
    def __eq__(self, other):
        return (self.n*other.d) == (other.n*self.d)

    def __lt__(self, other):
        return (self.n*other.d) < (other.n*self.d)

    def __le__(self, other):
        return (self.n*other.d) <= (other.n*self.d)

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
    Solve system A x = b using lumps-coded Gauss-Jordan.
    A is NxN lumps-coded matrix, b is Nx1 lumps-coded vector.
    Return lumps-coded solution vector of length N.
    """

    N = len(A)
    # Build augmented matrix
    mat = [row[:] + [bval] for row, bval in zip(A,b)]  # Nx(N+1)

    # Forward elimination
    for i in range(N):
        # pivot check
        if mat[i][i] == Lump(0):
            # swap row
            for r in range(i+1, N):
                if mat[r][i] != Lump(0):
                    mat[i], mat[r] = mat[r], mat[i]
                    break
        pivot = mat[i][i]
        if pivot == Lump(0):
            raise ValueError("Matrix is singular in lumps-coded sense.")

        # normalize pivot row
        for c in range(i, N+1):
            mat[i][c] = mat[i][c] / pivot

        # eliminate below pivot
        for r in range(i+1, N):
            factor = mat[r][i]
            if factor != Lump(0):
                for c in range(i, N+1):
                    mat[r][c] = mat[r][c] - factor*mat[i][c]

    # Back substitution
    for i in reversed(range(N)):
        for r in range(i):
            factor = mat[r][i]
            if factor != Lump(0):
                for c in range(i, N+1):
                    mat[r][c] = mat[r][c] - factor*mat[i][c]

    # solution in last col
    return [row[N] for row in mat]

def demo_gauss_jordan():
    print("\n===== Gauss-Jordan Demo =====")
    # example system: 2x +1y=-4, 3x+4y=-7
    A = [
      [Lump(2), Lump(1)],
      [Lump(3), Lump(4)]
    ]
    b = [Lump(-4), Lump(-7)]
    sol = gauss_jordan_solve(A, b)
    print("Solution lumps-coded:", sol)


###############################################################################
# 3. 2D Mesh (Discrete Geometry)
###############################################################################

class MeshNode:
    """
    A lumps-coded geometry node storing (x,y) as lumps-coded rationals
    """
    def __init__(self, x: Lump, y: Lump):
        self.x = x
        self.y = y

    def __repr__(self):
        return f"MeshNode({self.x},{self.y})"

def build_2d_mesh(width, height):
    """
    Build lumps-coded 2D mesh: width x height
    Use integer lumps for simplicity.
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
    print("\n===== 2D Mesh Demo =====")
    mesh = build_2d_mesh(3,2)
    for row in mesh:
        print(row)


###############################################################################
# 4. Lumps-coded Trapezoidal Integration
###############################################################################

def lumps_trap_func(x: Lump):
    # f(x)= x^2 + 1, lumps-coded
    # x*x + Lump(1)
    one = Lump(1)
    return x*x + one

def lumps_trapezoid_integration(a: Lump, b: Lump, n_steps: int):
    """
    lumps-coded integration of f(x)= x^2+1 from x=a..b with n_steps intervals
    """
    if b < a:
        raise ValueError("b < a in lumps-coded trapezoid?")
    # step = (b-a)/n_steps
    step = (b - a)/Lump(n_steps)
    # sum => f(a)+f(b)
    total = lumps_trap_func(a) + lumps_trap_func(b)
    x = a
    # middle sums
    for i in range(1, n_steps):
        x = x + step
        total = total + (Lump(2)*lumps_trap_func(x))
    # result => step/2 * total
    return (step/Lump(2))*total

def demo_trapezoid():
    print("\n===== Lumps-coded Trapezoidal Demo =====")
    a = Lump(0)
    b = Lump(5)
    n = 5
    area_approx = lumps_trapezoid_integration(a,b,n)
    print(f"Trapezoid area ~ {area_approx}")


###############################################################################
# 5. Simple ODE/PDE Discretization
###############################################################################

def lumps_forward_diff(yvals, dx: Lump):
    """
    Forward difference derivative approx: (y[i+1]-y[i])/dx
    returns lumps-coded array of len(yvals)-1
    """
    derivs=[]
    n = len(yvals)
    for i in range(n-1):
        slope = (yvals[i+1] - yvals[i])/dx
        derivs.append(slope)
    return derivs

def lumps_ode_demo():
    """
    Suppose y(x)= x^2+1 for x=0..4, lumps-coded steps dx=1
    forward diff => derivative
    """
    print("\n===== lumps-coded ODE Demo =====")
    dx = Lump(1)
    # y(0..4)
    yv = []
    for xint in range(5):
        xL = Lump(xint)
        yv.append(xL*xL + Lump(1))
    # derivative
    deriv_approx = lumps_forward_diff(yv, dx)
    print("y=", yv)
    print("dy/dx forward approx =>", deriv_approx)

def lumps_heat_step(u, alpha: Lump):
    """
    1D heat eq step:
    u[i]^(n+1)= u[i]^n + alpha*(u[i+1]-2u[i]+u[i-1])
    lumps-coded BC => 0 at boundary
    """
    n=len(u)
    nextu = [v for v in u]
    for i in range(1,n-1):
        mid = u[i+1] - Lump(2)*u[i] + u[i-1]
        nextu[i] = u[i] + alpha*mid
    # boundary => 0
    nextu[0]=Lump(0)
    nextu[-1]=Lump(0)
    return nextu

def lumps_pde_demo():
    """
    Small lumps-coded PDE heat step:
      domain x=0..4 with dx=1 => 5 lumps
    alpha=1/2
    We'll do 2 steps for demonstration
    """
    print("\n===== lumps-coded PDE Heat Demo =====")
    # initial
    u = [Lump(0),Lump(3),Lump(6), Lump(3), Lump(0)]
    alpha=Lump(1,2)
    print("u(0)=", u)
    for step in range(2):
        u = lumps_heat_step(u, alpha)
        print(f"u({step+1})=", u)


###############################################################################
# Putting it all together
###############################################################################

def main():
    # 1) Gauss-Jordan
    demo_gauss_jordan()

    # 2) 2D Mesh
    demo_2d_mesh()

    # 3) lumps-coded trapezoid integration
    demo_trapezoid()

    # 4) lumps-coded ODE forward difference
    lumps_ode_demo()

    # 5) lumps-coded PDE heat step
    lumps_pde_demo()

if __name__=="__main__":
    main()