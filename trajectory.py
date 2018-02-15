from operator import pos
import numpy as np
import warnings
import matplotlib.pyplot as plt


class Trajectory(object):
    def __init__(self, path):
        self.path = path
        self.setpoints = []
        self.right_trajectory = []
        self.left_trajectory = []

    def build_trajectory(self, width, max_v, max_a):
        self.build_center_trajectory(width, max_v, max_a)
        self.build_parallels_trajectories(width=width)

    def build_center_trajectory(self, width, max_v, max_a):

        self.setpoints = self.path.get_setpoints()
        # manually set the first setpoint
        self.setpoints[0].v = 0
        self.setpoints[0].h = 0
        self.setpoints[0].t = 0
        self.setpoints[0].curvature = 0

        for i in xrange(1, len(self.setpoints) - 1, 1):
            radius = abs(1 / self.setpoints[i].curvature)

            if radius < width / 2.0:
                print "********** WARNING: A radius could not be physically followed by the robot ***********"

            big_radius = radius + (width / 2.0)
            small_radius = radius - (width / 2.0)
            isolated_max_v = (max_v * (1.0 + (small_radius / big_radius))) / 2.0
            # v^2 = v0^2 + 2a*dx
            kinematic_v = np.sqrt(
                np.power(self.setpoints[i - 1].v, 2) + (2 * max_a * (self.setpoints[i].p - self.setpoints[i - 1].p)))
            if self.setpoints[i - 1].v < isolated_max_v < kinematic_v:
                self.setpoints[i].v = self.setpoints[i - 1].v
                self.setpoints[i].a = 0
            else:
                self.setpoints[i].v = min(isolated_max_v, kinematic_v)
                if self.setpoints[i].v == kinematic_v:
                    self.setpoints[i].a = max_a
                else:
                    self.setpoints[i].a = 999999999999
        self.setpoints[-1].v = 0
        for i in xrange(len(self.setpoints) - 2, 0, -1):
            kinematic_v = np.sqrt(
                np.power(self.setpoints[i + 1].v, 2) + (2 * -max_a * (self.setpoints[i].p - self.setpoints[i + 1].p)))
            self.setpoints[i].v = min(kinematic_v, self.setpoints[i].v)
            if self.setpoints[i].v == kinematic_v:
                self.setpoints[i].a = -max_a
            if self.setpoints[i + 1].v < self.setpoints[i].v < kinematic_v:
                self.setpoints[i].a = 0

    def build_parallels_trajectories(self, width):
        right_trajectory = []
        left_trajectory = []

        for i in xrange(0, len(self.setpoints)):
            right_trajectory.append(Setpoint(np.array([0, 0]), 0, 0, 0, 0, 0, 0))
            left_trajectory.append(Setpoint(np.array([0, 0]), 0, 0, 0, 0, 0, 0))

        time = 0
        right_pos = 0
        left_pos = 0
        right_trajectory[0] = Setpoint(p=0, v=0)
        left_trajectory[0] = Setpoint(p=0, v=0)
        right_trajectory[0].point, left_trajectory[0].point = self.get_normal_points(self.setpoints[0].point, width,
                                                                                     self.setpoints[0].heading)
        for i in xrange(1, len(self.setpoints)):

            # calculate the points of the right and the left sides
            right_trajectory[i].point, left_trajectory[i].point = self.get_normal_points(self.setpoints[i].point, width,
                                                                                         self.setpoints[i].heading)
            # calculate the positions for both sides
            right_trajectory[i].p = right_trajectory[i - 1].p + np.linalg.norm(
                right_trajectory[i].point - right_trajectory[i - 1].point)
            left_trajectory[i].p = left_trajectory[i - 1].p + np.linalg.norm(
                left_trajectory[i].point - left_trajectory[i - 1].point)

            # print "dx = {}".format(np.linalg.norm(left_trajectory[i].point - left_trajectory[i - 1].point))

            right_pos = right_pos + right_trajectory[i].p
            left_pos = left_pos + left_trajectory[i].p

            is_right_turn = self.setpoints[i].curvature <= 0

            # calculate the velocity for both sides based on the curvature
            radius = abs(1 / self.setpoints[i].curvature)
            big_radius = radius + (width / 2.0)
            small_radius = radius - (width / 2.0)
            big_v = (2 * self.setpoints[i].v * big_radius) / (big_radius + small_radius)
            small_v = (2 * self.setpoints[i].v * small_radius) / (big_radius + small_radius)

            if is_right_turn:
                right_trajectory[i].v = small_v
                left_trajectory[i].v = big_v
            else:
                right_trajectory[i].v = big_v
                left_trajectory[i].v = small_v

            # calculate the time at the current setpoint
            dx = self.setpoints[i - 1].p - self.setpoints[i].p
            roots = np.roots([0.5 * self.setpoints[i].a, self.setpoints[i].v, dx])
            if len(roots[roots > 0]) < 1:
                dt = 0.01
            elif not np.isreal(np.min(roots[roots > 0])):
                dt = 0.01
            else:
                dt = np.min(roots[roots > 0])
            time += dt
            # print dt

            self.setpoints[i].time = time
            right_trajectory[i].time = time
            left_trajectory[i].time = time

            right_trajectory[i - 1].a = (right_trajectory[i].v - right_trajectory[i - 1].v) / dt
            left_trajectory[i - 1].a = (left_trajectory[i].v - left_trajectory[i - 1].v) / dt

        right_trajectory[0].a = 0
        right_trajectory[-1].a = 0
        right_trajectory[-2].a = 0
        right_trajectory[-3].a = 0
        left_trajectory[0].a = 0
        left_trajectory[-1].a = 0
        left_trajectory[-2].a = 0
        left_trajectory[-3].a = 0

        self.right_trajectory = right_trajectory
        self.left_trajectory = left_trajectory

    def draw_trajectory(self):
        # plt.axes().set_aspect('equal', 'datalim')
        plt.subplot(2, 1, 1)
        plt.plot([s.point[0] for s in self.setpoints], [s.point[1] for s in self.setpoints],
                 [r.point[0] for r in self.right_trajectory], [r.point[1] for r in self.right_trajectory],
                 [l.point[0] for l in self.left_trajectory], [l.point[1] for l in self.left_trajectory])
        plt.title("trajectory")
        plt.subplot(2, 1, 2)
        plt.plot([c.time for c in self.setpoints], [c.v for c in self.setpoints],
                 [r.time for r in self.right_trajectory], [r.v for r in self.right_trajectory],
                 [l.time for l in self.left_trajectory], [l.v for l in self.left_trajectory])
        plt.ylabel("velocity")
        plt.xlabel("time")
        plt.show()

    def get_normal_points(self, point, width, heading):
        angle = 90 - heading
        vl = width * 0.5 * np.array([np.cos(np.deg2rad(angle + 90)), np.sin(np.deg2rad(angle + 90))])
        vr = width * 0.5 * np.array([np.cos(np.deg2rad(angle - 90)), np.sin(np.deg2rad(angle - 90))])
        # print v

        right_point = point + vr
        left_point = point + vl
        return right_point, left_point

    @staticmethod
    def trajectory_slice_constant_dt(trajectory, dt=0.01):

        updated_right_trajectory = [trajectory.right_trajectory[0]]
        updated_left_trajectory = [trajectory.left_trajectory[0]]
        i = 0
        for t in np.arange(dt, trajectory.right_trajectory[-1].time, dt):
            j = 0
            while not trajectory.right_trajectory[i + j].time < t < trajectory.right_trajectory[i + j + 1].time:
                j += 1
                if trajectory.right_trajectory[i + j].time == t:
                    break

            if abs(trajectory.right_trajectory[i + j].time - t) > abs(trajectory.right_trajectory[i + j + 1].time - t):
                updated_right_trajectory.append(trajectory.right_trajectory[i + j + 1])
                updated_left_trajectory.append(trajectory.left_trajectory[i + j + 1])
                print updated_right_trajectory[-1].time
            else:
                updated_right_trajectory.append(trajectory.right_trajectory[i + j])
                updated_left_trajectory.append(trajectory.left_trajectory[i + j])
                print updated_right_trajectory[-1].time

            i = i + j
        updated_left_trajectory.append(trajectory.left_trajectory[-1])
        updated_right_trajectory.append(trajectory.right_trajectory[-1])
        return updated_left_trajectory, updated_right_trajectory


class Setpoint(object):
    def __init__(self, point=np.array([0, 0]), p=0, v=0, a=0, curvature=0, heading=0, time=0):
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
