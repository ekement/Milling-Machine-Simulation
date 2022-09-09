import numpy as np
import math


# calculates multiple points on multiple circles going from the center to the outside
def calculate_circle_points(start_position, destination, circle_center, counter_clockwise_movement, f_z):
    circles = []

    distance_vector_from_center_to_start = start_position - circle_center
    distance_vector_from_center_to_destination = destination - circle_center

    radius = [np.linalg.norm(distance_vector_from_center_to_start)]

    distance_vector_from_center_to_start = distance_vector_from_center_to_start / radius
    distance_vector_from_center_to_destination = distance_vector_from_center_to_destination / radius

    if distance_vector_from_center_to_start[0] > 1:
        distance_vector_from_center_to_start[0] = 1
    if distance_vector_from_center_to_start[0] < -1:
        distance_vector_from_center_to_start[0] = -1

    if distance_vector_from_center_to_destination[0] > 1:
        distance_vector_from_center_to_destination[0] = 1
    if distance_vector_from_center_to_destination[0] < -1:
        distance_vector_from_center_to_destination[0] = -1

    if distance_vector_from_center_to_start[1] >= 0:
        alpha = math.acos(distance_vector_from_center_to_start[0])
    else:
        alpha = 2 * math.pi - math.acos(distance_vector_from_center_to_start[0])
    if distance_vector_from_center_to_destination[1] >= 0:
        beta = math.acos(distance_vector_from_center_to_destination[0])
    else:
        beta = 2 * math.pi - math.acos(distance_vector_from_center_to_destination[0])

    if counter_clockwise_movement:
        if beta < alpha:
            beta += 2 * math.pi
        #help_calculation = (beta - alpha) / 2 * math.pi
        step_distance = [(((beta - alpha) / 2 * math.pi) * 2 * math.pi * radius[0]) / f_z]
    else:
        if beta > alpha:
            beta -= 2 * math.pi
        #help_calculation = (alpha - beta) / 2 * math.pi
        step_distance = [(((alpha - beta) / 2 * math.pi) * 2 * math.pi * radius[0]) / f_z]

    for radius, step_distance in zip(radius, step_distance):
        t = np.linspace(alpha, beta, int(step_distance))
        x = radius * np.cos(t) + circle_center[0]
        y = radius * np.sin(t) + circle_center[1]

    for i in range(0, len(x)):
        circles.append([x[i], y[i], circle_center[2]])

    if step_distance - int(step_distance) is not 0:
        circles.append(destination)

    return circles
