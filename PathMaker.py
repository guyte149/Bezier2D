import numpy as np
import re
from bezyea import *
import matplotlib.pyplot as plt


curves = []
# path = BezierPath()

waypoints = []

print("[-] Please enter the waypoint of the path in the following format: [x], [y], [deg_angle] :  \n")
while True:
    inp = raw_input("> ")

    inp = str(inp)
    matches = re.search('''(\S+)\s?,\s?(\S+)\s?,\s?(\S+)''', inp)

    if matches is None:
        break

    x = float(matches.group(1))
    y = float(matches.group(2))
    ang = float(matches.group(3))
    waypoints.append((np.array([x, y]), ang))

for i in xrange(len(waypoints) - 1):
    p0 = waypoints[i][0]
    ang0 = waypoints[i][1]
    p1 = waypoints[i + 1][0]
    ang1 = waypoints[i + 1][1]

    curves.append(CubicBezierCurve.create_curve(p0, ang0, p1, ang1))

print("\n[-] Done! Calculating trajectory...")

path = BezierPath(curves)
trajectory = Trajectory(path)
# trajectory.build_trajectory(0.67, 2.18, 2)

for s in trajectory.setpoints:
    print s

# plt.plot([s.p for s in trajectory.setpoints], [s.v for s in trajectory.setpoints])
# plt.show()
path.draw_path()
