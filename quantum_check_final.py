from fractions import Fraction
import math

class BlockNode2D:
    """
    A block covering [x_min..x_max] x [y_min..y_max].
    'prob' is lumps-coded fraction. 'vantage' is local max denominator.
    'children' is either None (leaf) or a list of up to 4 sub-blocks.
    """

    __slots__ = ('x_min','x_max','y_min','y_max','prob','vantage','children')

    def __init__(self, x_min, x_max, y_min, y_max, prob=Fraction(0,1), vantage=100):
        self.x_min  = x_min
        self.x_max  = x_max
        self.y_min  = y_min
        self.y_max  = y_max
        self.prob   = prob
        self.vantage= vantage
        self.children = None  # None => leaf

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

# ---------------------------------------------------------------------
# Lumps-Coded Routines
# ---------------------------------------------------------------------

def sum_tree_2d(node):
    """Return lumps-coded sum of leaf probabilities."""
    if node.is_leaf():
        return node.prob
    s = Fraction(0,1)
    for c in node.children:
        s += sum_tree_2d(c)
    return s

def scale_tree_2d(node, factor):
    """Multiply each leaf's probability by 'factor' lumps-coded."""
    if node.is_leaf():
        node.prob *= factor
        refine_vantage_if_needed_2d(node)
    else:
        for c in node.children:
            scale_tree_2_2d(c, factor)

def scale_tree_2_2d(node, factor):
    # Because Python doesn’t allow calling the same function from inside,
    # we do a small subfunction to avoid confusion. 
    # But we can just inline it or rename. We'll just replicate for clarity.
    if node.is_leaf():
        node.prob *= factor
        refine_vantage_if_needed_2d(node)
    else:
        for c in node.children:
            scale_tree_2_2d(c, factor)

def normalize_tree_2d(node):
    total = sum_tree_2d(node)
    if total>0 and total!=1:
        factor = Fraction(1,1)/total
        scale_tree_2_2d(node, factor)

def refine_vantage_if_needed_2d(block):
    """
    If block.prob < 1/block.vantage, enlarge vantage so we can store that fraction.
    """
    if block.prob==0 or block.prob==1:
        return
    if block.prob < Fraction(1, block.vantage):
        inv = Fraction(1,1) / block.prob
        new_v = inv.numerator // inv.denominator
        if inv.numerator % inv.denominator != 0:
            new_v += 1
        # ensure vantage strictly grows
        new_v = max(new_v, block.vantage+1)
        block.vantage = new_v

def set_probability_2d(block, new_prob):
    block.prob = new_prob
    refine_vantage_if_needed_2d(block)

def get_leaves_2d(node, leaves=None):
    """Collect all leaves in ascending order of x_min,y_min for convenience."""
    if leaves is None: leaves=[]
    if node.is_leaf():
        leaves.append(node)
    else:
        for c in node.children:
            get_leaves_2d(c, leaves)
    return leaves

# ---------------------------------------------------------------------
# Splitting / Merging
# ---------------------------------------------------------------------

