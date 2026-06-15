import streamlit as st
import pandas as pd
import numpy as np
import pickle
import plotly.graph_objects as go
import datetime

# ==========================================
# 1. CONFIGURATION DE LA PAGE STREAMLIT
# ==========================================
st.set_page_config(
    page_title="Global Heat Risk Simulator",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ==========================================
# 2. CHARGEMENT DES MODÈLES (À adapter)
# ==========================================
@st.cache_resource
def load_models():
    # Chargement des modèles pré-entraînés et des encodeurs :
    with open('linear_model.pkl', 'rb') as f:
        linear_model = pickle.load(f)
    with open('logistic_model.pkl', 'rb') as f:
        logistic_model = pickle.load(f)
    with open('le_dict_log.pkl', 'rb') as f:
        le_dict = pickle.load(f)
    with open('scaler_log.pkl', 'rb') as f:
        scaler = pickle.load(f)
    return linear_model, logistic_model, le_dict, scaler
    #pass

# ==========================================
# 3. EN-TÊTE DU DASHBOARD
# ==========================================
st.markdown("<h1 style='text-align: center; color: orange;'>🌍 GLOBAL HEAT RISK SIMULATOR 🌡️</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center;'>Définissez votre scénario climatique pour estimer la Température de Surface Terrestre (LST) et classifier la zone de risque.</p>", unsafe_allow_html=True)
st.markdown("---")


# ==========================================
# 4. PANNEAU DE CONTRÔLE (SCÉNARIO)
# ==========================================
with st.form("scenario_form"):
    st.subheader("⚙️ Définir les paramètres du scénario")
    
    # Nous divisons les entrées en 4 colonnes pour un look Dashboard
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown("**📍 Localisation**")
        country = st.selectbox("Pays", ["France", "USA", "Bresil", "Japon", "Australie"])
        city = st.selectbox("Ville / Zone", ['Paris', 'Sahara', 'Amazonie', 'Tokyo', 'Siberie', 'Himalaya', 'Congo',
 'Atacama', 'Greenland', 'Kansas_Plains', 'Sydney', 'McMurdo'])
        region_type = st.selectbox("Type de Région", ["Urban_Temperate", "Tropical", "Arid", "Polar"])
        
    with col2:
        st.markdown("**🧭 Coordonnées & Altitude**")
        lat = st.number_input("Latitude", min_value=-90.0, max_value=90.0, value=48.85)
        lon = st.number_input("Longitude", min_value=-180.0, max_value=180.0, value=2.35)
        altitude = st.number_input("Altitude (m)", value=46.0)
        
    with col3:
        st.markdown("**☁️ Météorologie**")
        
        # Date d'entrée pour la simulation (avec calcul automatique du jour de l'année)
        selected_date = st.date_input("Date de la simulation", value=datetime.date.today())
        # Calcul automatique du jour de l'année (1 à 365)
        day_of_year = selected_date.timetuple().tm_yday
      # ----------------------------------------------------------------
        insolation = st.number_input("Insolation (W/m²)", value=200.0)
        cloud_cover = st.slider("Couverture Nuageuse (%)", 0.0, 100.0, 38.0)
        
    with col4:
        st.markdown("**🌿 Surfaces**")
        humidity = st.slider("Humidité (%)", 0.0, 100.0, 50.0)
        ndvi = st.slider("NDVI (Végétation)", -1.0, 1.0, 0.05)
        albedo = st.slider("Albédo (Réflectivité)", 0.0, 1.0, 0.15)
        
    # Le bouton de soumission
    submit_button = st.form_submit_button(label="🚀 Analyser le Scénario", use_container_width=True)

# ==========================================
# 5. RÉSULTATS DE LA SIMULATION (Au clic)
# ==========================================
if submit_button:
    st.markdown("---")
    
    # ----------------------------------------------------
    # Espace de prédiction (Mockup en attendant tes modèles)
    # ----------------------------------------------------
    #temp_pred = linear_model.predict(df_input)[0]
    #class_pred = logistic_model.predict(df_input)[0]
    #df_input = pd.DataFrame([{ 'Country': country, 'Region_Type': class_pred, 'City_Zone': city, 'Latitude': lat, #'Longitude': lon, 'Altitude_m': altitude, 'Day_of_year': day_of_year, 'Ndvi': ndvi, 'Albedo': albedo, #'Cloud_cover_pct': cloud_cover, 'Humidity_pct': humidity, 'Insolation_wm2': insolation, 'Lst_celsius': #temp_pred }])

    
    # Valeurs fictives pour voir le rendu visuel
    temp_pred = 36.2
    class_pred = "Risque Élevé (Îlot de Chaleur)"
    
    # ----------------------------------------------------
    # AFFICHAGE CÔTE À CÔTE DES DEUX MODÈLES
    # ----------------------------------------------------
    res_col1, res_col2 = st.columns(2)
    
    with res_col1:
        st.markdown("<h3 style='text-align: center;'>📈 MODÈLE DE RÉGRESSION</h3>", unsafe_allow_html=True)
        st.markdown("<p style='text-align: center;'>Estimation de la Température de Surface (LST)</p>", unsafe_allow_html=True)
        
        # Jauge Thermique (Thermomètre avec Plotly)
        fig = go.Figure(go.Indicator(
            mode = "gauge+number",
            value = temp_pred,
            number = {'suffix': " °C"},
            domain = {'x': [0, 1], 'y': [0, 1]},
            gauge = {
                'axis': {'range': [-20, 60], 'tickwidth': 1, 'tickcolor': "darkblue"},
                'bar': {'color': "black"},
                'bgcolor': "white",
                'borderwidth': 2,
                'bordercolor': "gray",
                'steps': [
                    {'range': [-20, 15], 'color': "royalblue"},
                    {'range': [15, 30], 'color': "lightskyblue"},
                    {'range': [30, 40], 'color': "orange"},
                    {'range': [40, 60], 'color': "red"}],
                'threshold': {
                    'line': {'color': "black", 'width': 4},
                    'thickness': 0.75,
                    'value': temp_pred}}
        ))
        fig.update_layout(height=350, margin=dict(l=20, r=20, t=30, b=20))
        st.plotly_chart(fig, use_container_width=True)
        
    with res_col2:
        st.markdown("<h3 style='text-align: center;'>🔍 MODÈLE DE CLASSIFICATION</h3>", unsafe_allow_html=True)
        st.markdown("<p style='text-align: center;'>Analyse du Profil de la Zone</p>", unsafe_allow_html=True)
        
        st.write("") # Espacement
        st.write("")
        
        # Affichage conditionnel du badge et des conseils de lutte contre le réchauffement
        if temp_pred > 35:
            st.error(f"🚨 **CLASSIFICATION : {class_pred}**")
            st.markdown("""
            **Recommandations de Lutte contre le Réchauffement :**
            * 🌳 **Végétalisation :** Planter des arbres à canopée large (augmentation du NDVI).
            * 🏢 **Toits Frais :** Peindre les toits en blanc pour augmenter l'Albédo.
            * 💧 **Points d'eau :** Intégrer des fontaines ou miroirs d'eau dans l'urbanisme.
            """)
        elif temp_pred > 25:
            st.warning("⚠️ **CLASSIFICATION : Zone à Risque Modéré**")
            st.markdown("""
            **Recommandations d'Amélioration :**
            * 🌿 **Murs végétaux :** Installer de la verdure sur les façades.
            * 🚶 **Sols perméables :** Remplacer le bitume par des pavés poreux.
            """)
        else:
            st.success("✅ **CLASSIFICATION : Zone Saine / Fraîche**")
            st.markdown("""
            **État de la zone :**
            * La zone bénéficie d'une bonne régulation thermique. 
            * Maintenir la couverture végétale actuelle et limiter l'expansion de béton.
            """)
            
    # ----------------------------------------------------
    # CARTE DU MONDE (DASHBOARD BI)
    # ----------------------------------------------------
    st.markdown("---")
    st.markdown("### 🗺️ Localisation du Scénario sur la Carte Globale")
    
    # Création d'un dataframe spécifique pour Streamlit Map
    map_data = pd.DataFrame({'lat': [lat], 'lon': [lon]})
    
    # Affichage de la carte interactive centrée sur les coordonnées saisies
    st.map(map_data, zoom=4, use_container_width=True)