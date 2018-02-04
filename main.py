import matplotlib.pyplot as plt
from bezyea import *

p0 = np.array([0, 0])
ang0 = 0
p1 = np.array([1, 0])
ang1 = 0

q = CubicBezierCurve.create_curve(p0, ang0, p1, ang1)
print q

y_list = []
x_list = []
for t in xrange(0, 1001):
    x_list.append(q(t/1000.0)[0])
    y_list.append(q(t/1000.0)[1])
    print 't={},  R={}'.format(t/1000.0, 1/q.get_curvature(t/1000.0))
# ls = q.get_equal_arcs(0.001)
# print len(ls)
# for p in ls:
#     # print p
#     x_list.append(p[0])
#     y_list.append(p[1])
plt.plot(x_list, y_list)
plt.show()
