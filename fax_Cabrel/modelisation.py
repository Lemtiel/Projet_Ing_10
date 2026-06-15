"""
Script 2 : Modélisation par régression - Prédiction LST
Projet ECAM-EPMI - Modélisation prédictive de la température de surface terrestre
"""

import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.model_selection import train_test_split, cross_val_score, KFold
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LinearRegression, Ridge, Lasso
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
from sklearn.inspection import permutation_importance
import joblib
import warnings
warnings.filterwarnings('ignore')

# ── Chargement ───────────────────────────────────────────────────────────
df = pd.read_csv('/home/claude/tp_temperature/dataset_LST_satellitaire.csv', parse_dates=['date'])

features = ['latitude','altitude_m','ndvi','albedo','cloud_cover_pct',
            'humidity_pct','insolation_wm2','day_of_year']
X = df[features].values
y = df['lst_celsius'].values

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

scaler = StandardScaler()
X_train_sc = scaler.fit_transform(X_train)
X_test_sc  = scaler.transform(X_test)

print("="*60)
print("MODÉLISATION PAR RÉGRESSION")
print("="*60)
print(f"Train : {X_train.shape[0]} | Test : {X_test.shape[0]}")

# ── Modèles ──────────────────────────────────────────────────────────────
models = {
    'Régression Linéaire': LinearRegression(),
    'Ridge (α=1.0)':       Ridge(alpha=1.0),
    'Lasso (α=0.1)':       Lasso(alpha=0.1, max_iter=5000),
    'Random Forest':       RandomForestRegressor(n_estimators=150, max_depth=12, random_state=42, n_jobs=-1),
    'Gradient Boosting':   GradientBoostingRegressor(n_estimators=200, max_depth=5, learning_rate=0.05, random_state=42),
}

results = {}
kf = KFold(n_splits=5, shuffle=True, random_state=42)

for name, model in models.items():
    if 'Forest' in name or 'Boosting' in name:
        model.fit(X_train, y_train)
        y_pred = model.predict(X_test)
        cv_scores = cross_val_score(model, X, y, cv=kf, scoring='r2', n_jobs=-1)
    else:
        model.fit(X_train_sc, y_train)
        y_pred = model.predict(X_test_sc)
        cv_scores = cross_val_score(model, scaler.transform(X), y, cv=kf, scoring='r2')

    rmse = np.sqrt(mean_squared_error(y_test, y_pred))
    mae  = mean_absolute_error(y_test, y_pred)
    r2   = r2_score(y_test, y_pred)
    results[name] = {'RMSE': rmse, 'MAE': mae, 'R2': r2,
                     'CV_R2_mean': cv_scores.mean(), 'CV_R2_std': cv_scores.std(),
                     'y_pred': y_pred}
    print(f"\n{name}")
    print(f"  RMSE : {rmse:.3f}°C  |  MAE : {mae:.3f}°C  |  R² : {r2:.4f}")
    print(f"  CV R² : {cv_scores.mean():.4f} ± {cv_scores.std():.4f}")

# ── Meilleur modèle ───────────────────────────────────────────────────────
best_name = max(results, key=lambda k: results[k]['R2'])
print(f"\n🏆 Meilleur modèle : {best_name} (R² = {results[best_name]['R2']:.4f})")

# Sauvegarder résultats
res_df = pd.DataFrame({k: {m: v for m, v in r.items() if m != 'y_pred'}
                        for k, r in results.items()}).T
res_df.to_csv('/home/claude/tp_temperature/resultats_modeles.csv')

# ── Figure 5 : Comparaison des modèles ───────────────────────────────────
fig, axes = plt.subplots(1, 3, figsize=(14, 5))
fig.suptitle('Comparaison des modèles de régression', fontsize=13, fontweight='bold')
model_names = list(results.keys())
short_names = ['Lin.','Ridge','Lasso','RF','GBM']
colors_bar = ['#90CAF9','#42A5F5','#1E88E5','#E57373','#C62828']

