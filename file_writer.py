import os
import csv


class File_Writer:
    def __init__(self, trajectory, name):
        self.trajectory = trajectory
        self.name = name

    def write(self):
        data_right = [s for s in self.trajectory.right_trajectory]
        data_left = [s for s in self.trajectory.left_trajectory]
        os.chdir(r"C:\Users\Guy\Documents\robotica\Paths")
        with open(self.name + '_right.csv', 'wb') as file:
            for x in range(0, data_right.__len__()):
                file.write(str(data_right[x].time) + ",")
                file.write(str(data_right[x].p) + ",")
                file.write(str(data_right[x].v) + ",")
                file.write(str(data_right[x].a) + "\n")
        with open(self.name + '_left.csv', 'wb') as file:
            for x in range(0, data_left.__len__()):
                file.write(str(data_left[x].time) + ",")
                file.write(str(data_left[x].p) + ",")
                file.write(str(data_left[x].v) + ",")
                file.write(str(data_left[x].a) + "\n")

                #    file.write(',')
                # for data in pos:
                #     file.write(str(l))
                #     file.write('\n')
