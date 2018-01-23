import numpy as np
import matplotlib.pyplot as plt


class CubicBezierCurve(object):

    def __init__(self, p0, c0, c1, p1):
        self.p0 = p0
        self.p1 = p1
        self.c0 = c0
        self.c1 = c1

    def __call__(self, *args, **kwargs):
        t = args[0]
        omt = 1 - t
        return (self.p0 * omt * omt * omt) + (self.c0 * 3 * omt * omt * t) + (self.c1 * 3 * omt * t * t) + (self.p1 * t * t * t)

    def draw_curve(self, res=1000.0):
        x_list = []
        y_list = []
        for t in xrange(0, int(res+1)):
            x_list.append(self(t / res)[0])
            y_list.append(self(t / res)[1])
            print 't={},  R={}'.format(t / res, 1 / self.get_curvature(t / res))
        plt.plot(x_list, y_list)
        plt.show()

    def bezier_derivative(self, t):
        omt = 1 - t
        return 3 * omt * omt * (self.c0 - self.p0) + 6 * omt * t * (self.c1 - self.c0) + 3 * t * t * (self.p1 - self.c1)

    def second_bezier_derivative(self, t):
        omt = 1-t
        return 6 * omt * (self.c1 - (2 * self.c0) + self.p0) + 6 * t * (self.p1 - (2 * self.c1) + self.c0)

    def get_curvature(self, t):
        x_tag = self.bezier_derivative(t)[0]
        y_tag = self.bezier_derivative(t)[1]
        x_tagai = self.second_bezier_derivative(t)[0]
        y_tagai = self.second_bezier_derivative(t)[1]

        return (x_tag * y_tagai - y_tag*x_tagai) / np.power((x_tag*x_tag) + (y_tag*y_tag), 1.5)

    def get_curve_length(self, res=1000.0):
        l = 0
        for t in xrange(0, int(res+1)):
            if t/res < 1:
                p1 = self(t/res)
                p2 = self((t/res) + (1/res))
                l += np.linalg.norm(p2 - p1)
        return l

    def get_equal_arcs(self, arc_length):
        p0 = self(0)
        # print p0
        t = 0
        lst = [p0]
        for i in xrange(0, 100001):
            # print i
            p1 = self(i/100000.0)
            if np.linalg.norm(p1 - p0) >= arc_length:
                lst.append(p1)
                p0 = p1
        return lst

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

        return CubicBezierCurve(p0, c0, c1, p1)

    def __str__(self):
        return 'p0- {} \nc0- {} \nc1- {} \np1- {} \nlength {}'.format(self.p0, self.c0, self.c1, self.p1, self.get_curve_length())


class BezierPath:

    def __init__(self, *curves):
        self.curves = curves

    def insert_curve(self, c):
        self.curves.append(c)

    # first argument is t, second argument is curve segment
    def __call__(self, *args, **kwargs):
        t = args[0]
        seg = args[1]
        return self.curves[seg](t)

    def __str__(self):
        return self.curves
