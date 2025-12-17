# Dashboard Growth – Arkose Montreuil

Application Streamlit de suivi de performance pour Arkose Montreuil, basée sur les données de fréquentation et de restauration 2025 fournies en CSV.

L’objectif est d’aider à améliorer la communication et le marketing en identifiant :
- les périodes fortes / creuses de fréquentation,
- la relation entre grimpe et restauration,
- les jours à fort potentiel pour des actions growth (bundles, events, offres spéciales).

---

## 1. Fonctionnalités

### Analyse globale
- Vue d’ensemble avec KPIs :
  - Total grimpeurs (Passage)
  - Total plats et entrées vendus
  - Nombre de jours observés
- Résumé automatique de la période (moyenne de passages/jour, jour de pic, etc.).

### Filtres & segmentations
- Filtres avancés :
  - par mois
  - par jour de la semaine
  - par plage de dates
- Segmentation rapide :
  - Tous les jours
  - Week-end uniquement
  - Semaine uniquement
  - Jours forts (top 20 % de fréquentation).

### Onglets d’analyse

1. **📈 Tendances temporelles**
   - Courbes journalières sur la métrique choisie (Passage / Plat / Entrée).
   - Évolution de la restauration dans le temps.
   - Tableau des top jours les plus fréquentés.

2. **📊 Profils de jours & mois**
   - Bar charts des passages moyens par mois.
   - Bar charts des passages moyens par jour de la semaine.
   - Explications et idées de ciblage marketing selon les jours / mois forts ou faibles.

3. **🍽️ Grimpe vs Restauration**
   - Nuages de points Passages vs Plats.
   - Nuages de points Passages vs Entrées.
   - Conseils pour utiliser des bundles grimpe + resto.

4. **🚀 Opportunités marketing**
   - Liste des jours “forte grimpe / faible resto” → jours à potentiel de montée en panier moyen.
   - Vue hebdomadaire des volumes (passages et restauration).
   - Recommandations adaptées à l’objectif choisi :
     - Remplir les jours creux
     - Maximiser le panier moyen
     - Lancer un nouvel event.

---

## 2. Structure du projet

.
├── app.py # Frontend Streamlit
├── data_service.py # Backend : chargement + analyse des données
├── ARKOSE-donnees_2025_graph.csv # Données fournies par Arkose
├── requirements.txt # Dépendances Python
└── .streamlit/
└── config.toml # Thème Streamlit (dark + couleurs Arkose)


Le backend (`data_service.py`) centralise la logique métier :
- chargement sécurisé du CSV,
- filtres (mois, jours, dates),
- segments rapides,
- calcul des KPIs globaux et hebdomadaires,
- détection des jours “haute grimpe / basse restauration”.

---

## 3. Installation

1. Cloner ou copier le projet dans un dossier local.
2. Placer le fichier `ARKOSE-donnees_2025_graph.csv` à la racine du projet.

Créer un environnement virtuel (recommandé) :

python -m venv env
source env/bin/activate # macOS / Linux

ou
env\Scripts\activate # Windows


Installer les dépendances :

pip install -r requirements.txt


---

## 4. Lancement de l’application

Depuis la racine du projet :

streamlit run app.py


L’application sera accessible sur :

- Local URL : `http://localhost:8502` (ou autre port indiqué par Streamlit).

---

## 5. Comment présenter le projet

Ce dashboard permet à Arkose Montreuil de :

- Comprendre ses patterns de fréquentation (jours forts/faibles, saisonnalité).
- Relier la performance de la restauration à la fréquentation de la salle.
- Identifier des jours à fort potentiel marketing (beaucoup de grimpeurs mais peu de consommation).
- Adapter la stratégie selon un objectif précis (remplir les jours creux, augmenter le panier moyen, lancer un event).
