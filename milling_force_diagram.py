from numba import jit
import math
import matplotlib.pyplot as plt
import numpy as np


def plot(forces):
    x = np.arange(0, len(forces), 1)
    plt.plot(x, forces)
    # naming the x axis
    plt.xlabel('Arbeitsschritt')
    # naming the y axis
    plt.ylabel('F(Kraft)')

    # giving a title to my graph
    plt.title('Kraftmessung')
    plt.show()


# @jit(nopython = True)
def definiere_kreis(diameter):
    origin = np.array([0, 0, 0])
    resolution_circle = 0.1
    diameter = int(diameter)
    umfang = math.pi * diameter
    schritte = np.array([])
    radien = np.array([])
    circles = []
    for x in range(int((diameter / 2) / resolution_circle) + 1):
        schritte = np.append(schritte, int(umfang / resolution_circle))
        radien = np.append(radien, x * resolution_circle)

    for r, schritte in zip(radien, schritte):
        t = np.linspace(0, 2 * math.pi, int(schritte))

        x = r * np.cos(t)
        y = r * np.sin(t)

        circles.append(np.c_[x, y].round(3))
    return circles


@jit(nopython=True)
def transform_coordinates_to_point(res, origin, kooX, kooY):
    x = int((kooX - origin[0]) / res[0])
    y = int((kooY - origin[1]) / res[1])
    return [x, y]


@jit(nopython=True)
def calculate_force(center, circles, heightfield, resolution, origin, dimension, material_faktor, mc):
    abstand = 0.1  # abstand zwischen den Kreisen guck definiere_kreis-> resolution_circle
    kraft = 0
    max = 0
    for x in range(len(circles[0])):
        if circles[-1][x][0] + center[0] > origin[0] and circles[-1][x][0] + center[0] < origin[0] + dimension[
            0]:  # ist x koo. vom punkt auf kreis im höhenfeld
            if circles[-1][x][1] + center[1] > origin[1] and circles[-1][x][1] + center[1] < origin[1] + dimension[
                1]:  # ist y koo. vom punkt auf kreis im höhenfeld
                schnittpunkt = transform_coordinates_to_point(resolution, origin, circles[-1][x][0],
                                                              circles[-1][x][1])

                hoehe = float(center[2])
                if heightfield[int(schnittpunkt[1])][int(schnittpunkt[0])] - dimension[
                    2] > hoehe:  # ist z koo. vom punkt auf kreis im höhenfeld

                    tiefe = 0
                    for y in range(
                            len(circles) - 1):  # gehe auf punkte von kleineren Kreisen mit gleichen winkel rein
                        if circles[-y][x][0] + center[0] > origin[0] and circles[-y][x][0] + center[0] < origin[0] + \
                                dimension[0]:  # same shit x
                            if circles[-y][x][1] + center[1] > origin[1] and circles[-y][x][1] + center[1] < origin[
                                1] + dimension[1]:  # same shit y
                                schnittpunkt = transform_coordinates_to_point(resolution, origin, circles[-1][x][0],
                                                                              circles[-1][x][1])

                                hoehe = float(center[2])
                                if heightfield[int(schnittpunkt[1])][int(schnittpunkt[0])] - dimension[2] > hoehe:
                                    tiefe += 1

                                else:
                                    break
                            else:
                                break
                        else:
                            break

                    spanungsbreite = heightfield[int(schnittpunkt[1])][int(schnittpunkt[0])] - dimension[2] - hoehe
                    kraft = material_faktor * math.pow((abstand * tiefe), (1 - mc)) * spanungsbreite
                    if kraft > max:
                        max = kraft
    return max


def main():
    pass


if __name__ == '__main__':
    main()
