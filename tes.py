from Bezier2D import *
import matplotlib.pyplot as plt
from VMath import *
from bezyea import CubicBezierCurves

p0 = np.array([0, 0])
ang0 = 90
p1 = np.array([1, 0])
ang1 = 270

q = CubicBezierCurves.create_curve(p0, ang0, p1, ang1)
# c = find_quardric_curve(Vector2D(0, 0), 70, Vector2D(1, 1), 20)
# c = QuadricCurve(Vector2D(0, 0), Vector2D(0, 1), Vector2D(1, 1))

print q
x_list = []
y_list = []

for i in xrange(0, 101):
    # curr_point = quadric_position(c, i/100.0)
    curr_point = q(i / 100.0)
    derivative_point = q.bezier_derivative(i/100.0)
    sec_der_point = q.second_bezier_derivative(i/100.0)
    x_list.append(curr_point[0])
    y_list.append(curr_point[1])
    print '{} = {}   {}'.format('t', i/100.0, q.get_curvature(i / 100.0))
    # x_list.append(derivative_point[0])
    # y_list.append(derivative_point[1])
    # x_list.append(sec_der_point[0])
    # y_list.append(sec_der_point[1])

plt.plot(x_list, y_list)
plt.show()
