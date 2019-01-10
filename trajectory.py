import numpy as np


class TrajectoryGenerator(object):
    def __init__(self, max_v, max_at, max_ar, width, dt=0.01):
        self.max_v = max_v
        self.max_at = max_at
        self.max_ar = max_ar
        self.width = width
        self.dt = dt
        self.range_points = None

    def get_path_range(self, start_u, end_u, last_u):
        assert self.range_points is not None

        start_index = int(np.round((start_u / float(last_u)) * len(self.range_points)))
        end_index = int(np.round((end_u / float(last_u)) * len(self.range_points)))

        # if start_index < end_index:
        #     return self.range_points[start_index:end_index]
        # else:
        #     return self.range_points[end_index:start_index][::-1]

        return self.range_points[start_index:end_index]

    def get_max_v(self, curvature):
        """
        return the maximum velocity possible in a certain point
        :param curvature: the curvature at that point
        :return: the maximum velocity
        """
        turn_radius = 1 / np.abs(curvature)

        # calculation based on the width of the robot
        max_turn_v = (turn_radius * self.max_v) / (turn_radius + (self.width / 2))
        # calculation based on circular motion and maximum radial acceleration, using ar = v**2 / r
        max_acceleration_v = np.sqrt(turn_radius * self.max_ar)

        return min(max_turn_v, max_acceleration_v)

    def get_max_vs(self, path):
        """
        useful if you want to plot the maximum velocities and compare it to the result trajectory
        :return: a vector of maximum velocities at certain us
        """
        result = []
        du = self.get_recommended_du(path)
        us = self.get_us_subset(0, len(path.curves), du)

        for u in us:
            max_v = self.get_max_v(path.get_curvature(u))
            result.append([u, max_v])

        return np.array(result)

    def get_recommended_du(self, path):
        """
        :return: a recommended delta u (path parameter) to use when generating the trajectory
        """
        return np.around(1.0 / ((path.get_length() / self.max_v) / self.dt), 7)

    def generate_one_way_trajectory(self, path, start_u=0, forward=True):
        """
        :param path: the path to use
        :param start_u: the u of the point to start from
        :param forward: True to calculate from the start point to the beginning
         or False if from the end to the start point
        :return: a vector of [u, v]
        """
        result = []

        du = self.get_recommended_du(path)

        end_u = path.end_u

        # check if we start from the beginning or the end
        if start_u in (0, end_u):
            v = 0
            result.append([start_u, v])
        else:
            # we are starting from a turning point
            v = self.get_max_v(path.get_curvature(start_u))
            result.append([start_u, v])

        # the way we generate backwards trajectories is by "flipping" the path
        #  and pretending to go forward from the end to the start
        if not forward:
            end_u = start_u
            start_u = 0

        # we need to use this function so that all the trajectories we generate will share the same us
        # this is needed for taking the minimum of two trajectories
        us = self.get_us_subset(start_u, end_u, path.end_u, du)
        pos = self.get_path_range(start_u, end_u, path.end_u)

        if not forward:
            pos = pos[::-1]
            us = us[::-1]

        for i in range(len(us) - 1):
            ds = np.linalg.norm(pos[i] - pos[i + 1])  # distance between this point and the next
            next_v = np.sqrt(v ** 2 + (2 * self.max_at * ds))  # using v**2 = v0**2 + 2a*ds

            next_max_v = self.get_max_v(path.get_curvature(us[i + 1]))

            # always take the minimum between what we want and the maximum physical velocity possible
            next_v = min(next_v, next_max_v)

            result.append(np.array([us[i + 1], next_v]))

            v = next_v

        if not forward:
            result.reverse()

        return np.array(result)

    def generate_trajectory(self, path):
        """
        :param path: the path to generate a trajectory for
        :return: two trajectories, one is (time, path parameter u) and the other is (time, velocity)
        """
        self.range_points = path.get_all_points(self.get_recommended_du(path))

        tps = path.find_turning_points()
        traj_forward = self.generate_one_way_trajectory(path, start_u=0, forward=True)
        traj_backward = self.generate_one_way_trajectory(path, start_u=path.end_u, forward=False)

        # create a basic trajectory from start to end and end to start
        current_traj = self.min_trajectories(traj_forward, traj_backward)

        # for each turning point, calculate a forward trajectory from it to the end,
        # and a backward trajectory from it to the start
        for tp in tps:
            traj_forward = self.generate_one_way_trajectory(path, start_u=tp, forward=True)
            traj_backward = self.generate_one_way_trajectory(path, start_u=tp, forward=False)

            # take the minimum of the trajectories so far
            current_traj = self.min_trajectories(current_traj, np.concatenate((traj_backward, traj_forward)))

        # use the velocities found to assign a time to each point
        time_trajectory = self.timestamp_trajectory(path, current_traj)

        # use linear interpolation to get trajectories with constant time difference dt
        # print time_trajectory
        v_trajectory = self.linear_interpolate_v(time_trajectory)
        pos_trajectory = self.linear_interpolate_u(time_trajectory)

        return pos_trajectory, v_trajectory

    def linear_interpolate_v(self, traj):
        """
        :param traj: a trajectory of [t, u, velocity]
        :return: a trajectory of [t, velocity] with constant time difference dt
        """
        t = traj.T[0]
        v = traj.T[2]

        new_t = np.arange(0, t[-1], self.dt)
        new_v = np.interp(new_t, t, v)

        return np.array([new_t, new_v]).T

    def linear_interpolate_u(self, traj):
        """
        this is not very accurate,
        linear interpolation is good for the velocity but i don't think it is exactly correct
        to do the same for the position.
        nevertheless it is close enough and much faster the calculating small distances along the path
        :param traj: a trajectory of [t, u, velocity]
        :return: a trajectory of [t, u] with constant time difference dt
        """
        t = traj.T[0]
        u = traj.T[1]

        new_t = np.arange(0, t[-1], self.dt)
        new_u = np.interp(new_t, t, u)

        return np.array([new_t, new_u]).T

    @staticmethod
    def timestamp_trajectory(path, trajectory):
        """
        :param path: the path that was used to build the trajectory
        :param trajectory: a trajectory of [u, velocity]
        :return: a trajectory with time as well, [t, u, velocity]
        """
        time = 0
        result = []

        for i in range(len(trajectory) - 1):
            u = trajectory[i][0]
            v = trajectory[i][1]

            result.append([time, u, v])

            ds = np.linalg.norm(path(u) - path(trajectory[i + 1][0]))  # distance between this point and the next
            # acceleration in this period, using v**2 = v0**2 + 2a*ds
            a = (trajectory[i + 1][1] ** 2 - v ** 2) / (2 * ds)
            if a == 0.0:
                a = np.finfo(float).tiny
                print "a = 0"
            time += np.abs((trajectory[i + 1][1] - v) / a)  # calculate the time it took using dv / dt

        result.append(([time, trajectory[-1][0], trajectory[-1][1]]))

        return np.array(result)

    @staticmethod
    def get_us_subset(start_u, end_u, last_u, du):
        """
        like np.arange but that always uses the same points.
        this is needed so that all trajectories that we generate will share the same us
        """
        us = np.arange(0, last_u, du)
        start_index = int(np.round((start_u / float(last_u)) * len(us)))
        end_index = int(np.round((end_u / float(last_u)) * len(us)))
        return us[start_index:end_index]

    @staticmethod
    def min_trajectories(t1, t2):
        """
        :param t1: trajectory one that looks like [u, v]
        :param t2: trajectory two that looks like [u, v]
        :return: the minimum of the two trajectories
        """
        return np.array([t1.T[0], np.minimum(t1.T[1], t2.T[1])]).T


