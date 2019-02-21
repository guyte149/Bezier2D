import pickle
import tkFileDialog
from Tkinter import *


pixel_to_meter = 55.528

height_picture = 457

master = Tk()
master.withdraw()
file_name = tkFileDialog.askopenfilenames(parent=master, title='Choose a file')
file_name = master.tk.splitlist(file_name)

with open(file_name[0], 'rb') as input_file:
    list_curves = pickle.load(input_file)[0]
    print list_curves
    for seg, point in enumerate(list_curves):
        # for i, point in enumerate(seg):
        if seg == 0 or seg == 5:
            point[0][0] /= pixel_to_meter
            point[0][1] = height_picture - point[0][1]
            point[0][1] /= pixel_to_meter
        else:
            point[0] /= pixel_to_meter
            point[1] = height_picture - point[1]
            point[1] /= pixel_to_meter
        print point
    print list_curves
    input_file.close()
#7.5256
#7.7592
#0.867
#6.3232