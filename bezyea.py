from random import *
from __builtin__ import xrange

import numpy as np
import matplotlib.animation as animation
import matplotlib.pyplot as plt

from math import *

from matplotlib.lines import Line2D
from pyparsing import range

from trajectory import *
import bezier


class BezierCurve(object):
    def __init__(self, p0, p1):
        self.p0 = p0
        self.p1 = p1

    def __call__(self, *args, **kwargs):
        raise NotImplemented

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
        raise NotImplemented

    def second_bezier_derivative(self, t):
        raise NotImplemented

    def get_curvature(self, t):
        x_tag = self.bezier_derivative(t)[0]
        y_tag = self.bezier_derivative(t)[1]
        x_tagai = self.second_bezier_derivative(t)[0]
        y_tagai = self.second_bezier_derivative(t)[1]
        number = (x_tag * y_tagai - y_tag * x_tagai) / np.power((x_tag * x_tag) + (y_tag * y_tag), 1.5)
        if number == 0:
            number = number
        # print number
        #     number = 6.9533558078350043e-310
        return number

    def get_max_curvature(self):
        l = np.linalg.norm(self.p1 - self.p0)
        res = 15.0 / (sqrt(2)) * l
        max_curvature = 0.0
        for i in np.arange(0.0, res + 1.0, 1.0):
            new_curvature = abs(self.get_curvature(i / res))
            if max_curvature < new_curvature:
                max_curvature = new_curvature
        return max_curvature

    def get_max_curvature_change(self, res=15.0):
        l = np.linalg.norm(self.p1 - self.p0)
        res = 15.0 / (sqrt(2)) * l
        max_curvature_change = 0.0
        for i in np.arange(0.0, res - 1.0, 1.0):
            absolute_curvature_change = abs(self.get_curvature((i + 1) / res)) - abs(self.get_curvature(i / res))
            if absolute_curvature_change > max_curvature_change:
                max_curvature_change = absolute_curvature_change
        return max_curvature_change

    def get_point_with_max_curvature_change(self, res=15.0):
        l = np.linalg.norm(self.p1 - self.p0)
        res = 15.0 / (sqrt(2)) * l
        max_curvature_change = 0.0
        point_max0 = np.array([0, 0])
        point_max1 = np.array([0, 0])
        for i in np.arange(0.0, res - 1.0, 1.0):
            absolute_curvature_change = abs(self.get_curvature((i + 1) / res)) - abs(self.get_curvature(i / res))
            if absolute_curvature_change > max_curvature_change:
                max_curvature_change = absolute_curvature_change
                point_max0 = self((i + 1) / res)
                point_max1 = self(i / res)
        return point_max0, point_max1

    def get_average_curvature_change(self, res=15.0):
        l = np.linalg.norm(self.p1 - self.p0)
        res = 15.0 / (sqrt(2)) * l
        sum_curvature_change = 0.0
        for i in np.arange(0, res - 1.0, 1.0):
            absolute_curvature_change = abs(self.get_curvature((i + 1) / res)) - abs(self.get_curvature(i / res))
            sum_curvature_change += absolute_curvature_change
        average_curvature_change = sum_curvature_change / res
        return average_curvature_change

    def get_angle(self, t):
        der = self.bezier_derivative(t)
        x_tag = der[0]
        y_tag = der[1]

        # if we are going straight up, we can't divide by zero and just return 90 deg
        if x_tag == 0:
            return 90
        # > 0, 0, 90
        # > 0, 3.15, 90
        # > 2.5, 4.25, 45
        # > 3.75, 5.275, 0
        # > 4.65, 5.275, 0
        # >
        m = y_tag / x_tag
        v = atan(m)
        ang = np.rad2deg(v)
        if y_tag >= 0 and x_tag < 0:
            ang = 180 + ang
        if x_tag < 0 and y_tag < 0:
            # print ang
            return 360 - ang
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
        raise NotImplemented

    @staticmethod
    def connect_curve(curve, q3, ang2):
        raise NotImplemented

    def __str__(self):
        raise NotImplemented


