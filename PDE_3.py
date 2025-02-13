

import math

###############################################
# 1) CONFIGURATION / CONSTANTS
###############################################
L = 1.0          # domain size
NX = 21          # number of grid points
DX = L/(NX-1)
D  = 0.3         # diffusion coefficient (bigger so changes are more visible!)
INIT_SCALE = 2.0 # lumps-coded scale factor
INIT_NCAP  = 20  # initial vantage capacity

# Time stepping
DT = 0.002      # bigger dt to see changes
TOTAL_TIME = 0.02

# We want partial sums not to vanish, so let's allow multiple vantage expansions
# if a single partial difference is below 1 lumps step, we'll refine vantage
# up to a max step or we do an iterative approach in multiplication.

REFINE_MAX_STEPS = 5  # how many times we might refine vantage if an operation is about to vanish
REFINE_FACTOR    = 2  # how much we multiply ncap each time

###############################################
# 2) LUMPS-CODED CLASS
###############################################
class LumpsValue:
    """
    Lumps-coded rational representation: value = (k / ncap) * scale.
    We'll do a more cunning multiply that can refine vantage if needed 
    to preserve partial increments.
    """
    def __init__(self, k, ncap, scale):
        self.k = k
        self.ncap = ncap
        self.scale = scale
    
    def to_float(self):
        return (self.k/self.ncap)*self.scale

    @staticmethod
    def encode(real_val, ncap, scale):
        k = int(round((real_val/scale)*ncap))
        return LumpsValue(k, ncap, scale)

    def copy(self):
        return LumpsValue(self.k, self.ncap, self.scale)

    def usage_fraction(self):
        """Return abs(k)/ncap, how 'far' we are in lumps range."""
        return abs(self.k)/self.ncap

    def __repr__(self):
        return f"LumpsValue(k={self.k}, ncap={self.ncap}, scale={self.scale:.2f})"

###############################################
# 3) BASIC ARITHMETIC (IMPROVED)
###############################################
def lumps_unify(a:LumpsValue, b:LumpsValue):
    """
    Unify vantage (ncap) for a,b by picking max(ncap), 
    rescaling k as needed.
    BUT we keep scale consistent, raising error if they differ.
    """
    if a.scale!=b.scale:
        raise ValueError("Scales differ. Keep scale uniform or unify them carefully!")
    if a.ncap==b.ncap:
        return a,b,a.ncap  # done

    new_ncap = max(a.ncap, b.ncap)
    # rescale a
    ak_new = (a.k*new_ncap)//a.ncap if (new_ncap!=a.ncap) else a.k
    # rescale b
    bk_new = (b.k*new_ncap)//b.ncap if (new_ncap!=b.ncap) else b.k

    a_new = LumpsValue(ak_new, new_ncap, a.scale)
    b_new = LumpsValue(bk_new, new_ncap, a.scale)
    return a_new, b_new, new_ncap

def lumps_add(a:LumpsValue, b:LumpsValue):
    a_u,b_u,nc = lumps_unify(a,b)
    return LumpsValue(a_u.k + b_u.k, nc, a_u.scale)

def lumps_sub(a:LumpsValue, b:LumpsValue):
    a_u,b_u,nc = lumps_unify(a,b)
    return LumpsValue(a_u.k - b_u.k, nc, a_u.scale)

def lumps_refine(val:LumpsValue, factor=2):
    """
    Double (or factor) vantage for val. 
    """
    new_ncap = val.ncap*factor
    new_k = (val.k*new_ncap)//val.ncap
    return LumpsValue(new_k, new_ncap, val.scale)

def lumps_mul(a:LumpsValue, b:LumpsValue):
    """
    Attempt a more cunning multiplication: 
    (a.k / a.ncap * a.scale) * (b.k / b.ncap * b.scale)
     = (a.k*b.k)/(a.ncap*b.ncap) * (a.scale*b.scale).

    We'll define a new lumps-coded object. 
    But we want the result to remain in the same scale??? 
    That is tricky if a.scale != b.scale, but we forbid that above. 
    We might unify vantage in steps, plus do some vantage expansions if the product < 1 lumps step.
    """
    # unify vantage first
    a_u, b_u, big_ncap = lumps_unify(a,b)

    # do exact integer multiply for k:  product_k = a_u.k * b_u.k
    product_k = a_u.k*b_u.k

    # the 'raw' vantage is big_ncap^2 if we interpret the ratio: product_k/(big_ncap^2)* scale^2
    # But let's define a new vantage = big_ncap^2 for exact rep. That might be huge. 
    # We'll store it in the same scale (???). 
    # Then value = product_k / (big_ncap^2)* (scale^2).

    # For a comedic approach, let's define result scale = a.scale**2, vantage=some big. 
    # We do want to preserve small increments if possible. Let's define vantage = big_ncap^2. 
    # But that might be enormous. We'll do an iterative approach if we want to keep vantage from meltdown. 
    # Let's be direct for now:

    new_scale = a_u.scale*a_u.scale
    raw_ncap = big_ncap*big_ncap

    # We create lumps-coded object: 
    #   new_k = product_k, new_ncap= raw_ncap, new_scale= new_scale
    # Then if raw_ncap is monstrous, we can reduce it by gcd if possible. 
    # But let's keep it. Then we might refine it or unify vantage with a simpler approach. 
    # We'll do a meltdown approach:

    val = LumpsValue(product_k, raw_ncap, new_scale)

    # if usage fraction is extremely small, we might do vantage expansions ironically in the negative sense?? 
    # It's complicated. We'll keep it simple for now:
    return val

