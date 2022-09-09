import milling_force_diagram
from numba import jit
import PySimpleGUI as sg
import numpy as np
import renderer


def read_file(file):
    text = open(file)
    nc = text.readlines()
    text.close()
    return nc


def split_nc_code_into_commands(nc_code):
    stripped_nc_code = nc_code.strip("\n")
    nc_commands_list = stripped_nc_code.split(" ")
    return nc_commands_list

# @jit(nopython = True)
def get_parameter():
    resolution = np.array([0.125, 0.125])  # 0.125, 0.125 war gut genug

    with open("NC_Code.txt") as myfile:
        # all_lines = myfile.readlines()
        # a = all_lines[1]
        # b = all_lines[2]
        next(myfile)
        head = [next(myfile) for x in range(2)]

    nc_command_list = split_nc_code_into_commands(head[0]), split_nc_code_into_commands(head[1])
    coordinates = []
    for eintrag in nc_command_list:
        x = eintrag[-3].strip("X")
        y = eintrag[-2].strip("Y")
        z = eintrag[-1].strip("Z")
        coordinates.append(np.array([float(x), float(y), float(z)]))

    dimension = coordinates[1] - coordinates[0]
    origin_work_piece = coordinates[0]
    origin_work_piece[2] = origin_work_piece[2] - dimension[2]
    cell_count = [int(dimension[0]) / resolution[0], int(dimension[1]) / resolution[1]]

    return [resolution, dimension, origin_work_piece, cell_count]


def init_heightfield(dimension, cell_count):
    heightfield = dimension[2] * np.ones([int(cell_count[1]), int(cell_count[0])])
    return heightfield


def render(vertices):
    color = np.zeros_like(vertices[0])
    color[:, 0] = 211 / 255
    color[:, 1] = 211 / 255
    color[:, 2] = 211 / 255
    data = np.column_stack((vertices[0], color))
    color = np.zeros_like(vertices[1])
    color[:, 0] = 128 / 255
    color[:, 1] = 128 / 255
    color[:, 2] = 128 / 255
    data2 = np.column_stack((vertices[1], color))
    render_block = renderer.Renderer(np.row_stack((data, data2)))
    render_block.run()


@jit(nopython=True)
def define_implicit_circle(heightfield, circle_center, radius, resolution, origin_work_piece):
    # mittelpunkt ist ein Punkt im Hoehenfeld
    center_point = transform_coordinates_to_point(resolution, origin_work_piece, circle_center[0], circle_center[1])

    # markierte_reichweite ist der Radius im Hoehenfeld
    radius_steps = int(radius / resolution[1])

    top_corner = [center_point[0] + radius_steps, center_point[1] + radius_steps]
    bottom_corner = [center_point[0] - radius_steps, center_point[1] - radius_steps]

    for x in range(bottom_corner[0], top_corner[0] + 1):
        for y in range(bottom_corner[1], top_corner[1] + 1):
            if x > len(heightfield[0]) - 1 or y > len(heightfield) - 1 or x < 0 or y < 0:
                continue
            else:
                destination = np.array(transform_point_to_coordinate(resolution, origin_work_piece, x, y, circle_center[2]))
                distance_vector_from_circle_center_to_destination = destination - circle_center
                circle_center_to_destination_distance = np.linalg.norm(distance_vector_from_circle_center_to_destination)

                if circle_center_to_destination_distance <= radius:

                    if heightfield[y][x] + origin_work_piece[2] > circle_center[2]:
                        heightfield[y][x] = circle_center[2] - origin_work_piece[2]
    return heightfield


