#!/usr/bin/env python3

class Lump:
    """
    A very simple lumps-coded rational: numerator/denominator, with no floating math.
    For example, Lump(3,10) ~ 0.3 in decimal, but we keep it in finite ratio form.
    """

    def __init__(self, numerator, denominator=1):
        # Force integers to avoid accidental floating arithmetic
        if denominator == 0:
            raise ValueError("Denominator cannot be zero in lumps-coded fraction.")
        self.num = int(numerator)
        self.den = int(denominator)

    def __repr__(self):
        return f"Lump({self.num}/{self.den})"

    def simplify(self):
        """Optional: reduce fraction by gcd."""
        from math import gcd
        g = gcd(self.num, self.den)
        self.num //= g
        self.den //= g
        return self

    def __add__(self, other):
        if not isinstance(other, Lump):
            other = Lump(other, 1)
        # (a/b) + (c/d) = (ad + bc) / bd
        new_num = self.num * other.den + other.num * self.den
        new_den = self.den * other.den
        return Lump(new_num, new_den).simplify()

    def __sub__(self, other):
        if not isinstance(other, Lump):
            other = Lump(other, 1)
        # (a/b) - (c/d) = (ad - bc) / bd
        new_num = self.num * other.den - other.num * self.den
        new_den = self.den * other.den
        return Lump(new_num, new_den).simplify()

    def __mul__(self, other):
        if not isinstance(other, Lump):
            other = Lump(other, 1)
        # (a/b)*(c/d) = (ac)/(bd)
        new_num = self.num * other.num
        new_den = self.den * other.den
        return Lump(new_num, new_den).simplify()

    def __truediv__(self, other):
        if not isinstance(other, Lump):
            other = Lump(other, 1)
        # (a/b) / (c/d) = (a/b)*(d/c) = ad/bc
        if other.num == 0:
            raise ZeroDivisionError("Divide by lumps-coded zero.")
        new_num = self.num * other.den
        new_den = self.den * other.num
        return Lump(new_num, new_den).simplify()

    def abs(self):
        return Lump(abs(self.num), abs(self.den))

    def to_decimal(self):
        """A quick method to see an approximate float (for printing/demos)."""
        return self.num / self.den


class Point2D:
    """
    A 2D point with lumps-coded x and y coordinates.
    """
    def __init__(self, x: Lump, y: Lump):
        self.x = x
        self.y = y

    def __repr__(self):
        return f"Point2D({self.x}, {self.y})"


def lumps_l1_distance(p1: Point2D, p2: Point2D) -> Lump:
    """
    L1 distance = |x2 - x1| + |y2 - y1| in lumps-coded form.
    """
    dx = (p2.x - p1.x).abs()
    dy = (p2.y - p1.y).abs()
    return dx + dy


def polygon_perimeter_l1(points):
    """
    Given a list of lumps-coded Point2D, compute the 'perimeter'
    under L1 distance, by summing each consecutive edge.
    (For a closed loop, we also connect the last point to the first.)
    """
    if len(points) < 2:
        return Lump(0, 1)

    perimeter = Lump(0, 1)
    for i in range(len(points)):
        p_current = points[i]
        p_next = points[(i+1) % len(points)]  # wrap around
        perimeter += lumps_l1_distance(p_current, p_next)

    return perimeter


def main():
    # Example of lumps-coded points
    p1 = Point2D(Lump(0), Lump(0))          # (0/1, 0/1)
    p2 = Point2D(Lump(1), Lump(2))          # (1/1, 2/1)
    p3 = Point2D(Lump(3), Lump(3))          # (3/1, 3/1)
    p4 = Point2D(Lump(-1), Lump(2))         # for variety, negative x

    # Compute lumps-coded L1 distances
    dist12 = lumps_l1_distance(p1, p2)
    dist23 = lumps_l1_distance(p2, p3)
    dist14 = lumps_l1_distance(p1, p4)

    print("Points:")
    print("  p1 =", p1)
    print("  p2 =", p2)
    print("  p3 =", p3)
    print("  p4 =", p4)
    print()
    print("L1 Distances (lumps-coded):")
    print("  d(p1,p2) =", dist12, "≈", dist12.to_decimal())
    print("  d(p2,p3) =", dist23, "≈", dist23.to_decimal())
    print("  d(p1,p4) =", dist14, "≈", dist14.to_decimal())

    # Suppose we treat [p1, p2, p3, p4] as a polygon and compute perimeter
    polygon_pts = [p1, p2, p3, p4]
    perim = polygon_perimeter_l1(polygon_pts)
    print("\nL1 Perimeter of polygon p1->p2->p3->p4->p1:", perim, "≈", perim.to_decimal())


if __name__=="__main__":
    main()