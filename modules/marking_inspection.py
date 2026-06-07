# Module 4 — Inspection des marquages au sol
# Source : TP3
#
# Pipeline :
#   Image marquage référence + Image marquage à inspecter
#   → Niveaux de gris              (cv2.cvtColor)
#   → Flou gaussien                (cv2.GaussianBlur)
#   → Seuillage Otsu               (cv2.threshold + THRESH_OTSU)
#   → Détection contours           (cv2.Canny)
#   → Trouver contours             (cv2.findContours)
#   → Prendre le plus grand contour de chaque image
#   → Comparer les formes          (cv2.matchShapes → score)
#   → score < 0.1  → OK      (marquage conforme)
#   → score < 0.3  → WARNING  (usure légère)
#   → score >= 0.3 → NOK      (marquage dégradé)
#   → [Optionnel] absdiff pour visualiser les zones dégradées

import cv2
import numpy as np

VERDICT_OK = "OK"
VERDICT_WARNING = "WARNING"
VERDICT_NOK = "NOK"


def inspect_marking(ref_path: str, test_path: str) -> tuple[float, str, np.ndarray]:
    """
    Vérifie la conformité d'un marquage au sol par rapport à une référence.

    Args:
        ref_path: chemin vers l'image de référence (marquage conforme)
        test_path: chemin vers l'image à inspecter

    Returns:
        (score_similarité, verdict, image_annotée)
        verdict : "OK" | "WARNING" | "NOK"
    """
    ref = cv2.imread(ref_path)
    test = cv2.imread(test_path)
    if ref is None:
        raise FileNotFoundError(f"Image référence introuvable : {ref_path}")
    if test is None:
        raise FileNotFoundError(f"Image test introuvable : {test_path}")

    score = 0.0
    verdict = VERDICT_OK
    result_img = test.copy()

    # TODO: implémenter le pipeline TP3
    # 1. Convertir en niveaux de gris (ref + test)
    # 2. GaussianBlur (ref + test)
    # 3. Seuillage Otsu (cv2.threshold + THRESH_BINARY + THRESH_OTSU)
    # 4. Canny (ref + test)
    # 5. findContours → prendre le plus grand contour de chaque image
    # 6. matchShapes → score
    # 7. Déterminer le verdict selon les seuils
    # 8. [Optionnel] absdiff pour surligner les zones dégradées en rouge

    return score, verdict, result_img
