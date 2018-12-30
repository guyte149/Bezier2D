# import matplotlib.pyplot as plt
from bezyea import *
from Optimization import *
from Animation import *

p0 = np.array([0, 0])
ang0 = 90
p1 = np.array([1, 4])
ang1 = 60
p2 = np.array([5, 5])
ang2 = 0
p3 = np.array([6, 6])
ang3 = 120

# c1 = ParticleSwarm.start_curves(p0, ang0, p1, ang1)
# anim = Animation(ang0, ang1, c1)
# anim.display()
c3 = ParticleSwarm.last_curves(p0, ang0, p1, ang1)
c2 = ParticleSwarm.last_curves_connect_first_derivative(c3.best_curve, ang1, p2, ang2)
c4 = ParticleSwarm.last_curves_connect_first_derivative(c2.best_curve, ang2, p3, ang3)
# c1 = ParticleSwarm.start_curves_connect(c3.best_curve, ang1, p2, ang2)
# anim = AnimationConnection(c3.best_curve, ang1, p2, ang2)
anim = AnimationConnection(c2.best_curve, ang2, p3, ang3)
anim.display()
# anim = Animation(ang0, ang1, c1)
# anim.display()

# print c4.best_curve.c2
path = BezierPath([c4.best_curve, c3.best_curve, c2.best_curve])
path.draw_path()
# c1 = QuanticBezierCurve.create_curve(p0, ang0, p1, ang1)
# path = BezierPath([c1])
# path.draw_path()

# c1 = ParticleSwarm.last_curves(p0, ang0, p1, ang1)
# print c1.best_curve
# c2 = ParticleSwarm.last_curves_conect(c1.best_curve, ang1, p2, ang2)

# path = BezierPath([c1.best_curve, c2.best_curve])
# path.display()rwt
# path.draw_path()
