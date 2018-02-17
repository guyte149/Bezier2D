import numpy as np
import matplotlib.pyplot as plt
from math import *
from trajectory import *
from progress.bar import Bar


class CubicBezierCurve(object):
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

    def draw_curve(self, res=1000.0):
        x_list = []
        y_list = []
        for t in xrange(0, int(res + 1)):
            x_list.append(self(t / res)[0])
            y_list.append(self(t / res)[1])
            print 't={},  R={}'.format(t / res, 1 / self.get_curvature(t / res))
        plt.plot(x_list, y_list)
        plt.show()

    def bezier_derivative(self, t):
        omt = 1 - t
        return 3 * omt * omt * (self.c0 - self.p0) + 6 * omt * t * (self.c1 - self.c0) + 3 * t * t * (self.p1 - self.c1)

    def second_bezier_derivative(self, t):
        omt = 1 - t
        return 6 * omt * (self.c1 - (2 * self.c0) + self.p0) + 6 * t * (self.p1 - (2 * self.c1) + self.c0)

    def get_curvature(self, t):
        x_tag = self.bezier_derivative(t)[0]
        y_tag = self.bezier_derivative(t)[1]
        x_tagai = self.second_bezier_derivative(t)[0]
        y_tagai = self.second_bezier_derivative(t)[1]

        return (x_tag * y_tagai - y_tag * x_tagai) / np.power((x_tag * x_tag) + (y_tag * y_tag), 1.5)

    def get_angle(self, t):
        der = self.bezier_derivative(t)
        x_tag = der[0]
        y_tag = der[1]
        m = y_tag / x_tag
        v = atan(m)
        ang = np.rad2deg(v)
        if (y_tag>=0 and x_tag<0):
            ang = 180+ang
        # print ang , m
        # if ang >= 0:
        #     return 90 - ang
        # else:
        #     return -90 - ang
        return ang

    def get_curve_length(self, res=1000.0):
        l = 0
        for t in xrange(0, int(res + 1)):
            if t / res < 1:
                p1 = self(t / res)
                p2 = self((t / res) + (1 / res))
                l += np.linalg.norm(p2 - p1)
        return l

    def get_setpoints(self, arc_length, start_poistion=0, step=0.0000025):
        """
        return a list of Setpoints, one arc_length apart from each other
        :param arc_length:
        :return:
        """
        p0 = self(0)
        last_curvature = 0
        position = start_poistion
        curr_arc = 0
        last_p = p0.copy()
        # initialize the first point
        setpoints = [Setpoint(point=p0, p=start_poistion, curvature=self.get_curvature(0), heading=self.get_angle(0))]
        # bar = Bar('processing', max=10)
        # print "bar on"
        for i in np.arange(0, 1, step):
            # if(i%)
            # bar.next()


            p1 = self(i)
            norm = np.linalg.norm(p1 - last_p)
            curr_arc += norm
            position += norm

            if curr_arc >= arc_length:
                # check if the previous point was closer to the arc_length than this one
                if abs(arc_length - curr_arc) > abs(arc_length - (curr_arc - norm)):
                    p1 = last_p.copy()
                    position -= norm
                # we found the closest point, move to search for the next one...
                setpoints.append(
                    Setpoint(point=p1, p=position, curvature=self.get_curvature(i), heading=self.get_angle(i)))
                p0 = p1
                # print(curr_arc)
                curr_arc = 0

            last_p = p1
        # bar.finish()
        # add the last point
        setpoints.append(
            Setpoint(point=self(1), p=start_poistion + self.get_curve_length(), curvature=setpoints[-1].curvature,
                     heading=self.get_angle(1)))
        return setpoints

    def find_parallel(self, t, width):
        der_x = self.bezier_derivative(t)[0]
        der_y = self.bezier_derivative(t)[1]
        derivative_length = np.sqrt(der_x * der_x)

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
        return 'p0- {} \nc0- {} \nc1- {} \np1- {} \nlength {}'.format(self.p0, self.c0, self.c1, self.p1,
                                                                      self.get_curve_length())


class BezierPath(object):
    def __init__(self, *curves):
        self.curves = curves
        self.max_v = 2
        self.max_a = 2

    # first argument is t, second argument is curve number
    def __call__(self, *args, **kwargs):
        t = args[0]
        seg = args[1]
        # print 'seg={}   curves seg - {}'.format(seg, self.curves[seg])
        return self.curves[0][seg](t)

    def draw_path(self, res=1000.0):
        x_list = []
        y_list = []
        for s in xrange(0, len(self.curves[0])):
            for t in xrange(0, int(res + 1)):
                x_list.append(self(t / res, s)[0])
                y_list.append(self(t / res, s)[1])
                # print 't={},  R={}'.format(t / res, 1 / self.get_curvature(t / res))

        plt.axes().set_aspect('equal', 'datalim')
        plt.plot(x_list, y_list)
        plt.show()

    def get_angle(self, t, seg):
        return self.curves[0][seg].get_angle(t)

    def get_setpoints(self, arc_length=0.00005):
        l = []
        start_position = 0
        for c in self.curves[0]:
            l = l + c.get_setpoints(arc_length, start_position)
            start_position += l[-1].p
        return l

    def __str__(self):
        return self.curves
