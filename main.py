import initHeigtfield
import WegBerechnung
import milling_force_diagram


def main():
    nc_code_file = "NC_Code.txt"
    coordinates_file = "coordinates.csv"
    WegBerechnung.calculate_coordinates(nc_code_file, coordinates_file)
    initHeigtfield.process_work_piece(coordinates_file)


if __name__ == '__main__':
    main()

