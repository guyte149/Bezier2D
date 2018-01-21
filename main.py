import matplotlib.pyplot as plt
from bezyea import *

p0 = np.array([0, 0])
ang0 = 90
p1 = np.array([1, 1])
ang1 = 0

q = CubicBezierCurves.create_curve(p0, ang0, p1, ang1)
print q

y_list = []
x_list = []
# for t in xrange(1, 1001):
#     x_list.append(q(t/1000.0)[0])
#     y_list.append(q(t/1000.0)[1])
ls = q.get_equal_arcs(0.01)
for p in ls:
    x_list.append(p[0])
    y_list.append(p[1])
plt.plot(x_list, y_list, 'ro')
plt.show()
