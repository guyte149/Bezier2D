from h import *
import matplotlib.pyplot as plt

c = Curve(Vector2D(0, 0), Vector2D(0, 1), Vector2D(1, 0), Vector2D(1, 1))
cr = find_circle_in_curve(c, res=0.01)
print "we got a cr"
p, m = find_parallel_curve(5, c, cr, 100)

plt.show()