def split_block_2d(node):
    """
    Quadrant-split a leaf if area>1, distributing node.prob equally among children.
    """
    if not node.is_leaf():
        return
    if node.area()<=1:
        return  # can't split further

    x_mid = (node.x_min + node.x_max)//2
    y_mid = (node.y_min + node.y_max)//2

    base_prob = node.prob / 4

    def mk_child(x0,x1,y0,y1, pr):
        if x0<=x1 and y0<=y1:
            c = BlockNode2D(x0,x1,y0,y1, prob=pr, vantage=node.vantage)
            return c
        return None

    c1 = mk_child(node.x_min, x_mid,     node.y_min, y_mid,     base_prob) # bottom-left
    c2 = mk_child(x_mid+1, node.x_max,  node.y_min, y_mid,     base_prob) # bottom-right
    c3 = mk_child(node.x_min, x_mid,     y_mid+1,   node.y_max, base_prob)# top-left
    c4 = mk_child(x_mid+1, node.x_max,  y_mid+1,   node.y_max, base_prob)# top-right

    new_children = [cc for cc in (c1,c2,c3,c4) if cc is not None]
    if len(new_children)>1:
        node.children = new_children
        node.prob = Fraction(0,1)  # internal node
    # else no real split

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
    - If leaf node prob >= split_thresh, we split (if area>1).
    - If internal node's children sum < merge_thresh, we merge them.
    - Recurse.
    """
    if node.is_leaf():
        if node.area()>1 and node.prob >= split_thresh:
            split_block_2d(node)
    else:
        # recurse
        for c in node.children:
            adaptive_split_merge_2d(c, split_thresh, merge_thresh)
        # check merge
        total = Fraction(0,1)
        for c in node.children:
            total += sum_tree_2d(c)
        if total < merge_thresh:
            merge_block_2d(node)

# ---------------------------------------------------------------------
# Neighbors & Flow
# ---------------------------------------------------------------------

def is_neighbor_2d(a, b):
    """
    True if blocks a,b share an edge in 2D coordinate space.
    They must have matching range in one dimension & abut in the other.
    """
    # horizontally adjacent?
    horiz_touch = (a.x_max+1 == b.x_min or b.x_max+1 == a.x_min)
    y_overlap = not (a.y_max < b.y_min or b.y_max < a.y_min)
    if horiz_touch and y_overlap:
        return True

    # vertically adjacent?
    vert_touch = (a.y_max+1 == b.y_min or b.y_max+1 == a.y_min)
    x_overlap = not (a.x_max < b.x_min or b.x_max < a.x_min)
    if vert_touch and x_overlap:
        return True

    return False

def find_neighbors_2d(leaves):
    """
    Return a list of lists: neighbor_map[i] = [indices j that neighbor i].
    O(n^2) approach for clarity.
    """
    n = len(leaves)
    neighbor_map = [[] for _ in range(n)]
    for i in range(n):
        for j in range(i+1, n):
            if is_neighbor_2d(leaves[i], leaves[j]):
                neighbor_map[i].append(j)
                neighbor_map[j].append(i)
    return neighbor_map

def flow_step_2d(root, alpha=Fraction(1,10), boundary='closed'):
    """
    Each leaf block pushes alpha of its lumps-coded prob to neighbors if boundary='closed'.
    If boundary='open', any leaf lacking neighbors in some direction might lose that portion
    of outflow. We'll do a simpler approach: we just split outflow equally among neighbors.

    Steps:
      1) Gather leaves, find neighbors.
      2) old_probs = [leaf.prob...]
      3) outflow = alpha * old_probs[i], remainder = old_probs[i] - outflow
      4) portion = outflow / len(neighbors)
      5) sum up new probabilities
      6) assign lumps-coded back
    """
    leaves = get_leaves_2d(root)
    neighbor_map = find_neighbors_2d(leaves)
    old_probs = [leaf.prob for leaf in leaves]
    new_probs = [Fraction(0,1) for _ in leaves]

    for i, p_i in enumerate(old_probs):
        outflow = p_i * alpha
        remainder = p_i - outflow
        new_probs[i] += remainder

        nbrs = neighbor_map[i]
        if nbrs:
            portion = outflow / len(nbrs)
            for j in nbrs:
                new_probs[j] += portion
        else:
            # if boundary='open', we lose outflow
            # if boundary='closed', you'd add it back to leaf i or reflect, etc.
            if boundary=='closed':
                # reflect back
                new_probs[i] += outflow

    # re-assign lumps-coded
    for i, block in enumerate(leaves):
        set_probability_2d(block, new_probs[i])

# ---------------------------------------------------------------------
# Demo: Put It All Together
# ---------------------------------------------------------------------

def main():
    # We'll define a 16x16 domain for a more interesting scale
    root = BlockNode2D(0,15,0,15, prob=Fraction(1,1), vantage=50)

    steps = 10
    alpha = Fraction(1,10)
    for step in range(steps):
        # 1) Flow
        flow_step_2d(root, alpha=alpha, boundary='open')
        # 2) Normalize
        normalize_tree_2d(root)
        # 3) Adaptive split/merge
        adaptive_split_merge_2d(root, split_thresh=Fraction(1,5), merge_thresh=Fraction(1,300))

    # final
    print_tree_2d(root)
    total = sum_tree_2d(root)
    print(f"Final lumps-coded prob = {float(total):.4f}")

def print_tree_2d(node, depth=0):
    indent = "  "*depth
    if node.is_leaf():
        print(f"{indent}Leaf [({node.x_min},{node.y_min})-({node.x_max},{node.y_max})] p={node.prob} v={node.vantage} ~ {float(node.prob):.4f}")
    else:
        print(f"{indent}Node [({node.x_min},{node.y_min})-({node.x_max},{node.y_max})] v={node.vantage}")
        for c in node.children:
            print_tree_2d(c, depth+1)

if __name__=="__main__":
    main()