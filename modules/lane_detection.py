
import cv2
import numpy as np


def _moyenne_ligne(segments: list, y_top: int, y_bottom: int):
    """Réduit un groupe de segments à une seule droite par régression linéaire."""
    if not segments:
        return None
    xs, ys = [], []
    for x1, y1, x2, y2 in segments:
        xs += [x1, x2]
        ys += [y1, y2]
    a, b = np.polyfit(ys, xs, 1)  
    return (int(a * y_bottom + b), y_bottom, int(a * y_top + b), y_top)


def detect_lanes(image_path: str) -> np.ndarray:
    """
    Détecte les voies de circulation sur une image d'entrée de parking.

    Args:
        image_path: chemin vers l'image d'entrée

    Returns:
        Image annotée avec les lignes de voie
    """
    img = cv2.imread(image_path)
    if img is None:
        raise FileNotFoundError(f"Image introuvable : {image_path}")


    # 1. Niveaux de gris + CLAHE — rehausse localement le contraste des marquages
    #    faibles (jaune/rouge sur béton gris sous éclairage fluorescent)
    img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    img_clahe = clahe.apply(img_gray)
    
    # 2. Appliquer GaussianBlur
    img_blur = cv2.GaussianBlur(img_clahe, (5, 5), 0)
    
    # 3. Détection de contours avec Canny
    img_canny = cv2.Canny(img_blur, 50, 150)
    
    # 4. Masque ROI en forme de trapèze
    h, w = img_canny.shape
    polygones = np.array([
        [int(w * 0.18), h],
        [int(w * 0.82), h],
        [int(w * 0.65), int(h * 0.62)],
        [int(w * 0.35), int(h * 0.62)],
    ], dtype=np.int32)
    mask = np.zeros_like(img_canny)
    cv2.fillPoly(mask, [polygones], 255)
    img_roi = cv2.bitwise_and(img_canny, mask)
    
    # 5. HoughLinesP
    lines = cv2.HoughLinesP(img_roi, 1, np.pi / 180, threshold=80, minLineLength=80, maxLineGap=150)
    
    # 6. Séparer les lignes gauche/droite par le signe de la pente
    
    left_lines = []
    right_lines = []
    if lines is not None:  
        for line in lines:
            x1, y1, x2, y2 = line[0]
            if x2 - x1 == 0:  
                continue
            slope = (y2 - y1) / (x2 - x1)
            if slope < -0.5:  # seuil pour les lignes gauche
                left_lines.append(line[0])
            elif slope > 0.5:  # seuil pour les lignes droite
                right_lines.append(line[0])
        
    
    # 7. Moyenner et dessiner
    y_top = int(h * 0.58) 
    img_result = img.copy()
    for segments, color in [
        (left_lines,  (0, 255, 0)),   # vert  — voie gauche
        (right_lines, (0, 0, 255)),   # rouge — voie droite
    ]:
        ligne = _moyenne_ligne(segments, y_top, h)
        if ligne is not None:
            cv2.line(img_result, (ligne[0], ligne[1]), (ligne[2], ligne[3]), color, 8)

    return img_result


if __name__ == "__main__":
    img = detect_lanes("data/entrance/road.jpg")
    cv2.namedWindow("Detection des voies", cv2.WINDOW_NORMAL)
    cv2.imshow("Detection des voies", img)
    cv2.waitKey(0)
    cv2.destroyAllWindows()
