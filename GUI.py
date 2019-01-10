import pickle
import time
from Tkinter import *

import keyboard
from PIL import ImageTk, Image
import numpy as np
from bezyea import *


class PointStart(object):
    def __init__(self, master, canvas, x, y, num_curve, index, load):
        self.master = master
        self.canvas = canvas
        self.index = index
        self.x = x
        self.y = y
        self.load = load
        self.angle = 0
        self.x_point = 0
        self.y_point = 0
        self.num_curve = num_curve
        self.oval = self.canvas.create_oval(self.x_point - 3, self.y_point - 3, self.x_point + 3, self.y_point + 3,
                                            fill="blue")
        self.create_window()

    def __call__(self, *args, **kwargs):
        return np.array([self.x_point, self.y_point])

    def create_window(self):
        self.messege0 = Message(self.master, text="p{} of curve{}".format(self.index, self.num_curve))
        self.messege0.place(x=self.x, y=self.y)

        self.messege1 = Message(self.master, text="x")
        self.messege1.place(x=self.x + 100, y=self.y)

        self.messege2 = Message(self.master, text="y")
        self.messege2.place(x=self.x + 200, y=self.y)

        self.messege3 = Message(self.master, text="degree", width=40)
        self.messege3.place(x=self.x + 300, y=self.y)

        self.text0 = Text(self.master, width=5, height=1)
        self.text0.place(x=self.x + 125, y=self.y)

        self.text1 = Text(self.master, width=5, height=1)
        self.text1.place(x=self.x + 225, y=self.y)

        self.text2 = Text(self.master, width=5, height=1)
        self.text2.place(x=self.x + 350, y=self.y)

        text_list = self.text0, self.text1, self.text2
        for i, text in enumerate(text_list):
            text.bind('<Tab>', lambda e, text=text, num=i + 1: self.focus_next(text, num))
            text.bind('<Shift-Tab>', lambda e, text=text, num=i + 1: self.focus_prev(text, num))
            text.bind('<Return>', lambda e: self.inputs(True))

        self.button = Button(self.master, text="submit", command=self.inputs)
        self.button.place(x=self.x + 425, y=self.y)

    @staticmethod
    def focus_next(text, num):
        if num % 3 == 0:
            text.tk_focusNext().tk_focusNext().focus_set()
        else:
            text.tk_focusNext().focus_set()
        return 'break'

    @staticmethod
    def focus_prev(text, num):
        print num
        if num == 1:
            text.tk_focusPrev().tk_focusPrev().focus_set()
        else:
            text.tk_focusPrev().focus_set()
        return 'break'

    def inputs(self, is_backspace):
        if is_backspace:
            keyboard.press_and_release('backspace')
        input = []
        self.canvas.delete(self.oval)
        # if self.x_point == 0 and self.y_point == 0:
        if not self.load:
            input.append(self.text0.get("1.0", 'end-1c'))
            input.append(self.text1.get("1.0", 'end-1c'))
            input.append(self.text2.get("1.0", 'end-1c'))
            self.x_point = float(input[0])
            self.y_point = float(input[1])
            self.angle = float(input[2])
        self.load = False
        self.x_point *= 55.528
        self.y_point *= 55.528
        self.oval = self.canvas.create_oval(self.x_point - 3, self.y_point - 3, self.x_point + 3, self.y_point + 3,
                                            fill="blue")

        board_curve.create_canvas()


class Point(object):
    def __init__(self, master, canvas, color, to_stop, index, last_x, last_y):
        self.master = master
        self.canvas = canvas
        self.color = color
        self.to_stop = to_stop
        self.master.bind("<Button-1>", self.mouse_clicked)
        self.index = index
        self.x = 10 + self.index * 100
        self.y = 10
        self.last_x = last_x
        self.last_y = last_y
        self.after = False
        self.oval = self.canvas.create_oval(self.x - 5, self.y - 5, self.x + 5, self.y + 5, fill=self.color)

    def __call__(self, *args, **kwargs):
        return np.array([float(self.x), float(self.y)])

    def mouse_clicked(self, event):
        self.canvas.delete(self.oval)
        self.x = event.x
        self.y = event.y
        self.oval = self.canvas.create_oval(self.x - 5, self.y - 5, self.x + 5, self.y + 5, fill=self.color)
        self.master.unbind("<Button-1>")
        self.to_stop = True
        self.after = True
        board_curve.create_canvas()

    def change_place_for_input(self, x, y):
        self.canvas.delete(self.oval)
        self.x = x
        self.y = y
        self.oval = self.canvas.create_oval(self.x - 5, self.y - 5, self.x + 5, self.y + 5, fill=self.color)
        self.after = False


