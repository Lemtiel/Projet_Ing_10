"""
Script 3 : Visualisation spatiale et temporelle des prédictions LST
Projet ECAM-EPMI
"""

import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
from matplotlib.gridspec import GridSpec
import joblib
import warnings
warnings.filterwarnings('ignore')

df = pd.read_csv('/home/claude/tp_temperature/dataset_LST_satellitaire.csv', parse_dates=['date'])
features = ['latitude','altitude_m','ndvi','albedo','cloud_cover_pct',
            'humidity_pct','insolation_wm2','day_of_year']

model = joblib.load('/home/claude/tp_temperature/meilleur_modele.pkl')
df['lst_predicted'] = model.predict(df[features].values)
df['residual'] = df['lst_celsius'] - df['lst_predicted']

# ── Figure 8 : Carte spatiale des prédictions ────────────────────────────
fig, axes = plt.subplots(1, 2, figsize=(15, 5))
fig.suptitle('Distribution spatiale de la LST — Réelle vs Prédite', fontsize=13, fontweight='bold')

cmap = plt.cm.RdYlBu_r
vmin, vmax = df['lst_celsius'].quantile(0.02), df['lst_celsius'].quantile(0.98)
norm = mcolors.Normalize(vmin=vmin, vmax=vmax)

for ax, col, title in zip(axes, ['lst_celsius','lst_predicted'], ['LST Réelle (°C)','LST Prédite (°C)']):
    sc = ax.scatter(df['longitude'], df['latitude'], c=df[col],
                    cmap=cmap, norm=norm, s=12, alpha=0.65)
    ax.set_xlabel('Longitude', fontsize=10)
    ax.set_ylabel('Latitude', fontsize=10)
    ax.set_title(title, fontsize=11, fontweight='bold')
    ax.axhline(0, color='gray', linestyle=':', linewidth=0.8, alpha=0.6)
    ax.grid(alpha=0.2)
    plt.colorbar(sc, ax=ax, label='°C', shrink=0.8)

plt.tight_layout()
plt.savefig('/home/claude/tp_temperature/fig8_carte_spatiale.png', dpi=150, bbox_inches='tight')
plt.close()
print("[OK] Figure 8 sauvegardée")

# ── Figure 9 : Évolution temporelle réel vs prédit ───────────────────────
monthly = df.groupby(df['date'].dt.to_period('M')).agg(
    lst_real=('lst_celsius','mean'),
    lst_pred=('lst_predicted','mean')
).reset_index()
monthly['date_dt'] = monthly['date'].dt.to_timestamp()

fig, axes = plt.subplots(2, 1, figsize=(13, 7), sharex=True)
fig.suptitle('Suivi temporel de la LST : Réel vs Prédit (2018–2023)', fontsize=12, fontweight='bold')

axes[0].plot(monthly['date_dt'], monthly['lst_real'], label='LST réelle', color='#E53935', linewidth=1.8)
axes[0].plot(monthly['date_dt'], monthly['lst_pred'], label='LST prédite', color='#1E88E5', linewidth=1.8, linestyle='--')
axes[0].set_ylabel('LST (°C)', fontsize=10)
axes[0].legend(fontsize=9)
axes[0].grid(alpha=0.3)
axes[0].set_title('Moyennes mensuelles', fontsize=10)

err = monthly['lst_real'] - monthly['lst_pred']
axes[1].bar(monthly['date_dt'], err, color=np.where(err >= 0, '#EF9A9A', '#90CAF9'),
            width=20, alpha=0.85)
axes[1].axhline(0, color='black', linewidth=1)
axes[1].set_ylabel('Erreur (°C)', fontsize=10)
axes[1].set_xlabel('Date', fontsize=10)
axes[1].set_title('Erreur mensuelle (Réel − Prédit)', fontsize=10)
axes[1].grid(alpha=0.3, axis='y')

plt.tight_layout()
plt.savefig('/home/claude/tp_temperature/fig9_temporal_pred.png', dpi=150, bbox_inches='tight')
plt.close()
print("[OK] Figure 9 sauvegardée")

# ── Figure 10 : Profils de température par latitude ─────────────────────
fig, ax = plt.subplots(figsize=(10, 5))
lat_bins = pd.cut(df['latitude'], bins=20)
lat_profile = df.groupby(lat_bins)[['lst_celsius','lst_predicted']].mean()
lat_centers = [interval.mid for interval in lat_profile.index]
ax.plot(lat_centers, lat_profile['lst_celsius'],  'o-', color='#E53935', label='LST réelle', linewidth=2, markersize=5)
ax.plot(lat_centers, lat_profile['lst_predicted'],'s--',color='#1E88E5', label='LST prédite', linewidth=2, markersize=5)
ax.fill_between(lat_centers,
                lat_profile['lst_celsius'],
                lat_profile['lst_predicted'],
                alpha=0.15, color='gray')
ax.set_xlabel('Latitude (°)', fontsize=11)
ax.set_ylabel('LST moyenne (°C)', fontsize=11)
ax.set_title('Profil latitudinal de la température de surface', fontsize=12, fontweight='bold')
ax.legend(fontsize=10); ax.grid(alpha=0.3)
ax.axvline(0, color='gray', linestyle=':', linewidth=0.8)
ax.text(2, ax.get_ylim()[0]+1, 'Équateur', fontsize=8, color='gray')
plt.tight_layout()
plt.savefig('/home/claude/tp_temperature/fig10_profil_latitude.png', dpi=150, bbox_inches='tight')
plt.close()
print("[OK] Figure 10 sauvegardée")

print("\n✅ Toutes les visualisations générées avec succès.")
