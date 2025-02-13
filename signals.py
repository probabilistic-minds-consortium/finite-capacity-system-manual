#!/usr/bin/env python3

"""
signals.py

Demonstration of environment signals and pattern compatibility 
matching Section 1.5 in your manual.

Key elements:
 - A finite set of environment states E (like envA, envB, envC).
 - Each environment e has a set of signals: SignalSet[e].
 - Patterns each have a finite set of features:
     feature_map[x] = {f1, f2, ...}
 - Compatibility: a pattern x is 'compatible' with environment e 
   if feature_map[x] is a subset of SignalSet[e].

We also show how lumps-coded probabilities could be updated 
when switching from env e to env'.
"""

from lump_probability import Mu, set_probability, get_probability, update_probability

# Suppose we define environment states as strings: "envA","envB","envC"
# Each environment has a finite set of signals:
SignalSet = {
    "envA": {"sig1", "sig2"},
    "envB": {"sig2", "sig3"},
    "envC": {"sigX"}
}

# Suppose we define patterns as strings, each with a set of features
feature_map = {
    "patternX": {"sig1"},
    "patternY": {"sig2", "sig3"},
    "patternZ": {"sigX"}
}

def is_compatible(x, e):
    """
    True if pattern x's features are all in SignalSet[e].
    """
    needed_features = feature_map.get(x, set())
    env_signals = SignalSet.get(e, set())
    return needed_features.issubset(env_signals)

def update_env_transition(a, old_e, new_e, capacity, patterns):
    """
    If we transition from environment old_e to new_e for observer a, 
    check each pattern x in 'patterns' for compatibility.
    If it's not compatible, lumps-coded probability => 0.
    Otherwise, preserve lumps-coded lumps (like a 1:1 mapping).
    """
    for x in patterns:
        old_k = Mu.get((a, old_e, x), 0)
        if not is_compatible(x, new_e):
            # pattern x no longer valid => lumps-coded measure => 0
            Mu[(a,new_e,x)] = 0
        else:
            # keep the old lumps-coded measure
            Mu[(a,new_e,x)] = old_k

def main():
    """
    Example usage:
      - We'll define an observer 'obs1', start in environment 'envA' 
        with lumps-coded probabilities for patterns X,Y,Z.
      - Then we switch to 'envB' and apply update_env_transition.
    """
    a = "obs1"
    e_initial = "envA"
    capacity = 10  # lumps-coded denominator for 'obs1'

    # Let's define lumps-coded probabilities for 3 patterns: patternX, patternY, patternZ
    set_probability(a, e_initial, "patternX", 5, capacity) # => 5/10
    set_probability(a, e_initial, "patternY", 3, capacity) # => 3/10
    set_probability(a, e_initial, "patternZ", 2, capacity) # => 2/10

    print("Initial lumps-coded probabilities at (obs1, envA):")
    for x in ["patternX","patternY","patternZ"]:
        p_val = get_probability(a, e_initial, x, capacity)
        print(f"  {x}: {p_val:.2f}")

    # Now we transition to environment 'envB'
    e_new = "envB"
    patterns = ["patternX","patternY","patternZ"]
    update_env_transition(a, e_initial, e_new, capacity, patterns)

    print(f"\nAfter transitioning from envA -> envB for observer={a}:")
    for x in patterns:
        # we can read lumps-coded measure from Mu[(obs1, envB, x)]
        lumps = Mu.get((a,e_new,x), 0)
        p_val = lumps/capacity
        print(f"  {x} => lumps={lumps}, prob={p_val:.2f}, compatible? {is_compatible(x,e_new)}")

    # For instance, if 'patternX' needed sig1, but envB only has sig2,sig3, 
    # lumps-coded measure for patternX => 0.
    # Meanwhile patternY might remain 3 lumps if it's compatible with sig2, sig3, etc.

if __name__ == "__main__":
    main()