# Projet_Ing_10
Modélisation prédictive de la température de surface terrestre à partir de données satellitaires

## 🚀 Nouveautés – LstApp v2.1.1

Cette version apporte une amélioration majeure de l'expérience utilisateur, de l'interactivité cartographique et de l'interprétation des résultats de prédiction de la température de surface terrestre (LST).

## 🌍 Sélection géographique interactive

### Carte interactive Folium

* Sélection directe d'un emplacement par clic sur la carte mondiale.
* Mise à jour automatique des coordonnées latitude/longitude.
* Affichage d'un marqueur sur le point sélectionné.
* Conservation du niveau de zoom et de la position de la carte après interaction grâce à `Streamlit Session State`.

### Gestion avancée de l'état de l'application

* Sauvegarde persistante des coordonnées sélectionnées.
* Conservation des résultats de prédiction après rafraîchissement de l'interface.
* Élimination des réinitialisations intempestives de la carte lors des interactions utilisateur.

---

## 🤖 Amélioration du moteur de prédiction

### Double prédiction IA

L'application combine désormais :

1. **Régression Random Forest**

   * Estimation de la Land Surface Temperature (LST).

2. **Classification Random Forest**

   * Identification automatique de la zone climatique la plus probable.

### Indicateur de confiance

Calcul et affichage de la probabilité de classification du modèle.

#### Code couleur de confiance

| Niveau de confiance | Couleur  |
| ------------------- | -------- |
| > 70 %              | 🟢 Vert  |
| 40 % – 70 %         | 🟡 Jaune |
| < 40 %              | 🔴 Rouge |

---

## 📊 Tableau de bord enrichi

### Métriques principales

* Température de surface prédite.
* Écart par rapport à la moyenne historique de la zone détectée.
* Zone climatique identifiée.
* Niveau de confiance du modèle.
* Niveau de risque thermique.

### Niveaux de risque

* 🟢 Normal
* 🟡 Modéré
* 🟠 Élevé
* 🔴 Critique

---

## 💡 Système expert de recommandations environnementales

Le module de recommandations a été considérablement enrichi.

### Cas analysés

#### Zones urbaines

* Détection des îlots de chaleur urbains.
* Suggestions de toitures réfléchissantes.
* Végétalisation des espaces urbains.
* Réduction des surfaces à faible albédo.

#### Zones désertiques

* Identification des températures extrêmes.
* Recommandations d'adaptation aux fortes chaleurs.
* Valorisation du potentiel solaire.

#### Zones agricoles

* Détection du stress thermique des cultures.
* Surveillance des risques d'érosion.
* Conseils de gestion des sols.

#### Zones tropicales

* Détection indirecte de phénomènes de déforestation.
* Analyse de la santé de la canopée.

#### Zones polaires

* Identification d'anomalies thermiques.
* Surveillance des phénomènes de fonte glaciaire.

#### Zones humides et côtières

* Suivi des risques liés à l'évaporation.
* Surveillance des écosystèmes sensibles.

---

## 🌐 Cartographie mondiale des zones similaires

### Nouvelle visualisation géospatiale

Après chaque prédiction, une carte mondiale est générée automatiquement.

Fonctionnalités :

* Mise en évidence de la zone climatique prédite.
* Affichage des centroïdes climatiques mondiaux.
* Représentation visuelle des étendues climatiques via des cercles colorés.
* Positionnement du point utilisateur.
* Liaison graphique entre le point utilisateur et le centroïde de la zone détectée.
* Consultation des statistiques climatiques via des fenêtres contextuelles interactives.

### Informations affichées

Pour chaque zone :

* Température moyenne observée.
* Température minimale observée.
* Température maximale observée.
* Coordonnées du centroïde climatique.

---

## 📈 Comparaison inter-zones

Ajout d'un tableau comparatif interactif présentant :

* Les 12 zones climatiques du modèle.
* Température moyenne.
* Température minimale.
* Température maximale.
* Écart-type.
* Mise en évidence automatique de la zone prédite.

---

## ⚙️ Optimisations techniques

### Performance

* Chargement des modèles avec `@st.cache_resource`.
* Mise en cache du dataset avec `@st.cache_data`.
* Réduction des recalculs inutiles.

### Interface utilisateur

* Mise en page responsive.
* Amélioration de la lisibilité des résultats.
* Affichage conditionnel des cartes et analyses.
* Compatibilité avec les nouvelles recommandations Streamlit (`width="stretch"`).

---

## 🎯 Résultat

L'application évolue d'un simple outil de prédiction LST vers une plateforme interactive d'analyse climatique permettant :

* la prédiction thermique,
* la classification climatique,
* l'analyse environnementale,
* l'aide à la décision,
* et la visualisation géospatiale mondiale.



## LstApp v2.0


### WebApp v1.2

C'est la version 1 du programme avec des modifications apportées sur l'UX. Contrairement à la v1.0 qui présente la même interface, cette version ci permet à l'utilisateur d'être informé sur un certain nombre de points pendant sa session de travail :
- Le dernier point renseigné sur la carte où a été effectué la prédiction à l'aide d'un marqueur/pointeur.
- Indique s'il faut cliquer ou pas sur le bouton prédire
