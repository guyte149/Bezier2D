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
        self.ax = plt.axes(xlim=(-1.5, 3), ylim=(-1.5, 3))
        self.plot_list = []
        plotcols = ["black", "red", "blue", "green", "yellow", "pink", "orange", "grey", "brown", "purple", "cyan",
                    "magenta", "gold", "silver", "turquoise"]
        for s in xrange(0, len(self.curves[0])):
            lobj = self.ax.plot([], [], lw=2, color=plotcols[s])[0]
            self.plot_list.append(lobj)
        for i in xrange(0, 4):
            plot_point = self.ax.plot([], [], 'ro')[0]
            self.plot_list.append(plot_point)

    # first argument is t, second argument is curve number
    def __call__(self, *args, **kwargs):
        t = args[0]
        seg = args[1]
        # print 'seg={}   cur/ves seg - {}'.format(seg, self.curves[seg])
        return self.curves[0][seg](t)

    # initialization function: plot the background of each frame
    def init(self):
        for plot in self.plot_list:
            plot.set_data([], [])
        return self.plot_list

    # animation function.  This is called sequentially
    def animate(self, i):

        curves = ParticleSwarm.next_curves(self.curves[0], self.ang0, self.ang1)[0]
        best_curve = ParticleSwarm.next_curves(self.curves[0], self.ang0, self.ang1)[1]
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

            self.plot_list[s].set_data(x_list, y_list)

        # setting data for control points
        self.plot_list[len(self.curves[0])].set_data(best_curve.c0[0], best_curve.c0[1])
        self.plot_list[len(self.curves[0]) + 1].set_data(best_curve.c1[0], best_curve.c1[1])
        self.plot_list[len(self.curves[0]) + 2].set_data(best_curve.c2[0], best_curve.c2[1])
        self.plot_list[len(self.curves[0]) + 3].set_data(best_curve.c3[0], best_curve.c3[1])

        return self.plot_list

    def display(self):
        # call the animator.  blit=True means only re-draw the parts that have changed.
        anim = animation.FuncAnimation(self.fig, self.animate, init_func=self.init,
                                       frames=10, interval=10, blit=True)

        plt.show()
