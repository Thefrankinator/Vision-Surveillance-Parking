# main.py — Orchestration du système de surveillance de parking
#
# Lance les 4 modules et affiche le tableau de bord final.

import matplotlib.pyplot as plt

from modules.lane_detection import detect_lanes
from modules.lpr import read_plate
from modules.parking_status import check_parking
from modules.marking_inspection import inspect_marking

# ---------------------------------------------------------------------------
# Configuration — adapter les chemins selon les images disponibles
# ---------------------------------------------------------------------------

ENTRANCE_ROAD = "data/entrance/road.jpg"
ENTRANCE_CAR  = "data/entrance/car.jpg"
PARKING_LOT   = "data/parking/lot.jpg"
PARKING_MARK  = "data/parking/marking_test.jpg"
REF_MARKING   = "data/reference/marking_ref.jpg"

# Coordonnées des places : liste de (x, y, w, h)
PARKING_SPOTS = [
    # TODO: définir les coordonnées réelles selon l'image utilisée
    # Exemple : (50, 100, 60, 120), (120, 100, 60, 120), ...
]

WHITELIST = []  # plaques autorisées, ex. ["12345-A-6", "67890-B-2"]

# ---------------------------------------------------------------------------
# Exécution des modules
# ---------------------------------------------------------------------------

# Module 1 — Détection des voies
lane_img = detect_lanes(ENTRANCE_ROAD)

# Module 2 — Lecture de la plaque
plate_text, lpr_img = read_plate(ENTRANCE_CAR, whitelist=WHITELIST)

# Module 3 — État des places
status_img, free, occupied = check_parking(PARKING_LOT, PARKING_SPOTS)

# Module 4 — Inspection des marquages
score, verdict, marking_img = inspect_marking(REF_MARKING, PARKING_MARK)

# ---------------------------------------------------------------------------
# Tableau de bord
# ---------------------------------------------------------------------------

fig, axes = plt.subplots(2, 2, figsize=(14, 10))
fig.suptitle("Tableau de bord — Surveillance de Parking", fontsize=14, fontweight="bold")

axes[0, 0].imshow(lane_img[:, :, ::-1])
axes[0, 0].set_title("Module 1 — Détection des voies")
axes[0, 0].axis("off")

axes[0, 1].imshow(lpr_img[:, :, ::-1])
axes[0, 1].set_title(f"Module 2 — Plaque : {plate_text if plate_text else 'non détectée'}")
axes[0, 1].axis("off")

axes[1, 0].imshow(status_img[:, :, ::-1])
axes[1, 0].set_title(f"Module 3 — Places : {free} libres / {occupied} occupées")
axes[1, 0].axis("off")

axes[1, 1].imshow(marking_img[:, :, ::-1])
axes[1, 1].set_title(f"Module 4 — Marquages : {verdict} (score={score:.3f})")
axes[1, 1].axis("off")

plt.tight_layout()
plt.savefig("output/dashboard.png")
plt.show()
