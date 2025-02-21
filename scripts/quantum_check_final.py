#!/usr/bin/env python3
"""
quantum_check_final.py

A toy example of a grains-coded approach to PDE discretization.
We model 1D diffusion using a cell-averaged (finite volume) method.
The domain is subdivided into cells (blocks). Each block holds a finite-coded probability.
All arithmetic is performed using exact fractions (from Python’s Fraction) – no floating point or infinite constructs.
"""

from fractions import Fraction
import math

###############################################################################
# 1. BlockNode2D Class (Finite-Coded)
###############################################################################

class BlockNode2D:
    """
    A block covering [x_min..x_max] x [y_min..y_max].
    'prob' is a grains-coded fraction (a Fraction instance).
    'vantage' is the local maximum denominator.
    'children' is either None (indicating a leaf) or a list of up to 4 sub-blocks.
    """
    __slots__ = ('x_min', 'x_max', 'y_min', 'y_max', 'prob', 'vantage', 'children')

    def __init__(self, x_min, x_max, y_min, y_max, prob=Fraction(0,1), vantage=100):
        self.x_min  = x_min
        self.x_max  = x_max
        self.y_min  = y_min
        self.y_max  = y_max
        self.prob   = prob
        self.vantage = vantage
        self.children = None  # None indicates a leaf node

    def is_leaf(self):
        return (self.children is None)

    def width(self):
        return self.x_max - self.x_min + 1

    def height(self):
        return self.y_max - self.y_min + 1

    def area(self):
        return self.width() * self.height()

    def __repr__(self):
        if self.is_leaf():
            return (f"Leaf[({self.x_min},{self.y_min})-({self.x_max},{self.y_max})] "
                    f"p={self.prob} v={self.vantage}")
        else:
            return (f"Node[({self.x_min},{self.y_min})-({self.x_max},{self.y_max})] "
                    f"v={self.vantage}")

###############################################################################
# 2. Basic Operations on the Block Tree
###############################################################################

def sum_tree_2d(node):
    """Return the grains-coded sum of leaf probabilities in the tree."""
    if node.is_leaf():
        return node.prob
    s = Fraction(0,1)
    for c in node.children:
        s += sum_tree_2d(c)
    return s

def scale_tree_2d(node, factor):
    """Multiply each leaf's probability by the given factor (a Fraction)."""
    if node.is_leaf():
        node.prob *= factor
        refine_vantage_if_needed_2d(node)
    else:
        for c in node.children:
            scale_tree_2d(c, factor)

def normalize_tree_2d(node):
    total = sum_tree_2d(node)
    if total > 0 and total != 1:
        factor = Fraction(1,1) / total
        scale_tree_2d(node, factor)

def refine_vantage_if_needed_2d(block):
    """
    If block.prob is less than 1/block.vantage, update the block's vantage so that the
    fraction can be represented more precisely.
    """
    if block.prob == 0 or block.prob == 1:
        return
    if block.prob < Fraction(1, block.vantage):
        inv = Fraction(1,1) / block.prob
        new_v = inv.numerator // inv.denominator
        if inv.numerator % inv.denominator != 0:
            new_v += 1
        new_v = max(new_v, block.vantage + 1)
        block.vantage = new_v

def set_probability_2d(block, new_prob):
    block.prob = new_prob
    refine_vantage_if_needed_2d(block)

def get_leaves_2d(node, leaves=None):
    """Collect all leaf nodes in ascending order of (x_min, y_min)."""
    if leaves is None:
        leaves = []
    if node.is_leaf():
        leaves.append(node)
    else:
        for c in node.children:
            get_leaves_2d(c, leaves)
    return leaves

###############################################################################
# 3. Splitting and Merging
###############################################################################

def split_block_2d(node):
    """
    Split a leaf block into up to four sub-blocks (quadrants) if the area is greater than 1.
    Distribute node.prob equally among the children.
    """
    if not node.is_leaf():
        return
    if node.area() <= 1:
        return  # Cannot split further

    x_mid = (node.x_min + node.x_max) // 2
    y_mid = (node.y_min + node.y_max) // 2

    base_prob = node.prob / 4

    def mk_child(x0, x1, y0, y1, pr):
        if x0 <= x1 and y0 <= y1:
            return BlockNode2D(x0, x1, y0, y1, prob=pr, vantage=node.vantage)
        return None

    c1 = mk_child(node.x_min, x_mid,     node.y_min, y_mid,     base_prob)  # bottom-left
    c2 = mk_child(x_mid+1, node.x_max,  node.y_min, y_mid,     base_prob)  # bottom-right
    c3 = mk_child(node.x_min, x_mid,     y_mid+1,   node.y_max, base_prob)  # top-left
    c4 = mk_child(x_mid+1, node.x_max,  y_mid+1,   node.y_max, base_prob)  # top-right

    new_children = [c for c in (c1, c2, c3, c4) if c is not None]
    if len(new_children) > 1:
        node.children = new_children
        node.prob = Fraction(0, 1)  # Internal nodes store no probability.
        