def process_work_piece(coordinates_file):
    diameter = 0
    center_all = read_file(coordinates_file)
    material = 0
    mc = 0.0
    plot = False

    layout = [[sg.Text('Welcher Zustand soll angezeigt werden?')],
              [sg.Combo(['Anfang', 'Mitte', 'Ende'], default_value='Anfang')],
              [sg.Text('Kraftmessung ausgeben?')],
              [sg.Combo(['Ja', 'Nein'], default_value='Nein')],
              [sg.Text('Welches Material wird benutzt?')],
              [sg.Combo(['Aluminium mit < 16% Si Messing',
                         'Aluminium mit > 16% Si Bronze, Kupfer',
                         'Automatenstahl mit geringem Kohlenstoffgehalt'], default_value='Aluminium mit < 16% Si Messing')],
              [sg.Button('Ok'), sg.Button('Cancel')]]

    window = sg.Window('Window Title', layout)
    while True:
        event, values = window.read()

        if event in (None, 'Cancel'):  # if user closes window or clicks cancel
            break
        if values[0] == 'Anfang':
            state = 1

        if values[0] == 'Mitte':
            state = len(center_all) // 4

        if values[0] == 'Ende':
            state = len(center_all)

        if values[1] == 'Ja':
            plot = True

        if values[1] == 'Nein':
            plot = False

        if values[2] == 'Aluminium mit < 16% Si Messing':
            material = 700
            mc = 0.25
            break
        if values[2] == 'Aluminium mit > 16% Si Bronze, Kupfer':
            material = 700
            mc = 0.27
            break
        if values[2] == 'Automatenstahl mit geringem Kohlenstoffgehalt':
            material = 1500
            mc = 0.22
            break

    window.close()

    center_all = center_all[:state]
    parameter = get_parameter()
    resolution = parameter[0]
    dimension = parameter[1]
    origin_work_piece = parameter[2]
    cell_count = parameter[3]
    heightfield = init_heightfield(dimension, cell_count)

    force_calculation_circle = milling_force_diagram.init_circle(diameter)
    forces = []
    for current_center in center_all:
        if current_center[0] == "T":
            diameter = current_center[-2]
            force_calculation_circle = milling_force_diagram.init_circle(diameter)
            continue

        current_center = np.array(current_center.split(","))
        current_center = current_center.astype(float)

        radius = float(diameter) / 2

        force = milling_force_diagram.calculate_force(current_center, force_calculation_circle, heightfield, resolution, origin_work_piece, dimension, material, mc)
        forces.append(force)

        heightfield = define_implicit_circle(heightfield, current_center, radius, resolution, origin_work_piece)

    print("Heightfield fertig")

    print("Berechne Vertices")
    vertices = calculate_Vertices(cell_count[0], cell_count[1], resolution, origin_work_piece, heightfield)

    print("Berechne Triangles")
    vertices_triangles = [np.array(vertices_horizontal_triangle(vertices, resolution, dimension)),
                          np.array(vertices_vertical_triangle(vertices, heightfield, resolution, dimension))]
    print("Renderer wird gestartet")
    # renderer2.pygameI(vertices_triangles)

    render(vertices_triangles)
    if plot:
        milling_force_diagram.plot(forces)




@jit(nopython=True)
def transform_coordinates_to_point(res, origin, x_coordinate, y_coordinate):
    x = int((x_coordinate - origin[0]) / res[0])
    y = int((y_coordinate - origin[1]) / res[1])
    return [x, y]


# Punkt zu Koordinate
@jit(nopython=True)
def transform_point_to_coordinate(res, origin, x_coordinate, y_coordinate, height):
    x = origin[0] + x_coordinate * res[0]
    y = origin[1] + y_coordinate * res[1]
    return [x, y, height]


@jit(nopython=True)
def calculate_vertices(point_width, point_depth, resolution, origin_work_piece, heightfield):
    vertices_ground = []
    vertices_ceiling = []
    for x in range(int(point_width)):
        for y in range(int(point_depth)):
            coordinate_vector = transform_point_to_coordinate(resolution, origin_work_piece, x, y, origin_work_piece[2])
            vertices_ground.append(coordinate_vector)
            vertices_ceiling.append([coordinate_vector[0], coordinate_vector[1], heightfield[y][x] + origin_work_piece[2]])

    return [np.array(vertices_ground), np.array(vertices_ceiling)]



