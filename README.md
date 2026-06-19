# Projet_Ing_10
Modélisation prédictive de la température de surface terrestre à partir de données satellitaires
---

# **🚀 Mise à jour v2.1.2 – Interface Interactive et Analyse Climatique Avancée**

Cette version apporte une amélioration majeure de l'expérience utilisateur, de la visualisation géospatiale et de l'interprétation des résultats.

---

## 🗺️ Sélection géographique interactive

### Nouveautés
- Sélection de coordonnées directement sur une carte mondiale interactive.
- Mise à jour automatique des champs Latitude et Longitude après un clic.
- Affichage d'un marqueur sur la position choisie.
- Conservation de la localisation sélectionnée pendant l'utilisation de l'application.

### Bénéfices
- Plus besoin de saisir manuellement les coordonnées.
- Réduction des erreurs de saisie.
- Navigation plus intuitive.

---

## 🌡️ Prédiction améliorée de la température de surface (LST)

Le système continue d'utiliser :

- Un modèle de régression Random Forest pour la prédiction de la température de surface terrestre (LST).
- Un modèle de classification Random Forest pour l'identification automatique de la zone climatique.

### Résultats affichés

- Température de surface prédite.
- Zone climatique détectée.
- Niveau de confiance du classifieur.
- Niveau de risque thermique.

---

## 🎯 Indicateur de confiance coloré

Le niveau de confiance du modèle est désormais mis en évidence visuellement :

| Niveau de confiance | Couleur |
|---------------------|----------|
| > 70 % | 🟢 Vert |
| 40 % – 70 % | 🟡 Jaune |
| < 40 % | 🔴 Rouge |

Cette visualisation permet d'évaluer rapidement la fiabilité de la classification.

---

## 💡 Système de recommandations enrichi

Les recommandations sont désormais générées en fonction :

- de la température prédite ;
- du NDVI ;
- de l'albedo ;
- de la couverture nuageuse ;
- de l'altitude ;
- du type de zone climatique détectée.

### Cas traités

#### Zones urbaines
- Détection des îlots de chaleur.
- Recommandations de végétalisation.
- Conseils sur les toitures réfléchissantes.
- Solutions de refroidissement urbain.

#### Zones désertiques
- Gestion des températures extrêmes.
- Surveillance de la désertification.
- Valorisation du potentiel photovoltaïque.

#### Zones polaires
- Détection d'anomalies thermiques.
- Surveillance de la fonte des glaces.
- Suivi du pergélisol.

#### Forêts tropicales
- Détection potentielle de déforestation.
- Évaluation de l'état de la canopée.
- Recommandations de restauration écologique.

#### Zones agricoles
- Évaluation du stress thermique des cultures.
- Gestion de l'irrigation.
- Prévention de l'érosion.

#### Zones humides
- Surveillance de l'évaporation.
- Protection des écosystèmes sensibles.

---

## 🌐 Carte mondiale des zones similaires

Une nouvelle carte dynamique est générée après chaque prédiction.

### Fonctionnalités

- Affichage des 12 grandes zones climatiques du dataset.
- Représentation géographique des centroïdes de chaque zone.
- Visualisation des zones sous forme de cercles colorés.
- Mise en évidence de la zone climatique prédite.
- Affichage du point utilisateur.
- Liaison visuelle entre la localisation utilisateur et le centroïde de la zone détectée.

### Informations disponibles

Pour chaque zone :

- Température moyenne.
- Température minimale.
- Température maximale.
- Position géographique représentative.

---

## 📊 Tableau comparatif climatique global

Ajout d'un tableau interactif permettant de comparer :

- la température moyenne ;
- la température minimale ;
- la température maximale ;
- l'écart-type thermique ;

pour l'ensemble des zones climatiques du système.

La zone prédite est automatiquement mise en évidence.

---

## 🎨 Améliorations de l'interface

- Mise en page optimisée.
- Cartes responsive.
- Affichage enrichi des recommandations.
- Code couleur cohérent selon le niveau de risque.
- Visualisation simplifiée des informations critiques.

---

## 🔬 Objectif scientifique

Cette version vise à transformer le modèle de prédiction en un véritable outil d'aide à l'interprétation environnementale en combinant :

- Intelligence artificielle ;
- Analyse climatique ;
- Visualisation géospatiale ;
- Aide à la décision environnementale.

L'utilisateur ne reçoit plus uniquement une prédiction de température, mais également une contextualisation climatique complète et des recommandations adaptées au scénario simulé.

---
## $ 🚀 Nouveautés – LstApp v2.1.1$

### $ WebApp v1.2 $
---
- Le dernier point renseigné sur la carte où a été effectué la prédiction à l'aide d'un marqueur/pointeur.
- Indique s'il faut cliquer ou pas sur le bouton prédire
