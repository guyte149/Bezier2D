import pickle
import time
from Tkinter import *

import keyboard
from PIL import ImageTk, Image
import numpy as np
from bezyea import *


def main():
    max_ar = 3
    max_at = 3
    max_v = 3
    width = 0.6
    dt = 0.01

    list_curves = [
        Bezier(np.array([0, 0]), np.array([0, 0.25]), np.array([0.25, 0.5]), np.array([0.75, 0.5]), np.array([1, 0.75]),
               np.array([1, 1]))]
    path = Path(list_curves)
    # path.draw_path()
    # master.destroy()

    # calculate the points along the path, just for drawing it
    us = np.arange(0, path.end_u, 0.01)
    ps = path.call_multi(us)

    # create the TrajectoryGenerator object
    generator = TrajectoryGenerator(max_v, max_at, max_ar, width)

    # generate the trajectories, one is (time, path parameter u) and the other is (time, velocity)
    pos_traj, v_traj = generator.generate_trajectory(path)

    # get the actual points along the trajectory so we can draw them nicely
    points_traj = path.call_multi(pos_traj.T[1])
    angles_traj = path.get_angles(pos_traj.T[1])

    # time, x, y
    points_time_traj = np.concatenate((np.row_stack(pos_traj.T[0]), points_traj), axis=1)
    # angles in radians
    angles_traj = np.reshape(angles_traj, (angles_traj.shape[0], 1))
    x_time_traj = np.concatenate((points_time_traj, angles_traj), axis=1)

    points_traj = points_traj[::30]  # take only some of the points so they wont be too close to each other

    # draw the path and the trajectory
    plt.figure()

    # draw the path
    plt.subplot(121)
    plt.axis('equal')
    plt.plot(ps.T[0], ps.T[1])
    plt.scatter(points_traj.T[0], points_traj.T[1], c='orange', s=10)

    # draw the velocity profile
    plt.subplot(122)
    plt.plot(v_traj.T[0], v_traj.T[1])

    plt.show()


if __name__ == '__main__':
    main()
