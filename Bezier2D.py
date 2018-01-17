import FitCurves
from numpy import *
import matplotlib.pyplot as plt
from VMath import *



class QuadricCurve:
    def __init__(self, p0, h0, p1):
        self.p0 = p0
        self.h0 = h0
        self.p1 = p1

    def __str__(self):
        return "p0: {}, h0: {}, p1: {}".format(self.p0, self.h0, self.p1)


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


def find_circle_in_curve(c, t0=0.0, t1=1.0, tol=1):
    working = True
    ret = []
    while working:
        if t0 == 1:
            return ret
        tc = t0 + (t1 - t0) / 2.0
        p0 = bezier_position(c, t0)
        p1 = bezier_position(c, t1)
        pc = bezier_position(c, tc)
        if distance_points(p0, p1) < tol:
            ret.append([t1, [0, (p0, p1)]])
            t0 = t1
            t1 = 1
            continue
        circle = find_circle_by_points(p0, pc, p1)

        te0 = t0 + (tc - t0) / 2.0
        te1 = tc + (tc - t0) / 2.0

        pte0 = bezier_position(c, te0)
        pte1 = bezier_position(c, te1)

        if circle[0] is None or circle[1] is None:
            if distance_line(pte0, p0, p1) < tol and distance_line(pte1, p0, p1) < tol:
                ret.append([t1, [0, (p0, p1)]])
                t0 = t1
                t1 = 1
                continue
            t1 = tc
            continue

        r0 = distance_points(pte0, circle[1])
        r1 = distance_points(pte1, circle[1])
        if in_range(r0, circle[0], tol) and in_range(r1, circle[0], tol):
            ret.append([t1, circle])
            t0 = t1
            t1 = 1
        else:
            t1 = tc


def find_current_circle(t, cr):
    for circle in cr:
        if t <= circle[0]:
            return circle[1]


def find_parallel_curve_2(c, cr, d, res):
    top_array = []
    bot_array = []

    for i in xrange(0, int(res + 1)):
        curr_point = bezier_position(c, i / res)
        curr_circle = find_current_circle(i / res, cr)
        if curr_circle[0] == 0:
            first_point = curr_circle[1][0]
            second_point = curr_circle[1][1]

            forward_vector = second_point - first_point

            norm = normalize(forward_vector) * d
            turned_v = turn_90_degrees(norm)

            top_array.append(curr_point + turned_v)
            bot_array.append(curr_point - turned_v)

        else:
            mid_vector = curr_circle[1] - curr_point

            norm = normalize(mid_vector) * d
            top_array.append(curr_point + norm)
            bot_array.append(curr_point - norm)

    plus_curve = FitCurves.fitCurve(array(top_array), 0.001)
    minus_curve = FitCurves.fitCurve(array(bot_array), 0.001)

    plus = translate_to_curve(plus_curve)
    minus = translate_to_curve(minus_curve)

    return [plus, minus]


def find_parallel_curve_3(c, d, res):
    top_array = []
    bot_array = []
    for i in xrange(0, int(res + 1)):
        curr_point = bezier_position(c, i / res)
        curr_der = bezier_der(c, i / res)

        norm = normalize(curr_der) * d
        turned_v = turn_90_degrees(norm)

        top_array.append(curr_point + turned_v)
        bot_array.append(curr_point - turned_v)

    plot_point(top_array)
    plot_point(bot_array)

    plus_curve = FitCurves.fitCurve(V2A(top_array), 0.00001)
    minus_curve = FitCurves.fitCurve(V2A(bot_array), 0.00001)

    plus = translate_to_curve(plus_curve)
    minus = translate_to_curve(minus_curve)

    return [plus, minus]


def V2A(v):
    a = []
    for i in v:
        a.append(array([i.x, i.y]))
    return array(a)


def V2L(v):
    x = []
    y = []
    for i in v:
        x.append(i.x)
        y.append(i.y)
    return x, y


def get_curve_points(c, res):
    l = []
    for i in xrange(0, int(res + 1)):
        l.append(bezier_position(c, i / res))
    return l


def plot_point(l):
    vlist = l
    llist = V2L(vlist)
    plt.plot(llist[0], llist[1])


def find_parallel(c, d, res):
    ret = []
    for cc in c:
        p, m = find_parallel_curve_3(cc, d, res)
        ret.append([p, m])
    return ret

def find_cubic_curve(p0, ang0, p1, ang1):
    linear_dis = distance_points(p0, p1)
    h0x = p0.x
    h1x = p1.x
    h0y = p1.y/2
    h1y = p1.y/2

    return Curve(p0, Vector2D(h0x, h0y), Vector2D(h1x, h1y), p1)


def find_quardric_curve(p0, ang0, p1, ang1):
    linear_dis = distance_points(p0, p1)
    p0slope = tan(radians(ang0))
    p1slope = tan(radians(ang1))
    bp0 = -(p0slope * p0.x) + p0.y
    bp1 = -(p1slope * p1.x) + p1.y
    x = (bp1-bp0)/(p0slope-p1slope)
    y = p0slope*x+bp0

    return QuadricCurve(p0, Vector2D(x, y), p1)


def main():
    circle = False

    if not circle:
        aa = array([array([0, 0]), array([0, 0.05]), array([1.995, 1.495]), array([2, 1.5])])
        a = FitCurves.fitCurve(aa, 0.00001)
        c = translate_to_curve(a)

        ret = find_parallel(c, 0.1, 50.0)
        #
        for cc in c:
            vlist = get_curve_points(cc, 50.0)
            llist = V2L(vlist)
            plt.plot(llist[0], llist[1])

        for ccc in ret:
            p = ccc[0]
            m = ccc[0]

            for cc in m:
                vlist1 = get_curve_points(cc, 50.0)
                llist1 = V2L(vlist1)
                plt.plot(llist1[0], llist1[1])

            for cc in p:
                vlist2 = get_curve_points(cc, 50.0)
                llist2 = V2L(vlist2)
                plt.plot(llist2[0], llist2[1])
        plt.show()

    else:
        c = Curve(Vector2D(0, 0), Vector2D(0, 1), Vector2D(1, 0), Vector2D(1, 1))

        cr = find_circle_in_curve(c, tol=0.001)

        fig, ax = plt.subplots()
        for cir in cr:
            print cir
            if cir[1][0] == 0:
                plt.plot([cir[1][1][0].x, cir[1][1][1].x], [cir[1][1][0].y, cir[1][1][1].y])
            else:
                c1 = plt.Circle((cir[1][1].x, cir[1][1].y), cir[1][0], Fill=False)
                ax.add_artist(c1)

        vlist = get_curve_points(c, 50.0)
        llist = V2L(vlist)
        plt.plot(llist[0], llist[1])
        plt.show()


if __name__ == "__main__":
    main()
