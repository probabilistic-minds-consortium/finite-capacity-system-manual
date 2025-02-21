#!/usr/bin/env python3
"""
PDE_1.py

A Toy Example of a grains-coded approach to PDE Discretization.
We model 1D diffusion (u_t = D * u_xx) with a basic cell-averaged method.
The spatial domain [0,1] is subdivided into a finite number of cells ("grains").
Each cell holds an average value (a Grain). Over each time step, we update these values 
by approximating the flux between neighboring cells using finite-coded arithmetic.
No floating-point or infinite operations are used in the core simulation.
"""

import matplotlib.pyplot as plt

###############################################################################
# 1. Grain Class (Finite-Coded Rational Arithmetic)
###############################################################################

from math import gcd

class Grain:
    """
    Grains-coded fraction:
      - Stored as integer numerator (n) and denominator (d)
      - All operations are performed exactly using integer arithmetic.
      - No floating-point arithmetic is used internally.
    """
    def __init__(self, numerator: int, denominator: int = 1):
        if denominator == 0:
            raise ValueError("Denominator cannot be zero in grains-coded rational.")
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
        """Convert to a float for display only."""
        return self.n / self.d

    # Arithmetic operations:
    def __add__(self, other):
        if not isinstance(other, Grain):
            raise TypeError("Grain can only be added with another Grain.")
        new_num = self.n * other.d + other.n * self.d
        new_den = self.d * other.d
        return Grain(new_num, new_den)

    def __sub__(self, other):
        return self.__add__(Grain(-other.n, other.d))

    def __mul__(self, other):
        if not isinstance(other, Grain):
            raise TypeError("Grain can only be multiplied with another Grain.")
        return Grain(self.n * other.n, self.d * other.d)

    def __truediv__(self, other):
        if not isinstance(other, Grain):
            raise TypeError("Grain can only be divided by another Grain.")
        if other.n == 0:
            raise ZeroDivisionError("Division by zero in grains-coded arithmetic.")
        return Grain(self.n * other.d, self.d * other.n)

    # Comparison operators (for use in algorithms):
    def __eq__(self, other):
        if not isinstance(other, Grain):
            return False
        return self.n == other.n and self.d == other.d

    def __lt__(self, other):
        return self.n * other.d < other.n * self.d

    def __le__(self, other):
        return self.n * other.d <= other.n * self.d

    def __gt__(self, other):
        return self.n * other.d > other.n * self.d

    def __ge__(self, other):
        return self.n * other.d >= other.n * self.d

###############################################################################
# 2. 1D Diffusion Simulation Using Grains-Coded Arithmetic
###############################################################################

def grains_diffusion_1D(n_cells=50, D=Grain(1,100), dt=Grain(1,2000), n_steps=200):
    """
    Simulate 1D diffusion (u_t = D * u_xx) using a finite-coded approach.
    
    Domain: x in [0,1] divided into n_cells cells.
    D: Diffusion coefficient as a Grain (e.g., 1/100 for D=0.01).
    dt: Time step as a Grain (e.g., 1/2000 for dt=0.0005).
    n_steps: Number of time steps to simulate.
    
    The update rule for each interior cell (i) is:
      u_new[i] = u[i] - D * (dt / (dx * dx)) * (u[i+1] - 2*u[i] + u[i-1])
    Boundary conditions: u[0] and u[n_cells-1] are fixed at Grain(0).
    
    Returns:
      x_centers: List of Grain representing cell centers.
      u: Final solution as a list of Grain.
    """
    # dx = 1 / n_cells
    dx = Grain(1, n_cells)
    
    # Build x_centers: for i=0..n_cells-1, center = (i + 0.5)/n_cells
    # Represent 0.5 as Grain(1,2); then center = (Grain(i) + Grain(1,2)) / Grain(n_cells)
    x_centers = []
    for i in range(n_cells):
        center = (Grain(i) + Grain(1,2)) / Grain(n_cells)
        x_centers.append(center)
    
    # Initial condition: set the middle cell to a nonzero value (e.g., Grain(10)) and others to Grain(0)
    u = [Grain(0) for _ in range(n_cells)]
    mid = n_cells // 2
    u[mid] = Grain(10)

    # Compute finite coefficient: factor = D * (dt / (dx * dx))
    factor = D * (dt / (dx * dx))

    # Time stepping loop
    for step in range(n_steps):
        u_new = u[:]  # Create a copy
        for i in range(1, n_cells - 1):
            laplacian = u[i+1] - Grain(2) * u[i] + u[i-1]
            u_new[i] = u[i] - factor * laplacian
        # Enforce boundary conditions: u[0] = u[n_cells-1] = Grain(0)
        u_new[0] = Grain(0)
        u_new[-1] = Grain(0)
        u = u_new

    return x_centers, u

###############################################################################
# 3. Main: Run the 1D Diffusion Simulation and Plot the Result
###############################################################################

def main():
    # Set parameters for the simulation
    n_cells = 50
    D = Grain(1, 100)        # Diffusion coefficient 1/100
    dt = Grain(1, 2000)      # Time step 1/2000
    n_steps = 200

    x_centers, u_final = grains_diffusion_1D(n_cells, D, dt, n_steps)

    # Convert final u values to floats for plotting (only for display)
    x_vals = [center.to_float() for center in x_centers]
    u_vals = [cell.to_float() for cell in u_final]

    # Plot the result using matplotlib (display conversion only)
    plt.figure(figsize=(8,5))
    plt.plot(x_vals, u_vals, 'o-', label=f'Finite-coded Diffusion, {n_steps} steps')
    plt.xlabel("x")
    plt.ylabel("u")
    plt.title("1D Diffusion with a Grains-Coded (Finite) Approach")
    plt.legend()
    plt.grid(True)
    plt.show()

if __name__ == "__main__":
    main()