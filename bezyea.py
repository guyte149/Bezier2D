from __builtin__ import xrange

import numpy as np
import matplotlib.animation as animation
import matplotlib.pyplot as plt

from math import *

from numpy.f2py.auxfuncs import throw_error
from pyparsing import range

from trajectory import *
from random import *
from progress.bar import Bar


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
        self.max_v = 2
        self.max_a = 2
        self.fig = plt.figure()
        self.plots = [plt.plot([], [])[0] for _ in range(len(curves[0]))]

    # first argument is t, second argument is curve number
    def __call__(self, *args, **kwaergs):
        t = args[0]
        seg = args[1]
        # print 'seg={}   curves seg - {}'.format(seg, self.curves[seg])
        return self.curves[0][seg](t)

    def get_angle(self, t, seg):
        return self.curves[0][seg].get_angle(t)

    def draw_path(self, res=1000.0):
        x_list = []
        x_list0 = []
        y_list = []
        y_list0 = []
        x_contorol_list = []
        y_contorol_list = []
        # ax = plt.axes(xlim=(0, 2), ylim=(0, 100))
        for s in xrange(0, len(self.curves)):
            for t in xrange(0, int(res + 1)):
                # print self.get_angle(t / res, s)
                x_list.append(self(t / res, s)[0])
                y_list.append(self(t / res, s)[1])

            plt.plot(x_list, y_list)
            x_list = []
            y_list = []
            # print 't={},  R={}'.format(t / res, 1 / self.get_curvature(t / res))
        #
        # for i in xrange(0, len(self.curves[0])):
        #     x_contorol_list.append(self.__str__()[0].c0[0][0])
        #     y_contorol_list.append(self(BezierPath.curves[0].c0[[1]])[1])

        # x_contorol_list.append(self.curves[0][0].c0[0])
        # x_contorol_list.append(self.curves[0][0].c1[0])
        # x_contorol_list.append(self.curves[0][0].c2[0])
        # x_contorol_list.append(self.curves[0][0].c3[0])
        #
        # y_contorol_list.append(self.curves[0][0].c0[1])
        # y_contorol_list.append(self.curves[0][0].c1[1])
        # y_contorol_list.append(self.curves[0][0].c2[1])
        # y_contorol_list.append(self.curves[0][0].c3[1])

        # point_max_list = self.curves[0][0].get_point_with_max_curvature_change()

        # l = np.linalg.norm(self.curves[0][0].p1 - self.curves[0][0].p0)
        # res = 15.0 / (sqrt(2)) * l

        # for s in xrange(0, len(self.curves[0])):
        #     for t in xrange(0, int(res + 1)):
        #         # print self.get_angle(t / res, s)
        #         x_list0.append(self(t / res, s)[0])
        #         y_list0.append(self(t / res, s)[1])

        # x_contorol_list.append(point_max[0])
        # y_contorol_list.append(point_max[1])

        # plt.axes().set_aspect('equal', 'datalim')
        plt.axis('equal')
        # plt.plot(x_list, y_list)
        # plt.plot(x_list0, y_list0, 'yo')
        # plt.plot(x_contorol_list, y_contorol_list, 'ro')
        # plt.plot(point_max_list[0][0], point_max_list[0][1], 'bo')
        # plt.plot(point_max_list[1][0], point_max_list[1][1], 'go')
        # plt
        # .plot(np.array(self.curves[0].c0))
        # plt.plot(self.c1)
        # plt.show()
        self.animate_init
        self.animate
        self.animation_draw
        plt.show()

    def get_setpoints(self, arc_length=0.00005):
        l = []
        start_position = 0
        for c in self.curves[0]:
            l = l + c.get_setpoints(arc_length, start_position)
            start_position += l[-1].p
        return l

    def animate_init(self):
        # update plots
        for i, plot in enumerate(self.plots):
            plot.set_data(self.curves[0][i])

        return self.plots

    def animate(self, i):
        # update plots
        for j, plot in enumerate(self.plots):
            plot.set_data([self.curves[j], i])

        return self.plots

    def animation_draw(self):
        ani = animation.FuncAnimation(self.fig, self.animate, init_func=self.animate_init, frames=500,
                                      interval=20, blit=True)
        # plt.show()
        return ani

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

    def __call__(self, *args, **kwargs):
        t = args[0]
        omt = 1 - t
        return (self.p0 * omt * omt * omt * omt * omt) + (self.c0 * 5 * t * omt * omt * omt * omt) + (
                self.c1 * 10 * t * t * omt * omt * omt) + (self.c2 * 10 * t * t * t * omt * omt) + (
                       self.c3 * 5 * t * t * t * t * omt) + (self.p1 * t * t * t * t * t)

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
    def random_search(p0, ang0, p1, ang1, res=175):
        l = np.linalg.norm(p1 - p0)

        random_length = 0.1 * l / sqrt(2)

        v0 = np.array([np.cos(np.deg2rad(ang0)), np.sin(np.deg2rad(ang0))])
        v1 = np.array([np.cos(np.deg2rad(ang1)), np.sin(np.deg2rad(ang1))])

        best_vector_multipler0 = 0.275
        best_vector_multipler1 = -0.275

        c0 = p0 + best_vector_multipler0 * v0
        c3 = p1 + best_vector_multipler1 * v1

        value_x = (p1[0] - p0[0]) * 0.25

        best_c1 = np.array([c0[0] + value_x, c0[1] + c0[1] * l / (l * l)])
        best_c2 = np.array([c3[0] - value_x, c3[1] + c3[1] * -v1[1] / (l * l)])

        best_curve = QuanticBezierCurve(p0, c0, best_c1, best_c2,
                                        c3, p1)
        best_rate = QuanticBezierCurve.rate_curve(best_curve)

        for i in range(res):
            new_vector_multipler0 = best_vector_multipler0 + uniform(-random_length, random_length)
            new_c1 = best_c1 + np.array(
                (uniform(-random_length, random_length), uniform(-random_length, random_length)))
            new_c2 = best_c2 + np.array(
                (uniform(-random_length, random_length), uniform(-random_length, random_length)))
            new_vector_multipler1 = best_vector_multipler1 + uniform(-random_length, random_length)
            new_curve = QuanticBezierCurve(p0, p0 + new_vector_multipler0 * l * v0, new_c1, new_c2, p1 +
                                           new_vector_multipler1 * l * v1, p1)
            new_rate = QuanticBezierCurve.rate_curve(new_curve)
            if 0 < new_rate < best_rate and new_vector_multipler0 > 0 > new_vector_multipler1:
                best_vector_multipler0 = new_vector_multipler0
                best_vector_multipler1 = new_vector_multipler1
                best_c1 = new_c1
                best_c2 = new_c2
                best_rate = new_rate
                best_curve = new_curve
        return best_curve

    @staticmethod
    def start_curves_particle_swarm(p0, ang0, p1, ang1, res=30):
        curves = []
        l = np.linalg.norm(p1 - p0)

        random_lenght_x = []
        random_lenght_y = []

        if ang0 - ang1 > 0:
            if p0[0] < p1[0] and p0[1] < p1[1]:
                random_lenght_x.append(p0[0])
                random_lenght_x.append(p1[0])
                random_lenght_y.append(p0[1])
                random_lenght_y.append(p1[1])

            elif p0[0] > p1[0] and p0[1] < p1[1]:
                random_lenght_x.append(p1[0] - abs(p1[0] - p0[0]) - abs(p1[1] - p0[1]))
                random_lenght_x.append(p0[0])
                random_lenght_y.append(p0[1])
                random_lenght_y.append(p1[1])

            elif p0[0] < p1[0] and p0[1] > p1[1]:
                random_lenght_x.append(p0[0])
                random_lenght_x.append(p1[0])
                random_lenght_y.append(p1[1])
                random_lenght_y.append(p0[1] + abs(p1[0] - p0[0]) + abs(p1[1] - p0[1]))

            elif p0[0] > p1[0] and p0[1] > p1[1]:
                random_lenght_x.append(p1[0] - abs(p1[0] - p0[0]) - abs(p1[1] - p0[1]))
                random_lenght_x.append(p0[0])
                random_lenght_y.append(p1[1])
                random_lenght_y.append(p0[1] + abs(p1[0] - p0[0]) + abs(p1[1] - p0[1]))

        elif ang0 - ang1 < 0:
            if p0[0] < p1[0] and p0[1] < p1[1]:
                random_lenght_x.append(p0[0])
                random_lenght_x.append(p1[0] + abs(p1[0] - p0[0]) + abs(p1[1] - p0[1]))
                random_lenght_y.append(p0[1] - abs(p1[0] - p0[0]) - abs(p1[1] - p0[1]))
                random_lenght_y.append(p1[1])

            elif p0[0] > p1[0] and p0[1] < p1[1]:
                random_lenght_x.append(p1[0])
                random_lenght_x.append(p0[0])
                random_lenght_y.append(p0[1])
                random_lenght_y.append(p1[1])

            elif p0[0] < p1[0] and p0[1] > p1[1]:
                random_lenght_x.append(p0[0])
                random_lenght_x.append(p1[0] + abs(p1[0] - p0[0]) + abs(p1[1] - p0[1]))
                random_lenght_y.append(p1[1])
                random_lenght_y.append(p0[1])

            elif p0[0] > p1[0] and p0[1] > p1[1]:
                random_lenght_x.append(p1[0] - abs(p1[0] - p0[0]) - abs(p1[1] - p0[1]))
                random_lenght_x.append(p0[0])
                random_lenght_y.append(p1[1])
                random_lenght_y.append(p0[1])

        elif ang0 == ang1:
            if p0[0] < p1[0] and p0[1] < p1[1]:
                random_lenght_x.append(p0[0])
                random_lenght_x.append(p1[0])
                random_lenght_y.append(p0[1])
                random_lenght_y.append(p1[1])

            elif p0[0] < p1[0] and p0[1] > p1[1]:
                random_lenght_x.append(p0[0])
                random_lenght_x.append(p1[0])
                random_lenght_y.append(p1[1] - abs(p1[0] - p0[0]) - abs(p1[1] - p0[1]))
                random_lenght_y.append(p0[1] + abs(p1[0] - p0[0]) + abs(p1[1] - p0[1]))

            elif p0[0] > p1[0] and p0[1] < p1[1]:
                random_lenght_x.append(p1[0])
                random_lenght_x.append(p0[0])
                random_lenght_y.append(p0[1])
                random_lenght_y.append(p1[1])

            elif p0[0] > p1[0] and p0[1] > p1[1]:
                random_lenght_x.append(p1[0])
                random_lenght_x.append(p0[0])
                random_lenght_y.append(p1[1] - abs(p1[0] - p0[0]) - abs(p1[1] - p0[1]))
                random_lenght_y.append(p0[1] + abs(p1[0] - p0[0]) + abs(p1[1] - p0[1]))

        v0 = np.array([np.cos(np.deg2rad(ang0)), np.sin(np.deg2rad(ang0))])
        v1 = np.array([np.cos(np.deg2rad(ang1)), np.sin(np.deg2rad(ang1))])

        for i in range(0, res, 1):
            u0 = uniform(0.0, random_lenght_x[1] - random_lenght_x[0])
            u1 = uniform(0.0, random_lenght_x[1] - random_lenght_x[0])

            c0 = p0 + u0 * v0
            c1 = np.array([uniform(random_lenght_x[0], random_lenght_x[1]), uniform(random_lenght_y[0],
                                                                                    random_lenght_y[1])])
            c2 = np.array([uniform(random_lenght_x[0], random_lenght_x[1]), uniform(random_lenght_y[0],
                                                                                    random_lenght_y[1])])
            c3 = p1 - u1 * v1
            curves.append(QuanticBezierCurve(p0, c0, c1, c2, c3, p1))

        return curves

    @staticmethod
    def particle_swarm(curves, ang0, ang1, a, b, res=5):
        # list_curves = [curves]

        v0 = np.array([np.cos(np.deg2rad(ang0)), np.sin(np.deg2rad(ang0))])
        v1 = np.array([np.cos(np.deg2rad(ang1)), np.sin(np.deg2rad(ang1))])

        best_rate = 9999.0

        best_curve = None

        for i in range(len(curves)):
            new_rate = curves[i].rate_curve(curves[i])
            if best_rate > new_rate:
                best_rate = new_rate
                best_curve = curves[i]

        # for i in range(res):
        for j in range(0, len(curves), 1):
            if best_curve != curves[j]:
                random_length_c0 = (best_curve.c0 - best_curve.p0) / v0 - (curves[j].c0 - curves[j].p0) / v0
                random_length_c1_x = best_curve.c1[0] - curves[j].c1[0]
                random_length_c1_y = best_curve.c1[1] - curves[j].c1[1]
                random_length_c2_x = best_curve.c2[0] - curves[j].c2[0]
                random_length_c2_y = best_curve.c2[1] - curves[j].c2[1]
                random_length_c3 = (best_curve.p1 - best_curve.c3) / v1 - (curves[j].p1 - curves[j].c3) / v1

                plus_c0 = uniform(random_length_c0 * a, random_length_c0 * b) * v0
                plus_c1 = np.array([uniform(random_length_c1_x * a, random_length_c1_x * b),
                                    uniform(random_length_c1_y * a, random_length_c1_y * b)])
                plus_c2 = np.array([uniform(random_length_c2_x * a, random_length_c2_x * b),
                                    uniform(random_length_c2_y * a, random_length_c2_y * b)])
                plus_c3 = uniform(random_length_c3 * a, random_length_c3 * b) * v1

                curves[j] = QuanticBezierCurve(curves[j].p0, curves[j].c0 + plus_c0, curves[j].c1 + plus_c1,
                                               curves[j].c2 + plus_c2, curves[j].c3 + plus_c3,
                                               curves[j].p1)
                new_rate = curves[j].rate_curve(curves[j])

                if best_rate > new_rate:
                    best_rate = new_rate
                    best_curve = curves[j]

            # list_curves.append(curves)

        # plt.show()
        return curves  # , best_curve

    @staticmethod
    def connect_curve(curve, q3, ang2):
        pass


def __str__(self):
    return 'p0- {} \nc0- {} \nc1- {} \nc2- {} \nc3- {} \np1- {} \nlength {}'.format(self.p0, self.c0, self.c1, self.c2,
                                                                                    self.c3, self.p1,
                                                                                    self.get_curve_length())
