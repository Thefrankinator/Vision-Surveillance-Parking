# Données — Système de Surveillance de Parking

Ce dossier contient les images utilisées par les 4 modules du projet.
Voici exactement quoi télécharger, où, et comment nommer chaque fichier.

---

## Structure attendue

```
data/
├── entrance/
│   ├── road.jpg          ← Module 1 : route avec voies visibles
│   └── car.jpg           ← Module 2 : véhicule avec plaque lisible
├── parking/
│   ├── lot.jpg           ← Module 3 : parking vue de dessus
│   └── marking_test.jpg  ← Module 4 : marquage à inspecter
└── reference/
    └── marking_ref.jpg   ← Module 4 : marquage de référence (conforme)
```

---

## Module 1 — `entrance/road.jpg`

**Besoin** : photo d'une route ou d'une entrée de parking avec des voies bien délimitées.
HoughLinesP détecte les lignes blanches/jaunes au sol.

| Source                    | Comment l'obtenir                                                          |
| ------------------------- | -------------------------------------------------------------------------- |
| **Unsplash** (recommandé) | unsplash.com → rechercher *"parking entrance road"* → télécharger en HD    |
| **Kaggle TuSimple**       | Kaggle → *"TuSimple Lane Detection"* → prendre 1 image du dossier `clips/` |
| **KITTI Road**            | cvlibs.net → Datasets → Road/Lane → télécharger 1 image de `image_2/`      |

**Conseil** : choisir une image avec des lignes bien contrastées et un angle de caméra en légère plongée.

---

## Module 2 — `entrance/car.jpg`

**Besoin** : photo d'un véhicule avec la plaque d'immatriculation lisible et bien cadrée.

| Source                             | Comment l'obtenir                                                                                                          |
| ---------------------------------- | -------------------------------------------------------------------------------------------------------------------------- |
| **Roboflow Universe** (recommandé) | universe.roboflow.com → rechercher *"license plate detection"* → choisir un dataset → *Download* → format *JPEG* → 1 image |
| **Kaggle Car Plate**               | Kaggle → *"Car License Plate Detection"* → dossier `images/` → prendre 1 image                                             |
| **UFPR-ALPR**                      | Kaggle → *"UFPR-ALPR dataset"* → dossier `testing/` → 1 image                                                              |

**Conseil** : préférer une image où la plaque est frontale, bien éclairée, sans reflet.

---

## Module 3 — `parking/lot.jpg`

**Besoin** : photo de parking vue de dessus avec des places clairement délimitées,
certaines libres (asphalte visible) et d'autres occupées (voiture présente).

| Source                           | Comment l'obtenir                                                                                    |
| -------------------------------- | ---------------------------------------------------------------------------------------------------- |
| **PKLot Dataset** ⭐ (recommandé) | Kaggle → *"PKLot Parking Lot Dataset"* → dossier `PUCPR/Cloudy/2012-09-12/` → prendre 1 image `.jpg` |
| **CNRPark**                      | GitHub → *fabiocarrara/deep-parking* → dossier `CNRPark/` → 1 image                                  |
| **Kaggle Parking Occupancy**     | Kaggle → *"Parking Space Occupancy Detection"* → dossier `test/` → 1 image                           |

**Conseil** : avec PKLot, le fichier XML associé à l'image donne les coordonnées exactes de chaque place —
pratique pour remplir `PARKING_SPOTS` dans `main.py`.

---

## Module 4 — `reference/marking_ref.jpg` et `parking/marking_test.jpg`

**Besoin** : 2 images du même type de marquage au sol (ligne de place, zébra, flèche) :
- `marking_ref.jpg` : marquage **conforme**, net, bien visible
- `marking_test.jpg` : marquage **dégradé**, usé ou partiellement effacé

| Source                               | Comment l'obtenir                                                                   |
| ------------------------------------ | ----------------------------------------------------------------------------------- |
| **Photo personnelle** ⭐ (recommandé) | Prendre 2 photos dans un parking réel : 1 marquage neuf + 1 marquage usé            |
| **Google Street View**               | maps.google.com → mode vue de rue → parking → capture d'écran (2 angles différents) |
| **Unsplash / Pexels**                | unsplash.com → *"parking lot markings"* → choisir 2 images comparables              |

**Conseil** : `matchShapes` compare les contours — plus les deux images représentent
le **même type** de marquage, plus le résultat est interprétable.
Une photo perso donne les meilleurs résultats.

---

## Résumé rapide

| Fichier | Source recommandée | Effort |
|---|---|---|
| `entrance/road.jpg` | Unsplash → "parking entrance" | 2 min |
| `entrance/car.jpg` | Roboflow Universe → "license plate" | 5 min |
| `parking/lot.jpg` | Kaggle PKLot | 10 min (téléchargement) |
| `reference/marking_ref.jpg` | Photo personnelle | 5 min |
| `parking/marking_test.jpg` | Photo personnelle | 5 min |
