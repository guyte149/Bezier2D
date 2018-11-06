# import matplotlib.pyplot as plt
from bezyea import *

p0 = np.array([0, 0])
ang0 = 90
p1 = np.array([1, 1])
ang1 = 90
p2 = np.array([2, 2])
ang2 = 0
#
# c2 = []
# for i in range(5):
#     c1 = Optimization.random_search(p0, ang0, p1, ang1)
#     c2.append(c1)
c1 = Optimization.start_curves_particle_swarm(p0, ang0, p1, ang1)
# print c1
c2 = Optimization.particle(c1, ang0, ang1, 0.1, 0.25)
path = BezierPath([c1])
path.draw_path()
# c1 = [QuanticBezierCurve.random_search(p0, ang0, p1, ang1)]
# c1 = QuanticBezierCurve.create_curve(p0, ang0, p1, ang1)
# # c1 = QuanticBezierCurve.random_search(p0, ang0, p1, ang1)
# c1 = QuanticBezierCurve.start_curves_particle_swarm(p0, ang0, p1, ang1)
# c2 = QuanticBezierCurve.particle_swarm(c1, ang0, ang1, 0.1, 0.25)
# list_curves = [c2]
# print c2.rate_curve(c2)
# path = BezierPath(c2)
# path.draw_path()
# for i in range(1, 5, 1):
#     c2 = QuanticBezierCurve.particle_swarm(c2, ang0, ang1, 0.1, 0.25)
#     list_curves.append(c2)
# path = BezierPath([c2])
# path.draw_path()

# print 'Curvature change at the beginning: {}'.format(c1.get_curvature(1.0 / 150.0) - c1.get_curvature(0.0 / 150.0))
# print 'Curvature change at the end: {}'.format(c1.get_curvature(150.0 / 150.0) - c1.get_curvature(149.0 / 150.0))
# print 'Max curvature change: {}'.format(c1.get_max_curvature_change())
# print 'Rate curve: {}'.format(c1.rate_curve(c1))
# print 'Length curve: {}'.format(c1.get_curve_length())
# print c1.get_curvature(0.5)
# c1 = [QuanticBezierCurve.random_search(p0, ang0, p1, kang1)]
# path = [BezierPath(c1)]
# for i in range(1, 3, 1):
#     c1.append(QuanticBezierCurve.random_search(p0, ang0, p1, ang1))
# for t in range(0, 10, 1):
#     path.append(BezierPath(([c1[t]])))
#     path[t].draw_path()
# c2 = QuanticBezierCurve.create_curve(p0, ang0, p1, ang1)
# # q = CubicBezierCurve.create_curve(p0, ang0, p1, ang1)
# q = CubicBezierCurve.connect_curve(c, p2, ang2)
# print c1[i].rate_curve(c1)
# for i in range(0, 5, 1):
#     path = BezierPath([c1[i]])
#     path.draw_path()
# print c2.rate_curve(c2)
# print c1.get_max_curvature_change()
# q1 = QuanticBezierCurve.random_search(p0, ang0, p1, ang1)
# p = BezierPath([c1])
# p = BezierPath(c1)
# p.draw_path()
# p = BezierPath([q])
# p.draw_path()
# print q.rate_curve(q)
# p = BezierPath([q])
# p.draw_path()
#

# print 'Curvature change at the beginning: {}'.format(q1.get_curvature(1.0 / 150.0) - q1.get_curvature(0.0 / 150.0))
# print 'Curvature change at the end: {}'.format(q1.get_curvature(150.0 / 150.0) - q1.get_curvature(149.0 / 150.0))
# print 'Max curvature change: {}'.format(q1.get_max_curvature_change())
# print 'Rate curve: {}'.format(q1.rate_curve(q1))
# print 'Length curve: {}'.format(q1.get_curve_length())
# p = BezierPath([c1])
# p.draw_path()

# y_list = []
# x_list = []p0, ang0, p1, ang1)
# TypeError: particle_swarm() takes at most 4 arguments (
# for t in xrange(0, 1001):
#     x_list.append(q(t/1000.0)[0])
#     y_list.append(q(t/1000.0)[1])
#     # print 't={},  R={}'.format(t/1000.0, 1/q.get_curvature(t/1000.0))
#     # print "t= {}    ang= {}".format(t,
# q.get_angle(t/1000.0))
# ls = q.get_setpoints(0.001)
# print len(ls)
# for p in ls:
#     # print p
#     x_list.append(p[0])
#     y_list.append(p[1])
# plt.axes().set_aspect('equal', 'datalim')
# plt.plot(x_list, y_list)
# plt.show()
