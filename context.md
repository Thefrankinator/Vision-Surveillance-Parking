# Projet Synthèse — Système Intelligent de Surveillance de Parking

## Contexte

Ce projet regroupe les notions abordées dans les TP3, TP5, TP6 et TP7 du cours de Vision Industrielle.
Il simule un système réel de surveillance d'un parking automatisé, composé de 4 modules indépendants
qui communiquent entre eux via un pipeline principal.

---

## Scénario général

```
[Caméra entrée]
    └── Module 1 : Détection des voies (TP5)
    └── Module 2 : Lecture de la plaque LPR (TP6)

[Caméra parking]
    └── Module 3 : État des places (TP7)

[Caméra sol]
    └── Module 4 : Inspection des marquages (TP3)

[main.py]
    └── Orchestre les 4 modules et affiche le tableau de bord final
```

---

## Structure des fichiers

```
Projet_Synthese/
│
├── context.md                  ← ce fichier
│
├── main.py                     ← point d'entrée, orchestre les 4 modules
│
├── modules/
│   ├── lane_detection.py       ← Module 1 (TP5)
│   ├── lpr.py                  ← Module 2 (TP6)
│   ├── parking_status.py       ← Module 3 (TP7)
│   └── marking_inspection.py   ← Module 4 (TP3)
│
├── data/
│   ├── entrance/               ← images de l'entrée du parking (voies + voitures)
│   ├── parking/                ← images vue de dessus du parking
│   └── reference/              ← marquages de référence (conformes) pour TP3
│
└── output/                     ← images annotées générées par chaque module
```

---

## Module 1 — Détection des voies `lane_detection.py`

**Source : TP5**

### Objectif
Détecter les voies de circulation à l'entrée du parking pour vérifier que le véhicule
est bien dans sa voie.

### Pipeline
```
Image entrée
    → Niveaux de gris         (cv2.cvtColor)
    → Flou gaussien           (cv2.GaussianBlur)
    → Détection contours      (cv2.Canny)
    → Masque ROI trapèze      (cv2.fillPoly + cv2.bitwise_and)
    → Hough probabiliste      (cv2.HoughLinesP)
    → Séparation gauche/droite (signe de la pente)
    → Moyennage des segments  → une ligne gauche + une ligne droite
    → Dessin sur l'image      (cv2.line)
```

### Fonctions clés OpenCV
- `cv2.GaussianBlur`, `cv2.Canny`
- `cv2.fillPoly`, `cv2.bitwise_and`
- `cv2.HoughLinesP`

### Sortie
Image annotée avec les deux lignes de voie (vert = dans la voie, rouge = hors voie).

---

## Module 2 — Reconnaissance de plaque `lpr.py`

**Source : TP6**

### Objectif
Lire automatiquement la plaque d'immatriculation d'un véhicule à l'entrée du parking.

### Pipeline
```
Image voiture
    → Niveaux de gris              (cv2.cvtColor)
    → Détection des contours       (cv2.Canny)
    → Trouver tous les contours    (cv2.findContours)
    → Trier par aire (top 10)      (sorted + cv2.contourArea)
    → Chercher un rectangle        (cv2.approxPolyDP, len == 4)
    → Extraire la ROI plaque       (découpage dans l'image originale)
    → Prétraitement OCR            (GaussianBlur + threshold)
    → OCR Tesseract                (pytesseract.image_to_string)
    → Retourner le texte lu
```

### Fonctions clés OpenCV
- `cv2.Canny`, `cv2.findContours`
- `cv2.approxPolyDP`, `cv2.contourArea`
- `pytesseract.image_to_string`

### Sortie
- Plaque encadrée en vert sur l'image
- Texte lu affiché (ex : `12345-A-6`)
- Décision : accès autorisé / non autorisé (si liste blanche définie)

---

## Module 3 — État des places `parking_status.py`

**Source : TP7**

### Objectif
Analyser une image de parking (vue de dessus) et détecter pour chaque place
si elle est libre ou occupée.

