#!/usr/bin/env python3
"""
A Toy Example of a 'Lumped' Approach to PDE Discretization
Here we model 1D diffusion (u_t = D * u_xx) with a basic cell-averaged method.

We subdivide the domain into 'lumps' (cells). Each cell holds a single average value
for the solution. Over each time step, we update those values by approximating
the flux of neighboring cells. This is akin to a cell-centered finite volume approach,
but kept as simple as possible to illustrate 'lumping' the domain into chunks.
"""

import numpy as np
import matplotlib.pyplot as plt

def initial_condition(x):
    """
    Example initial condition: a Gaussian bump in the middle.
    You can change this to anything you like.
    """
    return np.exp(-50.0 * (x - 0.5)**2)

def lumped_diffusion_1D(n_cells=50, D=0.01, dt=0.0005, tmax=0.1):
    """
    Solve the 1D diffusion equation with a 'lumped' approach:
        u_t = D * u_xx

    Domain: x in [0,1]
    We subdivide [0,1] into n_cells lumps, each cell having uniform average u.
    We use a simple finite difference approximation of flux between adjacent lumps.

    Parameters
    ----------
    n_cells : int
        Number of lumps (cells) in the spatial domain.
    D : float
        Diffusion coefficient.
    dt : float
        Time step size.
    tmax : float
        Final time for simulation.

    Returns
    -------
    x_centers : numpy array
        Spatial centers of each lump.
    u : numpy array
        Final solution (lumped values) at time tmax.
    """
    # 1) Setup the domain
    dx = 1.0 / n_cells  # cell width
    x_centers = np.linspace(dx/2, 1.0 - dx/2, n_cells)  # midpoint of each lump

    # 2) Initialize solution
    u = initial_condition(x_centers)

    # 3) Number of time steps
    n_steps = int(tmax / dt)

    # 4) March in time
    for step in range(n_steps):
        # We'll store next-step in u_next, then overwrite
        u_next = np.copy(u)

        # 'Flux' between lumps i and i+1
        # For a simple 1D diffusion, approximate flux by F_{i+1/2} ~ -D * (u_{i+1} - u_i)/dx
        # Then the cell i's new value is updated from flux in - flux out.
        # With 'lumping', each cell is uniform, so the flux is straightforward.

        for i in range(n_cells):
            # left neighbor
            iL = i - 1 if i > 0 else i  # if we use Neumann or Dirichlet, handle BC
            # right neighbor
            iR = i + 1 if i < n_cells - 1 else i

            # gradient to left neighbor
            flux_left  = -D * (u[i] - u[iL]) / dx
            # gradient to right neighbor
            flux_right = -D * (u[iR] - u[i]) / dx

            # If we want zero-flux BCs, we can do: iL= i if i==0, iR= i if i==n_cells-1
            # or do a separate condition. Right now, this lumps approach basically duplicates
            # the boundary lumps if i=0 or i=n_cells-1. That implies zero gradient at boundary.

            # net flux in is (flux_left) - (flux_right) if we define flux in as negative gradient to the left
            # but let's do a direct FD style:
            #   du/dt ~ (flux_in_left + flux_in_right)/(dx)
            # Actually, lumps approach: dU_i/dt = [F_{i-1/2} - F_{i+1/2}]/dx
            # where F_{i+1/2}= -D*(u[i+1]-u[i])/dx is the flux out of i. We'll keep it simpler.

            # net flux * dt / dx:
            #    + flux_left = inflow from left
            #    + flux_right = inflow from right
            # But note: flux_right is negative if u[iR]<u[i], etc.
            # We'll just do a direct standard approach for diffusion.

            # For lumps, the new value is:
            u_next[i] = u[i] + dt/dx * (flux_left + flux_right)

        # Overwrite
        u = u_next

    return x_centers, u

def main():
    # parameters
    n_cells = 60
    D = 0.02
    dt = 0.0004
    tmax = 0.1

    x_centers, u_final = lumped_diffusion_1D(n_cells, D, dt, tmax)

    # Plot the result
    plt.figure(figsize=(8,5))
    plt.plot(x_centers, u_final, 'o-', label='Lumped Diffusion, final t=%.3f'%tmax)
    plt.xlabel("x")
    plt.ylabel("u")
    plt.title("1D Diffusion with a Lumped/Cell-Averaged Approach")
    plt.legend()
    plt.grid(True)
    plt.show()

if __name__ == "__main__":
    main()