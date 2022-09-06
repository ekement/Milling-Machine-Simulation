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

    liste = split_nc_code_into_commands(head[0]), split_nc_code_into_commands(head[1])
    koordinaten = []
    for eintrag in liste:
        x = eintrag[-3].strip("X")
        y = eintrag[-2].strip("Y")
        z = eintrag[-1].strip("Z")
        koordinaten.append(np.array([float(x), float(y), float(z)]))

    dimension = koordinaten[1] - koordinaten[0]
    origin_werk = koordinaten[0]
    origin_werk[2] = origin_werk[2] - dimension[2]
    cell_count = [int(dimension[0]) / resolution[0], int(dimension[1]) / resolution[1]]

    return [resolution, dimension, origin_werk, cell_count]


def init_Heightfield(resolution, dimension, origin_werk, cell_count):
    heightfield = dimension[2] * np.ones([int(cell_count[1]), int(cell_count[0])])
    # vertices = berechne_Vertices(cell_count[0], cell_count[1], resolution, origin_werk, heightfield)
    # render(vertices)
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
def definiere_impliziten_Kreis(heightfield, center_koo, radius, resolution, origin):
    # mittelpunkt ist ein Punkt im Hoehenfeld
    mittelpunkt = transform_coordinates_to_point(resolution, origin, center_koo[0], center_koo[1])

    # markierte_reichweite ist der Radius im Hoehenfeld
    markierte_reichweite = int(radius / resolution[1])

    eckpunkt_oben = [mittelpunkt[0] + markierte_reichweite, mittelpunkt[1] + markierte_reichweite]
    eckpunkt_unten = [mittelpunkt[0] - markierte_reichweite, mittelpunkt[1] - markierte_reichweite]

    for x in range(eckpunkt_unten[0], eckpunkt_oben[0] + 1):
        for y in range(eckpunkt_unten[1], eckpunkt_oben[1] + 1):
            if x > len(heightfield[0]) - 1 or y > len(heightfield) - 1 or x < 0 or y < 0:
                continue
            else:
                endpunkt = np.array(wo_ist_Punkt(resolution, origin, x, y, center_koo[2]))
                vektor = endpunkt - center_koo
                vektor_laenge = np.linalg.norm(vektor)

                if vektor_laenge <= radius:

                    if heightfield[y][x] + origin[2] > center_koo[2]:
                        heightfield[y][x] = center_koo[2] - origin[2]
    return heightfield


def bearbeite_Werkstueck(coordinates_file):
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
            zustand = 1

        if values[0] == 'Mitte':
            zustand = len(center_all) // 4

        if values[0] == 'Ende':
            zustand = len(center_all)

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

    center_all = center_all[:zustand]
    parameter = get_parameter()
    resolution = parameter[0]
    dimension = parameter[1]
    origin = parameter[2]
    cell_count = parameter[3]
    heightfield = init_Heightfield(resolution, dimension, origin, cell_count)

    kreis_für_kraftmethode = milling_force_diagram.definiere_kreis(diameter)
    forces = []
    for current_center in center_all:
        if current_center[0] == "T":
            diameter = current_center[-2]
            kreis_für_kraftmethode = milling_force_diagram.definiere_kreis(diameter)
            continue

        current_center = np.array(current_center.split(","))
        current_center = current_center.astype(float)

        radius = float(diameter) / 2

        force = milling_force_diagram.calculate_force(current_center, kreis_für_kraftmethode, heightfield, resolution, origin, dimension, material, mc)
        forces.append(force)

        heightfield = definiere_impliziten_Kreis(heightfield, current_center, radius, resolution, origin)

    print("Heightfield fertig")

    print("Berechne Vertices")
    vertices = berechne_Vertices(cell_count[0], cell_count[1], resolution, origin, heightfield)

    print("Berechne Triangles")
    vertices_triangles = [np.array(vertices_horizontal_triangle(vertices, resolution, dimension)),
                          np.array(vertices_vertical_triangle(vertices, heightfield, resolution, dimension))]
    print("Renderer wird gestartet")
    # renderer2.pygameI(vertices_triangles)

    render(vertices_triangles)
    if plot:
        milling_force_diagram.plot(forces)




