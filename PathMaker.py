import numpy as np
from bezyea import *

curves = []
# path = BezierPath()
s = input("how many curves?")
for i in xrange(0, s):
    p0x = input("p0x:")
    p0y = input("p0y:")
    p0 = np.array([p0x, p0y])
    ang0 = input("angle 0:")
    p1x = input("p1x:")
    p1y = input("p1y:")
    p1 = np.array([p1x, p1y])
    ang1 = input("angle 1:")
    curves.append(CubicBezierCurve.create_curve(p0, ang0, p1, ang1))

path = BezierPath(curves)
path.draw_path()

