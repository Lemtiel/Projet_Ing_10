import numpy as np
import pandas as pd
from datetime import datetime, timedelta

np.random.seed(42)

# Paramètres
n_samples = 2000
dates = pd.date_range(start='2018-01-01', periods=n_samples, freq='D')

# Variables géophysiques simulées (basées sur des relations réelles NASA/Copernicus)
latitude = np.random.uniform(-60, 60, n_samples)
longitude = np.random.uniform(-180, 180, n_samples)
altitude = np.abs(np.random.normal(300, 400, n_samples))

# Saisonnalité
day_of_year = np.array([d.timetuple().tm_yday for d in dates])
year = np.array([d.year for d in dates])
season_signal = np.sin(2 * np.pi * day_of_year / 365.25)
season_signal2 = np.cos(2 * np.pi * day_of_year / 365.25)

# NDVI (indice végétation) : 0 = sol nu, 1 = végétation dense
ndvi = np.clip(0.4 + 0.3 * season_signal + 0.1 * np.cos(np.radians(latitude)) + np.random.normal(0, 0.1, n_samples), 0, 1)

# Albedo (réflectance surface) : neige élevée, forêt faible
albedo = np.clip(0.25 - 0.15 * np.cos(np.radians(latitude)) * season_signal + np.random.normal(0, 0.05, n_samples), 0.05, 0.85)

# Couverture nuageuse (%)
cloud_cover = np.clip(40 + 20 * np.sin(np.radians(longitude)) + np.random.normal(0, 15, n_samples), 0, 100)

# Humidité relative (%)
humidity = np.clip(60 + 20 * ndvi - 15 * (altitude / 1000) + np.random.normal(0, 10, n_samples), 10, 100)

# Insolation (W/m²)
insolation = np.clip(250 + 150 * np.cos(np.radians(latitude)) * (0.5 + 0.5 * season_signal) - 1.5 * cloud_cover + np.random.normal(0, 20, n_samples), 0, 800)

# Tendance climatique (réchauffement)
trend = 0.002 * (year - 2018) * 365 + 0.002 * day_of_year

# Température de surface (LST) - variable cible
# Relations physiques réalistes
lst = (
    25                                    # base tropicale
    - 0.45 * np.abs(latitude)            # gradient latitudinal
    + 12 * season_signal                 # saisonnalité
    - 0.006 * altitude                   # gradient altitudinal (6°C/1000m)
    + 8 * (1 - albedo)                   # effet albedo inverse
    + 5 * ndvi                           # effet végétation
    - 0.08 * humidity                    # effet humidité
    + 0.015 * insolation                 # effet insolation
    - 0.05 * cloud_cover                 # effet nuages
    + trend                              # tendance climatique
    + np.random.normal(0, 2.5, n_samples) # bruit réaliste
)

df = pd.DataFrame({
    'date': dates,
    'latitude': np.round(latitude, 4),
    'longitude': np.round(longitude, 4),
    'altitude_m': np.round(altitude, 1),
    'ndvi': np.round(ndvi, 4),
    'albedo': np.round(albedo, 4),
    'cloud_cover_pct': np.round(cloud_cover, 2),
    'humidity_pct': np.round(humidity, 2),
    'insolation_wm2': np.round(insolation, 2),
    'day_of_year': day_of_year,
    'month': [d.month for d in dates],
    'year': year,
    'lst_celsius': np.round(lst, 3)
})

df.to_csv('/home/claude/tp_temperature/dataset_LST_satellitaire.csv', index=False)
print(f"Dataset généré : {len(df)} lignes, {len(df.columns)} colonnes")
print(df.describe())