class CubicBezierCurve(BezierCurve):
    def __init__(self, p0, c0, c1, p1):
        super(CubicBezierCurve, self).__init__(p0, p1)
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
        return 3 * omt * omt * (self.c0 - self.p0) + 6 * omt * t * (self.c1 - self.c0) + 3 * t * t * (self.p1 - self.c1)

    def second_bezier_derivative(self, t):
        omt = 1 - t
        return 6 * omt * (self.c1 - (2 * self.c0) + self.p0) + 6 * t * (self.p1 - (2 * self.c1) + self.c0)

    @staticmethod
    def create_curve(p0, ang0, p1, ang1):
        l = np.linalg.norm(p1 - p0)
        u = 0.5 * l

        v0 = np.array([np.cos(np.deg2rad(ang0)), np.sin(np.deg2rad(ang0))])
        v1 = np.array([np.cos(np.deg2rad(ang1)), np.sin(np.deg2rad(ang1))])

        c0 = p0 + u * v0
        c1 = p1 - u * v1

        return CubicBezierCurve(p0, c0, c1, p1)

    @staticmethod
    def connect_curve(curve, q3, ang2):
        q1 = (2 * curve.p1) - curve.c1
        q2 = (curve.c0 + (2 * q1)) - (2 * curve.c1)
        Q = CubicBezierCurve(curve.p1, q1, q2, q3)
        return Q

    def __str__(self):
        return 'p0- {} \nc0- {} \nc1- {} \np1- {} \nlength {}'.format(self.p0, self.c0, self.c1, self.p1,
                                                                      self.get_curve_length())


class BezierPath(object):
    def __init__(self, *curves):
        self.curves = curves
        self.first_curves = curves
        # print self.curves
        self.max_v = 2
        self.max_a = 2

        # for j in range(0, len(self.curves[0]), 1):
        #     self.plots.append([plt.plot([], [])[0] for _ in range(len(self.curves[0]))])
        # self.patches = self.plots[0] + self.plots[1]
        # for j in range(2, len(self.curves[0]), 1):
        #     self.patches += self.plots[j]

    # first argument is t, second argument is curve number
    def __call__(self, *args, **kwargs):
        t = args[0]
        s = args[2]
        seg = args[1]
        # print 'seg={}   cur/ves seg - {}'.format(seg, self.curves[seg])
        return self.curves[0][seg](t)

    def get_angle(self, t, seg):
        return self.curves[self.counter1][seg].get_angle(t)

    def draw_path(self, res=1000.0):
        x_list = []
        y_list = []

        for s in xrange(0, len(self.curves[0])):
            for t in xrange(0, int(res + 1)):
                x_list.append(self(t / res, s, 0)[0])
                y_list.append(self(t / res, s, 0)[1])

            plt.plot(x_list, y_list)
            x_list = []
            y_list = []

        plt.axes().set_aspect('equal', 'datalim')

        plt.show()

    def get_setpoints(self, arc_length=0.00005):
        l = []
        start_position = 0
        for c in self.curves[0][0]:
            l = l + c.get_setpoints(arc_length, start_position)
            start_position += l[-1].p
        return l

    def __str__(self):
        return self.curves


class QuanticBezierCurve(BezierCurve):
    def __init__(self, p0, c0, c1, c2, c3, p1):
        super(QuanticBezierCurve, self).__init__(p0, p1)
        self.p0 = p0
        self.c0 = c0
        self.c1 = c1
        self.c2 = c2
        self.c3 = c3
        self.p1 = p1

        # branch changes
        nodes = np.array([p0, c0, c1, c2, c3, p1]).T
        self.bezier_lib = bezier.Curve(nodes, degree=5)

    def __call__(self, *args, **kwargs):
        t = args[0]
        # omt = 1 - t
        # return (self.p0 * omt * omt * omt * omt * omt) + (self.c0 * 5 * t * omt * omt * omt * omt) + (
        #         self.c1 * 10 * t * t * omt * omt * omt) + (self.c2 * 10 * t * t * t * omt * omt) + (
        #                self.c3 * 5 * t * t * t * t * omt) + (self.p1 * t * t * t * t * t)

        # branch changes
        return self.bezier_lib.evaluate(t)

    def bezier_derivative(self, t):
        omt = 1 - t
        return 5 * t * t * t * t * (self.p1 - self.c3) + 20 * omt * t * t * t * (self.c3 - self.c2) + (
                30 * omt * omt * t * t * (self.c2 - self.c1)) + 20 * omt * omt * omt * t * (self.c1 - self.c0) + (
                       5 * omt * omt * omt * omt * omt * (self.c0 - self.p0))

    def second_bezier_derivative(self, t):
        return 20 * (self.p1 - 5 * self.c3 + 10 * self.c2 - 10 * self.c1 + 5 * self.c0 - self.p0) * t * t * t + (
                15 * (4 * self.c3 - 16 * self.c2 + 24 * self.c1 - 16 * self.c0 + 4 * self.p0) * t * t) + (
                       10 * (6 * self.c2 - 18 * self.c1 + 18 * self.c0 - 6 * self.p0) * t) + (
                       20 * self.c1 - 40 * self.c0 + 20 * self.p0)

    @staticmethod
    def create_curve(p0, ang0, p1, ang1):
        l = np.linalg.norm(p1 - p0)
        u = 0.275 * l

        v0 = np.array([np.cos(np.deg2rad(ang0)), np.sin(np.deg2rad(ang0))])
        v1 = np.array([np.cos(np.deg2rad(ang1)), np.sin(np.deg2rad(ang1))])

        value_x = (p1[0] - p0[0]) * 0.25
        # value_y = p1[1] - p0[1]

        c0 = p0 + u * v0
        c1 = np.array([c0[0] + value_x, c0[1] + c0[1] / l])
        c3 = p1 - u * v1
        c2 = np.array([c3[0] - value_x, c3[1] + c3[1] * -v1[1] / (l * l)])
        # print c1[1], c2[1]

        return QuanticBezierCurve(p0, c0, c1, c2, c3, p1)

    @staticmethod
    def rate_curve(curve):
        return curve.get_max_curvature_change() + abs(curve.get_max_curvature())
        # return curve.get_max_curvature_change() + abs(curve.get_max_curvature()) + curve.get_curve_length()
        # return curve.get_max_curvature_change() + abs(curve.get_average_curvature_change())
        # return abs(curve.get_average_curvature_change())

    @staticmethod
    def connect_curve(curve, q3, ang2):
        pass


