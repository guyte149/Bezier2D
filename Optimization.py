from bezyea import *
import numpy as np


class Optimization(object):

    def __init__(self, p0, p1, best_curve):
        # l = np.linalg.norm(p1 - p0)
        self.p0 = p0
        self.p1 = p1
        self.best_curve = best_curve

    def __call__(self, *args, **kwargs):
        raise NotImplemented

    def __str__(self):
        raise NotImplemented


class RandomSearch(Optimization):
    def __init__(self, p0, p1, best_curve):
        super(RandomSearch, self).__init__(p0, p1, best_curve)
        # l = np.linalg.norm(p1 - p0)
        self.p0 = p0
        self.p1 = p1
        # self.vector_multiplier0 = vector_multiplier0
        # self.vector_multiplier1 = vector_multiplier1
        # self.random_length = random_length
        self.best_curve = best_curve

    def __call__(self, *args, **kwargs):
        t = args[0]
        return self.best_curve(t)

    @staticmethod
    def first_curve(p0, ang0, p1, ang1):
        best_curve = QuanticBezierCurve.create_curve(p0, ang0, p1, ang1)
        return best_curve

    @staticmethod
    def next_curve(p0, ang0, p1, ang1):
        l = np.linalg.norm(p1 - p0)

        random_length = 0.1 * l / sqrt(2)

        best_curve = RandomSearch.first_curve(p0, ang0, p1, ang1)
        best_rate = best_curve.rate_curve(best_curve)

        v0 = np.array([np.cos(np.deg2rad(ang0)), np.sin(np.deg2rad(ang0))])
        v1 = np.array([np.cos(np.deg2rad(ang1)), np.sin(np.deg2rad(ang1))])

        new_vector_multiplier0 = (best_curve.c0 - best_curve.p0) / v0 + uniform(-random_length, random_length)
        new_vector_multiplier1 = (best_curve.c3 - best_curve.p1) / v1 + uniform(-random_length, random_length)

        new_c1 = best_curve.c1 + np.array(
            [uniform(-random_length, random_length), uniform(-random_length, random_length)])

        new_c2 = best_curve.c2 + np.array(
            [uniform(-random_length, random_length), uniform(-random_length, random_length)])
        new_curve = QuanticBezierCurve(p0, p0 + new_vector_multiplier0 * l * v0, new_c1, new_c2, p1 +
                                       new_vector_multiplier1 * l * v1, p1)

        new_rate = new_curve.rate_curve(new_curve)

        if 0 < new_rate < best_rate and new_vector_multiplier0 > 0 > new_vector_multiplier1:
            best_curve = new_curve

        return best_curve

    @staticmethod
    def last_curve(p0, ang0, p1, ang1, res=175):
        best_curve = RandomSearch.first_curve(p0, ang0, p1, ang1)
        for i in range(res):
            best_curve = RandomSearch.next_curve(p0, ang0, p1, ang1)

        return RandomSearch(p0, p1, best_curve)

    def __str__(self):
        return self.best_curve