for ax, metric, ylabel in zip(axes, ['R2','RMSE','MAE'], ['R²','RMSE (°C)','MAE (°C)']):
    vals = [results[n][metric] for n in model_names]
    bars = ax.bar(short_names, vals, color=colors_bar, edgecolor='white')
    ax.set_title(ylabel, fontweight='bold')
    ax.set_ylabel(ylabel)
    for bar, val in zip(bars, vals):
        ax.text(bar.get_x()+bar.get_width()/2, bar.get_height()+0.001*max(vals),
                f'{val:.3f}', ha='center', va='bottom', fontsize=8.5, fontweight='bold')
    ax.grid(axis='y', alpha=0.3)
plt.tight_layout()
plt.savefig('/home/claude/tp_temperature/fig5_comparaison_modeles.png', dpi=150, bbox_inches='tight')
plt.close()
print("[OK] Figure 5 sauvegardée")

# ── Figure 6 : Valeurs réelles vs prédites (meilleur modèle) ─────────────
best_pred = results[best_name]['y_pred']
fig, axes = plt.subplots(1, 2, figsize=(13, 5))
fig.suptitle(f'Performance du meilleur modèle : {best_name}', fontsize=12, fontweight='bold')

axes[0].scatter(y_test, best_pred, alpha=0.35, s=12, color='#E53935')
lims = [min(y_test.min(), best_pred.min()), max(y_test.max(), best_pred.max())]
axes[0].plot(lims, lims, 'k--', linewidth=1.5, label='Prédiction parfaite')
axes[0].set_xlabel('LST réelle (°C)', fontsize=10)
axes[0].set_ylabel('LST prédite (°C)', fontsize=10)
axes[0].set_title(f'Réel vs Prédit (R²={results[best_name]["R2"]:.4f})')
axes[0].legend(); axes[0].grid(alpha=0.3)

residuals = y_test - best_pred
axes[1].hist(residuals, bins=40, color='#1E88E5', edgecolor='white', alpha=0.85)
axes[1].axvline(0, color='red', linestyle='--', linewidth=1.5)
axes[1].axvline(residuals.mean(), color='orange', linestyle='--', linewidth=1.5,
                label=f'Moyenne : {residuals.mean():.3f}°C')
axes[1].set_xlabel('Résidus (°C)', fontsize=10)
axes[1].set_ylabel('Fréquence', fontsize=10)
axes[1].set_title(f'Distribution des résidus (RMSE={results[best_name]["RMSE"]:.3f}°C)')
axes[1].legend(); axes[1].grid(alpha=0.3)
plt.tight_layout()
plt.savefig('/home/claude/tp_temperature/fig6_residus.png', dpi=150, bbox_inches='tight')
plt.close()
print("[OK] Figure 6 sauvegardée")

# ── Figure 7 : Importance des variables ─────────────────────────────────
best_model_obj = models[best_name]
if hasattr(best_model_obj, 'feature_importances_'):
    importances = best_model_obj.feature_importances_
else:
    perm = permutation_importance(best_model_obj, X_test_sc, y_test, n_repeats=10, random_state=42)
    importances = perm.importances_mean

sorted_idx = np.argsort(importances)
fig, ax = plt.subplots(figsize=(9, 5))
colors_imp = plt.cm.RdYlGn(np.linspace(0.2, 0.85, len(features)))
bars = ax.barh([features[i] for i in sorted_idx], importances[sorted_idx],
               color=colors_imp, edgecolor='white')
ax.set_xlabel("Importance relative", fontsize=10)
ax.set_title(f"Importance des variables — {best_name}", fontsize=12, fontweight='bold')
ax.grid(axis='x', alpha=0.3)
for bar, val in zip(bars, importances[sorted_idx]):
    ax.text(bar.get_width()+0.002, bar.get_y()+bar.get_height()/2,
            f'{val:.4f}', va='center', fontsize=8.5)
plt.tight_layout()
plt.savefig('/home/claude/tp_temperature/fig7_importance.png', dpi=150, bbox_inches='tight')
plt.close()
print("[OK] Figure 7 sauvegardée")

# ── Sauvegarder modèle ────────────────────────────────────────────────────
joblib.dump(best_model_obj, '/home/claude/tp_temperature/meilleur_modele.pkl')
joblib.dump(scaler, '/home/claude/tp_temperature/scaler.pkl')
print(f"\n✅ Modèle {best_name} sauvegardé.")
