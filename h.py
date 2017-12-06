import FitCurves
from numpy import *


class Vector2D:
    def __init__(self, x, y):
        self.x = float(x)
        self.y = float(y)

    def __mul__(self, other):
        new_x = self.x
        new_y = self.y
        if isinstance(other, int):
            other = float(other)
        if isinstance(other, float):
            new_x *= other
            new_y *= other
        elif isinstance(other, Vector2D):
            new_x *= other.x
            new_y *= other.y
        return Vector2D(new_x, new_y)

    def __add__(self, other):
        new_x = self.x
        new_y = self.y
        if isinstance(other, Vector2D):
            new_x += other.x
            new_y += other.y
            return Vector2D(new_x, new_y)

    def __sub__(self, other):
        new_x = self.x
        new_y = self.y
        if isinstance(other, Vector2D):
            new_x -= other.x
            new_y -= other.y
            return Vector2D(new_x, new_y)

    def __neg__(self):
        return Vector2D(-self.x, -self.y)

    def __str__(self):
        return "({}, {})".format(self.x, self.y)


class Curve:
    # a curve is a list of 4 points. two are points and two are headers
    # they are arranged in this order : point0 , header0, header1, point1
    def __init__(self, p0=0.0, h0=0.0, h1=0.0, p1=0.0):
        self.p0 = p0
        self.h0 = h0
        self.h1 = h1
        self.p1 = p1

    def set_linear(self):
        self.h0 = self.p0 * (2.0 / 3) + self.p1 * (1.0 / 3)
        self.h1 = self.p0 * (1.0 / 3) + self.p1 * (2.0 / 3)

    def __str__(self):
        return "p0:{}, h0:{}, h1:{}, p1:{}".format(self.p0, self.h0, self.h1, self.p1)

    def list_to_curve(self, l):
        self.p0 = l[0]
        self.h0 = l[1]
        self.h1 = l[2]
        self.p1 = l[3]


def bezier_position(c, t):
    t = float(t)
    omt = 1 - t
    return (c.p0 * omt * omt * omt) + (c.h0 * 3 * omt * omt * t) + (c.h1 * 3 * omt * t * t) + (c.p1 * t * t * t)


def bezier_der(c, t):
    # return (c.p0 * (-3 * (1 - t) * (1 - t))) + (c.h0 * 3 * ((1 - 4 * t) + (3 * t * t))) + (
    #     c.h1 * 3 * ((2 * t) - (3 * t * t))) + (c.p1 * 3 * t * t)
    return ((c.h0 - c.h1) * 3.0 * (1 - t) * (1 - t)) + ((c.h1 - c.h0) * 6 * (1 - t) * t) + ((c.p1 - c.h1) * 3 * t * t)


def bezier_der2(c, t):
    # return (c.p0 * 6 * (1 - t)) + (c.h0 * 3 * (-4 + (6 * t))) + (c.h1 * 3 * (2 - (6 * t))) + (c.p1 * 6 * t)
    return ((c.h1 - (c.h0 * 2) + c.p0) * 6 * (1 - t)) + ((c.p1 - (c.h1 * 2) + c.h0) * 6 * t)


def normal(p):
    return sqrt(float(pow(p.x, 2)) + float(pow(p.y, 2)))


def curvature_by_t(c, t):
    der1 = bezier_der(c, t)
    der2 = bezier_der2(c, t)
    return (der1.x * der2.y) - (der1.y * der2.x) * pow(normal(der1), 3)


def split_by_parameters(c, c0, c1, t):
    u = 1.0 - t
    c0.p0 = c.p0
    c0.h0 = c.p0 * u + c.h0 * t
    c0.h0 = c.p0 * u + c.h0 * t
    c1.h1 = c.p1 * t + c.h1 * u
    c1.p1 = c.p1
    #
    #  cv::Vec2d tmp = t*c.h1 + u*c.h0;
    tmp = c.h1 * t + c.h0 * u
    c0.h1 = tmp * t + c0.h0 * u
    c1.h0 = tmp * u + c1.h1 * t
    #
    c0.p1 = c0.h1 * u + c1.h0 * t
    c1.p0 = c0.p1
    return [c0, c1]


def dot(p1, p2):
    return float(p1.x * p2.x + p1.y * p2.y)


