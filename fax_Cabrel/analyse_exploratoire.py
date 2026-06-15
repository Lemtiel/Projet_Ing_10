"""
Script 1 : Analyse exploratoire des données satellitaires LST
Projet ECAM-EPMI - Modélisation prédictive de la température de surface terrestre
"""

import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib.gridspec import GridSpec
import warnings
warnings.filterwarnings('ignore')

# ── Chargement des données ──────────────────────────────────────────────────
df = pd.read_csv('/home/claude/tp_temperature/dataset_LST_satellitaire.csv', parse_dates=['date'])
print("="*60)
print("ANALYSE EXPLORATOIRE DES DONNÉES")
print("="*60)
print(f"\nDimensions : {df.shape[0]} observations × {df.shape[1]} variables")
print(f"\nVariables :\n{df.dtypes}")
print(f"\nValeurs manquantes :\n{df.isnull().sum()}")
print(f"\nStatistiques descriptives :\n{df.describe().round(3)}")

features = ['latitude','altitude_m','ndvi','albedo','cloud_cover_pct',
            'humidity_pct','insolation_wm2','day_of_year']

# ── Figure 1 : Distribution de la variable cible ──────────────────────────
fig, axes = plt.subplots(1, 2, figsize=(12, 4))
fig.suptitle('Distribution de la Température de Surface (LST)', fontsize=14, fontweight='bold')
axes[0].hist(df['lst_celsius'], bins=50, color='#E84545', edgecolor='white', alpha=0.85)
axes[0].axvline(df['lst_celsius'].mean(), color='navy', linestyle='--', linewidth=2, label=f"Moyenne : {df['lst_celsius'].mean():.1f}°C")
axes[0].set_xlabel('LST (°C)'); axes[0].set_ylabel('Fréquence'); axes[0].legend()
axes[0].set_title('Histogramme')
axes[1].boxplot(df['lst_celsius'], vert=True, patch_artist=True,
                boxprops=dict(facecolor='#E84545', alpha=0.7))
axes[1].set_ylabel('LST (°C)'); axes[1].set_title('Boîte à moustaches')
plt.tight_layout()
plt.savefig('/home/claude/tp_temperature/fig1_distribution_LST.png', dpi=150, bbox_inches='tight')
plt.close()
print("\n[OK] Figure 1 sauvegardée")

# ── Figure 2 : Corrélations ──────────────────────────────────────────────
fig, ax = plt.subplots(figsize=(10, 8))
corr_cols = features + ['lst_celsius']
corr = df[corr_cols].corr()
mask = np.triu(np.ones_like(corr, dtype=bool))
sns.heatmap(corr, mask=mask, annot=True, fmt='.2f', cmap='RdBu_r',
            center=0, square=True, ax=ax, cbar_kws={'shrink': 0.8},
            annot_kws={'size': 9})
ax.set_title('Matrice de corrélation', fontsize=13, fontweight='bold')
plt.tight_layout()
plt.savefig('/home/claude/tp_temperature/fig2_correlation.png', dpi=150, bbox_inches='tight')
plt.close()
print("[OK] Figure 2 sauvegardée")

# ── Figure 3 : LST vs variables clés ─────────────────────────────────────
fig = plt.figure(figsize=(14, 10))
gs = GridSpec(2, 3, figure=fig, hspace=0.4, wspace=0.35)
plot_vars = [
    ('latitude','Latitude (°)'),
    ('insolation_wm2','Insolation (W/m²)'),
    ('altitude_m','Altitude (m)'),
    ('ndvi','NDVI'),
    ('albedo','Albedo'),
    ('humidity_pct','Humidité (%)'),
]
colors = ['#2196F3','#FF5722','#4CAF50','#9C27B0','#FF9800','#00BCD4']
for i, ((var, label), color) in enumerate(zip(plot_vars, colors)):
    ax = fig.add_subplot(gs[i//3, i%3])
    ax.scatter(df[var], df['lst_celsius'], alpha=0.15, s=8, color=color)
    z = np.polyfit(df[var], df['lst_celsius'], 1)
    p = np.poly1d(z)
    x_line = np.linspace(df[var].min(), df[var].max(), 100)
    ax.plot(x_line, p(x_line), 'k--', linewidth=1.5)
    r = df[[var,'lst_celsius']].corr().iloc[0,1]
    ax.set_xlabel(label, fontsize=9)
    ax.set_ylabel('LST (°C)', fontsize=9)
    ax.set_title(f'r = {r:.3f}', fontsize=10, fontweight='bold')
    ax.tick_params(labelsize=8)
fig.suptitle('Relations entre LST et variables géophysiques', fontsize=13, fontweight='bold')
plt.savefig('/home/claude/tp_temperature/fig3_scatter_features.png', dpi=150, bbox_inches='tight')
plt.close()
print("[OK] Figure 3 sauvegardée")

# ── Figure 4 : Évolution temporelle ──────────────────────────────────────
fig, axes = plt.subplots(2, 1, figsize=(13, 7), sharex=True)
monthly = df.groupby(['year','month'])['lst_celsius'].agg(['mean','std']).reset_index()
monthly['date_plot'] = pd.to_datetime(monthly[['year','month']].assign(day=1))
axes[0].plot(monthly['date_plot'], monthly['mean'], color='#E84545', linewidth=2, label='Moyenne mensuelle')
axes[0].fill_between(monthly['date_plot'],
                     monthly['mean'] - monthly['std'],
                     monthly['mean'] + monthly['std'],
                     alpha=0.25, color='#E84545', label='±1 écart-type')
axes[0].set_ylabel('LST (°C)', fontsize=10)
axes[0].set_title('Évolution temporelle de la LST (2018–2023)', fontsize=12, fontweight='bold')
axes[0].legend(); axes[0].grid(alpha=0.3)

yearly_mean = df.groupby('year')['lst_celsius'].mean()
axes[1].bar(yearly_mean.index, yearly_mean.values, color='#2196F3', alpha=0.8, edgecolor='white')
axes[1].axhline(yearly_mean.mean(), color='red', linestyle='--', linewidth=1.5, label=f'Moyenne globale : {yearly_mean.mean():.2f}°C')
axes[1].set_xlabel('Année', fontsize=10); axes[1].set_ylabel('LST moy. (°C)', fontsize=10)
axes[1].set_title('Moyenne annuelle', fontsize=11, fontweight='bold')
axes[1].legend(); axes[1].grid(alpha=0.3, axis='y')
plt.tight_layout()
plt.savefig('/home/claude/tp_temperature/fig4_temporal.png', dpi=150, bbox_inches='tight')
plt.close()
print("[OK] Figure 4 sauvegardée")

print("\n✅ Analyse exploratoire terminée.")