@jit(nopython=True)
def transform_coordinates_to_point(res, origin, kooX, kooY):
    x = int((kooX - origin[0]) / res[0])
    y = int((kooY - origin[1]) / res[1])
    return [x, y]


# Punkt zu Koordinate
@jit(nopython=True)
def wo_ist_Punkt(res, origin, kooX, kooY, hoehe):
    x = origin[0] + kooX * res[0]
    y = origin[1] + kooY * res[1]
    return [x, y, hoehe]


@jit(nopython=True)
def berechne_Vertices(punkte_breite, punkte_tiefe, resolution, origin, heightfield):
    vertices_boden = []
    vertices_decke = []
    for x in range(int(punkte_breite)):
        for y in range(int(punkte_tiefe)):
            vektor = wo_ist_Punkt(resolution, origin, x, y, origin[2])
            vertices_boden.append(vektor)
            vertices_decke.append([vektor[0], vektor[1], heightfield[y][x] + origin[2]])

    return [np.array(vertices_boden), np.array(vertices_decke)]



# @jit(nopython = True)
def vertices_vertical_triangle(vertices, heightfield, resolution, dimension):
    boden = vertices[0][0][2]
    origin = get_parameter()[2]

    vertices_vertical = []

    for vertex in vertices[1]:
        if vertex[0] >= dimension[0] or vertex[1] >= dimension[1]:
            continue

        else:
            # Seite vorne
            position = transform_coordinates_to_point(resolution, origin, kooX=vertex[0], kooY=vertex[1])

            if position[1] == 0 or heightfield[position[1]][position[0]] > heightfield[position[1] - 1][position[0]]:
                vertices_vertical.append([vertex[0], vertex[1], boden])
                vertices_vertical.append([vertex[0] + resolution[0], vertex[1], vertex[2]])
                vertices_vertical.append([vertex[0], vertex[1], vertex[2]])

                vertices_vertical.append([vertex[0], vertex[1], boden])
                vertices_vertical.append([vertex[0] + resolution[0], vertex[1], vertex[2]])
                vertices_vertical.append([vertex[0] + resolution[0], vertex[1], boden])

            # Seite links
            if position[0] == 0 or heightfield[position[1]][position[0]] > heightfield[position[1]][position[0] - 1]:
                vertices_vertical.append([vertex[0], vertex[1], boden])
                vertices_vertical.append([vertex[0], vertex[1] + resolution[1], vertex[2]])
                vertices_vertical.append([vertex[0], vertex[1], vertex[2]])

                vertices_vertical.append([vertex[0], vertex[1], boden])
                vertices_vertical.append([vertex[0], vertex[1] + resolution[1], vertex[2]])
                vertices_vertical.append([vertex[0], vertex[1] + resolution[1], boden])

            # Seite rechts
            if position[0] == len(heightfield[0]) - 1 or heightfield[position[1]][position[0]] > \
                    heightfield[position[1]][position[0] + 1]:
                vertices_vertical.append([vertex[0] + resolution[0], vertex[1], boden])
                vertices_vertical.append([vertex[0] + resolution[0], vertex[1], vertex[2]])
                vertices_vertical.append([vertex[0] + resolution[0], vertex[1] + resolution[1], vertex[2]])

                vertices_vertical.append([vertex[0] + resolution[0], vertex[1] + resolution[1], boden])
                vertices_vertical.append([vertex[0] + resolution[0], vertex[1] + resolution[1], vertex[2]])
                vertices_vertical.append([vertex[0] + resolution[0], vertex[1], boden])

            # Seite hinten
            if position[1] == len(heightfield) - 1 or \
                    heightfield[position[1]][position[0]] > \
                    heightfield[position[1] + 1][position[0]]:
                vertices_vertical.append([vertex[0], vertex[1] + resolution[1], boden])
                vertices_vertical.append([vertex[0] + resolution[0], vertex[1] + resolution[1], vertex[2]])
                vertices_vertical.append([vertex[0], vertex[1] + resolution[1], vertex[2]])

                vertices_vertical.append([vertex[0], vertex[1] + resolution[1], boden])
                vertices_vertical.append([vertex[0] + resolution[0], vertex[1] + resolution[1], vertex[2]])
                vertices_vertical.append([vertex[0] + resolution[0], vertex[1] + resolution[1], boden])

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
