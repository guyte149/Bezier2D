import os
import csv


class FileWriter:
    def __init__(self, left_trajectory, right_trajectory, name, dir):
        self.left_trajectory = left_trajectory
        self.right_trajectory = right_trajectory
        self.name = name
        self.dir = dir

    def write(self):
        os.chdir(self.dir)
        with open(self.name + '_right.csv', 'wb') as file:
            file.write("Time" + ",")
            file.write("Position" + ",")
            file.write("Velocity" + ",")
            file.write("Acceleration" + "\n")
            for i in xrange(0, len(self.right_trajectory)):
                file.write(str(self.right_trajectory[i].time) + ",")
                file.write(str(self.right_trajectory[i].p) + ",")
                file.write(str(self.right_trajectory[i].v) + ",")
                file.write(str(self.right_trajectory[i].a) + "\n")
        with open(self.name + '_left.csv', 'wb') as file:
            file.write("Time" + ",")
            file.write("Position" + ",")
            file.write("Velocity" + ",")
            file.write("Acceleration" + "\n")
            for i in xrange(0, len(self.left_trajectory)):
                file.write(str(self.left_trajectory[i].time) + ",")
                file.write(str(self.left_trajectory[i].p) + ",")
                file.write(str(self.left_trajectory[i].v) + ",")
                file.write(str(self.left_trajectory[i].a) + "\n")

