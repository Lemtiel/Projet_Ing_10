import streamlit as st
import pandas as pd
import numpy as np
import joblib
import folium
from streamlit_folium import st_folium
from datetime import date

# ── Config ──────────────────────────────────
st.set_page_config(
    page_title="LST Predictor",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ── Initialize session state ─────────────────────────────

if "prediction_done" not in st.session_state:
    st.session_state.prediction_done = False

if "lst_pred" not in st.session_state:
    st.session_state.lst_pred = None

if "zone_name" not in st.session_state:
    st.session_state.zone_name = None

if "confidence" not in st.session_state:
    st.session_state.confidence = None



# ===============================================
# initialize session state for map interactions
# ===============================================   
if "clicked_location" not in st.session_state:
    st.session_state["clicked_location"] = None



if "prediction_result" not in st.session_state:
    st.session_state.prediction_result = None

# ── Load models ─────────────────────────────
@st.cache_resource
def load_models():
    reg_model = joblib.load("rf_lst_model_cv.pkl")
    clf_model = joblib.load("rf_region_classifier.pkl")
    le = joblib.load("label_encoder.pkl")
    return reg_model, clf_model, le

@st.cache_data
def load_dataset():
    df = pd.read_csv("Dataset_LST_Massive_20k.csv")
    return df

reg_model, clf_model, le = load_models()
df_full = load_dataset()

# ── Couleurs par zone ────────────────────────
ZONE_COLORS = {
    "Dense_Urban_Temperate":          "#FF6B35",
    "Subtropical_Urban_Canopy":       "#FF9500",
    "Hyper_Arid_Desert_Floor":        "#C8A217",
    "Arid_Sandy_Desert":              "#E8C547",
    "Tropical_Rainforest_Canopy":     "#2D8A4E",
    "Equatorial_Wetland_Basin":       "#1B6B3A",
    "Continental_Boreal_Taiga":       "#4A90D9",
    "High_Altitude_Alpine":           "#7B68EE",
    "Polar_Ice_Sheet":                "#00CED1",
    "Polar_Coastal_Desert":           "#5F9EA0",
    "Intensive_Agricultural_Plain":   "#8BC34A",
    "Coastal_Oceanic_Forest":         "#20B2AA",
}

# Centroïdes réels issus du dataset (lat/lon moyens par zone)
ZONE_CENTROIDS = {
    "Arid_Sandy_Desert":              (22.52,  12.45),
    "Coastal_Oceanic_Forest":         (-33.89, 150.91),
    "Continental_Boreal_Taiga":       (60.02,  99.86),
    "Dense_Urban_Temperate":          (48.86,   2.34),
    "Equatorial_Wetland_Basin":       (-0.79,  23.00),
    "High_Altitude_Alpine":           (27.53,  86.49),
    "Hyper_Arid_Desert_Floor":        (-23.00, -68.97),
    "Intensive_Agricultural_Plain":   (38.01, -98.41),
    "Polar_Coastal_Desert":           (-77.26, 165.19),
    "Polar_Ice_Sheet":                (72.55,  -39.83),
    "Subtropical_Urban_Canopy":       (35.66, 139.68),
    "Tropical_Rainforest_Canopy":     (-3.40,  -62.51),
}

# Stats LST réelles par zone
ZONE_LST_STATS = {
    "Arid_Sandy_Desert":              {"mean": 37.6,  "std": 8.9,  "min": 17.1, "max": 52.5},
    "Coastal_Oceanic_Forest":         {"mean": 24.3,  "std": 7.6,  "min": 9.9,  "max": 44.3},
    "Continental_Boreal_Taiga":       {"mean": -1.9,  "std": 19.5, "min": -39.5,"max": 32.0},
    "Dense_Urban_Temperate":          {"mean": 20.1,  "std": 10.2, "min": 0.1,  "max": 38.1},
    "Equatorial_Wetland_Basin":       {"mean": 27.5,  "std": 1.4,  "min": 22.8, "max": 31.8},
    "High_Altitude_Alpine":           {"mean": 14.4,  "std": 12.0, "min": -21.5,"max": 40.3},
    "Hyper_Arid_Desert_Floor":        {"mean": 39.0,  "std": 9.3,  "min": 4.8,  "max": 57.5},
    "Intensive_Agricultural_Plain":   {"mean": 24.0,  "std": 10.5, "min": 1.8,  "max": 44.6},
    "Polar_Coastal_Desert":           {"mean": -26.6, "std": 10.2, "min": -46.3,"max": -4.2},
    "Polar_Ice_Sheet":                {"mean": -31.1, "std": 13.5, "min": -58.4,"max": -5.5},
    "Subtropical_Urban_Canopy":       {"mean": 27.1,  "std": 10.2, "min": 8.2,  "max": 43.3},
    "Tropical_Rainforest_Canopy":     {"mean": 27.8,  "std": 1.8,  "min": 1.8,  "max": 36.5},
}

# ── Rayons de cercle sur carte (km → degrés approx) ──
ZONE_RADIUS_KM = {
    "Dense_Urban_Temperate":          60,
    "Subtropical_Urban_Canopy":       50,
    "Hyper_Arid_Desert_Floor":        200,
    "Arid_Sandy_Desert":              250,
    "Tropical_Rainforest_Canopy":     350,
    "Equatorial_Wetland_Basin":       300,
    "Continental_Boreal_Taiga":       500,
    "High_Altitude_Alpine":           200,
    "Polar_Ice_Sheet":                600,
    "Polar_Coastal_Desert":           300,
    "Intensive_Agricultural_Plain":   400,
    "Coastal_Oceanic_Forest":         100,
}

# ──────────────────────────────────────────────────────────────
# RECOMMANDATIONS ENRICHIES
# ──────────────────────────────────────────────────────────────
def get_recommendations(zone: str, ndvi: float, albedo: float,
                        lst: float, cloud: float, altitude: int,
                        lat: float, lon: float) -> list[dict]:
    """
    Retourne une liste de dicts {niveau, emoji, titre, detail}
    niveau : "critical" | "warning" | "info" | "ok"
    """
    recs = []
    stats = ZONE_LST_STATS.get(zone, {})
    mean_lst = stats.get("mean", lst)
    max_lst   = stats.get("max",  lst)

    # ── 1. Îlot de chaleur urbain ────────────────────────────
    if "Urban" in zone or "Dense" in zone:
        if lst > 35:
            recs.append({"niveau": "critical", "emoji": "🔥",
                "titre": "Îlot de chaleur urbain sévère",
                "detail": f"LST actuelle ({lst:.1f}°C) dépasse le seuil critique de 35°C. "
                           "Risque de surmortalité en canicule. "
                           "→ Déployer des fontaines/brumisateurs dans les espaces publics, "
                           "ouvrir des centres de refroidissement, renforcer les alertes canicule."})
        elif lst > 28:
            recs.append({"niveau": "warning", "emoji": "🏙️",
                "titre": "Stress thermique urbain modéré",
                "detail": f"LST à {lst:.1f}°C — 8°C au-dessus de la moyenne de zone ({mean_lst:.1f}°C). "
                           "→ Installer des toits végétalisés (réduction jusqu'à 3°C), "
                           "peindre les toitures en blanc (cool roofs, albedo +0.4), "
                           "planter des arbres à feuillage dense en bordure de rues."})

    # ── 2. Albedo critique ───────────────────────────────────
    if albedo < 0.10 and ("Urban" in zone or "Dense" in zone):
        recs.append({"niveau": "critical", "emoji": "⚫",
            "titre": "Albedo extrêmement faible — absorption maximale",
            "detail": f"Albedo = {albedo:.2f} (bitume/asphalte pur). Contribution directe à +5°C de LST. "
                       "→ Changer les revêtements de sol vers béton clair (albedo 0.35+), "
                       "priorité : parkings, cours d'école, zones industrielles."})
    elif albedo < 0.15 and ("Urban" in zone or "Dense" in zone):
        recs.append({"niveau": "warning", "emoji": "🏗️",
            "titre": "Albedo faible — matériaux sombres dominants",
            "detail": f"Albedo = {albedo:.2f}. Surfaces sombres absorbant ~85% du rayonnement solaire. "
                       "→ Envisager cool roofs (matériaux à albedo > 0.65), "
                       "normes constructives à réviser pour les nouvelles constructions."})

    # ── 3. NDVI / végétation ────────────────────────────────
    if ndvi < 0.0:
        recs.append({"niveau": "critical", "emoji": "🏜️",
            "titre": "Surface minérale / eau / glace — NDVI négatif",
            "detail": f"NDVI = {ndvi:.2f} : absence totale de végétation photosynthétique. "
                       "Zone non végétalisable ou en stress hydrique extrême. "
                       "→ Vérifier si désertification anthropique en cours."})
    elif ndvi < 0.15:
        recs.append({"niveau": "warning", "emoji": "🌵",
            "titre": "Végétation quasi-absente",
            "detail": f"NDVI = {ndvi:.2f}. Moins de 10% de couvert végétal actif. "
                       "→ Programme de végétalisation d'urgence : "
                       "espèces résistantes à la sécheresse (xérophytes), "
                       "irrigation goutte-à-goutte si ressource hydrique disponible."})
    elif ndvi < 0.30:
        recs.append({"niveau": "warning", "emoji": "🌿",
            "titre": "Végétation insuffisante",
            "detail": f"NDVI = {ndvi:.2f}. Couvert végétal partiel. "
                       "Potentiel de refroidissement par évapotranspiration sous-exploité. "
                       "→ Objectif NDVI > 0.50 : planter des essences locales adaptées, "
                       "interdire la coupe dans un rayon de 500m des zones habitées."})

    # ── 4. Désert aride ─────────────────────────────────────
    if "Arid" in zone or "Desert" in zone:
        if lst > 45:
            recs.append({"niveau": "critical", "emoji": "☀️",
                "titre": "Température extrême désertique",
                "detail": f"LST = {lst:.1f}°C. Proche du maximum enregistré pour cette zone ({max_lst:.1f}°C). "
                           "→ Aucune activité humaine possible sans protection. "
                           "Systèmes d'irrigation solaire à envisager pour toute installation permanente. "
                           "Architecture bioclimatique obligatoire (ventilation passive, adobe)."})
        else:
            recs.append({"niveau": "info", "emoji": "🏜️",
                "titre": "Zone aride — conditions normales",
                "detail": f"LST = {lst:.1f}°C (moyenne zone : {mean_lst:.1f}°C). "
                           "→ Surveiller l'expansion désertique (désertification). "
                           "Potentiel solaire photovoltaïque très élevé : "
                           "ensoleillement optimal pour fermes solaires."})

    # ── 5. Zone polaire ─────────────────────────────────────
    if "Polar" in zone:
        if lst > -10:
            recs.append({"niveau": "critical", "emoji": "🧊",
                "titre": "Anomalie thermique polaire — fonte anormale",
                "detail": f"LST = {lst:.1f}°C alors que la moyenne est {mean_lst:.1f}°C. "
                           f"Écart de +{lst - mean_lst:.1f}°C au-dessus de la normale. "
                           "→ Indicateur fort de déglaciation accélérée. "
                           "Surveiller les niveaux de méthane (pergélisol). "
                           "Alerte montée des eaux : zones côtières vulnérables."})
        else:
            recs.append({"niveau": "info", "emoji": "❄️",
                "titre": "Zone polaire — surveillance continue requise",
                "detail": f"LST = {lst:.1f}°C. "
                           "→ Monitoring satellite hebdomadaire de l'étendue des glaces, "
                           "suivi des anomalies de la couche d'ozone, "
                           "alertes précoces pour les communautés côtières arctiques."})

    # ── 6. Forêt tropicale ──────────────────────────────────
    if "Tropical" in zone or "Rainforest" in zone:
        if ndvi < 0.60:
            recs.append({"niveau": "warning", "emoji": "🌳",
                "titre": "Déforestation détectée en zone tropicale",
                "detail": f"NDVI = {ndvi:.2f} — anormalement bas pour une forêt tropicale (attendu > 0.70). "
                           "→ Risque de libération de CO₂ séquestré (effet serre amplifié). "
                           "Restauration écologique prioritaire, surveillance par satellite."})
        else:
            recs.append({"niveau": "ok", "emoji": "🌿",
                "titre": "Forêt tropicale en bonne santé",
                "detail": f"NDVI = {ndvi:.2f}. Canopée dense assurant refroidissement par évapotranspiration. "
                           "→ Maintenir les protections légales existantes. "
                           "Cartographier les corridors biologiques pour la biodiversité."})

    # ── 7. Zone alpine ──────────────────────────────────────
    if "Alpine" in zone and altitude > 3000:
        recs.append({"niveau": "warning", "emoji": "⛰️",
            "titre": "Zone alpine d'altitude — glaciers menacés",
            "detail": f"Altitude {altitude}m, LST = {lst:.1f}°C. "
                       "→ Surveiller le recul glaciaire (impact direct sur l'approvisionnement en eau douce). "
                       "Éviter les aménagements touristiques en zone de permafrost instable."})

    # ── 8. Agriculture intensive ─────────────────────────────
    if "Agricultural" in zone:
        if lst > 38:
            recs.append({"niveau": "critical", "emoji": "🌾",
                "titre": "Stress thermique agricole — rendements en danger",
                "detail": f"LST = {lst:.1f}°C > seuil de stress des cultures (38°C). "
                           "→ Activer l'irrigation de refroidissement nocturne, "
                           "anticiper le changement de variétés (cultivars thermotolérants), "
                           "envisager des filets d'ombrage sur les cultures sensibles."})
        elif ndvi < 0.35:
            recs.append({"niveau": "warning", "emoji": "🚜",
                "titre": "Couvert agricole faible — risque d'érosion",
                "detail": f"NDVI = {ndvi:.2f} en période de culture. Sol à nu ou stress végétatif. "
                           "→ Mettre en place des cultures de couverture entre les cycles, "
                           "restaurer les haies bocagères (brise-vent + biodiversité)."})

    # ── 9. Zone humide ───────────────────────────────────────
    if "Wetland" in zone or "Oceanic" in zone:
        if cloud < 20:
            recs.append({"niveau": "info", "emoji": "💧",
                "titre": "Zone humide avec faible couverture nuageuse — évaporation intense",
                "detail": f"Cloud cover = {cloud}%. Rayonnement solaire direct élevé sur zone humide. "
                           "→ Surveiller la salinité et les niveaux d'eau des zones marécageuses, "
                           "protéger les mangroves côtières (barrières naturelles contre les cyclones)."})

    # ── 10. Nuages et insolation ──────────────────────────────
    if cloud > 70 and lst > 25:
        recs.append({"niveau": "info", "emoji": "☁️",
            "titre": "Couverture nuageuse élevée mais LST anormalement haute",
            "detail": f"Cloud = {cloud}% avec LST = {lst:.1f}°C. Effet de serre local probable. "
                       "→ Analyser les sources d'humidité chaude (eaux de surface, industries). "
                       "Vérifier la qualité de l'air (vapeur d'eau + polluants)."})

    # ── 11. Situation équilibrée ──────────────────────────────
    if not recs or all(r["niveau"] == "ok" for r in recs):
        recs.append({"niveau": "ok", "emoji": "✅",
            "titre": "Zone climatiquement équilibrée",
            "detail": f"Paramètres dans les normes pour une zone {zone.replace('_', ' ')}. "
                       f"LST = {lst:.1f}°C (moyenne : {mean_lst:.1f}°C), NDVI = {ndvi:.2f}, Albedo = {albedo:.2f}. "
                       "→ Maintenir les pratiques actuelles. "
                       "Mettre en place un monitoring régulier pour détecter toute dérive."})

    return recs


# ──────────────────────────────────────────────────────────────
# CARTE DES ZONES SIMILAIRES
# ──────────────────────────────────────────────────────────────
def build_similar_zones_map(predicted_zone: str, user_lat: float, user_lon: float, lst_pred: float):
    """
    Crée une carte Folium affichant :
    - Les zones similaires (même type) issues du dataset
    - Le point utilisateur
    - Un cercle coloré autour du centroïde de la zone
    """
    color = ZONE_COLORS.get(predicted_zone, "#888888")
    centroid = ZONE_CENTROIDS.get(predicted_zone, (user_lat, user_lon))
    radius_km = ZONE_RADIUS_KM.get(predicted_zone, 200)

    # Centrer la carte sur le centroïde de la zone détectée
    m = folium.Map(location=[centroid[0], centroid[1]], zoom_start=3, tiles="CartoDB positron")

    # ── Afficher TOUTES les zones du dataset ────────────────
    for zone_name, zone_color in ZONE_COLORS.items():
        zone_centroid = ZONE_CENTROIDS.get(zone_name)
        zone_r = ZONE_RADIUS_KM.get(zone_name, 200)
        stats = ZONE_LST_STATS.get(zone_name, {})
        
        if zone_name == predicted_zone:
            # Zone prédite : cercle plein + contour épais
            fill_opacity = 0.35
            weight = 3
        else:
            # Autres zones : contour léger pour contexte
            fill_opacity = 0.08
            weight = 1

        if zone_centroid:
            popup_html = f"""
            <div style='font-family:sans-serif;min-width:180px'>
              <b style='color:{zone_color}'>{zone_name.replace('_',' ')}</b><br>
              <hr style='margin:4px 0'>
              🌡️ LST moy. : <b>{stats.get('mean', '?'):.1f}°C</b><br>
              📊 Plage : {stats.get('min','?')}°C → {stats.get('max','?')}°C<br>
              📍 Centre : {zone_centroid[0]:.2f}°N, {zone_centroid[1]:.2f}°E
            </div>"""
            
            folium.Circle(
                location=zone_centroid,
                radius=zone_r * 1000,      # km → m
                color=zone_color,
                fill=True,
                fill_color=zone_color,
                fill_opacity=fill_opacity,
                weight=weight,
                popup=folium.Popup(popup_html, max_width=220),
                tooltip=zone_name.replace("_", " ")
            ).add_to(m)

            # Label centroïde (toutes les zones)
            folium.Marker(
                location=zone_centroid,
                icon=folium.DivIcon(
                    html=f"<div style='font-size:9px;font-weight:bold;color:{zone_color};"
                         f"text-shadow:0 0 3px #fff,0 0 3px #fff;white-space:nowrap'>"
                         f"{zone_name.replace('_',' ')}</div>",
                    icon_size=(180, 20),
                    icon_anchor=(90, 10)
                )
            ).add_to(m)

    # ── Point utilisateur ────────────────────────────────────
    user_popup = f"""
    <div style='font-family:sans-serif'>
      <b>📍 Votre point</b><br>
      {user_lat:.4f}°N, {user_lon:.4f}°E<br>
      🌡️ LST prédite : <b>{lst_pred:.1f}°C</b><br>
      🗺️ Zone : <b>{predicted_zone.replace('_', ' ')}</b>
    </div>"""

    folium.Marker(
        location=[user_lat, user_lon],
        popup=folium.Popup(user_popup, max_width=220),
        tooltip="Votre localisation",
        icon=folium.Icon(color="red", icon="star", prefix="fa")
    ).add_to(m)

    # Ligne du centroïde au point utilisateur
    folium.PolyLine(
        locations=[centroid, [user_lat, user_lon]],
        color=color,
        weight=2,
        dash_array="8 4",
        opacity=0.7,
        tooltip=f"Distance au centroïde de {predicted_zone.replace('_',' ')}"
    ).add_to(m)

    return m


# ══════════════════════════════════════════════════════════════
# UI PRINCIPALE
# ═════════════════════════════════════════════════════════════
st.markdown(
    "<h1 style='text-align:center;color:orange;'>🌍 GLOBAL HEAT RISK SIMULATOR 🌡️</h1>",
    unsafe_allow_html=True
)
st.markdown(
    "<p style='text-align:center;'>Définissez votre scénario climatique pour estimer la "
    "Température de Surface Terrestre (LST) et identifier la zone de risque.</p>",
    unsafe_allow_html=True
)
st.markdown("---")
st.markdown(
    "<p style='text-align:center;'>choisissez un emplacement sur la carte ou entrez les coordonnées manuellement.</p>",
    unsafe_allow_html=True
)

col_map, col_params = st.columns([2.5, 2])

with col_map:
    m_input = folium.Map(
        location=[20, 0],
        zoom_start=2
    )
    if st.session_state["clicked_location"] is not None:
        folium.Marker(
            location=st.session_state["clicked_location"],
            popup="Position sélectionnée",
            icon=folium.Icon(
            color="red",
            icon="map-marker"
            )
        ).add_to(m_input)

    map_data = st_folium(
    m_input,
    key="main_map",
    height=400,
    width=900,
    returned_objects=[
        "last_clicked",
        "center",
        "zoom"
    ])

    # Sauvegarde du clic
    if map_data.get("last_clicked"):
        st.session_state["clicked_location"] = [
            map_data["last_clicked"]["lat"],
            map_data["last_clicked"]["lng"]
        ]

    if map_data and map_data.get("last_clicked"):
        st.session_state.clicked_location = [
            map_data["last_clicked"]["lat"],
            map_data["last_clicked"]["lng"]
        ]
    # Récupération des coords depuis le clic carte

    if "selected_lat" not in st.session_state:
        st.session_state.selected_lat = 48.85

    if "selected_lon" not in st.session_state:
        st.session_state.selected_lon = 2.35
    if map_data and map_data.get("last_clicked"):

        st.session_state.selected_lat = map_data["last_clicked"]["lat"]
        st.session_state.selected_lon = map_data["last_clicked"]["lng"]

with col_params:
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("**📍 Localisation**")
        lat = st.number_input(
        "Latitude",
        value=st.session_state.selected_lat
        )

        lon = st.number_input(
            "Longitude",
            value=st.session_state.selected_lon
        )
        altitude  = st.number_input("Altitude (m)",  value=35, min_value=0, max_value=8849)

    with col2:
        st.markdown("**🍃 Environnement**")
        ndvi  = st.slider("NDVI (végétation)",       -0.2, 1.0, 0.3,  0.01)
        albedo = st.slider("Albedo (réflectivité)",   0.0, 1.0, 0.15, 0.01)
        cloud  = st.slider("Couverture nuageuse (%)", 0, 100, 30)

    selected_date = st.date_input("Date", value=date.today())
    predict_btn   = st.button("🔮 Prédire", use_container_width=True)
    if predict_btn:
        st.session_state.prediction_done = True

def validate_inputs(lat, lon, altitude, ndvi, albedo, cloud):
    errors = []

    if not (-90 <= lat <= 90):
        errors.append("Latitude invalide (-90 à 90).")

    if not (-180 <= lon <= 180):
        errors.append("Longitude invalide (-180 à 180).")

    if altitude < 0:
        errors.append("Altitude négative impossible.")

    if not (-0.2 <= ndvi <= 1):
        errors.append("NDVI hors limites physiques.")

    if not (0 <= albedo <= 1):
        errors.append("Albedo doit être compris entre 0 et 1.")

    if not (0 <= cloud <= 100):
        errors.append("Couverture nuageuse doit être comprise entre 0 et 100 %.")

    # Cas incohérents

    if ndvi > 0.8 and albedo < 0.05:
        errors.append(
            "Scénario peu réaliste : végétation très dense avec albedo extrêmement faible."
        )

    if altitude > 6000 and ndvi > 0.7:
        errors.append(
            "Scénario peu réaliste : végétation dense à très haute altitude."
        )

    if altitude > 5000 and cloud == 0:
        errors.append(
            "Scénario atypique : haute montagne avec absence totale de couverture nuageuse."
        )

    return errors

errors = validate_inputs(
    lat,
    lon,
    altitude,
    ndvi,
    albedo,
    cloud
)
if errors:
    st.info(
        """
        ⚠️ Certains paramètres semblent incohérents.

        Vérifiez :
        - latitude / longitude
        - altitude
        - NDVI
        - albedo
        - couverture nuageuse

        Les prédictions hors domaine d'apprentissage peuvent être peu fiables.
        """
    )

# ══════════════════════════════════════════════════════════════
# PRÉDICTION + RÉSULTATS
# ══════════════════════════════════════════════════════════════
if predict_btn:

    day_of_year = selected_date.timetuple().tm_yday

    input_reg = pd.DataFrame([{
        "Latitude": lat,
        "Longitude": lon,
        "Altitude_m": altitude,
        "Ndvi": ndvi,
        "Albedo": albedo,
        "Cloud_cover_pct": cloud,
        "day_sin": np.sin(2*np.pi*day_of_year/365),
        "day_cos": np.cos(2*np.pi*day_of_year/365)
    }])

    lst_pred = reg_model.predict(input_reg)[0]

    input_clf = input_reg.copy()
    input_clf["Lst_celsius"] = lst_pred

    zone_encoded = clf_model.predict(input_clf)[0]
    zone_proba = clf_model.predict_proba(input_clf)[0]

    zone_name = le.inverse_transform([zone_encoded])[0]
    confidence = zone_proba.max()

    st.session_state.prediction_result = {
    "lst_pred": lst_pred,
    "zone_name": zone_name,
    "confidence": confidence,
    "lat": lat,
    "lon": lon,
    "altitude": altitude,
    "ndvi": ndvi,
    "albedo": albedo,
    "cloud": cloud,
    "date": selected_date
}
    
    if st.session_state.prediction_result:

        result = st.session_state.prediction_result

        lst_pred = result["lst_pred"]
        zone_name = result["zone_name"]
        confidence = result["confidence"]

        lat = result["lat"]
        lon = result["lon"]

        altitude = result["altitude"]
        ndvi = result["ndvi"]
        albedo = result["albedo"]
        cloud = result["cloud"]

    # Couleur de la zone
    zone_color = ZONE_COLORS.get(zone_name, "#888888")
    stats       = ZONE_LST_STATS.get(zone_name, {})

    # ── Métriques ────────────────────────────────────────────
    st.divider()
    res1, res2, res3 = st.columns(3)
    with res1:
        delta_mean = lst_pred - stats.get("mean", lst_pred)
        st.metric(
            "🌡️ Température de surface",
            f"{lst_pred:.1f} °C",
            delta=f"{delta_mean:+.1f}°C vs moyenne zone"
        )
    with res2:
        st.metric(
            "🗺️ Zone climatique",
            zone_name.replace("_", " "),
            f"Confiance : {confidence:.0%}"
        )
    with res3:
        risk_level = (
            "🔴 Critique"  if lst_pred > 40 or (lst_pred > 35 and "Urban" in zone_name) else
            "🟠 Élevé"     if lst_pred > 30 or (lst_pred < -20) else
            "🟡 Modéré"    if lst_pred > 22 or (lst_pred < -10) else
            "🟢 Normal"
        )
        st.metric("⚠️ Niveau de risque thermique", risk_level)

    # ── Barre de contexte zone ───────────────────────────────
    st.markdown(
        f"<div style='background:{zone_color}22;border-left:4px solid {zone_color};"
        f"padding:10px 14px;border-radius:4px;margin:8px 0'>"
        f"<b style='color:{zone_color}'>{zone_name.replace('_',' ')}</b> — "
        f"LST moy. {stats.get('mean','?'):.1f}°C    |    plage {stats.get('min','?')}→{stats.get('max','?')}°C    |    "
        f"σ = ±{stats.get('std','?'):.1f}°C"
        f"</div>",
        unsafe_allow_html=True
    )

    # ── Recommandations enrichies ────────────────────────────
    st.subheader("💡 Recommandations d'intervention")

    COLOR_MAP = {
        "critical": ("#FF4444", "🔴"),
        "warning":  ("#FF9500", "🟠"),
        "info":     ("#4A90D9", "🔵"),
        "ok":       ("#2D8A4E", "🟢"),
    }

    recommendations = get_recommendations(
        zone_name, ndvi, albedo, lst_pred, cloud, altitude, lat, lon
    )

    for rec in recommendations:
        bg, _ = COLOR_MAP.get(rec["niveau"], ("#888", "⚪"))
        st.markdown(
            f"<div style='background:{bg}18;border-left:4px solid {bg};"
            f"padding:12px 16px;border-radius:4px;margin:6px 0'>"
            f"<b>{rec['emoji']} {rec['titre']}</b><br>"
            f"<span style='color:#444;font-size:0.92em'>{rec['detail']}</span>"
            f"</div>",
            unsafe_allow_html=True
        )

    # ── CARTE DES ZONES SIMILAIRES ───────────────────────────
    st.divider()
    st.subheader(f"🌐 Zones similaires dans le monde — {zone_name.replace('_', ' ')}")
    st.markdown(
        f"La zone **{zone_name.replace('_', ' ')}** est mise en évidence "
        f"(cercle <span style='color:{zone_color};font-weight:bold'>■</span> plein). "
        "Les autres zones apparaissent en transparence pour le contexte global. "
        "**Cliquez** sur un cercle pour voir les statistiques.",
        unsafe_allow_html=True
    )

    similar_map = build_similar_zones_map(zone_name, lat, lon, lst_pred)
    st_folium(
    similar_map,
    height=480,
    width="stretch",
    returned_objects=[]
)
    # st_folium(similar_map, height=480, width=None, use_container_width=True, key="similar_map")

    # ── Tableau comparatif toutes zones ─────────────────────
    with st.expander("📊 Comparatif LST — toutes les zones climatiques"):
        rows = []
        for z, s in ZONE_LST_STATS.items():
            rows.append({
                "Zone": z.replace("_", " "),
                "LST moy. (°C)": s["mean"],
                "Écart-type": s["std"],
                "Min (°C)": s["min"],
                "Max (°C)": s["max"],
                "Sélectionnée": "✅" if z == zone_name else ""
            })
        df_compare = pd.DataFrame(rows).sort_values("LST moy. (°C)", ascending=False)
        st.dataframe(
            df_compare.style.apply(
                lambda row: ["background-color:#FF650022" if row["Sélectionnée"] == "✅"
                             else "" for _ in row],
                axis=1
            ),
            use_container_width=True,
            hide_index=True
        )
    
    st.session_state.lst_pred = lst_pred
    st.session_state.zone_name = zone_name
    st.session_state.confidence = confidence
    st.session_state.prediction_done = True
else:
    st.info("Veuillez saisir des entrées valides.")