def merge_block_2d(node):
    if node.is_leaf():
        return
    total = Fraction(0,1)
    for c in node.children:
        total += sum_tree_2d(c)
    node.prob = total
    node.children = None

def adaptive_split_merge_2d(node, split_thresh=Fraction(1,5), merge_thresh=Fraction(1,200)):
    """
    Recursively adapt the block tree:
      - If a leaf's probability is at least split_thresh and the area > 1, split it.
      - If an internal node's total probability is below merge_thresh, merge its children.
    """
    if node.is_leaf():
        if node.area() > 1 and node.prob >= split_thresh:
            split_block_2d(node)
    else:
        for c in node.children:
            adaptive_split_merge_2d(c, split_thresh, merge_thresh)
        total = Fraction(0,1)
        for c in node.children:
            total += sum_tree_2d(c)
        if total < merge_thresh:
            merge_block_2d(node)

###############################################################################
# 4. Neighbors & Flow
###############################################################################

def is_neighbor_2d(a, b):
    """
    Return True if blocks a and b share an edge (are adjacent) in 2D.
    They must have matching ranges in one dimension and be contiguous in the other.
    """
    horiz_touch = (a.x_max + 1 == b.x_min or b.x_max + 1 == a.x_min)
    y_overlap = not (a.y_max < b.y_min or b.y_max < a.y_min)
    if horiz_touch and y_overlap:
        return True

    vert_touch = (a.y_max + 1 == b.y_min or b.y_max + 1 == a.y_min)
    x_overlap = not (a.x_max < b.x_min or b.x_max < a.x_min)
    if vert_touch and x_overlap:
        return True

    return False

def find_neighbors_2d(leaves):
    """
    Return a list of neighbor lists: neighbor_map[i] = [indices j of leaves that neighbor i].
    Uses an O(n^2) approach for clarity.
    """
    n = len(leaves)
    neighbor_map = [[] for _ in range(n)]
    for i in range(n):
        for j in range(i+1, n):
            if is_neighbor_2d(leaves[i], leaves[j]):
                neighbor_map[i].append(j)
                neighbor_map[j].append(i)
    return neighbor_map

def flow_step_2d(root, alpha=Fraction(1,10), boundary='open'):
    """
    Each leaf block transfers a fraction alpha of its grains-coded probability to its neighbors.
    If boundary='open', missing neighbors result in loss of outflow; if 'closed', outflow is reflected.
    
    Process:
      1) Gather leaves and their neighbors.
      2) For each leaf, compute outflow = alpha * p and remainder = p - outflow.
      3) Distribute outflow equally among neighbors.
      4) Reassign updated probability values to leaves.
    """
    leaves = get_leaves_2d(root)
    neighbor_map = find_neighbors_2d(leaves)
    old_probs = [leaf.prob for leaf in leaves]
    new_probs = [Fraction(0,1) for _ in leaves]

    for i, p in enumerate(old_probs):
        outflow = p * alpha
        remainder = p - outflow
        new_probs[i] += remainder
        nbrs = neighbor_map[i]
        if nbrs:
            portion = outflow / len(nbrs)
            for j in nbrs:
                new_probs[j] += portion
        else:
            if boundary == 'closed':
                new_probs[i] += outflow

    for i, block in enumerate(leaves):
        set_probability_2d(block, new_probs[i])

###############################################################################
# 5. Demo: Putting It All Together
###############################################################################

def print_tree_2d(node, depth=0):
    indent = "  " * depth
    if node.is_leaf():
        print(f"{indent}Leaf [({node.x_min},{node.y_min})-({node.x_max},{node.y_max})] p={node.prob} v={node.vantage} ~ {float(node.prob):.4f}")
    else:
        print(f"{indent}Node [({node.x_min},{node.y_min})-({node.x_max},{node.y_max})] v={node.vantage}")
        for c in node.children:
            print_tree_2d(c, depth+1)

def main():
    # Define a 16x16 domain
    root = BlockNode2D(0, 15, 0, 15, prob=Fraction(1,1), vantage=50)

    steps = 10
    alpha = Fraction(1,10)
    for step in range(steps):
        flow_step_2d(root, alpha=alpha, boundary='open')
        normalize_tree_2d(root)
        adaptive_split_merge_2d(root, split_thresh=Fraction(1,5), merge_thresh=Fraction(1,300))
    print_tree_2d(root)
    total = sum_tree_2d(root)
    print(f"Final grains-coded prob = {float(total):.4f}")

if __name__ == "__main__":
    main()