import numpy as np
from bezyea import *

p0 = np.array([0, 0])
ang0 = 45
p1 = np.array([1, 1])
ang1 = 45
q = CubicBezierCurve.create_curve(p0, ang0, p1, ang1)

q.draw_curve()