### Pipeline
```
Image parking (vue de dessus)
    → Niveaux de gris              (cv2.cvtColor)
    → Flou gaussien                (cv2.GaussianBlur)
    → Binarisation adaptative      (cv2.adaptiveThreshold)
    → Pour chaque place (ROI) :
        → Découper la zone         (image[y:y+h, x:x+w])
        → Compter les pixels blancs (cv2.countNonZero)
        → count < seuil → LIBRE
        → count >= seuil → OCCUPÉE
    → Dessiner rectangles verts/rouges
    → Afficher compteur total libre / occupé
```

### Fonctions clés OpenCV
- `cv2.GaussianBlur`, `cv2.adaptiveThreshold`
- `cv2.countNonZero`
- `cv2.rectangle`, `cv2.putText`

### Sortie
Image annotée : rectangles verts (libres), rouges (occupées) + compteur.

---

## Module 4 — Inspection des marquages `marking_inspection.py`

**Source : TP3**

### Objectif
Vérifier si les marquages au sol du parking (lignes de places, zébras, flèches)
sont conformes ou dégradés, en les comparant à un marquage de référence.

### Pipeline
```
Image marquage référence + Image marquage à inspecter
    → Niveaux de gris              (cv2.cvtColor)
    → Flou gaussien                (cv2.GaussianBlur)
    → Seuillage Otsu               (cv2.threshold + THRESH_OTSU)
    → Détection contours           (cv2.Canny)
    → Trouver contours             (cv2.findContours)
    → Prendre le plus grand contour de chaque image
    → Comparer les formes          (cv2.matchShapes → score)
    → score < 0.1  → OK  (marquage conforme)
    → score < 0.3  → WARNING (usure légère)
    → score >= 0.3 → NOK (marquage dégradé)
    → [Optionnel] absdiff pour visualiser les zones dégradées
```

### Fonctions clés OpenCV
- `cv2.threshold` (Otsu), `cv2.Canny`, `cv2.findContours`
- `cv2.matchShapes` (Moments de Hu)
- `cv2.absdiff`

### Sortie
- Score de similarité affiché
- Verdict : OK / WARNING / NOK
- [Optionnel] zones dégradées surlignées en rouge

---

## `main.py` — Orchestration

Le script principal charge les images, appelle les 4 modules et affiche un tableau
de bord récapitulatif avec `matplotlib`.

```python
# Pseudo-code du main.py

from modules.lane_detection      import detect_lanes
from modules.lpr                 import read_plate
from modules.parking_status      import check_parking
from modules.marking_inspection  import inspect_marking

# Module 1
lane_img = detect_lanes("data/entrance/road.jpg")

# Module 2
plate_text, lpr_img = read_plate("data/entrance/car.jpg")

# Module 3
status_img, free, occupied = check_parking("data/parking/lot.jpg", spots)

# Module 4
score, verdict, marking_img = inspect_marking(
    "data/reference/marking_ref.jpg",
    "data/parking/marking_test.jpg"
)

# Affichage tableau de bord
plt.subplot(2,2,1) → lane_img
plt.subplot(2,2,2) → lpr_img  + plate_text
plt.subplot(2,2,3) → status_img + f"{free} libres / {occupied} occupées"
plt.subplot(2,2,4) → marking_img + verdict
```

---

## Notions couvertes par module

| Notion | M1 Lane | M2 LPR | M3 Parking | M4 Marquage |
|---|:---:|:---:|:---:|:---:|
| Prétraitement (gris, flou) | X | X | X | X |
| Seuillage (Otsu, adaptatif) | | X | X | X |
| Détection contours (Canny) | X | X | | X |
| findContours + tri | | X | | X |
| ROI (masque / découpage) | X | X | X | |
| Transformée de Hough | X | | | |
| matchShapes (Moments de Hu) | | | | X |
| approxPolyDP (forme rectangle) | | X | | |
| countNonZero (comptage pixels) | | | X | |
| absdiff (différence pixel) | | | | X |
| Décision automatique | X | X | X | X |
| OCR (Tesseract) | | X | | |

---

## Dépendances

```bash
pip install opencv-python numpy matplotlib pytesseract
```

Tesseract doit également être installé séparément :
- Windows : https://github.com/UB-Mannheim/tesseract/wiki
- Puis configurer : `pytesseract.pytesseract.tesseract_cmd = r"C:\...\tesseract.exe"`
