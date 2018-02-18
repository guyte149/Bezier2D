import numpy as np
import re
from bezyea import *
import matplotlib.pyplot as plt
from filewriter import FileWriter

curves = []

waypoints = []

path_name = raw_input("Path name: ")


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
# > 0,0,90
# # > 1,1,0
# # > 3,-1.575,0
print("\n[-] Done! Calculating trajectory...")

path = BezierPath(curves)
trajectory = Trajectory(path)

# trajectory.build_center_trajectory(0.67, 1, 1)
trajectory.build_trajectory(0.67, 1.4, 0.7)
print len(trajectory.right_trajectory)
# for s in trajectory.left_trajectory:
#     print s
right_trajectory_sliced, left_trajectory_sliced = Trajectory.trajectory_slice_constant_dt(trajectory)
fw = FileWriter(left_trajectory_sliced, right_trajectory_sliced, path_name)
fw.write()
trajectory.draw_trajectory()
