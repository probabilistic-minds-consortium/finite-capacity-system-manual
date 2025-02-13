class Lump:
    """Potentially storing an integer or a rational (numerator, denominator)."""
    def __init__(self, numerator, denominator=1):
        # naive rational approach
        self.num = numerator
        self.den = denominator

    def __repr__(self):
        return f"Lump({self.num}/{self.den})"

# Helper gcd for simplifying lumps
def gcd(a, b):
    if b == 0:
        return a
    return gcd(b, a % b)

def lumps_add(l1, l2):
    """(n1/d1) + (n2/d2) => (n1*d2 + n2*d1)/(d1*d2)."""
    num = l1.num*l2.den + l2.num*l1.den
    den = l1.den * l2.den
    g = gcd(abs(num), abs(den))
    return Lump(num//g, den//g)

def lumps_sub(l1, l2):
    """(n1/d1) - (n2/d2)."""
    num = l1.num*l2.den - l2.num*l1.den
    den = l1.den * l2.den
    g = gcd(abs(num), abs(den))
    return Lump(num//g, den//g)

def lumps_mult(l1, l2):
    """(n1/d1) * (n2/d2)."""
    num = l1.num*l2.num
    den = l1.den*l2.den
    g = gcd(abs(num), abs(den))
    return Lump(num//g, den//g)

def lumps_div(l1, l2):
    """(n1/d1) / (n2/d2) => (n1*d2)/(n2*d1)."""
    num = l1.num * l2.den
    den = l1.den * l2.num
    # handle zero or sign
    if den == 0:
        raise ZeroDivisionError("lumps_div: denominator zero.")
    g = gcd(abs(num), abs(den))
    return Lump(num//g, den//g)

def lumps_zero():
    return Lump(0, 1)

def lumps_one():
    return Lump(1, 1)

def gauss_jordan_solve(A, b):
    """
    Solve A*x = b using lumps-coded Gauss-Jordan.
    - A is list of lists of Lump
    - b is list of Lump
    Returns x as list of Lump.
    """
    n = len(A)
    # build augmented matrix
    aug = [row[:] + [bval] for row, bval in zip(A, b)]  # each row: [A[i], b[i]]

    # Forward elimination + pivot
    for i in range(n):
        # 1) pivot: ideally pick pivot row s.t. aug[i][i] != 0
        pivot = aug[i][i]
        if pivot.num == 0:
            # lumps-coded pivot swap logic (naive approach)
            for r in range(i+1, n):
                if aug[r][i].num != 0:
                    aug[i], aug[r] = aug[r], aug[i]
                    pivot = aug[i][i]
                    break
        
        # now pivot != 0 (hopefully)
        # 2) normalize row i: divide entire row by pivot
        div_factor = pivot
        for col in range(n+1):
            aug[i][col] = lumps_div(aug[i][col], div_factor)

        # 3) eliminate below and above
        for r in range(n):
            if r != i:
                factor = aug[r][i]
                # row r <- row r - factor * row i
                for c in range(i, n+1):
                    product = lumps_mult(factor, aug[i][c])
                    aug[r][c] = lumps_sub(aug[r][c], product)

    # Now we have an identity in left part => solution in last column
    # solution x[i] = aug[i][n]
    x = [row[n] for row in aug]
    return x


# Example usage:
A = [
  [Lump(2), Lump(1)],
  [Lump(1), Lump(-1)]
]
b = [Lump(5), Lump(-1)]

sol = gauss_jordan_solve(A, b)
print("Lumps-coded Gauss-Jordan solution:", sol)