# from operator import pos
# import numpy as np
# import warnings
# import matplotlib.pyplot as plt
#
#
# class Trajectory(object):
#     def __init__(self, path):
#         self.path = path
#         self.setpoints = []
#         self.right_trajectory = []
#         self.left_trajectory = []
#
#     def build_trajectory(self, width, max_v, max_a):
#         self.build_center_trajectory(width, max_v, max_a)
#         self.build_parallels_trajectories(width=width, max_v=max_v)
#
#     def build_center_trajectory(self, width, max_v, max_a):
#
#         np.seterr(all='raise')
#
#         self.setpoints = self.path.get_setpoints()
#         # manually set the first setpoint
#         self.setpoints[0].v = 0
#         self.setpoints[0].h = 0
#         self.setpoints[0].t = 0
#         self.setpoints[0].curvature = 0
#
#         for i in xrange(1, len(self.setpoints) - 1, 1):
#
#             if self.setpoints[i].curvature != 0:
#                 radius = abs(1.0 / self.setpoints[i].curvature)
#
#                 if radius < width / 2.0:
#                     print "********** WARNING: A radius could not be physically followed by the robot ***********"
#                 # print radius
#                 big_radius = radius + (width / 2.0)
#                 small_radius = radius - (width / 2.0)
#                 isolated_max_v = (max_v * (1.0 + (small_radius / big_radius))) / 2.0
#             else:
#                 isolated_max_v = max_v
#
#             # v^2 = v0^2 + 2a*dx
#             kinematic_v = np.sqrt(
#                 np.power(self.setpoints[i - 1].v, 2) + (2 * max_a * (self.setpoints[i].p - self.setpoints[i - 1].p)))
#             if self.setpoints[i - 1].v < isolated_max_v < kinematic_v:
#                 self.setpoints[i].v = self.setpoints[i - 1].v
#                 self.setpoints[i].a = 0
#             else:
#                 self.setpoints[i].v = min(isolated_max_v, kinematic_v)
#                 if self.setpoints[i].v == kinematic_v:
#                     self.setpoints[i].a = max_a
#                 else:
#                     self.setpoints[i].a = 999999999999
#         self.setpoints[-1].v = 0
#         for i in xrange(len(self.setpoints) - 2, 0, -1):
#             kinematic_v = np.sqrt(
#                 np.power(self.setpoints[i + 1].v, 2) + (2 * -max_a * (self.setpoints[i].p - self.setpoints[i + 1].p)))
#             self.setpoints[i].v = min(kinematic_v, self.setpoints[i].v)
#             if self.setpoints[i].v == kinematic_v:
#                 self.setpoints[i].a = -max_a
#             if self.setpoints[i + 1].v < self.setpoints[i].v < kinematic_v:
#                 self.setpoints[i].a = 0
#
#     def build_parallels_trajectories(self, width, max_v):
#         right_trajectory = []
#         left_trajectory = []
#
#         for i in xrange(0, len(self.setpoints)):
#             right_trajectory.append(Setpoint(np.array([0, 0]), 0, 0, 0, 0, 0, 0))
#             left_trajectory.append(Setpoint(np.array([0, 0]), 0, 0, 0, 0, 0, 0))
#
#         time = 0
#         right_trajectory[0] = Setpoint(p=0, v=0)
#         left_trajectory[0] = Setpoint(p=0, v=0)
#         right_trajectory[0].point, left_trajectory[0].point = self.get_normal_points(self.setpoints[0].point, width,
#                                                                                      self.setpoints[0].heading)
#         for i in xrange(1, len(self.setpoints)):
#
#             # calculate the points of the right and the left sides
#             right_trajectory[i].point, left_trajectory[i].point = self.get_normal_points(self.setpoints[i].point, width,
#                                                                                          self.setpoints[i].heading)
#             # calculate the positions for both sides
#             right_trajectory[i].p = right_trajectory[i - 1].p + np.linalg.norm(
#                 right_trajectory[i].point - right_trajectory[i - 1].point)
#             left_trajectory[i].p = left_trajectory[i - 1].p + np.linalg.norm(
#                 left_trajectory[i].point - left_trajectory[i - 1].point)
#
#             # print "dx = {}".format(np.linalg.norm(left_trajectory[i].point - left_trajectory[i - 1].point))
#
#             is_right_turn = self.setpoints[i].curvature <= 0
#
#             # calculate the velocity for both sides based on the curvature
#             # if left_trajectory[i].p >= 1.61664109064914:
#             #     print ''
#             if self.setpoints[i].curvature != 0:
#                 radius = abs(1.0 / self.setpoints[i].curvature)
#                 big_radius = radius + (width / 2.0)
#                 small_radius = radius - (width / 2.0)
#                 big_v = (2 * self.setpoints[i].v * big_radius) / (big_radius + small_radius)
#                 small_v = (2 * self.setpoints[i].v * small_radius) / (big_radius + small_radius)
#                 if is_right_turn:
#                     right_trajectory[i].v = small_v
#                     left_trajectory[i].v = big_v
#                 else:
#                     right_trajectory[i].v = big_v
#                     left_trajectory[i].v = small_v
#             else:
#                 right_trajectory[i].v = self.setpoints[i].v
#                 left_trajectory[i].v = self.setpoints[i].v
#                 # print self.setpoints[i].curvature
#                 # print self.setpoints[i-1].curvature
#                 # print right_trajectory[i-1].v
#                 # print left_trajectory[i-1].v
#                 # exit(0)
#
#             # calculate the time at the current setpoint
#             dx = self.setpoints[i - 1].p - self.setpoints[i].p
#             roots = np.roots([0.5 * self.setpoints[i].a, self.setpoints[i].v, dx])
#             # print self.setpoints[i]
#             if len(roots[roots > 0]) < 1:
#                 dt = 0.01
#             elif not np.isreal(np.min(roots[roots > 0])):
#                 dt = 0.01
#                 # print "dsadas"
#             elif np.min(roots[roots > 0]) > 0.01:
#                 # print roots
#                 # print roots
#                 # print self.right_trajectory[i]
#                 # print dx
#                 # print self.right_trajectory[i-1]
#                 # print self.right_trajectory[i - 2]
#                 # print self.right_trajectory[i - 3]
#                 # print self.right_trajectory[i - 4]
#                 dt = 0.0000000001
#             else:
#                 dt = np.min(roots[roots > 0])
#                 # if dt < 0.01:
#                 # dt = 0.01
#
#                 # print roots
#
#             time += dt
#
#             # print time
#
#             self.setpoints[i].time = time
#             right_trajectory[i].time = time
#             left_trajectory[i].time = time
#
#             right_trajectory[i - 1].a = (right_trajectory[i].v - right_trajectory[i - 1].v) / dt
#             left_trajectory[i - 1].a = (left_trajectory[i].v - left_trajectory[i - 1].v) / dt
#
#             # if left_trajectory[i].v >= 1.22976637137963:
#             # print ""
#
#         right_trajectory[0].a = 0
#         right_trajectory[-1].a = 0
#         right_trajectory[-2].a = 0
#         right_trajectory[-3].a = 0
#         left_trajectory[0].a = 0
#         left_trajectory[-1].a = 0
#         left_trajectory[-2].a = 0
#         left_trajectory[-3].a = 0
#
#         self.right_trajectory = right_trajectory
#         self.left_trajectory = left_trajectory
#
#     def draw_trajectory(self, filename, dir=""):
#         plt.subplots(figsize=(18, 7))
#         plt.subplots(figsize=(18, 7))
#         plt.subplot(1, 2, 1)
#         plt.axis('equal')
#         plt.plot([s.point[0] for s in self.setpoints], [s.point[1] for s in self.setpoints],
#                  [r.point[0] for r in self.right_trajectory], [r.point[1] for r in self.right_trajectory],
#                  [l.point[0] for l in self.left_trajectory], [l.point[1] for l in self.left_trajectory])
#         plt.title("trajectory")
#         plt.subplot(1, 2, 2)
#         plt.plot([c.time for c in self.setpoints], [c.v for c in self.setpoints],
#                  [r.time for r in self.right_trajectory], [r.v for r in self.right_trajectory],
#                  [l.time for l in self.left_trajectory], [l.v for l in self.left_trajectory])
#         plt.ylabel("velocity")
#         plt.xlabel("time")
#
#         if filename:
#             plt.savefig(filename + '.png')
#         else:
#             plt.show()
#
#     def get_normal_points(self, point, width, heading):
#         angle = heading
#         # print angle
#         vl = width * 0.5 * np.array([np.cos(np.deg2rad(angle + 90)), np.sin(np.deg2rad(angle + 90))])
#         vr = width * 0.5 * np.array([np.cos(np.deg2rad(angle - 90)), np.sin(np.deg2rad(angle - 90))])
#         # print v
#
#         right_point = point + vr
#         left_point = point + vl
#         return right_point, left_point
#
#     @staticmethod
#     def trajectory_slice_constant_dt(trajectory, dt=0.01):
#
#         updated_right_trajectory = [trajectory.right_trajectory[0]]
#         updated_left_trajectory = [trajectory.left_trajectory[0]]
#         i = 0
#         for t in np.arange(dt, trajectory.right_trajectory[-1].time, dt):
#             j = 0
#             while not trajectory.right_trajectory[i + j].time < t < trajectory.right_trajectory[i + j + 1].time:
#                 j += 1
#                 if trajectory.right_trajectory[i + j].time == t:
#                     break
#
#             if abs(trajectory.right_trajectory[i + j].time - t) > abs(trajectory.right_trajectory[i + j + 1].time - t):
#                 updated_right_trajectory.append(trajectory.right_trajectory[i + j + 1])
#                 updated_left_trajectory.append(trajectory.left_trajectory[i + j + 1])
#                 # print updated_right_trajectory[-1].time
#             else:
#                 updated_right_trajectory.append(trajectory.right_trajectory[i + j])
#                 updated_left_trajectory.append(trajectory.left_trajectory[i + j])
#                 # print updated_right_trajectory[-1].time
#
#             i = i + j
#         updated_left_trajectory.append(trajectory.left_trajectory[-1])
#         updated_right_trajectory.append(trajectory.right_trajectory[-1])
#         return updated_left_trajectory, updated_right_trajectory
#
#
class Setpoint(object):
    def __init__(self, point=np.array([0, 0]), p=0, v=0, a=0, curvature=0., heading=0, time=0):
        self.p = p
        self.point = point
        self.v = v
        self.a = a
        self.curvature = curvature
        self.heading = heading
        self.time = time

    def __str__(self):
        return "point=[{}, {}], p={}, v={}, a={}, c={}, h={}, t={}".format(self.point[0], self.point[1], self.p, self.v,
                                                                           self.a, self.curvature, self.heading,
                                                                           self.time)