# @jit(nopython = True)
def vertices_vertical_triangle(vertices, heightfield, resolution, dimension):
    ground = vertices[0][0][2]
    origin_work_piece = get_parameter()[2]

    vertices_vertical = []

    for vertex in vertices[1]:
        if vertex[0] >= dimension[0] or vertex[1] >= dimension[1]:
            continue

        else:
            # front
            position = transform_coordinates_to_point(resolution, origin_work_piece, x_coordinate=vertex[0], y_coordinate=vertex[1])

            if position[1] == 0 or heightfield[position[1]][position[0]] > heightfield[position[1] - 1][position[0]]:
                vertices_vertical.append([vertex[0], vertex[1], ground])
                vertices_vertical.append([vertex[0] + resolution[0], vertex[1], vertex[2]])
                vertices_vertical.append([vertex[0], vertex[1], vertex[2]])

                vertices_vertical.append([vertex[0], vertex[1], ground])
                vertices_vertical.append([vertex[0] + resolution[0], vertex[1], vertex[2]])
                vertices_vertical.append([vertex[0] + resolution[0], vertex[1], ground])

            # left side
            if position[0] == 0 or heightfield[position[1]][position[0]] > heightfield[position[1]][position[0] - 1]:
                vertices_vertical.append([vertex[0], vertex[1], ground])
                vertices_vertical.append([vertex[0], vertex[1] + resolution[1], vertex[2]])
                vertices_vertical.append([vertex[0], vertex[1], vertex[2]])

                vertices_vertical.append([vertex[0], vertex[1], ground])
                vertices_vertical.append([vertex[0], vertex[1] + resolution[1], vertex[2]])
                vertices_vertical.append([vertex[0], vertex[1] + resolution[1], ground])

            # right side
            if position[0] == len(heightfield[0]) - 1 or heightfield[position[1]][position[0]] > \
                    heightfield[position[1]][position[0] + 1]:
                vertices_vertical.append([vertex[0] + resolution[0], vertex[1], ground])
                vertices_vertical.append([vertex[0] + resolution[0], vertex[1], vertex[2]])
                vertices_vertical.append([vertex[0] + resolution[0], vertex[1] + resolution[1], vertex[2]])

                vertices_vertical.append([vertex[0] + resolution[0], vertex[1] + resolution[1], ground])
                vertices_vertical.append([vertex[0] + resolution[0], vertex[1] + resolution[1], vertex[2]])
                vertices_vertical.append([vertex[0] + resolution[0], vertex[1], ground])

            # back
            if position[1] == len(heightfield) - 1 or \
                    heightfield[position[1]][position[0]] > \
                    heightfield[position[1] + 1][position[0]]:
                vertices_vertical.append([vertex[0], vertex[1] + resolution[1], ground])
                vertices_vertical.append([vertex[0] + resolution[0], vertex[1] + resolution[1], vertex[2]])
                vertices_vertical.append([vertex[0], vertex[1] + resolution[1], vertex[2]])

                vertices_vertical.append([vertex[0], vertex[1] + resolution[1], ground])
                vertices_vertical.append([vertex[0] + resolution[0], vertex[1] + resolution[1], vertex[2]])
                vertices_vertical.append([vertex[0] + resolution[0], vertex[1] + resolution[1], ground])

    return vertices_vertical


# @jit(nopython = True)
def vertices_horizontal_triangle(vertices, resolution, dimension):
    vertices_horizontal = []

    for vertex in vertices[0]:
        if vertex[0] >= dimension[0] or vertex[1] >= dimension[1]:
            continue

        else:
            vertices_horizontal.append([vertex[0], vertex[1], vertex[2]])
            vertices_horizontal.append([vertex[0] + resolution[0], vertex[1], vertex[2]])
            vertices_horizontal.append([vertex[0], vertex[1] + resolution[0], vertex[2]])

            vertices_horizontal.append([vertex[0] + resolution[0], vertex[1], vertex[2]])
            vertices_horizontal.append([vertex[0], vertex[1] + resolution[0], vertex[2]])
            vertices_horizontal.append([vertex[0] + resolution[0], vertex[1] + resolution[0], vertex[2]])

    for vertex in vertices[1]:
        if vertex[0] >= dimension[0] or vertex[1] >= dimension[1]:
            continue

        else:
            vertices_horizontal.append([vertex[0], vertex[1], vertex[2]])
            vertices_horizontal.append([vertex[0] + resolution[0], vertex[1], vertex[2]])
            vertices_horizontal.append([vertex[0], vertex[1] + resolution[0], vertex[2]])

            vertices_horizontal.append([vertex[0] + resolution[0], vertex[1], vertex[2]])
            vertices_horizontal.append([vertex[0], vertex[1] + resolution[0], vertex[2]])
            vertices_horizontal.append([vertex[0] + resolution[0], vertex[1] + resolution[0], vertex[2]])

    return vertices_horizontal


def main():
    pass


if __name__ == '__main__':
    main()
