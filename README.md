# Système Intelligent de Surveillance de Parking

Projet de synthèse du cours **Vision en Milieu Industriel** — ENSA Agadir.  
Simule un système réel de surveillance d'un parking automatisé via trois modules indépendants orchestrés par un pipeline principal (`main.py`).

> Auteur : **Nde Mba Kouetche Franklin** — 4ème année Big Data, Data Science & IA — ENSA Agadir

---

## Fonctionnalités

- **Détection des voies de circulation** à l'entrée du parking par transformée de Hough probabiliste (TP5)
- **Reconnaissance automatique de plaque d'immatriculation (LPR/OCR)** avec contrôle d'accès par liste noire (TP6)
- **Analyse de l'état des places** (libre / occupée) à partir d'une vue de dessus et d'un fichier de définition des emplacements XML (TP7)
- **Tableau de bord matplotlib** généré automatiquement (`output/dashboard.png`) avec les trois résultats côte à côte

---

## Architecture

```
[Caméra entrée]
    ├── Module 1 : Détection des voies     → modules/lane_detection.py
    └── Module 2 : Lecture de plaque LPR   → modules/lpr.py

[Caméra parking]
    └── Module 3 : État des places         → modules/parking_status.py

[main.py] → orchestre les 3 modules + tableau de bord matplotlib (layout 1×3)
```

---

## Stack technique

| Composant | Version minimale |
|---|---|
| Python | 3.10+ (syntaxe `list[str] \| None` utilisée) |
| OpenCV | `opencv-python` |
| NumPy | `numpy` |
| Matplotlib | `matplotlib` |
| Tesseract OCR | binaire externe — voir ci-dessous |
| pytesseract | `pytesseract` |

### Installation des dépendances Python

```bash
pip install opencv-python numpy matplotlib pytesseract
```

### Installation de Tesseract OCR (Windows)

1. Télécharger l'installeur depuis [UB-Mannheim/tesseract](https://github.com/UB-Mannheim/tesseract/wiki)
2. Installer (chemin par défaut : `C:\Program Files\Tesseract-OCR\tesseract.exe`)
3. Le chemin est déjà configuré dans `modules/lpr.py` :

```python
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
```

Adapter ce chemin si Tesseract est installé ailleurs.

---

## Structure du projet

```
Vision-Surveillance-Parking/
│
├── main.py                     ← Point d'entrée — orchestre les 3 modules
│
├── modules/
│   ├── lane_detection.py       ← Module 1 : détection des voies (Hough)
│   ├── lpr.py                  ← Module 2 : lecture de plaque (OCR Tesseract)
│   └── parking_status.py       ← Module 3 : état des places (binarisation adaptative)
│
├── data/
│   ├── entrance/
│   │   └── road.jpg            ← Image de la voie d'entrée (Module 1)
│   └── parking/
│       ├── cars_5.png          ← Image du véhicule à identifier (Module 2)
│       ├── lots.jpg            ← Image vue de dessus du parking (Module 3)
│       ├── lot_empty.xml       ← Définition XML des emplacements de places
│       └── lots_empty.jpg      ← Image de référence vide (calibration)
│
├── output/
│   └── dashboard.png           ← Tableau de bord généré par main.py
│
├── context.md                  ← Documentation détaillée des modules
├── _context.md                 ← Contexte projet (système IPCRA)
└── rapport.html                ← Rapport de projet (HTML)
```

---

## Utilisation

### Lancer le pipeline complet

```bash
python main.py
```

Cela exécute les trois modules en séquence, affiche le tableau de bord dans une fenêtre matplotlib et sauvegarde le résultat dans `output/dashboard.png`.

### Lancer un module individuellement

Chaque module dispose d'un bloc `__main__` et peut être exécuté seul :

```bash
# Module 1 — Détection des voies
python modules/lane_detection.py

# Module 2 — Lecture de plaque
python modules/lpr.py

# Module 3 — État des places
python modules/parking_status.py
```

---

## Configuration

Les chemins d'images et le paramètre de seuil sont définis en tête de `main.py` :

```python
ENTRANCE_ROAD  = "data/entrance/road.jpg"
ENTRANCE_CAR   = "data/parking/cars_5.png"
PARKING_LOT    = "data/parking/lots.jpg"
PARKING_SPOTS  = load_spots("data/parking/lot_empty.xml")

BLACKLIST = []  # plaques non autorisées, ex. ["98765-C-4", "43210-D-8"]
```

Le seuil de détection des places est passé à `check_parking` :

```python
status_img, free, occupied = check_parking(PARKING_LOT, PARKING_SPOTS, threshold=43.5)
```

