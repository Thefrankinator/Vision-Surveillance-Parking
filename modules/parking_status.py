# Module 3 — État des places de parking
# Source : TP7
#
# Pipeline :
#   Image parking (vue de dessus)
#   → Niveaux de gris              (cv2.cvtColor)
#   → Flou gaussien                (cv2.GaussianBlur)
#   → Binarisation adaptative      (cv2.adaptiveThreshold)
#   → Pour chaque place (ROI) :
#       → Découper la zone         (image[y:y+h, x:x+w])
#       → Compter les pixels blancs (cv2.countNonZero)
#       → count < seuil → LIBRE
#       → count >= seuil → OCCUPÉE
#   → Dessiner rectangles verts/rouges
#   → Afficher compteur total libre / occupé

import cv2
import numpy as np
import xml.etree.ElementTree as ET

# Format d'une place : (x, y, w, h)
SpotList = list[tuple[int, int, int, int]]


def load_spots(xml_path: str) -> SpotList:
    """
    Charge les emplacements des places de parking depuis un fichier XML (format lot.xml).

    Chaque <contour> est converti en bounding box axis-aligned (x, y, w, h).
    """
    tree = ET.parse(xml_path)
    root = tree.getroot()
    spots = []
    for space in root.findall("space"):
        pts = np.array(
            [(int(p.get("x")), int(p.get("y"))) for p in space.find("contour").findall("point")],
            dtype=np.int32,
        )
        x, y, w, h = cv2.boundingRect(pts)
        spots.append((x, y, w, h))
    return spots


def _binarize(image_path: str) -> np.ndarray:
    """Applique le pipeline gray → blur → adaptiveThreshold."""
    img = cv2.imread(image_path)
    if img is None:
        raise FileNotFoundError(f"Image introuvable : {image_path}")
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray, (5, 5), 0)
    return cv2.adaptiveThreshold(blur, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY_INV, 11, 2)


def calibrate(image_path: str, spots: SpotList) -> None:
    """
    Affiche le pourcentage de pixels blancs pour chaque place sur une image de référence.
    Utiliser avec l'image vide pour trouver le bon threshold.
    """
    binary = _binarize(image_path)
    img = cv2.imread(image_path)
    values = []
    for (x, y, w, h) in spots:
        roi = binary[y:y+h, x:x+w]
        fill_pct = cv2.countNonZero(roi) / (w * h) * 100
        values.append(fill_pct)
        label = f"{fill_pct:.0f}%"
        cv2.rectangle(img, (x, y), (x + w, y + h), (255, 165, 0), 2)
        cv2.putText(img, label, (x + 2, y + h - 4), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 165, 0), 1)

    print(f"fill% — min: {min(values):.1f}  max: {max(values):.1f}  "
          f"median: {np.median(values):.1f}")
    print("Valeurs par place :", [f"{v:.1f}" for v in values])

    cv2.imshow("Calibration", img)
    cv2.waitKey(0)
    cv2.destroyAllWindows()


def check_parking(image_path: str, spots: SpotList, threshold: int = 20) -> tuple[np.ndarray, int, int]:
    """
    Analyse l'état (libre/occupé) de chaque place de parking.

    Args:
        image_path: chemin vers l'image vue de dessus
        spots: liste de tuples (x, y, w, h) définissant chaque place
        threshold: pourcentage max de pixels blancs pour qu'une place soit libre (0-100)

    Returns:
        (image_annotée, nb_libres, nb_occupées)
    """
    img = cv2.imread(image_path)
    if img is None:
        raise FileNotFoundError(f"Image introuvable : {image_path}")

    binary = _binarize(image_path)
    free = 0
    occupied = 0

    for (x, y, w, h) in spots:
        roi = binary[y:y+h, x:x+w]
        fill_pct = cv2.countNonZero(roi) / (w * h) * 100
        if fill_pct < threshold:
            free += 1
            color = (0, 255, 0)
        else:
            occupied += 1
            color = (0, 0, 255)
        cv2.rectangle(img, (x, y), (x + w, y + h), color, 2)

    cv2.putText(img, f"Libres: {free}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
    cv2.putText(img, f"Occupees: {occupied}", (10, 70), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

    return img, free, occupied


if __name__ == "__main__":
    spots = load_spots("data/parking/lot_empty.xml")

    # Etape 1 : lancer calibrate() avec l'image VIDE pour lire les fill% de référence,
    # puis choisir un threshold entre les valeurs vides et les valeurs occupées.
    #calibrate("data/parking/lots_empty.jpg", spots)

    img, free, occupied = check_parking("data/parking/lots.jpg", spots, threshold=41    )
    print(f"Places libres: {free}, Places occupées: {occupied}")
    cv2.imshow("Parking Status", img)
    cv2.waitKey(0)
    cv2.destroyAllWindows()