def lumps_scalar(a:LumpsValue, scalar:float):
    """
    multiply lumps-coded a by float scalar => lumps-coded result 
    but do a modest vantage expansion if partial increments vanish
    """
    # repeated approach:
    val = a.to_float() * scalar
    # encode at same vantage for now
    test = LumpsValue.encode(val, a.ncap, a.scale)
    # if test usage is < some small threshold, we might refine vantage. 
    # We'll do an iterative refine at most REFINE_MAX_STEPS times
    step_count=0
    while test.k==0 and abs(val)>1e-14 and step_count<REFINE_MAX_STEPS:
        # refine vantage
        test = lumps_refine(test, factor=REFINE_FACTOR)
        step_count+=1
    return test

###############################################
# PDE: 1D Heat eq solver
###############################################
def refine_if_tiny(u_list):
    """
    If a big chunk of them is near 1 lumps step or partial updates vanish, we refine vantage. 
    We'll do a simpler approach: if usage fraction < some small threshold => refine
    Actually let's do the opposite: if usage fraction is > 0.95 => refine. 
    But we do so for the entire array. We'll keep it simpler.
    """
    # or do we do the partial difference approach? 
    max_usage = 0
    for val in u_list:
        if val.usage_fraction()>max_usage:
            max_usage=val.usage_fraction()
    if max_usage>0.95:
        # refine entire array
        for i, val in enumerate(u_list):
            u_list[i] = lumps_refine(val)
        print(f"[REFINE] vantage doubled to ncap={u_list[0].ncap}")

def heat_step(u_current, alpha):
    """
    Lumps-coded explicit heat step:
      u^{n+1}_j = u^n_j + alpha*(u^n_{j+1} - 2u^n_j + u^n_{j-1})
    We'll do lumps-coded ops carefully, possibly refining vantage if the partial difference is < 1 lumps step.
    """
    n=len(u_current)
    u_next = [v.copy() for v in u_current]
    # boundaries
    # lumps-coded zero
    zero_lumps = LumpsValue.encode(0.0, u_current[0].ncap, u_current[0].scale)
    u_next[0]  = zero_lumps
    u_next[-1] = zero_lumps

    for j in range(1,n-1):
        # diff_expr = (u_{j+1} - 2u_j + u_{j-1})
        # lumps-coded: 
        two = LumpsValue.encode(2.0, u_current[j].ncap, u_current[j].scale)
        tmpA = lumps_sub(u_current[j+1], lumps_mul(two, u_current[j]))
        tmpB = lumps_add(tmpA, u_current[j-1])
        # multiply by alpha
        diff = lumps_mul(alpha, tmpB)
        # final 
        partial = lumps_add(u_current[j], diff)
        # if partial usage fraction < small => refine vantage in partial. 
        # or if partial usage fraction> ~1 => refine. We'll keep it simpler for now:
        u_next[j] = partial

    return u_next

def print_solution(u_arr, label=""):
    dec = [v.to_float() for v in u_arr]
    print(label, " ".join(f"{val:.4f}" for val in dec))

def main():
    # 0) build lumps-coded initial
    xvals = [i*DX for i in range(NX)]
    u = []
    for x in xvals:
        val = math.exp(-((x-0.5)/0.1)**2)  # some gaussian
        lumpsv = LumpsValue.encode(val, INIT_NCAP, INIT_SCALE)
        u.append(lumpsv)
    # boundary => 0
    zero_lumps = LumpsValue.encode(0.0, INIT_NCAP, INIT_SCALE)
    u[0]  = zero_lumps
    u[-1] = zero_lumps

    # lumps-coded alpha
    raw_alpha = D*(DT)/(DX*DX)
    alpha     = LumpsValue.encode(raw_alpha, INIT_NCAP, INIT_SCALE)

    print_solution(u, f"Initial (ncap={INIT_NCAP}):")

    t=0.0
    step=0
    while t<TOTAL_TIME:
        # do step
        step+=1
        # refine if near usage>0.95 
        refine_if_tiny(u)
        # unify alpha vantage if changed
        if alpha.ncap!=u[0].ncap:
            alpha_val = alpha.to_float()
            alpha = LumpsValue.encode(alpha_val, u[0].ncap, alpha.scale)

        u = heat_step(u, alpha)
        t += DT
        # check vantage again if partial difference is small
        refine_if_tiny(u)

        if step%10==0:
            print_solution(u, f"step={step}, t={t:.4f}")

    print_solution(u, f"Final (step={step}, t={t:.4f}):")

if __name__=="__main__":
    main()