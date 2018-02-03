import numpy as np


class Trajectory(object):
    def __init__(self, path):
        self.path = path
        self.setpoints = []

    def build_trajectory(self):
        self.setpoints = self.path.get_setpoints()


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
        return "point=[{}, {}], p={}, v={}, a={}, c={}, h={}, t={}".format(self.point[0], self.point[1], self.p, self.v, self.a, self.curvature, self.heading, self.time)