class Curves(object):
    def __init__(self, master, canvas, first, place, num_curve, load):
        self.master = master
        self.canvas = canvas
        self.canvas.focus_set()
        self.to_stop = False

        self.place = place

        self.curve = None
        self.start_points = []
        self.first = first
        if self.first:
            self.start_points.append(PointStart(self.master, self.canvas, 0, place - 25, num_curve, 0, load))
        self.start_points.append(PointStart(self.master, self.canvas, 0, place, num_curve, 1, load))
        self.points = [Point(self.master, self.canvas, "red", True, 1, 10 + 1 * 100, 10)]
        self.choose_points()
        self.finish = False
        self.m0 = 0
        self.b0 = 0
        self.m1 = 0
        self.b1 = 0

    def is_finish(self):
        if len(self.points) == 6:
            return True
        return False

    def choose_points(self):
        for i in range(2, 5, 1):
            if self.points[len(self.points) - 1].to_stop:
                self.points.append(Point(self.master, self.canvas, "red", True, i, 10 + i * 100, 10))

    def __call__(self, *args, **kwargs):
        t = args[0]
        return self.curve(t)

    def create_curve(self, first):
        if not first:
            self.curve = Bezier(self.start_points[0](), self.points[0](), self.points[1](),
                                self.points[2](), self.points[3](), self.start_points[1]())
        else:
            self.curve = Bezier.create_curve(self.start_points[0](), self.start_points[0].angle,
                                             self.start_points[1](), self.start_points[1].angle)
            self.points[0].change_place_for_input(self.curve.p1[0], self.curve.p1[1])
            self.points[1].change_place_for_input(self.curve.p2[0], self.curve.p2[1])
            self.points[2].change_place_for_input(self.curve.p3[0], self.curve.p3[1])
            self.points[3].change_place_for_input(self.curve.p4[0], self.curve.p4[1])
        return self.curve

    def connect_curve(self, curve0, first):
        self.points[0].color = "green"
        self.points[1].color = "green"
        c0 = self.points[0]()
        c1 = self.points[1]()
        c2 = self.points[2]()
        c3 = self.points[3]()

        if first:
            new_curve = Bezier.create_curve(curve0.curve.p5,
                                            curve0.start_points[len(curve0.start_points) - 1].angle,
                                            self.start_points[0](), self.start_points[0].angle)
            c2 = new_curve.p3
            c3 = new_curve.p4

        c0 = 2 * curve0.curve.p5 - curve0.curve.p4
        c1 = curve0.curve.p3 + 2 * c0 - 2 * curve0.curve.p4

        self.curve = Bezier(curve0.curve.p5, c0, c1, c2, c3, self.start_points[0]())
        return curve0

    def correct_angle(self, to_work):
        if not to_work:
            if self.first:
                if self.start_points[0].angle != 90:
                    # find first start point linear equation
                    x0 = self.start_points[0].x_point
                    y0 = self.start_points[0].y_point
                    self.m0 = tan(np.deg2rad(self.start_points[0].angle))
                    self.b0 = y0 - self.m0 * x0
                    # find first control point y parameter
                    x = self.points[0].x
                    y = self.m0 * x + self.b0
                    y = int(y)
                    self.points[0].change_place_for_input(x, y)

                    for i in range(int(x0), int(x0) + 100, 1):
                        y = self.m0 * i + self.b0
                        y = int(y)
                        self.canvas.create_oval(i, y, i, y, fill="salmon")

                else:
                    x = self.start_points[0].x_point
                    y = self.points[0].y
                    self.points[0].change_place_for_input(x, y)
                    for i in range(int(self.start_points[0].y_point), int(self.start_points[0].y_point) + 100, 1):
                        y0 = i
                        self.canvas.create_oval(x, y0, x, y0, fill="salmon")

                if self.start_points[1].angle != 90:
                    # find second start point linear equation
                    x0 = self.start_points[1].x_point
                    y0 = self.start_points[1].y_point
                    self.m1 = tan(np.deg2rad(self.start_points[1].angle))
                    self.b1 = y0 - self.m1 * x0
                    # find second control point y parameter
                    x = self.points[3].x
                    y = self.m1 * x + self.b1
                    y = int(y)
                    self.points[3].change_place_for_input(x, y)

                    for i in range(int(x0) - 100, int(x0), 1):
                        y = self.m1 * i + self.b1
                        y = int(y)
                        self.canvas.create_oval(i, y, i, y, fill="salmon")

                else:
                    x = self.start_points[1].x_point
                    y = self.points[3].y
                    self.points[3].change_place_for_input(x, y)
                    for i in range(int(self.start_points[1].y_point) - 100, int(self.start_points[1].y_point), 1):
                        y0 = i
                        self.canvas.create_oval(x, y0, x, y0, fill="salmon")

            else:
                if self.start_points[0].angle != 90:
                    # find second start point linear equation
                    x0 = self.start_points[0].x_point
                    y0 = self.start_points[0].y_point
                    self.m1 = tan(np.deg2rad(self.start_points[0].angle))
                    self.b1 = y0 - self.m1 * x0
                    # find second control point y parameter
                    x = self.points[3].x
                    y = self.m1 * x + self.b1
                    y = int(y)
                    self.points[3].change_place_for_input(x, y)

                    for i in range(int(x0) - 100, int(x0), 1):
                        y = self.m1 * i + self.b1
                        y = int(y)
                        self.canvas.create_oval(i, y, i, y, fill="salmon")

                else:
                    x = self.start_points[0].x_point
                    y = self.points[3].y
                    self.points[3].change_place_for_input(x, y)
                    for i in range(int(self.start_points[0].y_point) - 100, int(self.start_points[0].y_point), 1):
                        y0 = i
                        self.canvas.create_oval(x, y0, x, y0, fill="salmon")