def __str__(self):
    return 'p0- {} \nc0- {} \nc1- {} \nc2- {} \nc3- {} \np1- {} \nlength {}'.format(self.p0, self.c0, self.c1, self.c2,
                                                                                    self.c3, self.p1,
                                                                                    self.get_curve_length())


class Bezier(object):
    def __init__(self, p0, p1, p2, p3, p4, p5):
        self.p0 = p0
        self.p1 = p1
        self.p2 = p2
        self.p3 = p3
        self.p4 = p4
        self.p5 = p5

        nodes = np.array([p0, p1, p2, p3, p4, p5]).T

        # we use the bezier library because it can calculate multiple points together much faster than python
        # the backend of the library is written in C
        self.bezier_lib = bezier.Curve(nodes, degree=5)

    def call_multi(self, us):
        """
        :param us: a vector of us (the path parameter)
        :return: a vector of points that correspond to the u vector
        """

        return self.bezier_lib.evaluate_multi(us).T
        # return self.bezier_lib.evaluate_multi(us)[0].T

    def __call__(self, u):
        """"
        :param u: path parameter
        :return: the point on the path
        """
        return self.bezier_lib.evaluate(u)

    def bezier_derivative(self, t):
        omt = 1 - t
        return 5 * t * t * t * t * (self.p5 - self.p4) + 20 * omt * t * t * t * (self.p4 - self.p3) + (
                30 * omt * omt * t * t * (self.p3 - self.p2)) + 20 * omt * omt * omt * t * (self.p2 - self.p1) + (
                       5 * omt * omt * omt * omt * omt * (self.p1 - self.p0))

    def second_bezier_derivative(self, t):
        return 20 * (self.p5 - 5 * self.p4 + 10 * self.p3 - 10 * self.p2 + 5 * self.p1 - self.p0) * t * t * t + (
                15 * (4 * self.p4 - 16 * self.p3 + 24 * self.p2 - 16 * self.p1 + 4 * self.p0) * t * t) + (
                       10 * (6 * self.p3 - 18 * self.p2 + 18 * self.p1 - 6 * self.p0) * t) + (
                       20 * self.p2 - 40 * self.p1 + 20 * self.p0)

    def get_length(self):
        """
        use the library to get the total length of the path.
        this is also faster than doing it in python
        :return: the total length of the path
        """
        return self.bezier_lib.length

    def get_curvature(self, u):
        fd = self.bezier_derivative(u)
        sd = self.second_bezier_derivative(u)

        k = ((fd[0] * sd[1]) - (fd[1] * sd[0])) \
            / np.power((fd[0] ** 2) + (fd[1] ** 2), 1.5)

        return k

    @staticmethod
    def create_curve(p0, ang0, p1, ang1):
        l = np.linalg.norm(p1 - p0)
        u = 0.275 * l

        v0 = np.array([np.cos(np.deg2rad(ang0)), np.sin(np.deg2rad(ang0))])
        v1 = np.array([np.cos(np.deg2rad(ang1)), np.sin(np.deg2rad(ang1))])

        value_x = (p1[0] - p0[0]) * 0.25
        # value_y = p1[1] - p0[1]

        c0 = p0 + u * v0
        c1 = np.array([c0[0] + value_x, c0[1] + c0[1] / l])
        c3 = p1 - u * v1
        c2 = np.array([c3[0] - value_x, c3[1] + c3[1] * -v1[1] / (l * l)])
        # print c1[1], c2[1]

        return Bezier(p0, c0, c1, c2, c3, p1)

    def find_turning_points(self):
        """
        a hackish way to find the points of maximum curvature.
        there should be a faster more correct and accurate way of doing this
        :return: a vector of us representing the turning points along the path
        """
        du = 0.005
        turning_points = []

        for u in np.arange(0 + du, 1 - du, du):
            prev_k = np.abs(self.get_curvature(u - du))
            k = np.abs(self.get_curvature(u))
            next_k = np.abs(self.get_curvature(u + du))

            # check if the point's curvature is bigger than its neighbors, if it is than it's a maximum
            if prev_k < k > next_k:
                turning_points.append(u)

        return np.array(turning_points)

    def get_angle(self, u):
        v = self.bezier_derivative(u)
        return np.angle(v[0] + v[1] * 1j)

    def get_angles(self, us):
        return np.row_stack(np.array([self.get_angle(u) for u in us]))


