from numba import jit
import math
import matplotlib.pyplot as plt
import numpy as np
from numba.core.errors import NumbaDeprecationWarning, NumbaPendingDeprecationWarning
import warnings

warnings.simplefilter('ignore', category=NumbaPendingDeprecationWarning)


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
def init_circle(diameter):
    origin = np.array([0, 0, 0])
    resolution_circle = 0.1
    diameter = int(diameter)
    perimeter = math.pi * diameter
    steps = np.array([])
    radii = np.array([])
    circles = []
    for x in range(int((diameter / 2) / resolution_circle) + 1):
        steps = np.append(steps, int(perimeter / resolution_circle))
        radii = np.append(radii, x * resolution_circle)

    for r, steps in zip(radii, steps):
        t = np.linspace(0, 2 * math.pi, int(steps))

        x = r * np.cos(t)
        y = r * np.sin(t)

        circles.append(np.c_[x, y].round(3))
    return circles


@jit(nopython=True)
def transform_coordinates_to_point(res, origin, x_coordinate, y_coordinate):
    x = int((x_coordinate - origin[0]) / res[0])
    y = int((y_coordinate - origin[1]) / res[1])
    return [x, y]


@jit(nopython=True)
def calculate_force(center, circles, heightfield, resolution, origin_work_piece, dimension, material_factor, mc):
    point_distance = 0.1  # distance between circle points
    max_force = 0
    for x in range(len(circles[0])):
        if circles[-1][x][0] + center[0] > origin_work_piece[0] and circles[-1][x][0] + center[0] < origin_work_piece[
            0] + dimension[
            0]:  # ist x koo. vom punkt auf kreis im höhenfeld
            if circles[-1][x][1] + center[1] > origin_work_piece[1] and circles[-1][x][1] + center[1] < \
                    origin_work_piece[1] + dimension[
                1]:  # ist y koo. vom punkt auf kreis im höhenfeld
                intersection = transform_coordinates_to_point(resolution, origin_work_piece, circles[-1][x][0],
                                                              circles[-1][x][1])

                height = float(center[2])
                if heightfield[int(intersection[1])][int(intersection[0])] - dimension[
                    2] > height:  # ist z koo. vom punkt auf kreis im höhenfeld

                    depth = 0
                    for y in range(
                            len(circles) - 1):  # gehe auf punkte von kleineren Kreisen mit gleichen winkel rein
                        if circles[-y][x][0] + center[0] > origin_work_piece[0] and circles[-y][x][0] + center[0] < \
                                origin_work_piece[0] + \
                                dimension[0]:  # same shit x
                            if circles[-y][x][1] + center[1] > origin_work_piece[1] and circles[-y][x][1] + center[1] < \
                                    origin_work_piece[
                                        1] + dimension[1]:  # same shit y
                                intersection = transform_coordinates_to_point(resolution, origin_work_piece,
                                                                              circles[-1][x][0],
                                                                              circles[-1][x][1])

                                height = float(center[2])
                                if heightfield[int(intersection[1])][int(intersection[0])] - dimension[2] > height:
                                    depth += 1

                                else:
                                    break
                            else:
                                break
                        else:
                            break

                    cutting_width = heightfield[int(intersection[1])][int(intersection[0])] - dimension[2] - height
                    force = material_factor * math.pow((point_distance * depth), (1 - mc)) * cutting_width
                    if force > max_force:
                        max_force = force
    return max_force


def main():
    pass


if __name__ == '__main__':
    main()
