import numpy as np
#import matplotlib.pyplot as plt
import math


def circle_points(L, C, CC, dr_plus , f_z):
    circles = []

    v1Neu= L-CC
    v2Neu= C-CC

    r = [np.linalg.norm(v1Neu)]

    v1Neu = v1Neu/r
    v2Neu = v2Neu/r

    if v1Neu[0] > 1:
        v1Neu[0] = 1
    if v1Neu[0] < -1:
        v1Neu[0] = -1

    if v2Neu[0] > 1:
        v2Neu[0] = 1
    if v2Neu[0] < -1:
        v2Neu[0] = -1


    if v1Neu[1] >= 0:
        alpha = math.acos(v1Neu[0])
    else:
        alpha = 2*math.pi - math.acos(v1Neu[0])
    if v2Neu[1] >= 0:
        beta = math.acos(v2Neu[0])
    else:
        #print(v2Neu)
        #print(math.acos(v2Neu[0]))
        beta = 2*math.pi - math.acos(v2Neu[0])


    if dr_plus:
            if beta < alpha:
                beta += 2*math.pi
            zwischen_rechnung = (beta - alpha)/2*math.pi
            schritte = [(zwischen_rechnung*2*math.pi * r[0])/f_z]
    else:
            if beta > alpha:
                beta -= 2*math.pi
            zwischen_rechnung = (alpha - beta)/2*math.pi
            schritte = [(zwischen_rechnung*2*math.pi * r[0])/f_z]

    for r, schritte in zip(r, schritte):
            t = np.linspace(alpha, beta, int(schritte))
            x = r * np.cos(t) + CC[0]
            y = r * np.sin(t) + CC[1]

    for i in range(0, len(x)):
        circles.append([x[i], y[i], CC[2]])

    if schritte - int(schritte) is not 0:
        circles.append(C)


    # fig, ax = plt.subplots()
    # for circle in circles:
    #     ax.scatter(circle[:, 0], circle[:, 1])
    # ax.set_aspect('equal')
    # plt.show()

    return circles



