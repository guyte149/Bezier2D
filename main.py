import matplotlib.pyplot as plt
from bezyea import *

p0 = np.array([0, 0])
ang0 = 0
p1 = np.array([1, 1])
ang1 = 0

q = CubicBezierCurves.create_curve(p0, ang0, p1, ang1)
print q

y_list = []
x_list = []
for t in xrange(1, 101):
    x_list.append(q(t/100.0)[0])
    y_list.append(q(t/100.0)[1])

plt.plot(x_list, y_list)
plt.show()
