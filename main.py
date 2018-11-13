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

c1 = ParticleSwarm.start_curves(p0, ang0, p1, ang1)
anim = Animation(ang0, ang1, c1)
anim.display()


# path = BezierPath(c1)
# path.display()
# path.draw_path()
