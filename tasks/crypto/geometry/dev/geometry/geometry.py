from typing import Iterable, Self
import math

PRECISION = 1e-9

class SymmetryGroup:

    n: int
    vertex_order: tuple[int]

    def __init__(self, n: int, vertex_order: Iterable[int]=None):
        if vertex_order is None:
            vertex_order = range(n)

        vertex_order = tuple(vertex_order)

        assert n == len(vertex_order)

        for i, v in enumerate(vertex_order):
            assert set((vertex_order[(i - 1) % n], vertex_order[(i + 1) % n])) == set(((v + 1) % n, (v - 1) % n))

        self.n = n
        self.vertex_order = vertex_order

    def rotate(self, deg: float):
        # rotate the figure by deg degrees
        point_rotation_float = deg / (2 * math.pi) * self.n
        point_rotation = round(point_rotation_float) % self.n

        assert abs(point_rotation - point_rotation_float) < PRECISION


        return SymmetryGroup(self.n,
                             self.vertex_order[point_rotation:] +
                             self.vertex_order[:point_rotation]
                             )

    def mirror(self, point: int):
        # mirror the fugire on the altitude from point
        assert point < self.n

        return SymmetryGroup(self.n,
                             self.vertex_order[point + 1:][::-1] +
                             (self.vertex_order[point], ) +
                             self.vertex_order[:point][::-1]
                             )

    def __mul__(self, g: Self):
        assert self.n == g.n

        return SymmetryGroup(self.n, (self.vertex_order[g] for g in g.vertex_order))

    def __pow__(self, exp: int) -> int:
        res = SymmetryGroup(self.n)
        base = self

        while exp:
            if exp % 2:
                res = res * base
            base *= base
            exp //= 2

        return res

    def __str__(self):
        return f"SymmetryGroup({self.n}, {self.vertex_order})"

    def __hash__(self):
        return hash(self.vertex_order)

    def __eq__(self, g: Self):
        return self.vertex_order == g.vertex_order
