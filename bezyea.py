import numpy as np


class CubicBezierCurves(object):

    def __init__(self, p0, c0, c1, p1):
        self.p0 = p0
        self.p1 = p1
        self.c0 = c0
        self.c1 = c1

    def __call__(self, *args, **kwargs):
        t = args[0]
        omt = 1 - t
        return (self.p0 * omt * omt * omt) + (self.c0 * 3 * omt * omt * t) + (self.c1 * 3 * omt * t * t) + (
        self.p1 * t * t * t)

    def bezier_derivative(self, t):
        omt = 1 - t
        return 3 * omt * omt *(self.c0 - self.p0) + 6 * omt * t * (self.c1 - self.c0) + 3 * t * t * t * (self.p1 - self.c1)

    def second_bezier_derivative(self, t):
        omt = 1-t
        return 6 * omt *(self.c1 - (2 * self.c0) + self.p0) + 6 * t *(self.p1 - (2 * self.c1) + self.c1)

    def get_curvature(self, t):
        x_tag = self.bezier_derivative(t)[0]
        y_tag = self.bezier_derivative(t)[1]
        x_tagai = self.second_bezier_derivative(t)[0]
        y_tagai = self.second_bezier_derivative(t)[1]

        return (x_tag * y_tagai - y_tag*x_tagai) / np.power((x_tag*x_tag) + (y_tag*y_tag), 1.5)

    def find_parallel(self, t, width):
        der_x = self.bezier_derivative(t)[0]
        der_y = self.bezier_derivative(t)[1]
        derivative_length = np.sqrt(der_x*der_x)

    @staticmethod
    def create_curve(p0, ang0, p1, ang1):
        l = np.linalg.norm(p1 - p0)
        u = 0.5 * l

        v0 = np.array([np.cos(np.deg2rad(ang0)), np.sin(np.deg2rad(ang0))])
        v1 = np.array([np.cos(np.deg2rad(ang1)), np.sin(np.deg2rad(ang1))])

        c0 = p0 + u * v0
        c1 = p1 - u * v1

        return CubicBezierCurves(p0, c0, c1, p1)


    def __str__(self):
        return "P0 = %s\nC0 = %s\nC1 = %sP1 = %s" % (self.p0, self.c0, self.c1, self.p1)
