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

    @staticmethod
    def function_random(min_random, max_random, x):
        m = max_random - min_random
        return m * x + min_random

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

        min_random = -random_length
        max_random = random_length

        new_vector_multiplier0 = (best_curve.c0 - best_curve.p0) / v0 + RandomSearch.function_random(min_random,
                                                                                                     max_random,
                                                                                                     np.random.random())
        new_vector_multiplier1 = (best_curve.c3 - best_curve.p1) / v1 + RandomSearch.function_random(min_random,
                                                                                                     max_random,
                                                                                                     np.random.random())

        new_c1 = best_curve.c1 + np.array(
            [RandomSearch.function_random(min_random,
                                          max_random,
                                          np.random.random()), RandomSearch.function_random(min_random,
                                                                                            max_random,
                                                                                            np.random.random())])

        new_c2 = best_curve.c2 + np.array(
            [RandomSearch.function_random(min_random,
                                          max_random,
                                          np.random.random()), RandomSearch.function_random(min_random,
                                                                                            max_random,
                                                                                            np.random.random())])
        new_curve = QuanticBezierCurve(p0, p0 + new_vector_multiplier0 * l * v0, new_c1, new_c2, p1 +
                                       new_vector_multiplier1 * l * v1, p1)

        new_rate = new_curve.rate_curve(new_curve)

        if 0 < new_rate < best_rate:
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

            elif p0[0] >= p1[0] and p0[1] < p1[1]:
                random_length_x.append(p1[0] - abs(p1[0] - p0[0]) - abs(p1[1] - p0[1]))
                random_length_x.append(p0[0])
                random_length_y.append(p0[1])
                random_length_y.append(p1[1])

            elif p0[0] < p1[0] and p0[1] >= p1[1]:
                random_length_x.append(p0[0])
                random_length_x.append(p1[0])
                random_length_y.append(p1[1])
                random_length_y.append(p0[1] + abs(p1[0] - p0[0]) + abs(p1[1] - p0[1]))

            elif p0[0] >= p1[0] and p0[1] >= p1[1]:
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

            elif p0[0] <= p1[0] and p0[1] >= p1[1]:
                random_length_x.append(p0[0])
                random_length_x.append(p1[0] + abs(p1[0] - p0[0]) + abs(p1[1] - p0[1]))
                random_length_y.append(p1[1])
                random_length_y.append(p0[1])

            elif p0[0] >= p1[0] and p0[1] >= p1[1]:
                random_length_x.append(p1[0] - abs(p1[0] - p0[0]) - abs(p1[1] - p0[1]))
                random_length_x.append(p0[0])
                random_length_y.append(p1[1])
                random_length_y.append(p0[1])

        elif ang0 == ang1:
            if p0[0] <= p1[0] and p0[1] < p1[1]:
                random_length_x.append(p0[0])
                random_length_x.append(p1[0])
                random_length_y.append(p0[1])
                random_length_y.append(p1[1])

            elif p0[0] <= p1[0] and p0[1] >= p1[1]:
                random_length_x.append(p0[0])
                random_length_x.append(p1[0])
                random_length_y.append(p1[1] - abs(p1[0] - p0[0]) - abs(p1[1] - p0[1]))
                random_length_y.append(p0[1] + abs(p1[0] - p0[0]) + abs(p1[1] - p0[1]))

            elif p0[0] > p1[0] and p0[1] < p1[1]:
                random_length_x.append(p1[0])
                random_length_x.append(p0[0])
                random_length_y.append(p0[1])
                random_length_y.append(p1[1])

            elif p0[0] > p1[0] and p0[1] >= p1[1]:
                random_length_x.append(p1[0])
                random_length_x.append(p0[0])
                random_length_y.append(p1[1] - abs(p1[0] - p0[0]) - abs(p1[1] - p0[1]))
                random_length_y.append(p0[1] + abs(p1[0] - p0[0]) + abs(p1[1] - p0[1]))

        v0 = np.array([np.cos(np.deg2rad(ang0)), np.sin(np.deg2rad(ang0))])
        v1 = np.array([np.cos(np.deg2rad(ang1)), np.sin(np.deg2rad(ang1))])

        min_random_x = random_length_x[0]
        min_random_y = random_length_y[0]
        max_random_x = random_length_x[1]
        max_random_y = random_length_y[1]

        for i in range(0, res, 1):
            u0 = abs(ParticleSwarm.function_random(min_random_x, max_random_x, np.random.random()))
            u1 = abs(ParticleSwarm.function_random(min_random_x, max_random_x, np.random.random()))

            c0 = p0 + u0 * v0
            c1 = np.array([ParticleSwarm.function_random(min_random_x, max_random_x, np.random.random()),
                           ParticleSwarm.function_random(min_random_y, max_random_y, np.random.random())])
            c2 = np.array([ParticleSwarm.function_random(min_random_x, max_random_x, np.random.random()),
                           ParticleSwarm.function_random(min_random_y, max_random_y, np.random.random())])
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

        min_random = 0.1
        max_random = 0.375

        for j in range(0, len(curves), 1):
            if best_curve != curves[j]:
                random_length_c0 = (best_curve.c0 - best_curve.p0) / v0 - (curves[j].c0 - curves[j].p0) / v0
                random_length_c1 = best_curve.c1 - curves[j].c1
                random_length_c2 = best_curve.c2 - curves[j].c2
                random_length_c3 = (best_curve.c3 - best_curve.p1) / v1 - (curves[j].c3 - curves[j].p1) / v1

                plus_c0 = ParticleSwarm.function_random(min_random, max_random,
                                                        np.random.random()) * random_length_c0 * v0
                plus_c1 = np.array([ParticleSwarm.function_random(min_random, max_random, np.random.random()),
                                    ParticleSwarm.function_random(min_random, max_random,
                                                                  np.random.random())]) * random_length_c1
                plus_c2 = np.array([ParticleSwarm.function_random(min_random, max_random, np.random.random()),
                                    ParticleSwarm.function_random(min_random, max_random,
                                                                  np.random.random())]) * random_length_c2
                plus_c3 = ParticleSwarm.function_random(min_random, max_random,
                                                        np.random.random()) * random_length_c3 * v1

                curves[j] = QuanticBezierCurve(curves[j].p0, curves[j].c0 + plus_c0, curves[j].c1 + plus_c1,
                                               curves[j].c2 + plus_c2, curves[j].c3 + plus_c3,
                                               curves[j].p1)
                new_rate = curves[j].rate_curve(curves[j])

                if best_rate > new_rate:
                    best_rate = new_rate
                    best_curve = curves[j]

        return curves, best_curve

    @staticmethod
    def last_curves(p0, ang0, p1, ang1, res=15):
        curves = [ParticleSwarm.start_curves(p0, ang0, p1, ang1)]
        for i in range(1, res, 1):
            curves.append(ParticleSwarm.next_curves(curves[i - 1], ang0, ang1)[0])

        best_rate = 9999
        best_curve = None

        for i in range(0, len(curves[res - 1]), 1):
            new_rate = curves[res - 1][i].rate_curve(curves[res - 1][i])
            if 0 < new_rate < best_rate:
                best_rate = new_rate
                best_curve = curves[res - 1][i]

        return ParticleSwarm(p0, p1, best_curve, curves[0], curves[res - 1])

    @staticmethod
    def start_curves_connect(curve, ang1, p2, ang2, res=15):
        curves = []
        l = np.linalg.norm(p2 - curve.p1)

        random_length_x = []
        random_length_y = []

        if ang1 - ang2 > 0:
            if curve.p1[0] < p2[0] and curve.p1[1] < p2[1]:
                random_length_x.append(curve.p1[0])
                random_length_x.append(p2[0])
                random_length_y.append(curve.p1[1])
                random_length_y.append(p2[1])

            elif curve.p1[0] > p2[0] and curve.p1[1] < p2[1]:
                random_length_x.append(p2[0] - abs(p2[0] - curve.p1[0]) - abs(p2[1] - curve.p1[1]))
                random_length_x.append(curve.p1[0])
                random_length_y.append(curve.p1[1])
                random_length_y.append(p2[1])

            elif curve.p1[0] < p2[0] and curve.p1[1] > p2[1]:
                random_length_x.append(curve.p1[0])
                random_length_x.append(p2[0])
                random_length_y.append(p2[1])
                random_length_y.append(curve.p1[1] + abs(p2[0] - curve.p1[0]) + abs(p2[1] - curve.p1[1]))

            elif curve.p1[0] > p2[0] and curve.p1[1] > p2[1]:
                random_length_x.append(p2[0] - abs(p2[0] - curve.p1[0]) - abs(p2[1] - curve.p1[1]))
                random_length_x.append(curve.p1[0])
                random_length_y.append(p2[1])
                random_length_y.append(curve.p1[1] + abs(p2[0] - curve.p1[0]) + abs(p2[1] - curve.p1[1]))

        elif ang1 - ang2 < 0:
            if curve.p1[0] < p2[0] and curve.p1[1] < p2[1]:
                random_length_x.append(curve.p1[0])
                random_length_x.append(p2[0] + abs(p2[0] - curve.p1[0]) + abs(p2[1] - curve.p1[1]))
                random_length_y.append(curve.p1[1] - abs(p2[0] - curve.p1[0]) - abs(p2[1] - curve.p1[1]))
                random_length_y.append(p2[1])

            elif curve.p1[0] > p2[0] and curve.p1[1] < p2[1]:
                random_length_x.append(p2[0])
                random_length_x.append(curve.p1[0])
                random_length_y.append(curve.p1[1])
                random_length_y.append(p2[1])

            elif curve.p1[0] < p2[0] and curve.p1[1] > p2[1]:
                random_length_x.append(curve.p1[0])
                random_length_x.append(p2[0] + abs(p2[0] - curve.p1[0]) + abs(p2[1] - curve.p1[1]))
                random_length_y.append(p2[1])
                random_length_y.append(curve.p1[1])

            elif curve.p1[0] > p2[0] and curve.p1[1] > p2[1]:
                random_length_x.append(p2[0] - abs(p2[0] - curve.p1[0]) - abs(p2[1] - curve.p1[1]))
                random_length_x.append(curve.p1[0])
                random_length_y.append(p2[1])
                random_length_y.append(curve.p1[1])

        elif ang1 == ang2:
            if curve.p1[0] < p2[0] and curve.p1[1] < p2[1]:
                random_length_x.append(curve.p1[0])
                random_length_x.append(p2[0])
                random_length_y.append(curve.p1[1])
                random_length_y.append(p2[1])

            elif curve.p1[0] < p2[0] and curve.p1[1] > p2[1]:
                random_length_x.append(curve.p1[0])
                random_length_x.append(p2[0])
                random_length_y.append(p2[1] - abs(p2[0] - curve.p1[0]) - abs(p2[1] - curve.p1[1]))
                random_length_y.append(curve.p1[1] + abs(p2[0] - curve.p1[0]) + abs(p2[1] - curve.p1[1]))

            elif curve.p1[0] > p2[0] and curve.p1[1] < p2[1]:
                random_length_x.append(p2[0])
                random_length_x.append(curve.p1[0])
                random_length_y.append(curve.p1[1])
                random_length_y.append(p2[1])

            elif curve.p1[0] > p2[0] and curve.p1[1] > p2[1]:
                random_length_x.append(p2[0])
                random_length_x.append(curve.p1[0])
                random_length_y.append(p2[1] - abs(p2[0] - curve.p1[0]) - abs(p2[1] - curve.p1[1]))
                random_length_y.append(curve.p1[1] + abs(p2[0] - curve.p1[0]) + abs(p2[1] - curve.p1[1]))

        v0 = np.array([np.cos(np.deg2rad(ang1)), np.sin(np.deg2rad(ang1))])
        v1 = np.array([np.cos(np.deg2rad(ang2)), np.sin(np.deg2rad(ang2))])

        min_random_x = random_length_x[0]
        min_random_y = random_length_y[0]
        max_random_x = random_length_x[1]
        max_random_y = random_length_y[1]

        for i in range(0, res, 1):
            # u0 = ParticleSwarm.function_random(min_random_x, max_random_x, np.random.random())
            u1 = ParticleSwarm.function_random(min_random_x, max_random_x, np.random.random())

            # c0 = curve.p1 + u0 * v0
            c0 = 2 * curve.p1 - curve.c3
            # c1 = np.array([ParticleSwarm.function_random(min_random_x, max_random_x, np.random.random()),
            #                ParticleSwarm.function_random(min_random_y, max_random_y, np.random.random())])
            c1 = curve.c2 + 2 * c0 - 2 * curve.c3
            c2 = np.array([ParticleSwarm.function_random(min_random_x, max_random_x, np.random.random()),
                           ParticleSwarm.function_random(min_random_y, max_random_y, np.random.random())])
            c3 = p2 - u1 * v1
            curves.append(QuanticBezierCurve(curve.p1, c0, c1, c2, c3, p2))

        return curves

    @staticmethod
    def next_curves_connect(curves, ang1, ang2):

        v0 = np.array([np.cos(np.deg2rad(ang1)), np.sin(np.deg2rad(ang1))])
        v1 = np.array([np.cos(np.deg2rad(ang2)), np.sin(np.deg2rad(ang2))])

        best_rate = 9999.0

        best_curve = None

        for i in range(len(curves)):
            new_rate = curves[i].rate_curve(curves[i])
            if best_rate > new_rate:
                best_rate = new_rate
                best_curve = curves[i]

        min_random = 0.1
        max_random = 0.375

        for j in range(0, len(curves), 1):
            if best_curve != curves[j]:
                # random_length_c0 = (best_curve.c0 - best_curve.p0) / v0 - (curves[j].c0 - curves[j].p0) / v0
                # random_length_c1 = best_curve.c1 - curves[j].c1
                random_length_c2 = best_curve.c2 - curves[j].c2
                random_length_c3 = (best_curve.c3 - best_curve.p1) / v1 - (curves[j].c3 - curves[j].p1) / v1

                # plus_c0 = ParticleSwarm.function_random(min_random, max_random,
                #                                         np.random.random()) * random_length_c0 * v0
                # plus_c1 = np.array([ParticleSwarm.function_random(min_random, max_random, np.random.random()),
                #                     ParticleSwarm.function_random(min_random, max_random,
                #                                                   np.random.random())]) * random_length_c1
                plus_c2 = np.array([ParticleSwarm.function_random(min_random, max_random, np.random.random()),
                                    ParticleSwarm.function_random(min_random, max_random,
                                                                  np.random.random())]) * random_length_c2
                plus_c3 = ParticleSwarm.function_random(min_random, max_random,
                                                        np.random.random()) * random_length_c3 * v1

                curves[j] = QuanticBezierCurve(curves[j].p0, curves[j].c0, curves[j].c1,
                                               curves[j].c2 + plus_c2, curves[j].c3 + plus_c3,
                                               curves[j].p1)
                new_rate = curves[j].rate_curve(curves[j])

                if best_rate > new_rate:
                    best_rate = new_rate
                    best_curve = curves[j]

        return curves

    @staticmethod
    def last_curves_connect(curve, ang1, p2, ang2, res=15):
        curves = [ParticleSwarm.start_curves_connect(curve, ang1, p2, ang2)]
        for i in range(1, res, 1):
            curves.append(ParticleSwarm.next_curves_connect(curves[i - 1], ang1, ang2))

        best_rate = 9999
        best_curve = None

        for i in range(0, len(curves[res - 1]), 1):
            new_rate = curves[res - 1][i].rate_curve(curves[res - 1][i])
            if 0 < new_rate < best_rate:
                best_rate = new_rate
                best_curve = curves[res - 1][i]

        return ParticleSwarm(curve.p1, p2, best_curve, curves[0], curves[res - 1])

    def __str__(self):
        return self.curves
