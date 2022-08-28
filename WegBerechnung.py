import numpy as np
import math
from math import pi
import kreis
import csv
#import matplotlib.pyplot as plt
import os



#def plot():

   # data = np.loadtxt('Koordinaten.csv', delimiter=',')
   # print(data)
   # plt.plot(data[:, 0], data[:, 1])
   # plt.show()



# diese Methode liest den NC-Code aus einer .txt datei
def dateiLesen():
    text = open("NC_Code.txt")
    #text = open("test.txt")
    nc = text.readlines()
    text.close()
    os.remove('Koordinaten.csv')
    return nc

def dateiSchreiben(liste):
    with open('Koordinaten.csv', 'a', newline='') as csvFile:
        writer = csv.writer(csvFile)
        writer.writerows(liste)
    csvFile.close()

def dateiSchreibenString(String):
        with open('Koordinaten.csv', 'a') as csvFile:
            writer = csvFile.write(String + "\n")
        csvFile.close()


# diese Hilfsmethode verarbeitet die .txt datei indem es Backspaces aus den Zeilen entfehrnt
def split(liste):
    sp = liste.strip("\n")
    sp = sp.split(" ")
    return sp


# diese Methode berechnet eine gerade zwischen zwei Punkten und gibt die Zwischenschritte zurück
# Paremeter: liste= NC-Code, anfangsPunkt=3-dim Vektor, drehzahl,schneiden,v = Integer
def lBewegung(liste, anfangsPunkt, drehzahl, schneiden, v):
    fmax = False
    m_91 = False
    MAX = 2000
    x = None
    y = None
    z = None


    for wort in liste:
        if wort == "FMAX":
            fmax = True
        elif wort.find("F") == 0:
            v = wort.strip("F")
        if wort.find("X") == 0:
            x = wort.strip("X")
        if wort.find("Y") == 0:
            y = wort.strip("Y")
        if wort.find("Z") == 0:
            z = wort.strip("Z")
        if wort == "M91":
            m_91 = True
    if x is None:
        x = float(anfangsPunkt[0])
    if y is None:
        y = float(anfangsPunkt[1])
    if z is None:
        z = float(anfangsPunkt[2])
    if m_91:
        anfangsPunkt[2] = anfangsPunkt[2]+1000
        z = float(z)+1000

    endPunkt = np.array([float(x), float(y), float(z)])
    vektorListe = []
    f_z = 1

    if fmax and drehzahl != 0:
        f_z = MAX / (drehzahl * schneiden)
    if fmax is False and drehzahl != 0:
        f_z = float(v) / (drehzahl * schneiden)
    if drehzahl == 0:
        vektorListe.append(endPunkt)
        return [vektorListe, endPunkt, v]

    vektor = endPunkt - anfangsPunkt
    laenge = np.linalg.norm(vektor)
    schritte = laenge / f_z

    if (schritte == 0.0):
        schritte = 1
    nvektor = vektor / schritte
    if f_z > laenge:
        vektorListe.append(endPunkt)
        return [vektorListe, endPunkt, v]

    for i in range(1, int(schritte) + 1):
        wegVektor = anfangsPunkt + nvektor * i
        vektorListe.append(wegVektor)
        if schritte - i < 1 and schritte - i > 0:
            wegVektor = anfangsPunkt + nvektor * schritte
            vektorListe.append(wegVektor)

    return [vektorListe, wegVektor, v]


# 30 CC X29.2387 Y19.4175
# diese Methode gibt einen 3-dim Vektor der die Kreismitte beschreibt zurück
def kreisMittelpunkt(liste, anfangsPunkt):
    x = None
    y = None
    z = None
    for wort in liste:
        if wort.find("X") == 0:
            x = wort.strip("X")
        if wort.find("Y") == 0:
            y = wort.strip("Y")
        if wort.find("Z") == 0:
            z = wort.strip("Z")
    if x is None:
        x = float(anfangsPunkt[0])
    if y is None:
        y = float(anfangsPunkt[1])
    if z is None:
        z = float(anfangsPunkt[2])
    kreisMitte = np.array([float(x), float(y), float(z)])
    return kreisMitte


def kreisBewegung(liste, anfangsPunkt, kreisMitte, f_z):
    x = None
    y = None
    z = None
    dr_plus = None
    for wort in liste:
        if wort.find("X") == 0:
            x = wort.strip("X")
        if wort.find("Y") == 0:
            y = wort.strip("Y")
        if wort.find("Z") == 0:
            z = wort.strip("Z")
        if wort == "DR+":
            dr_plus = True
        if wort == "DR-":
            dr_plus = False
    if x is None:
        x = float(anfangsPunkt[0])
    if y is None:
        y = float(anfangsPunkt[1])
    if z is None:
        z = float(anfangsPunkt[2])
    endPunkt = np.array([float(x), float(y), float(z)])
    return kreis.circle_points(anfangsPunkt, endPunkt, kreisMitte, dr_plus, f_z)


# diese Methode list die Eigenschaften des Werkstücks ein und initialiesiert Koodinaten des Nullpunktes vom Werkstück
def initWerkstueck(liste):
    global relNullpunkt
    x = liste[-3].strip("X")
    y = liste[-2].strip("Y")
    z = liste[-1].strip("Z")
    relNullpunkt = np.array([float(x), float(y), float(z)])


def toolCall(liste):
    drehzahl = 0
    schneiden = [2, 2]
    durchmesser = [5,2]     #[5,2]
    print(liste[3])
    for stelle in liste:
        if stelle.find("S") == 0:
            drehzahl = stelle.strip("S")
    return [int(drehzahl), schneiden[int(liste[3]) - 1], durchmesser[int(liste[3]) - 1]]



def main():
    nullpunkt = np.array([0, 0, 100])
    v = 0
    drehzahl = 0
    schneiden = 2
    anfangsPunkt = np.array([-500, -420, 100])
    kreisMitte = np.array([0, 0, 0])

    for line in dateiLesen():

        zeile = split(line)

        if zeile[0] == "1":
            initWerkstueck(zeile)
        if zeile[1] == "L":
            bewegungen = lBewegung(zeile, anfangsPunkt, drehzahl, schneiden, v)
            vektorList = bewegungen[0]
            dateiSchreiben(vektorList)
            anfangsPunkt = bewegungen[1]
            v = bewegungen[2]
        if zeile[1] == "CC":
            kreisMitte = kreisMittelpunkt(zeile, anfangsPunkt)
        if zeile[1] == "C":
            f_z = float(v) / (drehzahl * schneiden)
            kreis_Weg = kreisBewegung(zeile, anfangsPunkt, kreisMitte, f_z)
            anfangsPunkt = kreis_Weg[len(kreis_Weg)-1]
            dateiSchreiben(kreis_Weg)
        if zeile[1] == "TOOL":
            array = toolCall(zeile)
            print(array)
            drehzahl = array[0]
            schneiden = array[1]
            toolcall = "Tool Durchmesser " + str(array[2])
            dateiSchreibenString(toolcall)


main()
#plot()
