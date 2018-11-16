# import matplotlib.pyplot as plt
from bezyea import *
from Optimization import *
from Animation import *

p0 = np.array([0, 0])
ang0 = 90
p1 = np.array([1, 1])
ang1 = 90
p2 = np.array([2, 2])
ang2 = 0

# c1 = ParticleSwarm.start_curves(p0, ang0, p1, ang1)
# anim = Animation(ang0, ang1, c1)
# anim.display()
c3 = ParticleSwarm.last_curves(p0, ang0, p1, ang1)
c2 = ParticleSwarm.start_curves_connect(c3.best_curve, ang1, p2, ang2)
anim = AnimationConnection(c3.best_curve, ang1, ang2, c2)
anim.display()

# c1 = QuanticBezierCurve.create_curve(p0, ang0, p1, ang1)
# path = BezierPath([c1])
# path.draw_path()

# c1 = ParticleSwarm.last_curves(p0, ang0, p1, ang1)
# print c1.best_curve
# c2 = ParticleSwarm.last_curves_conect(c1.best_curve, ang1, p2, ang2)

# path = BezierPath([c1.best_curve, c2.best_curve])
# path.display()
# path.draw_path()
