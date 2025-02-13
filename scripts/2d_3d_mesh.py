#!/usr/bin/env python3

class Lump:
    """
    A minimal lumps-coded fraction class, storing numerator (num) and denominator (den).
    This is a simple version, suitable for small integer-based examples.
    """
    def __init__(self, num, den=1):
        if den == 0:
            raise ValueError("Denominator cannot be zero in a lumps-coded fraction.")
        self.num = num
        self.den = den

    def __repr__(self):
        return f"Lump({self.num}/{self.den})"

class MeshNode:
    """Represents a lumps-coded 2D mesh node (x, y). Stores lumps-coded coords and adjacency."""
    def __init__(self, x_lump, y_lump):
        self.x = x_lump
        self.y = y_lump
        self.neighbors = []  # references to other MeshNode objects

    def __repr__(self):
        # e.g. MeshNode(2/1, 3/1) if x=2, y=3
        return f"MeshNode({self.x.num}/{self.x.den}, {self.y.num}/{self.y.den})"

def build_2d_mesh(nx, ny):
    """
    Create a lumps-coded mesh of size nx x ny, with integer lumps-coded
    coordinates and 8-way adjacency (including diagonals).
    """
    # Create the node grid
    nodes = []
    for i in range(nx):
        row_nodes = []
        for j in range(ny):
            node = MeshNode(Lump(i), Lump(j))
            row_nodes.append(node)
        nodes.append(row_nodes)

    # Link neighbors: 8 possible directions
    directions = [
        (1, 0), (-1, 0), (0, 1), (0, -1),   # up/down/left/right
        (1, 1),  (1, -1), (-1, 1), (-1, -1) # diagonals
    ]
    for i in range(nx):
        for j in range(ny):
            node = nodes[i][j]
            for di, dj in directions:
                ni, nj = i + di, j + dj
                if 0 <= ni < nx and 0 <= nj < ny:
                    node.neighbors.append(nodes[ni][nj])

    return nodes

if __name__ == "__main__":
    # Example usage: build a 3x2 mesh and print adjacency
    mesh = build_2d_mesh(3, 2)
    print("Lumps-coded 2D mesh with 8-way adjacency:")
    for row in mesh:
        for node in row:
            neigh_list = [
                f"({n.x.num}/{n.x.den}, {n.y.num}/{n.y.den})" for n in node.neighbors
            ]
            print(f"{node} neighbors: {neigh_list}")