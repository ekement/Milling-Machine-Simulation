import init_heightfield
import path_calculation
import milling_force_diagram


def main():
    nc_code_file = "NC_Code.txt"
    coordinates_file = "coordinates.csv"
    print("Starte Berechnung der Koordinaten für die Darstellung des Werkstücks.")
    path_calculation.calculate_coordinates(nc_code_file, coordinates_file)
    print("Berechnung der Koordinaten beendet.")

    print("Bitte Eingaben tätigen.")
    init_heightfield.process_work_piece(coordinates_file)
    print("Darstellung beendet")

if __name__ == '__main__':
    main()

