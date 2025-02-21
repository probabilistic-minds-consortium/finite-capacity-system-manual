#!/usr/bin/env python3
"""
PDE_3.py

A toy example of a grains-coded approach to PDE discretization.
We model 1D diffusion (u_t = D * u_xx) using a basic cell-averaged (finite volume) method.
The spatial domain [0,1] is subdivided into a finite number of cells (“grains”).
All arithmetic is performed exactly using finite-coded rational arithmetic.
No floating-point operations or infinite constructs are used in the core simulation.
"""

import matplotlib.pyplot as plt

###############################################################################
# 1. Grain Class (Finite-Coded Rational Arithmetic)
###############################################################################

from math import gcd

class Grain:
    """
    Grain: a finite-coded fraction represented as an integer numerator (n) and denominator (d).
    All operations (addition, subtraction, multiplication, division) are performed exactly
    using integer arithmetic. No floating-point arithmetic is used internally.
    """
    def __init__(self, numerator: int, denominator: int = 1):
        if denominator == 0:
            raise ValueError("Denominator cannot be zero in Grain.")
        if not (isinstance(numerator, int) and isinstance(denominator, int)):
            raise TypeError("Grain requires integer numerator and denominator.")
        sign = -1 if (numerator * denominator < 0) else 1
        num = abs(numerator)
        den = abs(denominator)
        g = gcd(num, den)
        self.n = sign * (num // g)
        self.d = den // g

    def __repr__(self):
        return f"Grain({self.n}/{self.d})"

    def to_float(self):
        """For display only: convert to a float."""
        return self.n / self.d

    # Arithmetic operations:
    def __add__(self, other):
        if not isinstance(other, Grain):
            raise TypeError("Grain can only be added to another Grain.")
        new_num = self.n * other.d + other.n * self.d
        new_den = self.d * other.d
        return Grain(new_num, new_den)

    def __sub__(self, other):
        if not isinstance(other, Grain):
            raise TypeError("Grain can only be subtracted by another Grain.")
        new_num = self.n * other.d - other.n * self.d
        new_den = self.d * other.d
        return Grain(new_num, new_den)

    def __mul__(self, other):
        if not isinstance(other, Grain):
            raise TypeError("Grain can only be multiplied by another Grain.")
        return Grain(self.n * other.n, self.d * other.d)

    def __truediv__(self, other):
        if not isinstance(other, Grain):
            raise TypeError("Grain can only be divided by another Grain.")
        if other.n == 0:
            raise ZeroDivisionError("Division by zero in Grain arithmetic.")
        return Grain(self.n * other.d, self.d * other.n)

    def __neg__(self):
        return Grain(-self.n, self.d)

    # Comparison operators:
    def __eq__(self, other):
        if not isinstance(other, Grain):
            return False
        return self.n == other.n and self.d == other.d

    def __lt__(self, other):
        return self.n * other.d < other.n * self.d

    def __le__(self, other):
        return self.n * other.d <= other.n * other.d

    def __gt__(self, other):
        return self.n * other.d > other.n * self.d

    def __ge__(self, other):
        return self.n * other.d >= other.n * other.d

###############################################################################
# 2. Finite-Coded Exponential Function (Taylor Series)
###############################################################################

def finite_exp(x: Grain, terms=12):
    """
    Compute exp(x) as a finite-coded approximation using the Taylor series:
       exp(x) = sum_{n=0}^{terms-1} x^n / n!
    All operations use Grain arithmetic.
    """
    result = Grain(1)  # term for n=0: 1
    term = Grain(1)
    for n in range(1, terms):
        term = term * x / Grain(n)
        result = result + term
    return result

###############################################################################
# 3. Finite-Coded Initial Condition
###############################################################################

def initial_condition(x: Grain):
    """
    Compute the initial condition:
        u(x) = exp(-((x - 1/2)/1/10)^2)
    using finite-coded arithmetic.
    """
    half = Grain(1,2)
    tenth = Grain(1,10)
    diff = x - half
    ratio = diff / tenth
    ratio_sq = ratio * ratio
    # Compute negative value: 0 - ratio_sq
    neg_ratio_sq = Grain(0) - ratio_sq
    return finite_exp(neg_ratio_sq, terms=12)

###############################################################################
# 4. PDE 1D Diffusion Simulation (Grains-Coded)
###############################################################################

def grains_diffusion_1D(n_cells=21, total_time=Grain(2,100), dt=Grain(2,1000)):
    """
    Solve the 1D diffusion equation u_t = D * u_xx using a grains-coded cell-averaged approach.
    
    Domain: x in [0, 1]
    n_cells: number of grid points.
    D: Diffusion coefficient (finite-coded, defined below).
    dt: Time step (finite-coded).
    total_time: Final time (finite-coded).
    
    Returns:
       x_centers: list of Grain representing cell centers.
       u: final solution as list of Grain.
    """
    # Configuration constants as finite-coded values:
    L = Grain(1)  # Domain size = 1
    NX = n_cells  # Number of grid points
    DX = L / Grain(NX - 1)  # Cell width
    D = Grain(3,10)         # Diffusion coefficient = 0.3

    # Build x_centers using a loop (center of each cell: (i + 0.5) / (NX - 1))
    x_centers = []
    for i in range(NX):
        center = (Grain(i) + Grain(1,2)) / Grain(NX - 1)
        x_centers.append(center)

    # Initialize solution u with the initial condition computed using finite_exp.
    u = []
    for x in x_centers:
        u_val = initial_condition(x)
        u.append(u_val)
    # Enforce boundary conditions: u[0] = u[NX-1] = Grain(0)
    zero_val = Grain(0)
    u[0] = zero_val
    u[-1] = zero_val

    # Compute the finite-coded coefficient: factor = D * (dt / (DX * DX))
    factor = D * (dt / (DX * DX))

    # Determine the number of time steps: total_time/dt (assuming dt divides total_time exactly)
    n_steps = 0
    current_time = Grain(0)
    while current_time < total_time:
        n_steps += 1
        current_time = current_time + dt

    # Time stepping loop: update u using a finite difference approximation.
    for step in range(n_steps):
        u_next = u[:]  # Copy current state
        for i in range(1, NX - 1):
            laplacian = u[i+1] - Grain(2)*u[i] + u[i-1]
            u_next[i] = u[i] + factor * laplacian
        # Enforce boundary conditions
        u_next[0] = zero_val
        u_next[-1] = zero_val
        u = u_next

    return x_centers, u

###############################################################################
# 5. Main: Run the Diffusion Simulation and Plot the Result
###############################################################################

def main():
    # Set simulation parameters using finite-coded values
    NX = 21
    dt = Grain(2, 1000)         # 0.002 as a fraction 2/1000
    total_time = Grain(2, 100)   # 0.02 as a fraction 2/100

    x_centers, u_final = grains_diffusion_1D(n_cells=NX, total_time=total_time, dt=dt)

    # For plotting, convert finite-coded (Grain) values to floats (display conversion only)
    x_vals = [x.to_float() for x in x_centers]
    u_vals = [u.to_float() for u in u_final]

    # Plot the result
    plt.figure(figsize=(8,5))
    plt.plot(x_vals, u_vals, 'o-', label=f'Grains-coded Diffusion, final t={total_time.to_float():.3f}')
    plt.xlabel("x")
    plt.ylabel("u")
    plt.title("1D Diffusion with a Grains-Coded (Finite) Approach")
    plt.legend()
    plt.grid(True)
    plt.show()

if __name__ == "__main__":
    main()