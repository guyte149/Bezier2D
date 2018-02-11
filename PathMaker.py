import numpy as np
import re
from bezyea import *
import matplotlib.pyplot as plt
from file_writer import File_Writer

curves = []

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

# angle at the first point is always 90 deg
waypoints[0] = (waypoints[0][0], 90)

for i in xrange(len(waypoints) - 1):
    p0 = waypoints[i][0]
    ang0 = waypoints[i][1]
    p1 = waypoints[i + 1][0]
    ang1 = waypoints[i + 1][1]

    curves.append(CubicBezierCurve.create_curve(p0, ang0, p1, ang1))

print("\n[-] Done! Calculating trajectory...")

path = BezierPath(curves)
trajectory = Trajectory(path)

# trajectory.build_center_trajectory(0.67, 1, 1)
trajectory.build_trajectory(0.67, 2.18, 1.5)
# for s in trajectory.left_trajectory:
#     print s
fw = File_Writer(trajectory)
fw.write()
trajectory.draw_trajectory()