def flatten(c, tol):
    total_length = 0
    curr_beg = 0
    ret = [(c.p0, curr_beg, total_length)]

    end_stack = [(c, 1)]

    while len(end_stack):
        cc = end_stack[-1][0]
        curr_end = end_stack[-1][1]

        end_stack.pop(-1)

        p0 = cc.p0
        dir = cc.p1 - p0
        h0 = cc.h0 - p0
        h1 = cc.h1 - p0

        length2 = dot(dir, dir)

        p = Vector2D(dir.x, -dir.y)

        e0 = dot(p, h0)
        e1 = dot(p, h1)

        if ((e0 * e0) > length2 * (tol * tol) or (e1 * e1) > length2 * (tol * tol) or (dot(dir, h0) * dot(dir, h0)) < - \
                length2 * (tol * tol) * 0.01 or (dot(dir, h1) * dot(dir, h1)) < -length2 * (
                    tol * tol) * 0.01) and curr_end != 0:
            c0 = Curve()
            c1 = Curve()

            mid = (curr_end + curr_beg) * 0.5

            temp_c = split_by_parameters(cc, c0, c1, 0.5)
            c0 = temp_c[0]
            c1 = temp_c[1]

            end_stack.append((c1, curr_end))
            end_stack.append((c0, mid))
        else:

            total_length += math.sqrt(length2)
            ret.append((cc.p1, curr_end, total_length))
            curr_beg = curr_end

    return ret


def get_bezier_length(vp1, vp1_tan, vp2_tan, vp2, eps):
    c = Curve(vp1, vp1_tan, vp2_tan, vp2)
    flat_res = flatten(c, eps)
    if len(flat_res) == 0:
        return 0.0

    flt = flat_res[-1]
    leng = flt[2]
    return float(leng)


# tol in length from actual line
# this function is not inserting the first point
def interpolate_bezier(points, vp1, vp1_h, vp2_h, vp2, eps):
    c = Curve(vp1, vp1_h, vp2_h, vp2)
    # point, params and total length
    flat_res = flatten(c, eps)

    # enumerate all the points
    prev_len = 0
    for i in flat_res[1:]:
        # add only if the point has some length
        curr_len = flat_res[i][2]
        if curr_len > prev_len:
            points.append([flat_res[i]])
        prev_len = curr_len

    return points


def get_length_by_time(c, max_speed):
    total_length = get_bezier_length(c.p0, c.h0, c.h1, c.p1, 0.01)

    total_time = ((total_length / (max_speed * 0.8)) * 100) + 1
    ret = []

    for i in xrange(0, int(total_time)):
        c0 = split_by_parameters(c, Curve(), Curve(), i / total_time)[0]
        i_length = get_bezier_length(c0.p0, c0.h0, c0.h1, c0.p1, 0.01)
        ret.append((i, i_length))

    return ret


def translate_to_curve(arr):
    curve_list = []
    if isinstance(arr[0], ndarray):
        c = Curve()
        a = []
        for i in arr[0]:
            a.append(Vector2D(i[0], i[1]))
        c.list_to_curve(a)
        curve_list.append(c)
    else:
        for i in arr:
            c = Curve()
            a = []
            for j in i:
                a.append(Vector2D(j[0], j[1]))
            c.list_to_curve(a)
            curve_list.append(c)
    return curve_list


def find_circle_by_points(p1, p2, p3, tol=0.001):
    if (in_range(p1.x, p2.x, tol) and in_range(p1.y, p2.y, tol)) or (
                in_range(p2.x, p3.x, tol) and in_range(p2.y, p3.y, tol)) or (
                in_range(p1.x, p3.x, tol) and in_range(p1.y, p3.y, tol)):
        print "error some points are on the same line"
        return [None, Vector2D(0, 0), 0, 0]

    if (p3.y - p2.y) / (p3.x - p2.x) == (p2.y - p1.y) / (p2.x - p1.x):
        print "error points on the same line"
        return [None, Vector2D(0, 0), 0, 0]

    a = p1.x * (p2.y - p3.y) - p1.y * (p2.x - p3.x) + p2.x * p3.y - p3.x * p2.y
    b = (pow(p1.x, 2) + pow(p1.y, 2)) * (p3.y - p2.y) + (pow(p2.x, 2) + pow(p2.y, 2)) * (p1.y - p3.y) + (pow(p3.x,
                                                                                                             2) + pow(
        p3.y, 2)) * (p2.y - p1.y)
    c = (pow(p1.x, 2) + pow(p1.y, 2)) * (p2.x - p3.x) + (pow(p2.x, 2) + pow(p2.y, 2)) * (p3.x - p1.x) + (pow(p3.x,
                                                                                                             2) + pow(
        p3.y, 2)) * (p1.x - p2.x)
    d = (pow(p1.x, 2) + pow(p1.y, 2)) * (p3.x * p2.y - p2.x * p3.y) + (pow(p2.x, 2) + pow(p2.y, 2)) * (
        p1.x * p3.y - p3.x * p1.y) + (pow(p3.x, 2) + pow(p3.y, 2)) * (p2.x * p1.y - p1.x * p2.y)
    if a == 0:
        return [None, Vector2D(0, 0), 0, 0]
    radius = sqrt((b * b + c * c - 4 * a * d) / (4 * a * a))
    center_x = -b / (2 * a)
    center_y = -c / (2 * a)
    return [radius, Vector2D(center_x, center_y)]


