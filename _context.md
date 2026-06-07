# Vision — Surveillance de Parking (Mini-projet)

## Description

Projet synthèse du cours de Vision en Milieu Industriel.
Simule un système réel de surveillance d'un parking automatisé via 4 modules indépendants orchestrés par un pipeline principal.

Couvre les notions des TP3, TP5, TP6 et TP7.

## Statut

- **Phase** : initialisation
- **Lien exam** : Vision en Milieu Industriel — 02/06/2026 (Chaouki)
- **Lien révision** : [[planning]]

## Architecture

```
[Caméra entrée]
    └── Module 1 : Détection des voies     (TP5) → lane_detection.py
    └── Module 2 : Lecture plaque LPR      (TP6) → lpr.py

[Caméra parking]
    └── Module 3 : État des places         (TP7) → parking_status.py

[Caméra sol]
    └── Module 4 : Inspection des marquages(TP3) → marking_inspection.py

[main.py] → orchestre les 4 modules + tableau de bord matplotlib
```

## Modules

| Fichier | Source | Rôle |
|---|---|---|
| `modules/lane_detection.py` | TP5 | Détection des voies (Hough) |
| `modules/lpr.py` | TP6 | Lecture plaque immatriculation (OCR Tesseract) |
| `modules/parking_status.py` | TP7 | État libre/occupé des places |
| `modules/marking_inspection.py` | TP3 | Inspection conformité marquages au sol |
| `main.py` | — | Orchestration + tableau de bord |

## Données

| Dossier | Contenu |
|---|---|
| `data/entrance/` | Images entrée parking (voies + voitures) |
| `data/parking/` | Images vue de dessus du parking |
| `data/reference/` | Marquages de référence conformes (Module 4) |
| `output/` | Images annotées générées par chaque module |

## Stack

```bash
pip install opencv-python numpy matplotlib pytesseract
```

Tesseract : installer séparément (Windows : UB-Mannheim), puis :
```python
pytesseract.pytesseract.tesseract_cmd = r"C:\...\tesseract.exe"
```

## Décisions

- Architecture modulaire : chaque module est indépendant et testable seul.
- `main.py` charge les images, appelle les 4 modules, affiche le dashboard matplotlib.
- Les sorties de chaque module sont sauvegardées dans `output/`.
