# import matplotlib.pyplot as plt
from bezyea import *

p0 = np.array([0, 0])
ang0 = 90
p1 = np.array([1, 1])
ang1 = 90
p2 = np.array([2, 2])
ang2 = 0

c = CubicBezierCurve.create_curve(p0, ang0, p1, ang1)
q = CubicBezierCurve.connect_curve(c, p2, ang2)
path = BezierPath([c, q])
path.draw_path()

# y_list = []
# x_list = []
# for t in xrange(0, 1001):
#     x_list.append(q(t/1000.0)[0])
#     y_list.append(q(t/1000.0)[1])
#     # print 't={},  R={}'.format(t/1000.0, 1/q.get_curvature(t/1000.0))
#     # print "t= {}    ang= {}".format(t, q.get_angle(t/1000.0))
# ls = q.get_setpoints(0.001)
# print len(ls)
# # for p in ls:
# #     # print p
# #     x_list.append(p[0])
# #     y_list.append(p[1])
# plt.axes().set_aspect('equal', 'datalim')
# plt.plot(x_list, y_list)
# plt.show()
