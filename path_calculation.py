import numpy as np
import circle
import csv
from enum import Enum


def read_from_file(nc_code_file):
    with open(nc_code_file) as nc_code:
        lines = nc_code.readlines()
    return lines


def create_coordinates_file(coordinates_file):
    with open(coordinates_file, 'w'):
        pass


def append_multiple_coordinates_to_file(coordinates_file, list_of_coordinates):
    with open(coordinates_file, 'a', newline='') as csvFile:
        writer = csv.writer(csvFile)
        writer.writerows(list_of_coordinates)
    csvFile.close()


def append_toolcall_diameter_to_file(coordinates_file, toolcall_diameter):
    with open(coordinates_file, 'a') as csvFile:
        csvFile.write(toolcall_diameter + "\n")
    csvFile.close()


def separate_line_into_single_commands(nc_code_line):
    nc_code_line = nc_code_line.strip("\n")
    nc_code_list = nc_code_line.split(" ")
    return nc_code_list


# diese Methode berechnet eine gerade zwischen zwei Punkten und gibt die Zwischenschritte zurück
# Paremeter: liste= NC-Code, anfangsPunkt=3-dim Vektor, drehzahl,schneiden,v = Integer
def calculate_linear_movement_coordinates(nc_code_list, start_position, rpm, tool_blade_count, velocity):
    use_max_velocity = False
    m_91 = False
    MAX_VELOCITY = 2000
    x = None
    y = None
    z = None

    for command in nc_code_list:
        if command == "FMAX":
            use_max_velocity = True
        elif command.find("F") == 0:
            velocity = command.strip("F")
        if command.find("X") == 0:
            x = command.strip("X")
        if command.find("Y") == 0:
            y = command.strip("Y")
        if command.find("Z") == 0:
            z = command.strip("Z")
        if command == "M91":
            m_91 = True
    if x is None:
        x = float(start_position[0])
    if y is None:
        y = float(start_position[1])
    if z is None:
        z = float(start_position[2])
    if m_91:
        start_position[2] = start_position[2] + 1000
        z = float(z) + 1000

    destination = np.array([float(x), float(y), float(z)])
    coordinates_of_path = []
    # f_z = feed per tooth
    f_z = 1

    if use_max_velocity and rpm != 0:
        f_z = MAX_VELOCITY / (rpm * tool_blade_count)
    if use_max_velocity is False and rpm != 0:
        f_z = float(velocity) / (rpm * tool_blade_count)
    if rpm == 0:
        coordinates_of_path.append(destination)
        return [coordinates_of_path, destination, velocity]

    path_vector = destination - start_position
    path_length = np.linalg.norm(path_vector)
    step_count = path_length / f_z

    if (step_count == 0.0):
        step_count = 1
    step_length = path_vector / step_count
    if f_z > path_length:
        coordinates_of_path.append(destination)
        return [coordinates_of_path, destination, velocity]

    for i in range(1, int(step_count) + 1):
        steps_from_start_to_destination = start_position + step_length * i
        coordinates_of_path.append(steps_from_start_to_destination)
        if step_count - i < 1 and step_count - i > 0:
            steps_from_start_to_destination = start_position + step_length * step_count
            coordinates_of_path.append(steps_from_start_to_destination)

    return [coordinates_of_path, steps_from_start_to_destination, velocity]


# 30 CC X29.2387 Y19.4175
# diese Methode gibt einen 3-dim Vektor der die Kreismitte beschreibt zurück
def calculate_circle_center(nc_command_line, start_point):
    x = None
    y = None
    z = None
    for command in nc_command_line:
        if command.find("X") == 0:
            x = command.strip("X")
        if command.find("Y") == 0:
            y = command.strip("Y")
        if command.find("Z") == 0:
            z = command.strip("Z")

    circle_center = create_np_array(start_point, x, y, z)

    return circle_center


def calculate_circle_movement(nc_command_line, start_point, circle_center, f_z):
    x = None
    y = None
    z = None
    counter_clockwise_movement = None
    for command in nc_command_line:
        if command.find("X") == 0:
            x = command.strip("X")
        if command.find("Y") == 0:
            y = command.strip("Y")
        if command.find("Z") == 0:
            z = command.strip("Z")
        if command == "DR+":
            counter_clockwise_movement = True
        if command == "DR-":
            counter_clockwise_movement = False

    destination = create_np_array(start_point, x, y, z)

    return circle.calculate_circle_points(start_point, destination, circle_center, counter_clockwise_movement, f_z)


def create_np_array(start_point, x, y, z):
    if x is None:
        x = float(start_point[0])
    if y is None:
        y = float(start_point[1])
    if z is None:
        z = float(start_point[2])

    return np.array([float(x), float(y), float(z)])


# diese Methode list die Eigenschaften des Werkstücks ein und initialiesiert Koodinaten des Nullpunktes vom Werkstück
def init_work_piece(nc_command_list):
    global RELATIVE_ORIGIN
    x = nc_command_list[-3].strip("X")
    y = nc_command_list[-2].strip("Y")
    z = nc_command_list[-1].strip("Z")
    RELATIVE_ORIGIN = np.array([float(x), float(y), float(z)])


def tool_call(nc_command_list):
    rpm = 0
    tool_blade_count = [2, 2]
    tool_diameter = [5, 2]

    for command in nc_command_list:
        if command.find("S") == 0:
            rpm = command.strip("S")
    return [int(rpm), tool_blade_count[int(nc_command_list[3]) - 1], tool_diameter[int(nc_command_list[3]) - 1]]


class MovementCommands(Enum):
    INIT = "1"
    LINE = "L"
    CIRCLE_CENTER = "CC"
    CIRCLE = "C"
    TOOLCALL = "TOOL"


def calculate_coordinates(nc_code_file, coordinates_file):
    # origin = np.array([0, 0, 100])
    velocity = 0
    rpm = 0
    tool_blade_count = 2
    start_position = np.array([-500, -420, 100])
    circle_center = np.array([0, 0, 0])

    create_coordinates_file(coordinates_file)

    for line in read_from_file(nc_code_file):

        command_line = separate_line_into_single_commands(line)

        if command_line[0] == MovementCommands.INIT.value:
            init_work_piece(command_line)

        if command_line[1] == MovementCommands.LINE.value:
            movement = calculate_linear_movement_coordinates(command_line, start_position, rpm, tool_blade_count,
                                                             velocity)
            path_coordinates = movement[0]
            append_multiple_coordinates_to_file(coordinates_file, path_coordinates)
            start_position = movement[1]
            velocity = movement[2]

        if command_line[1] == MovementCommands.CIRCLE_CENTER.value:
            circle_center = calculate_circle_center(command_line, start_position)

        if command_line[1] == MovementCommands.CIRCLE.value:
            f_z = float(velocity) / (rpm * tool_blade_count)
            circle_path = calculate_circle_movement(command_line, start_position, circle_center, f_z)
            start_position = circle_path[len(circle_path) - 1]
            append_multiple_coordinates_to_file(coordinates_file, circle_path)

        if command_line[1] == MovementCommands.TOOLCALL.value:
            array = tool_call(command_line)
            rpm = array[0]
            tool_blade_count = array[1]
            toolcall = "Tool Durchmesser " + str(array[2])
            append_toolcall_diameter_to_file(coordinates_file, toolcall)


def main():
    pass


if __name__ == '__main__':
    main()
