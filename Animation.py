from __builtin__ import xrange
import matplotlib.animation as animation
from trajectory import *
from Optimization import *


class Animation(object):

    def __init__(self, ang0, ang1, *curves):

        self.ang0 = ang0
        self.ang1 = ang1

        # First set up the figure, the axis, and the plot element we want to animate
        self.curves = curves
        self.first_curves = curves
        self.fig = plt.figure()
        self.ax = plt.axes(xlim=(-0.5, 2), ylim=(-0.5, 2))
        self.line, = self.ax.plot([], [], lw=2)
        self.line_list = []
        plotcols = ["black", "red", "blue", "green", "yellow", "pink", "orange", "grey", "brown", "purple", "cyan",
                    "magenta", "gold", "silver", "turquoise"]
        for s in xrange(0, len(self.curves[0])):
            lobj = self.ax.plot([], [], lw=2, color=plotcols[s])[0]
            self.line_list.append(lobj)

    # first argument is t, second argument is curve number
    def __call__(self, *args, **kwargs):
        t = args[0]
        seg = args[1]
        # print 'seg={}   cur/ves seg - {}'.format(seg, self.curves[seg])
        return self.curves[0][seg](t)

    # initialization function: plot the background of each frame
    def init(self):
        for line in self.line_list:
            line.set_data([], [])
        return self.line_list

    # animation function.  This is called sequentially
    def animate(self, i):

        curves = ParticleSwarm.next_curves(self.curves[0], self.ang0, self.ang1)
        for j in xrange(0, len(self.curves[0]), 1):
            self.curves[0][j] = curves[j]

        t_list = np.linspace(0.0, 1.0, 1000.0)

        for s in xrange(0, len(self.curves[0])):

            x_list = []
            y_list = []

            for t in t_list:
                # print self.get_angle(t / res, s)
                x_list.append(self(t, s)[0])
                y_list.append(self(t, s)[1])

            self.line_list[s].set_data(x_list, y_list)
            # self.line.set_data(x_list, y_list)
        return self.line_list

    def display(self):
        # call the animator.  blit=True means only re-draw the parts that have changed.
        anim = animation.FuncAnimation(self.fig, self.animate, init_func=self.init,
                                       frames=10, interval=10, blit=True)

        plt.show()
