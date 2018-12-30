import time
from Tkinter import *
from PIL import ImageTk, Image
import numpy as np
from bezyea import *


class PointStart(object):
    def __init__(self, master, canvas, x, y, num_curve):
        self.master = master
        self.canvas = canvas
        self.x = x
        self.y = y
        self.x_point = 0
        self.y_point = 0
        self.num_curve = num_curve
        self.create_window()

    def __call__(self, *args, **kwargs):
        return np.array([self.x_point, self.y_point])

    def create_window(self):
        self.messege0 = Message(self.master, text="p1 of curve{}".format(self.num_curve))
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

        self.button = Button(self.master, text="submit", command=self.inputs)
        self.button.place(x=self.x + 425, y=self.y)

    def inputs(self):
        input = []
        input.append(self.text0.get("1.0", 'end-1c'))
        input.append(self.text1.get("1.0", 'end-1c'))
        input.append(self.text2.get("1.0", 'end-1c'))
        self.x_point = float(input[0])
        self.y_point = float(input[1])
        self.oval = self.canvas.create_oval(self.x_point - 3, self.y_point - 3, self.x_point + 3, self.y_point + 3,
                                            fill="blue")


class Point(object):
    def __init__(self, master, canvas, color, to_stop, index, last_x, last_y):
        self.master = master
        # self.master.bind("<Key>", self.stop)
        self.canvas = canvas
        self.color = color
        self.to_stop = to_stop
        # self.canvas.bind("<Key>", self.stop)
        self.master.bind("<Button-1>", self.mouse_clicked)
        self.index = index
        self.x = 10 + self.index * 100
        self.y = 10
        self.last_x = last_x
        self.last_y = last_y
        self.after = False
        self.oval = self.canvas.create_oval(self.x - 5, self.y - 5, self.x + 5, self.y + 5, fill=self.color)

    def __call__(self, *args, **kwargs):
        if self.x == self.last_x and self.y == self.last_y:
            self.after = False
        else:
            self.after = True
        return np.array([float(self.x), float(self.y)])

    # def stop(self, event):
    #     if event.char == 'a':
    #         self.master.unbind("<Button-1>")
    #         self.master.unbind("<Key>")
    #         self.to_stop = True
    #         self.after = True

    def mouse_clicked(self, event):
        self.canvas.delete(self.oval)
        self.x = event.x
        self.y = event.y
        self.oval = self.canvas.create_oval(self.x - 5, self.y - 5, self.x + 5, self.y + 5, fill=self.color)
        self.master.unbind("<Button-1>")
        # self.master.unbind("<Key>")
        self.to_stop = True
        board_curve.create_canvas()

    def change_place_for_input(self, x, y):
        self.canvas.delete(self.oval)
        self.x = x
        self.y = y
        self.oval = self.canvas.create_oval(self.x - 5, self.y - 5, self.x + 5, self.y + 5, fill=self.color)


class Curves(object):
    def __init__(self, master, canvas, first, place):
        self.master = master
        self.canvas = canvas
        self.canvas.focus_set()
        self.to_stop = False

        self.place = place

        self.curve = None
        self.start_points = []
        if first:
            self.start_points.append(PointStart(self.master, self.canvas, 0, place - 25, 0))
        self.start_points.append(PointStart(self.master, self.canvas, 0, place, 0))
        self.points = [Point(self.master, self.canvas, "red", True, 1, 10 + 1 * 100, 10)]
        self.choose_points()
        self.finish = False

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

    def create_curve(self):
        self.curve = QuanticBezierCurve(self.start_points[0](), self.points[0](), self.points[1](), self.points[2](),
                                        self.points[3](), self.start_points[1]())
        return self.curve

    def connect_curve(self, curve0):
        c0 = self.points[0]()
        c1 = self.points[1]()
        if self.points[0].after:
            curve0.curve.c3 = 2 * curve0.curve.p1 - c0
        else:
            c0 = 2 * curve0.curve.p1 - curve0.curve.c3
        if self.points[1].after:
            curve0.curve.c2 = c1 - 2 * c0 + 2 * curve0.curve.c3
        else:
            c1 = curve0.curve.c2 + 2 * c0 - 2 * curve0.curve.c3
        self.curve = QuanticBezierCurve(curve0.curve.p1, c0, c1, self.points[2](), self.points[3](),
                                        self.start_points[0]())
        return curve0


