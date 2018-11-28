import os
import re
from bezyea import *
import math
from filewriter import FileWriter
from PIL import Image
from PIL import ImageFont
from PIL import ImageDraw
import tkFileDialog

curves = []
waypoints = []
max_v = 1.6
max_a = 1.25
path_name = raw_input("Path name: ")

points_text_list = []
print("[-] Please enter the waypoint of the path in the following format: [x], [y], [deg_angle] :  \n")
while True:
    inp = raw_input("> ")

    inp = str(inp)
    matches = re.search('''(\S+)\s?,\s?(\S+)\s?,\s?(\S+)''', inp)

    if matches is None:
        break
    point_text = "{}, {}, {}".format(matches.group(1), matches.group(2), matches.group(3))
    points_text_list.append(point_text)
    x = float(matches.group(1))
    y = float(matches.group(2))
    ang = float(matches.group(3))
    waypoints.append((np.array([x, y]), ang))

# angle at the first point is always 90 deg

# print waypoints[0][1]
if (waypoints[0][1] - 90) % 360 != 0:
    if waypoints[0][1] % 90 != 0:
        for i in xrange(1, len(waypoints)):
            x = [waypoints[0][0][0]]
            y = [waypoints[0][0][1]]
            ang = [waypoints[0][1]]
            x.append(waypoints[i][0][0])
            y.append(waypoints[i][0][1])
            ang.append(waypoints[i][1])
            newX = [y[0]]
            newY = [x[0]]
            newAng = [90]

            yAxis = math.tan(math.radians(ang[0] - 90))
            xAxis = math.tan(math.radians(ang[0]))
            x.append((yAxis * x[1] - y[1]) / (yAxis - xAxis))
            y.append(xAxis * (x[2]))
            x.append((xAxis * x[1] - y[1]) / (xAxis - yAxis))
            y.append((xAxis * (x[3] - x[1]) + y[1]))

            ynew = (math.sqrt(pow(x[3] - x[1], 2) + pow(y[3] - y[1], 2)) * ((y[1] - y[3]) / abs(y[1] - y[3])))
            xnew = (math.sqrt(pow(x[2] - x[1], 2) + pow(y[2] - y[1], 2)) * ((x[1] - x[2]) / abs(x[1] - x[2])))
            angNew = (90 - (ang[0] - ang[1]))
            waypoints[i] = (np.array([xnew, ynew]), angNew)
        waypoints[0] = (np.array([0, 0]), 90)
    elif waypoints[0][1] % 360:
        for i in xrange(1, len(waypoints)):
            ang = [waypoints[0][1]]
            ang.append(waypoints[i][1])
            angNew = (90 - (ang[0] - ang[1]))
            waypoints[i] = (np.array([-waypoints[i][0][1], waypoints[i][0][0]]), angNew)
        waypoints[0] = (np.array([0, 0]), 90)
    elif (waypoints[0][1] - 180) % 360:
        for i in xrange(1, len(waypoints)):
            ang = [waypoints[0][1]]
            ang.append(waypoints[i][1])
            angNew = (90 - (ang[0] - ang[1]))
            waypoints[i] = (np.array([waypoints[i][0][1], -waypoints[i][0][0]]), angNew)
        waypoints[0] = (np.array([0, 0]), 90)
    elif (waypoints[0][1] - 270) % 360:
        for i in xrange(1, len(waypoints)):
            ang = [waypoints[0][1]]
            ang.append(waypoints[i][1])
            angNew = (90 - (ang[0] - ang[1]))
            waypoints[i] = (np.array([-waypoints[i][0][0], -waypoints[i][0][1]]), angNew)
        waypoints[0] = (np.array([0, 0]), 90)

print waypoints
for i in xrange(len(waypoints) - 1):
    p0 = waypoints[i][0]
    ang0 = waypoints[i][1]
    p1 = waypoints[i + 1][0]
    ang1 = waypoints[i + 1][1]
    # if p0[1] == p1[1] and ang0 == ang1 == 0:
    #     p1[1] = p1[1]-0.005
    curves.append(CubicBezierCurve.create_curve(p0, ang0, p1, ang1))
# > 0,0,90
# > -0.7,4,90
# > 3.5,5.5,0
print("\n[-] Done! Calculating trajectory...")

path = BezierPath(curves)
trajectory = Trajectory(path)

# trajectory.build_center_trajectory(0.67, 1, 1)
trajectory.build_trajectory(0.664534, max_v, max_a)

# print len(trajectory.right_trajectory)
# for s in trajectory.left_trajectory:
#     print s

right_trajectory_sliced, left_trajectory_sliced = Trajectory.trajectory_slice_constant_dt(trajectory)
trajectory.left_trajectory = left_trajectory_sliced
trajectory.right_trajectory = right_trajectory_sliced

if path_name:
    directory = tkFileDialog.askdirectory()
    print directory
    fw = FileWriter(left_trajectory_sliced, right_trajectory_sliced, name=path_name, dir=directory)
    fw.write()
    trajectory.draw_trajectory(path_name, directory)
    img = Image.open(directory + "/" + path_name + ".png")
    draw = ImageDraw.Draw(img)
    size = 35
    font = ImageFont.truetype("arial.ttf", size)
    for i in range(0, len(points_text_list)):
        draw.text((820, (i * size)), points_text_list[i], (255, 0, 0), font=font)
    img.save(path_name + '.png')
    os.startfile(path_name + '.png')
else:
    directory = ""
    trajectory.draw_trajectory(path_name, directory)
points_text_list.append("max_v = {}, max_a = {}".format(max_v, max_a))
points_text_list.append("total_time = {}".format(right_trajectory_sliced[-1].time))

# draw.text((x, y),"Sample Text",(r,g,b))


# > 0,0,90
# > -0.65,4.3,90
# > 0,6.95,105
