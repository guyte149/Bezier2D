import FitCurves
from numpy import *
import matplotlib.pyplot as plt
from Bezier2D import *


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

    def slope(self, other):
        return (other.y - self.y) / (other.x / self.x)


class LinearEquation:
    def __init__(self, p, m):
        self.p = p
        self.m = m

    def find_points_by_length(self, r):
        a = (pow(self.m, 2) + 1)
        b = (2 * pow(self.m, 2) * self.p.x) - (2 * self.p.x)
        c = (- pow(r, 2)) + pow(self.p.x, 2) + (pow(self.m, 2) * self.p.x)

        d = b ** 2 - 4 * a * c  # discriminant

        if d < 0:
            print ("Error delta is less than 0")
        elif d == 0:
            x = (-b + math.sqrt(b ** 2 - 4 * a * c)) / 2 * a
            return [Vector2D(x, (self.m * x) - (self.m * self.p.x) + self.p.y)]
        else:
            x1 = (-b + math.sqrt((b ** 2) - (4 * (a * c)))) / (2 * a)
            x2 = (-b - math.sqrt((b ** 2) - (4 * (a * c)))) / (2 * a)
            return [Vector2D(x1, (self.m * x1) - (self.m * self.p.x) + self.p.y),
                    Vector2D(x2, (self.m * x2) - (self.m * self.p.x) + self.p.y)]


def bezier_position(c, t):
    t = float(t)
    omt = 1 - t
    return (c.p0 * omt * omt * omt) + (c.h0 * 3 * omt * omt * t) + (c.h1 * 3 * omt * t * t) + (c.p1 * t * t * t)


def bezier_der(c, t):
    return (c.p0 * (-3 * (1 - t) * (1 - t))) + (c.h0 * 3 * ((1 - 4 * t) + (3 * t * t))) + (
        c.h1 * 3 * ((2 * t) - (3 * t * t))) + (c.p1 * 3 * t * t)
    # return ((c.h0 - c.h1) * 3.0 * (1 - t) * (1 - t)) + ((c.h1 - c.h0) * 6 * (1 - t) * t) + ((c.p1 - c.h1) * 3 * t * t)


def bezier_der2(c, t):
    # return (c.p0 * 6 * (1 - t)) + (c.h0 * 3 * (-4 + (6 * t))) + (c.h1 * 3 * (2 - (6 * t))) + (c.p1 * 6 * t)
    return ((c.h1 - (c.h0 * 2) + c.p0) * 6 * (1 - t)) + ((c.p1 - (c.h1 * 2) + c.h0) * 6 * t)


def length(p):
    return sqrt(float(pow(p.x, 2)) + float(pow(p.y, 2)))


def length2(p):
    return float(pow(p.x, 2)) + float(pow(p.y, 2))


def normalize(v):
    return v * (1 / length(v))


def dot(p1, p2):
    return float(p1.x * p2.x + p1.y * p2.y)


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


def distance_line(p, ps, pe):
    V = pe - ps
    W = p - ps
    Dot = dot(V, W)
    if Dot <= 0:
        return length(W)

    SqrNorm = length2(V)
    if SqrNorm <= Dot:
        W = p - pe
        return length(W)

    T = Dot / SqrNorm
    norm = W - (V * T)
    return length(norm)


def turn_90_degrees(v):
    return Vector2D(v.y, -v.x)