---

## Description des modules

### Module 1 — Détection des voies (`modules/lane_detection.py`)

**Fonction exportée :** `detect_lanes(image_path: str) -> np.ndarray`

Pipeline appliqué :

1. Conversion en niveaux de gris
2. CLAHE (`clipLimit=2.0`, `tileGridSize=(8,8)`) — rehausse le contraste des marquages
3. Flou gaussien (`5×5`)
4. Détection de contours Canny (seuils `50` / `150`)
5. Masque ROI en trapèze (18 %–82 % en largeur, à partir de 62 % en hauteur)
6. Transformée de Hough probabiliste (`HoughLinesP`, `threshold=80`, `minLineLength=80`, `maxLineGap=150`)
7. Séparation gauche / droite par le signe de la pente (seuil `±0.5`)
8. Régression linéaire (`np.polyfit`) pour moyenner les segments en une droite par côté
9. Tracé : voie gauche en **vert** `(0,255,0)`, voie droite en **rouge** `(0,0,255)`, épaisseur 8 px

---

### Module 2 — Reconnaissance de plaque LPR (`modules/lpr.py`)

**Fonction exportée :** `read_plate(image_path: str, blacklist: list[str] | None = None) -> tuple[str, np.ndarray]`

Pipeline appliqué :

1. Conversion en niveaux de gris
2. Filtre bilatéral (`bilateralFilter`, d=11, sigmaColor=17, sigmaSpace=17)
3. Détection de contours Canny (seuils `100` / `200`)
4. `findContours` → tri par aire décroissante, top 10
5. `approxPolyDP` — recherche d'un contour à 4 ou 5 points (rectangle de plaque)
6. Extraction de la ROI plaque (`cv2.boundingRect`)
7. Flou gaussien (`5×5`) sur la ROI
8. OCR Tesseract (`--psm 8 --oem 3`, whitelist `A-Z0-9`)
9. Encadrement de la plaque sur l'image originale :
   - **Vert** + label `AUTORISE` si la plaque n'est pas dans la liste noire
   - **Rouge** + label `REFUSE` si la plaque est dans la liste noire

**Retour :** `(texte_plaque, image_annotée)`

---

### Module 3 — État des places (`modules/parking_status.py`)

**Fonctions exportées :**
- `load_spots(xml_path: str) -> list[tuple[int, int, int, int]]`
- `check_parking(image_path: str, spots: SpotList, threshold: int = 20) -> tuple[np.ndarray, int, int]`
- `calibrate(image_path: str, spots: SpotList) -> None` *(outil de calibration)*

**Format XML attendu (`lot_empty.xml`) :**

```xml
<parking>
  <space>
    <contour>
      <point x="..." y="..." />
      ...
    </contour>
  </space>
  ...
</parking>
```

Chaque `<contour>` est converti en bounding box axis-aligned `(x, y, w, h)` via `cv2.boundingRect`.

Pipeline `check_parking` :

1. Conversion en niveaux de gris → flou gaussien (`5×5`)
2. Binarisation adaptative (`adaptiveThreshold`, `ADAPTIVE_THRESH_MEAN_C`, `THRESH_BINARY_INV`, blockSize=11, C=2)
3. Pour chaque place : calcul du pourcentage de pixels blancs (`cv2.countNonZero / (w*h) * 100`)
   - `fill_pct < threshold` → **LIBRE** (rectangle vert)
   - `fill_pct >= threshold` → **OCCUPÉE** (rectangle rouge)
4. Compteurs affichés sur l'image (`Libres` / `Occupees`)

**Calibration du seuil** : lancer `calibrate()` avec l'image vide (`lots_empty.jpg`) pour lire les `fill%` de référence, puis choisir un `threshold` entre les valeurs vides et les valeurs occupées.

**Retour :** `(image_annotée, nb_libres, nb_occupées)`

---

## Entrées / Sorties

| Module | Entrée | Sortie |
|---|---|---|
| `detect_lanes` | `data/entrance/road.jpg` | Image BGR annotée (`np.ndarray`) |
| `read_plate` | `data/parking/cars_5.png` | `(str, np.ndarray)` — texte plaque + image annotée |
| `check_parking` | `data/parking/lots.jpg` + `lot_empty.xml` | `(np.ndarray, int, int)` — image + compteurs |
| `main.py` | Les trois images ci-dessus | `output/dashboard.png` |

---

## Auteur

**Nde Mba Kouetche Franklin**  
4ème année — Big Data, Data Science & Intelligence Artificielle  
ENSA Agadir, Maroc  
[franklinnmkf@gmail.com](mailto:franklinnmkf@gmail.com)
