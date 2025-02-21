#!/usr/bin/env python3

"""
signals.py

Demonstration of environment signals and pattern compatibility 
as described in Section 1.5 of the manual.

Key elements:
 - A finite set of environment states E (e.g., "envA", "envB", "envC").
 - Each environment e has a set of signals: SignalSet[e].
 - Patterns each have a finite set of features:
     feature_map[x] = {f1, f2, ...}
 - Compatibility: a pattern x is compatible with environment e 
   if feature_map[x] ⊆ SignalSet[e].

We also show how grains-coded probabilities can be updated when transitioning 
from one environment to another.
"""

from grain_probability import Mu, set_probability, get_probability, update_probability

# Define environment states and their finite sets of signals:
SignalSet = {
    "envA": {"sig1", "sig2"},
    "envB": {"sig2", "sig3"},
    "envC": {"sigX"}
}

# Define patterns with their respective sets of features:
feature_map = {
    "patternX": {"sig1"},
    "patternY": {"sig2", "sig3"},
    "patternZ": {"sigX"}
}

def is_compatible(x, e):
    """
    Return True if all features of pattern x are contained in the signal set for environment e.
    """
    needed_features = feature_map.get(x, set())
    env_signals = SignalSet.get(e, set())
    return needed_features.issubset(env_signals)

def update_env_transition(a, old_e, new_e, capacity, patterns):
    """
    When transitioning from environment old_e to new_e for observer a,
    check each pattern x in 'patterns':
      - If x is not compatible with new_e, set its grains-coded probability to 0.
      - Otherwise, preserve its current grains-coded probability.
    """
    for x in patterns:
        old_k = Mu.get((a, old_e, x), 0)
        if not is_compatible(x, new_e):
            Mu[(a, new_e, x)] = 0
        else:
            Mu[(a, new_e, x)] = old_k

def main():
    """
    Example usage:
      - Define an observer 'obs1' starting in environment 'envA' with grains-coded probabilities for patterns.
      - Then transition to 'envB' and update the probabilities based on compatibility.
    """
    a = "obs1"
    e_initial = "envA"
    capacity = 10  # grains-coded denominator for observer 'obs1'

    # Set grains-coded probabilities for three patterns.
    set_probability(a, e_initial, "patternX", 5, capacity)  # 5/10
    set_probability(a, e_initial, "patternY", 3, capacity)  # 3/10
    set_probability(a, e_initial, "patternZ", 2, capacity)  # 2/10

    print("Initial grains-coded probabilities at (obs1, envA):")
    for x in ["patternX", "patternY", "patternZ"]:
        p_val = get_probability(a, e_initial, x, capacity)
        print(f"  {x}: {p_val:.2f}")

    # Transition to environment 'envB'
    e_new = "envB"
    patterns = ["patternX", "patternY", "patternZ"]
    update_env_transition(a, e_initial, e_new, capacity, patterns)

    print(f"\nAfter transitioning from envA to envB for observer {a}:")
    for x in patterns:
        grains_val = Mu.get((a, e_new, x), 0)
        p_val = grains_val / capacity  # this division is for display only
        print(f"  {x}: grains = {grains_val}, prob = {p_val:.2f}, compatible? {is_compatible(x, e_new)}")

if __name__ == "__main__":
    main()