class ParticleSwarm(Optimization):
    def __init__(self, p0, p1, best_curve, start_curves, curves):
        super(ParticleSwarm, self).__init__(p0, p1, best_curve)
        self.p0 = p0
        self.p1 = p1
        self.start_curves = start_curves
        self.curves = curves
        self.best_curve = best_curve

    def __call__(self, *args, **kwargs):
        # i = args[0]
        return self.curves

    @staticmethod
    def start_curves(p0, ang0, p1, ang1, res=15):
        curves = []
        l = np.linalg.norm(p1 - p0)

        random_length_x = []
        random_length_y = []

        if ang0 - ang1 > 0:
            if p0[0] < p1[0] and p0[1] < p1[1]:
                random_length_x.append(p0[0])
                random_length_x.append(p1[0])
                random_length_y.append(p0[1])
                random_length_y.append(p1[1])

            elif p0[0] > p1[0] and p0[1] < p1[1]:
                random_length_x.append(p1[0] - abs(p1[0] - p0[0]) - abs(p1[1] - p0[1]))
                random_length_x.append(p0[0])
                random_length_y.append(p0[1])
                random_length_y.append(p1[1])

            elif p0[0] < p1[0] and p0[1] > p1[1]:
                random_length_x.append(p0[0])
                random_length_x.append(p1[0])
                random_length_y.append(p1[1])
                random_length_y.append(p0[1] + abs(p1[0] - p0[0]) + abs(p1[1] - p0[1]))

            elif p0[0] > p1[0] and p0[1] > p1[1]:
                random_length_x.append(p1[0] - abs(p1[0] - p0[0]) - abs(p1[1] - p0[1]))
                random_length_x.append(p0[0])
                random_length_y.append(p1[1])
                random_length_y.append(p0[1] + abs(p1[0] - p0[0]) + abs(p1[1] - p0[1]))

        elif ang0 - ang1 < 0:
            if p0[0] < p1[0] and p0[1] < p1[1]:
                random_length_x.append(p0[0])
                random_length_x.append(p1[0] + abs(p1[0] - p0[0]) + abs(p1[1] - p0[1]))
                random_length_y.append(p0[1] - abs(p1[0] - p0[0]) - abs(p1[1] - p0[1]))
                random_length_y.append(p1[1])

            elif p0[0] > p1[0] and p0[1] < p1[1]:
                random_length_x.append(p1[0])
                random_length_x.append(p0[0])
                random_length_y.append(p0[1])
                random_length_y.append(p1[1])

            elif p0[0] < p1[0] and p0[1] > p1[1]:
                random_length_x.append(p0[0])
                random_length_x.append(p1[0] + abs(p1[0] - p0[0]) + abs(p1[1] - p0[1]))
                random_length_y.append(p1[1])
                random_length_y.append(p0[1])

            elif p0[0] > p1[0] and p0[1] > p1[1]:
                random_length_x.append(p1[0] - abs(p1[0] - p0[0]) - abs(p1[1] - p0[1]))
                random_length_x.append(p0[0])
                random_length_y.append(p1[1])
                random_length_y.append(p0[1])

        elif ang0 == ang1:
            if p0[0] < p1[0] and p0[1] < p1[1]:
                random_length_x.append(p0[0])
                random_length_x.append(p1[0])
                random_length_y.append(p0[1])
                random_length_y.append(p1[1])

            elif p0[0] < p1[0] and p0[1] > p1[1]:
                random_length_x.append(p0[0])
                random_length_x.append(p1[0])
                random_length_y.append(p1[1] - abs(p1[0] - p0[0]) - abs(p1[1] - p0[1]))
                random_length_y.append(p0[1] + abs(p1[0] - p0[0]) + abs(p1[1] - p0[1]))

            elif p0[0] > p1[0] and p0[1] < p1[1]:
                random_length_x.append(p1[0])
                random_length_x.append(p0[0])
                random_length_y.append(p0[1])
                random_length_y.append(p1[1])

            elif p0[0] > p1[0] and p0[1] > p1[1]:
                random_length_x.append(p1[0])
                random_length_x.append(p0[0])
                random_length_y.append(p1[1] - abs(p1[0] - p0[0]) - abs(p1[1] - p0[1]))
                random_length_y.append(p0[1] + abs(p1[0] - p0[0]) + abs(p1[1] - p0[1]))

        v0 = np.array([np.cos(np.deg2rad(ang0)), np.sin(np.deg2rad(ang0))])
        v1 = np.array([np.cos(np.deg2rad(ang1)), np.sin(np.deg2rad(ang1))])

        for i in range(0, res, 1):
            u0 = uniform(0.0, random_length_x[1] - random_length_x[0])
            u1 = uniform(0.0, random_length_x[1] - random_length_x[0])

            c0 = p0 + u0 * v0
            c1 = np.array([uniform(random_length_x[0], random_length_x[1]), uniform(random_length_y[0],
                                                                                    random_length_y[1])])
            c2 = np.array([uniform(random_length_x[0], random_length_x[1]), uniform(random_length_y[0],
                                                                                    random_length_y[1])])
            c3 = p1 - u1 * v1
            curves.append(QuanticBezierCurve(p0, c0, c1, c2, c3, p1))

        return curves

    @staticmethod
    def next_curves(curves, ang0, ang1):

        v0 = np.array([np.cos(np.deg2rad(ang0)), np.sin(np.deg2rad(ang0))])
        v1 = np.array([np.cos(np.deg2rad(ang1)), np.sin(np.deg2rad(ang1))])

        best_rate = 9999.0

        best_curve = None

        for i in range(len(curves)):
            new_rate = curves[i].rate_curve(curves[i])
            if best_rate > new_rate:
                best_rate = new_rate
                best_curve = curves[i]

        for j in range(0, len(curves), 1):
            if best_curve != curves[j]:
                random_length_c0 = (best_curve.c0 - best_curve.p0) / v0 - (curves[j].c0 - curves[j].p0) / v0
                random_length_c1_x = best_curve.c1[0] - curves[j].c1[0]
                random_length_c1_y = best_curve.c1[1] - curves[j].c1[1]
                random_length_c2_x = best_curve.c2[0] - curves[j].c2[0]
                random_length_c2_y = best_curve.c2[1] - curves[j].c2[1]
                random_length_c3 = (best_curve.c3 - best_curve.p1) / v1 - (curves[j].c3 - curves[j].p1) / v1

                plus_c0 = uniform(random_length_c0 * 0.1, random_length_c0 * 0.375) * v0
                plus_c1 = np.array([uniform(random_length_c1_x * 0.1, random_length_c1_x * 0.375),
                                    uniform(random_length_c1_y * 0.1, random_length_c1_y * 0.375)])
                plus_c2 = np.array([uniform(random_length_c2_x * 0.1, random_length_c2_x * 0.375),
                                    uniform(random_length_c2_y * 0.1, random_length_c2_y * 0.375)])
                plus_c3 = uniform(random_length_c3 * 0.1, random_length_c3 * 0.375) * v1

                curves[j] = QuanticBezierCurve(curves[j].p0, curves[j].c0 + plus_c0, curves[j].c1 + plus_c1,
                                               curves[j].c2 + plus_c2, curves[j].c3 + plus_c3,
                                               curves[j].p1)
                new_rate = curves[j].rate_curve(curves[j])

                if best_rate > new_rate:
                    best_rate = new_rate
                    best_curve = curves[j]

        return curves

    @staticmethod
    def last_curves(p0, ang0, p1, ang1, res=15):
        curves = [ParticleSwarm.start_curves(p0, ang0, p1, ang1)]
        for i in range(1, res, 1):
            curves.append(ParticleSwarm.next_curves(curves[i-1], ang0, ang1))

        best_rate = 9999
        best_curve = None

        for i in range(0, len(curves[res - 1]), 1):
            new_rate = curves[res - 1][i].rate_curve(curves[res - 1][i])
            if 0 < new_rate < best_rate:
                best_rate = new_rate
                best_curve = curves[res - 1][i]

        return ParticleSwarm(p0, p1, best_curve, curves[0], curves[res - 1])

    def __str__(self):
        return self.curves
