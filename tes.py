from Bezier2D import *
import matplotlib.pyplot as plt
from VMath import *

c = find_cubic_curve(Vector2D(0, 0), 90, Vector2D(1, 1), 90)
# c = find_quardric_curve(Vector2D(0, 0), 70, Vector2D(1, 1), 20)
# c = QuadricCurve(Vector2D(0, 0), Vector2D(0, 1), Vector2D(1, 1))

print c
x_list = []
y_list = []
for i in xrange(0, 101):
    # curr_point = quadric_position(c, i/100.0)
    curr_point = bezier_position(c, i/100.0)
    x_list.append(curr_point.x)
    y_list.append(curr_point.y)
plt.plot(x_list, y_list)

plt.show()
