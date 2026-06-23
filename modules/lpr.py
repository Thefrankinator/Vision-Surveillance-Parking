
import cv2
import numpy as np
import pytesseract


pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"


def read_plate(image_path: str, blacklist: list[str] | None = None) -> tuple[str, np.ndarray]:
    """
    Lit la plaque d'immatriculation d'un véhicule.

    Args:
        image_path: chemin vers l'image du véhicule
        blacklist: liste de plaques  non autorisées (optionnel)

    Returns:
        (texte_plaque, image_annotée)
    """
    img = cv2.imread(image_path)
    if img is None:
        raise FileNotFoundError(f"Image introuvable : {image_path}")

    plate_text = ""

   
    # 1. Convertir en niveaux de gris
    img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    
    # 2. Canny pour détecter les contours
    img_blur  = cv2.bilateralFilter(img_gray, 11, 17, 17)
    img_canny = cv2.Canny(img_blur, 100, 200)
    # 3. findContours → trier par aire (top 10)

    contours, _ = cv2.findContours(img_canny, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
    contours = sorted(contours, key=cv2.contourArea, reverse=True)[:10]
    
    # 4. approxPolyDP → chercher un quadrilatère (len == 4)
    plate_contour = None
    for contour in contours:
        approx = cv2.approxPolyDP(contour, 0.04 * cv2.arcLength(contour, True), True)
        if len(approx) == 5 or len(approx) == 4:  # tolérance pour les plaques légèrement arrondies
            plate_contour = approx
            break
        
    for c in contours:
        epsilon = 0.04 * cv2.arcLength(c, True)
        approx = cv2.approxPolyDP(c, epsilon, True)
    
    # 5. Extraire la ROI de la plaque
    if plate_contour is not None:
        x, y, w, h = cv2.boundingRect(plate_contour)
        img_plate = img[y:y+h, x:x+w]       
    else:
        img_plate = img_gray
        
    # 6. Prétraitement : GaussianBlur + threshold pour améliorer la lisibilité de la plaque
    
    img_plate = cv2.GaussianBlur(img_plate, (5, 5), 0)
    #_, img_plate = cv2.threshold(cv2.cvtColor(img_plate, cv2.COLOR_BGR2GRAY), 0, 255,cv2.THRESH_OTSU)
 
    # 7. pytesseract.image_to_string
    plate_text = pytesseract.image_to_string(img_plate, config='--psm 8 --oem 3 -c tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789')
    plate_text = plate_text.strip().replace(" ", "").replace("\n", "")
    
    # 8. Encadrer la plaque en vert sur l'image originale

    if blacklist is not None:
        not_access = plate_text in blacklist
        label = "AUTORISE" if not not_access else "REFUSE"
        color = (0, 255, 0) if not not_access else (0, 0, 255)
        cv2.putText(img, label, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, color, 2)
        cv2.rectangle(img, (x, y), (x + w, y + h), color, 2)
    else:
        cv2.rectangle(img, (x, y), (x + w, y + h), (0, 255, 0), 2)  

        

    return plate_text, img


if __name__ == "__main__":
    
    # Exemple d'utilisation
    plaque, img_annotée = read_plate("data/parking/cars_2.png", blacklist=["ALR466"])
    print(f"Plaque détectée : {plaque}")
    cv2.imshow("Plaque annotée", img_annotée)
    cv2.waitKey(0)
    cv2.destroyAllWindows()