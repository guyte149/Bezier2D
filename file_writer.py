import csv


class File_Writer:
    def __init__(self, trajectory):
        self.trajectory = trajectory

    def write(self):
        print "in"
        positions = [s.p for s in self.trajectory.setpoints]
        with open("hi.csv", 'wb') as my_file:
            wr = csv.writer(my_file, quoting=csv.QUOTE_NONE)
            wr.writerow(positions)