class Boards(object):
    def __init__(self, x, y, master, img):
        self.x = x
        self.y = y
        self.master = master

        self.colors = ["blue", "green", "yellow", "pink", "orange", "grey", "brown", "purple", "cyan",
                       "magenta", "gold", "silver", "turquoise", "salmon", "black", "red", "green", "yellow",
                       "pink", "orange", "grey", "brown", "purple"]

        self.canvas = Canvas(self.master, width=1000, height=406)
        self.img = img
        self.canvas.create_image(500, 203, image=self.img)
        self.canvas.place(x=0, y=0)
        self.canvas.focus_set()
        self.place = 435
        self.curves = [Curves(self.master, self.canvas, True, self.place)]
        # self.curves.append(Curves(self.master))
        # self.curves[0].choose_points()
        # self.curves[0].create_curve()
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

        # self.create_canvas()

    def __call__(self, *args, **kwargs):
        t = args[0]
        seg = args[1]
        return self.curves[seg](t)

    def draw_scales(self):
        messeges_x = []
        messeges_y = []
        for i in range(1, 11, 1):
            messeges_x.append(Message(self.master, text=i * 100))
            messeges_x[i - 1].place(x=i * 100, y=380)
        for i in range(1, 5, 1):
            messeges_y.append(Message(self.master, text=i * 100))
            messeges_y[i - 1].place(x=0, y=i * 100)

    def create_canvas(self, res=1000.0):

        for seg in xrange(0, len(self.curves), 1):
            if seg == 0:
                self.curves[seg].create_curve()
            else:
                self.curves[seg - 1] = self.curves[seg].connect_curve(self.curves[seg - 1])
            # for i in range(0, 4, 1):
            self.curves[seg].points[0].change_place_for_input(self.curves[seg].curve.c0[0],
                                                              self.curves[seg].curve.c0[1])
            self.curves[seg].points[1].change_place_for_input(self.curves[seg].curve.c1[0],
                                                              self.curves[seg].curve.c1[1])
            self.curves[seg].points[2].change_place_for_input(self.curves[seg].curve.c2[0],
                                                              self.curves[seg].curve.c2[1])
            self.curves[seg].points[3].change_place_for_input(self.curves[seg].curve.c3[0],
                                                              self.curves[seg].curve.c3[1])

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

        self.button = Button(self.master, text="create", command=self.action_button)
        self.button.place(x=1100, y=100)

        self.button_add_curve = Button(self.master, text="connect curve", command=self.button_connect_curve)
        self.button_add_curve.place(x=1100, y=300)

        # curve = self.curves[0]
        # self.curves.append(curve)

        # self.curve = QuanticBezierCurve(np.array([0.0, 0.0]), np.array([0.0, 25.0]), np.array([25.0, 50.0]),
        # np.array([75.0, 50.0]), np.array([100.0, 75.0]), np.array([100.0, 100.0]))

        # return curve

    def button_connect_curve(self):
        self.place += 25
        self.connect_curves[len(self.connect_curves) - 1] = True
        self.connect_curves.append(False)
        self.curves.append(Curves(self.master, self.canvas, False, self.place))
        self.ovals_curves = []
        for t in range(0, 1000, 1):
            self.ovals_curves.append(self.canvas.create_oval(10, 10, 10, 10, fill="blue"))
        self.list_ovals_curves.append(self.ovals_curves)

    def action_button(self):
        if not self.canvas_on:
            self.create_canvas()
            # self.canvas_on = True
        elif self.canvas_on:
            self.canvas.destroy()
            self.canvas_on = False


# inputs = []
master = Tk()
master.attributes('-fullscreen', True)

path = "field.png"
image = Image.open(path)
image = image.resize((1000, 406), Image.ANTIALIAS)
img = ImageTk.PhotoImage(image)

board_curve = Boards(0, 425, master, img)

repaint = True

master.mainloop()
