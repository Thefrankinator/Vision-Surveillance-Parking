# main.py — Orchestration du système de surveillance de parking

import matplotlib.pyplot as plt

from modules.lane_detection import detect_lanes
from modules.lpr import read_plate
from modules.parking_status import check_parking, load_spots

# ---------------------------------------------------------------------------
# Configuration — adapter les chemins selon les images disponibles
# ---------------------------------------------------------------------------

ENTRANCE_ROAD = "data/entrance/road.jpg"
ENTRANCE_CAR  = "data/parking/cars_5.png"
PARKING_LOT   = "data/parking/lots.jpg"
PARKING_SPOTS = load_spots("data/parking/lot_empty.xml")


BLACKLIST = []  # plaques non autorisées, ex. ["98765-C-4", "43210-D-8"]

# ---------------------------------------------------------------------------
# Exécution des modules
# ---------------------------------------------------------------------------

# Module 1 — Détection des voies
lane_img = detect_lanes(ENTRANCE_ROAD)

# Module 2 — Lecture de la plaque
plate_text, lpr_img = read_plate(ENTRANCE_CAR, blacklist=BLACKLIST)

# Module 3 — État des places
status_img, free, occupied = check_parking(PARKING_LOT, PARKING_SPOTS, threshold=43.5)

# ---------------------------------------------------------------------------
# Tableau de bord
# ---------------------------------------------------------------------------

fig, axes = plt.subplots(1, 3, figsize=(18, 6))
fig.suptitle("Tableau de bord — Surveillance de Parking", fontsize=14, fontweight="bold")

axes[0].imshow(lane_img[:, :, ::-1])
axes[0].set_title("Module 1 — Détection des voies")
axes[0].axis("off")

axes[1].imshow(lpr_img[:, :, ::-1])
axes[1].set_title(f"Module 2 — Plaque : {plate_text if plate_text else 'non détectée'}")
axes[1].axis("off")

axes[2].imshow(status_img[:, :, ::-1])
axes[2].set_title(f"Module 3 — Places : {free} libres / {occupied} occupées")
axes[2].axis("off")

plt.tight_layout()
plt.savefig("output/dashboard.png")
plt.show()
