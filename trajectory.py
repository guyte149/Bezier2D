import numpy as np
import warnings

class Trajectory(object):
    def __init__(self, path):
        self.path = path
        self.setpoints = []

    def build_trajectory(self, width, max_v, max_a):

        self.setpoints = self.path.get_setpoints()
        # manually set the first setpoint
        self.setpoints[0].v = 0
        self.setpoints[0].h = 0
        self.setpoints[0].t = 0

        for i in xrange(1, len(self.setpoints) - 1, 1):
            radius = abs(1 / self.setpoints[i].curvature)

            if radius < width / 2.0:
                print "********** WARNING: A radius could not be physically followed by the robot ***********"

            big_radius = radius + (width/2.0)
            small_radius = radius - (width/2.0)
            isolated_max_v = (max_v * (1.0 + (small_radius / big_radius))) / 2.0
            # v^2 = v0^2 + 2a*dx
            kinematic_v = np.sqrt(np.power(self.setpoints[i-1].v, 2) + (2 * max_a * (self.setpoints[i].p - self.setpoints[i-1].p)))
            if self.setpoints[i - 1].v < isolated_max_v < kinematic_v:
                self.setpoints[i].v = self.setpoints[i - 1].v
                self.setpoints[i].a = 0
            else:
                self.setpoints[i].v = min(isolated_max_v, kinematic_v)
                if self.setpoints[i] == kinematic_v:
                    self.setpoints[i].a = max_a
                else:
                    self.setpoints[i].a = 999999999999
        # for i in xrange(len(self.setpoints - 1), 1)


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
        return "point=[{}, {}], p={}, v={}, a={}, c={}, h={}, t={}".format(self.point[0], self.point[1], self.p, self.v, self.a, 1 / self.curvature, self.heading, self.time)