class Path(object):
    def __init__(self, curves):
        self.curves = curves
        self.end_u = len(curves)

    def __call__(self, u):
        return self.curves[int(u)](u - int(u))

    def get_all_points(self, du):
        u_range = np.arange(0, 1, du)
        range_points = None
        for c in self.curves:
            if range_points is None:
                range_points = c.call_multi(u_range)
            else:
                range_points = np.concatenate((range_points, c.call_multi(u_range)))
        range_points = np.array(range_points)
        return range_points

    def call_multi(self, us):
        # organized_us = []
        # int_first_u = int(us[0])
        # int_last_u = int(us[len(us) - 1])
        #
        # if us[len(us) - 1] <= float(int_first_u + 1):
        #     # calculate the only one
        #     organized_us.append(TrajectoryGenerator.get_us_subset(us[0], us[len(us) - 1], du))
        #
        # else:
        #     # calculate first one
        #     organized_us.append(TrajectoryGenerator.get_us_subset(us[0], float(int_first_u + 1), du))
        #
        #     # calculate middle ones
        #     for i in xrange(int_first_u + 1, int_last_u):
        #         organized_us.append(TrajectoryGenerator.get_us_subset(float(i) + du, i + 1, du))
        #
        #     # calculate last one
        #     organized_us.append(TrajectoryGenerator.get_us_subset(float(int_last_u) + du, us[len(us) - 1], du))
        #
        # calculated_us = self.curves[int(organized_us[0][0])].call_multi(organized_us[0])
        # for i in xrange(1, len(organized_us)):
        #     print "calc_u = {}, call multi = {}".format(calculated_us.shape,
        #                                                 self.curves[int(organized_us[i][0])].call_multi(
        #                                                     organized_us[i]).shape)
        #     np.concatenate(calculated_us, self.curves[int(organized_us[i][0])].call_multi(organized_us[i]))
        return np.array([self(u).flatten() for u in us])

    def bezier_derivative(self, t):
        return self.curves[int(t)].bezier_derivative(t - int(t))

    def second_bezier_derivative(self, t):
        return self.curves[int(t)].second_bezier_derivative(t - int(t))

    def get_length(self):
        length = 0
        for bezier in self.curves:
            length += bezier.get_length()

        return length

    def get_curvature(self, u):
        return self.curves[int(u)].get_curvature(u - int(u))

    def find_turning_points(self):
        tps = self.curves[0].find_turning_points()
        for i in xrange(1, len(self.curves)):
            np.concatenate((tps, self.curves[i].find_turning_points()))
        return tps

    def get_angle(self, u):
        return self.curves[int(u)].get_angle(u - int(u))

    def get_angles(self, us):
        # organized_us = []
        # int_first_u = int(us[0])
        # int_last_u = int(us[len(us) - 1])
        #
        # if us[len(us) - 1] <= float(int_first_u + 1):
        #     # calculate the only one
        #     organized_us.append(TrajectoryGenerator.get_us_subset(us[0], us[len(us) - 1]), du)
        #
        # else:
        #     # calculate first one
        #     organized_us.append(TrajectoryGenerator.get_us_subset(us[0], float(int_first_u + 1), du))
        #
        #     # calculate middle ones
        #     for i in xrange(int_first_u + 1, int_last_u):
        #         organized_us.append(TrajectoryGenerator.get_us_subset(float(i) + du, i + 1, du))
        #
        #     # calculate last one
        #     organized_us.append(TrajectoryGenerator.get_us_subset(float(int_last_u) + du, us[len(us) - 1], du))
        #
        # calculated_angles = np.array(self.get_angle(organized_us[0][0]))
        # for i in xrange(1, len(organized_us[0])):
        #     np.concatenate(calculated_angles, np.array(self.get_angle(i)))
        #
        # angles = calculated_angles
        # for i in xrange(1, len(organized_us)):
        #     for u in i:
        #         np.concatenate(calculated_angles, self.get_angle(u))
        #     np.concatenate(angles, np.array(calculated_angles))
        #
        # return np.row_stack(angles)
        return np.array([self.get_angle(u) for u in us])