class Boards(object):
    def __init__(self, x, y, master, img):
        self.x = x
        self.y = y
        self.master = master

        self.colors = ["blue", "green", "yellow", "pink", "orange", "grey", "brown", "purple", "cyan",
                       "magenta", "gold", "silver", "turquoise", "salmon", "black", "red", "green", "yellow",
                       "pink", "orange", "grey", "brown", "purple"]

        # self.canvas = Canvas(self.master, width=1000, height=406)
        self.canvas = Canvas(self.master, width=919, height=457)
        self.img = img
        self.canvas.create_image(459, 228, image=self.img)
        self.canvas.place(x=20, y=5)
        self.canvas.focus_set()
        self.place = 515

        self.num_curve = 0
        self.counters = [0]

        self.curves = [Curves(self.master, self.canvas, True, self.place, self.num_curve, False)]
        self.canvas_on = False

        self.connect_curves = []
        self.connect_curves.append(False)

        self.draw_scales()

        self.master.bind("<Button-3>", self.change_point)
        self.create_buttons()

        self.ovals_curves = []
        for t in range(0, 1000, 1):
            self.ovals_curves.append(self.canvas.create_oval(10, 10, 10, 10, fill="blue"))
        self.list_ovals_curves = [self.ovals_curves]

    def __call__(self, *args, **kwargs):
        t = args[0]
        seg = args[1]
        return self.curves[seg](t)

    def draw_scales(self):
        messeges_x = []
        messeges_y = []
        for i in range(1, 17, 1):
            messeges_x.append(Message(self.master, text=i))
            messeges_x[i - 1].place(x=i * 55 + 20, y=465)
        for i in range(1, 9, 1):
            messeges_y.append(Message(self.master, text=i))
            messeges_y[i - 1].place(x=0, y=i * 55 + 5)

    def create_canvas(self, res=1000.0):
        for i in range(len(self.counters)):
            self.counters[i] += 1

        for seg in xrange(0, len(self.curves), 1):
            if seg == 0:
                self.curves[seg].correct_angle(self.counters[0] <= 3)
                self.curves[seg].create_curve(self.counters[0] <= 3)
            else:
                self.curves[seg].correct_angle(self.counters[seg] <= 2)
                # self.curves[seg].points[0].after = False
                self.curves[seg - 1] = self.curves[seg].connect_curve(self.curves[seg - 1], self.counters[seg] <= 2)
            # for i in range(0, 4, 1):
            self.curves[seg].points[0].change_place_for_input(self.curves[seg].curve.p1[0],
                                                              self.curves[seg].curve.p1[1])
            self.curves[seg].points[1].change_place_for_input(self.curves[seg].curve.p2[0],
                                                              self.curves[seg].curve.p2[1])
            self.curves[seg].points[2].change_place_for_input(self.curves[seg].curve.p3[0],
                                                              self.curves[seg].curve.p3[1])
            self.curves[seg].points[3].change_place_for_input(self.curves[seg].curve.p4[0],
                                                              self.curves[seg].curve.p4[1])

        for seg in xrange(0, len(self.curves), 1):
            for t in xrange(0, int(res), 1):
                self.canvas.delete(self.list_ovals_curves[seg][t])
                self.list_ovals_curves[seg][t] = self.canvas.create_oval(int(self(t / res, seg)[0]),
                                                                         int(self(t / res, seg)[1]),
                                                                         int(self(t / res, seg)[0]),
                                                                         int(self(t / res, seg)[1]),
                                                                         fill=self.colors[seg])

    def change_point(self, event):
        for seg in xrange(0, len(self.curves), 1):
            for point in range(0, len(self.curves[seg].points), 1):
                if self.curves[seg].points[point]()[0] - 5 <= event.x <= self.curves[seg].points[point]()[0] + 5 and \
                        self.curves[seg].points[point]()[1] - 5 <= event.y <= self.curves[seg].points[point]()[1] + 5:
                    self.canvas.delete(self.curves[seg].points[point].oval)
                    self.curves[seg].points[point] = Point(self.master, self.canvas, "red", False, point,
                                                           self.curves[seg].points[point]()[0],
                                                           self.curves[seg].points[point]()[1])

    def create_buttons(self):

        self.save_button = Button(self.master, text="save", command=self.save)
        self.save_button.place(x=1164, y=100)

        self.name_file_text_save = Text(self.master, width=10, height=1)
        self.name_file_text_save.place(x=1120, y=150)

        self.load_button = Button(self.master, text="load", command=self.load)
        self.load_button.place(x=1164, y=200)

        self.name_file_text_load = Text(self.master, width=10, height=1)
        self.name_file_text_load.place(x=1120, y=250)

        self.button_add_curve = Button(self.master, text="connect curve", command=self.button_connect_curve)
        self.button_add_curve.place(x=1164, y=300)

        self.set_trajectory_button = Button(self.master, text="set trajectory", command=self.get_set_points)
        self.set_trajectory_button.place(x=1164, y=350)

        self.set_trajectory_text = Text(self.master, width=10, height=1)
        self.set_trajectory_text.place(x=1164, y=400)

    def button_connect_curve(self):
        self.num_curve += 1
        self.place += 25
        self.connect_curves[len(self.connect_curves) - 1] = True
        self.connect_curves.append(False)
        self.curves.append(Curves(self.master, self.canvas, False, self.place, self.num_curve, False))
        self.ovals_curves = []
        for t in range(0, 1000, 1):
            self.ovals_curves.append(self.canvas.create_oval(10, 10, 10, 10, fill="blue"))
        self.list_ovals_curves.append(self.ovals_curves)
        self.counters.append(0)

    def save(self):
        file_name = self.name_file_text_save.get("1.0", 'end-1c')
        with open(r'curves\{}'.format(file_name), 'wb') as f:
            list_curves = []
            for seg in range(len(self.curves)):
                list_points = []
                if seg == 0:
                    list_points.append([self.curves[seg].start_points[0](), self.curves[seg].start_points[0].angle])
                    for point in range(len(self.curves[seg].points)):
                        list_points.append(self.curves[seg].points[point]())
                    list_points.append([self.curves[seg].start_points[1](), self.curves[seg].start_points[1].angle])
                else:
                    for point in range(len(self.curves[seg].points)):
                        list_points.append(self.curves[seg].points[point]())
                    list_points.append([self.curves[seg].start_points[0](), self.curves[seg].start_points[0].angle])
                list_curves.append(list_points)
            pickle.dump(list_curves, f)
            f.close()

    def load(self):
        file_name = self.name_file_text_load.get("1.0", 'end-1c')
        with open(r'curves\{}'.format(file_name), "rb") as input_file:
            list_curves = pickle.load(input_file)
            for seg in range(len(list_curves)):
                self.counters[seg] = 4
                if seg == 0:
                    self.curves[seg].start_points[0].x_point = list_curves[seg][0][0][0]
                    self.curves[seg].start_points[0].y_point = list_curves[seg][0][0][1]
                    self.curves[seg].start_points[0].angle = list_curves[seg][0][1]
                    for i in range(1, 5, 1):
                        self.curves[seg].points[i - 1].change_place_for_input(list_curves[seg][i][0],
                                                                              list_curves[seg][i][1])
                    self.curves[seg].start_points[1].x_point = list_curves[seg][5][0][0]
                    self.curves[seg].start_points[1].y_point = list_curves[seg][5][0][1]
                    self.curves[seg].start_points[1].angle = list_curves[seg][5][1]
                else:
                    self.num_curve += 1
                    self.curves.append(Curves(self.master, self.canvas, False, self.place, self.num_curve, True))
                    for i in range(0, 4, 1):
                        self.curves[seg].points[i].change_place_for_input(list_curves[seg][i][0],
                                                                          list_curves[seg][i][1])
                    self.curves[seg].start_points[0].x_point = list_curves[seg][4][0][0]
                    self.curves[seg].start_points[0].y_point = list_curves[seg][4][0][1]
                    self.curves[seg].start_points[0].angle = list_curves[seg][4][1]
                    self.counters.append(4)
                    self.ovals_curves = []
                    res = 1000.0
                    self.connect_curves[len(self.connect_curves) - 1] = True
                    self.connect_curves.append(False)
                    for t in range(0, int(res), 1):
                        self.ovals_curves.append(self.canvas.create_oval(10, 10, 10, 10, fill="blue"))
                    self.list_ovals_curves.append(self.ovals_curves)

                print self.curves[seg].start_points[0]()
                print list_curves[seg][0]
                self.place += 25
            self.create_canvas()

    def get_set_points(self):
        max_ar = 3
        max_at = 3
        max_v = 3
        width = 0.6
        dt = 0.01
        list_curves = []
        # for seg in range(len(self.curves)):
        #     list_set_points = []
        #     if seg == 0:
        #         list_set_points.append(self.curves[seg].start_points[0]())
        #         for i in range(0, 4, 1):
        #             list_set_points.append(self.curves[seg].points[i]())
        #         list_set_points.append(self.curves[seg].start_points[1]())
        #
        #         list_curves.append(list_set_points)
        #     else:
        #         list_set_points.append(self.curves[seg - 1].start_points[1]())
        #         for i in range(0, 4, 1):
        #             list_set_points.append(self.curves[seg].points[i]())
        #         list_set_points.append(self.curves[seg].start_points[0]())
        #         list_curves.append(list_curves)
        for seg in range(len(self.curves)):
            curve = Bezier(self.curves[seg].curve.p0 / 55.528, self.curves[seg].curve.p1 / 55.528,
                           self.curves[seg].curve.p2 / 55.528, self.curves[seg].curve.p3 / 55.528,
                           self.curves[seg].curve.p4 / 55.528, self.curves[seg].curve.p5 / 55.528)
            list_curves.append(curve)

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

        points_time_traj = np.concatenate((np.row_stack(pos_traj.T[0]), points_traj), axis=1)

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
        # file_name = self.set_trajectory_text.get("1.0", 'end-1c')
        # with open(r'curves\{}'.format(file_name), 'wb') as f:
        #     pickle.dump(list_curves, f)
        #     f.close()


master = Tk()
master.attributes('-fullscreen', True)

path = "filed2019big.png"
image = Image.open(path)
image = image.resize((919, 457), Image.ANTIALIAS)
img = ImageTk.PhotoImage(image)

board_curve = Boards(0, 425, master, img)

repaint = True

master.mainloop()