def in_range(c_num, num, tol):
    return abs(num - c_num) <= tol


def distance_points(p0, p1):
    return sqrt(pow(p1.x - p0.x, 2) + pow(p1.y - p0.y, 2))


def find_circle_in_curve(c, t0=0.0, t1=1.0, res=1):
    working = True
    ret = []
    while working:
        tc = t0 + (t1 - t0) / 2.0
        p0 = bezier_position(c, t0)
        p1 = bezier_position(c, t1)
        pc = bezier_position(c, tc)
        if distance_points(p0, p1) < 0.1:
            ret.append([t1, [0, None]])
            t0 = t1
            t1 = 1
            continue
        circle = find_circle_by_points(p0, pc, p1)
        if circle[0] is None or circle[1] is None:
            ret.append([t1, [0, None]])
            t0 = t1
            t1 = 1
            continue
        te0 = t0 + (tc - t0) / 2.0
        te1 = tc + (tc - t0) / 2.0

        pte0 = bezier_position(c, te0)
        pte1 = bezier_position(c, te1)
        r0 = distance_points(pte0, circle[1])
        r1 = distance_points(pte1, circle[1])
        if in_range(r0, circle[0], res) and in_range(r1, circle[0], res):
            ret.append([t1, circle])
            t0 = t1
            t1 = 1
            if t0 == 1:
                return ret
        else:
            t1 = tc

def main():
    curve = FitCurves.fitCurve(
        array([array([0, 1]), array([1, 0]), array([2, 1]), array([1, 2]), array([0, 1])]), 0.001)

    p = translate_to_curve(curve)
    # c = Curve(Vector2D(0, 2), Vector2D(0, 0), Vector2D(2, 2), Vector2D(2, 0))
    # c.set_linear()

    # c0, c1 = split_by_parameters(c, Curve(), Curve(), 0.5)
    # c = 0.551915024494
    # p = [Curve(Vector2D(0, 1), Vector2D(c, 1), Vector2D(1, c), Vector2D(1, 0)),
    #      Curve(Vector2D(1, 0), Vector2D(1, -c), Vector2D(c, -1), Vector2D(0, -1)),
    #      Curve(Vector2D(0, -1), Vector2D(-c, -1), Vector2D(-1, -c), Vector2D(-1, 0)),
    #      Curve(Vector2D(-1, 0), Vector2D(-1, c), Vector2D(-c, 1), Vector2D(0, 1))]

    for i, curve in enumerate(p):
        cr = find_circle_in_curve(curve, res=0.01)
        print "-------curve {}------".format(i+1)
        for c in cr:
            print "t:{}: {}, {}".format(c[0], c[1][0], c[1][1])
        # for i in xrange(1, 10):
        #   p = bezier_position(curve, i / 10.0)
        #   print curvature_by_t(curve, i / 10.0)

        #       print get_length_by_time(c, 4)
        # print "{}, {}".format(bezier_der(p[0], 0.5), bezier_der(p[2], 0.5))
        # print "{}, {}".format(curvature_by_t(p[0], 0.5), curvature_by_t(p[2], 0.5))
        # outp = find_circle_by_points(Vector2D(0, 0), Vector2D(1, 1), Vector2D(2, 0))
        # print "{} {}".format(outp[0], outp[1])


main()
