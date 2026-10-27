"""
Quick script to regenerate fig19, fig20, fig22 with VERTICAL layouts.
Uses pre-saved results to avoid re-running expensive ML computations.
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from scipy import stats
from scipy.cluster.hierarchy import dendrogram, linkage
import os
import warnings
warnings.filterwarnings('ignore')

from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
from sklearn.ensemble import RandomForestRegressor
import xgboost as xgb
import shap

# ─── Configuration ────────────────────────────────────────────────────
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, 'data')
RESULTS_DIR = os.path.join(BASE_DIR, 'results')
FIGURES_DIR = os.path.join(BASE_DIR, 'figures')

plt.rcParams.update({
    'figure.dpi': 300, 'savefig.dpi': 300,
    'font.family': 'sans-serif', 'font.size': 11,
    'axes.titlesize': 14, 'axes.labelsize': 12,
    'xtick.labelsize': 10, 'ytick.labelsize': 10,
    'legend.fontsize': 10, 'axes.spines.top': False, 'axes.spines.right': False,
})

COLORS = {
    'primary': '#2563EB', 'secondary': '#7C3AED', 'accent': '#059669',
    'warm': '#DC2626', 'orange': '#EA580C', 'teal': '#0D9488',
    'slate': '#475569', 'bg': '#FAFBFC', 'grid': '#E2E8F0', 'gold': '#D97706',
}

# ─── Load Data ────────────────────────────────────────────────────────
df = pd.read_csv(os.path.join(DATA_DIR, 'unified_state_dataset.csv'))
target_col = 'CE_Behavior_Score'
y = df[target_col].values
state_names = df['State'].values

feature_cols = [
    'Tele_Density_Percent', 'UPI_PerCapita_Transactions',
    'Per_Capita_NSDP_Rs', 'Literacy_Rate_Percent',
    'Urban_Percent', 'Population_Mn'
]
X = df[feature_cols].values

# Load pre-saved results
nested_df = pd.read_csv(os.path.join(RESULTS_DIR, 'nested_cv_results.csv'))
stability_df = pd.read_csv(os.path.join(RESULTS_DIR, 'repeated_kfold_stability.csv'))

print("Loaded data and pre-saved results.")

# ─── Fit models needed for figures (fast) ─────────────────────────────
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

# XGBoost for SHAP
xgb_for_shap = xgb.XGBRegressor(
    n_estimators=100, max_depth=2, learning_rate=0.1,
    min_child_weight=3, reg_alpha=1.0, reg_lambda=2.0,
    random_state=42, verbosity=0
)
xgb_for_shap.fit(X, y)
xgb_importance = xgb_for_shap.feature_importances_

explainer = shap.TreeExplainer(xgb_for_shap)
shap_values = explainer.shap_values(X)
mean_shap = np.abs(shap_values).mean(axis=0)

# Clustering
best_k = 2  # From previous run
km_final = KMeans(n_clusters=best_k, random_state=42, n_init=20)
cluster_labels = km_final.fit_predict(X_scaled)

cluster_names = {}
cp_list = []
for c in range(best_k):
    mask = cluster_labels == c
    mean_dci = df.loc[mask, 'DCI'].mean()
    cp_list.append((c, mean_dci))
cp_list.sort(key=lambda x: -x[1])
name_options = ['Digital Leaders', 'Emerging States']
for i, (c, _) in enumerate(cp_list):
    cluster_names[c] = name_options[i]

linkage_matrix = linkage(X_scaled, method='ward')

# RF for fig22
rf_for_compare = RandomForestRegressor(n_estimators=500, max_depth=3,
                                        min_samples_leaf=3, random_state=42)
rf_for_compare.fit(X, y)
rf_imp = rf_for_compare.feature_importances_

# Repeated K-Fold scores (re-run quickly for violin plot data)
from sklearn.model_selection import RepeatedKFold, cross_val_score
from sklearn.linear_model import Ridge, Lasso, ElasticNet
from sklearn.pipeline import Pipeline

rkf = RepeatedKFold(n_splits=4, n_repeats=100, random_state=42)
stability_models = {
    'Ridge': Pipeline([('scaler', StandardScaler()), ('model', Ridge(alpha=1.0))]),
    'Lasso': Pipeline([('scaler', StandardScaler()), ('model', Lasso(alpha=0.5, max_iter=10000))]),
    'ElasticNet': Pipeline([('scaler', StandardScaler()), ('model', ElasticNet(alpha=0.5, l1_ratio=0.5, max_iter=10000))]),
    'Random Forest': Pipeline([('scaler', StandardScaler()),
                               ('model', RandomForestRegressor(n_estimators=500, max_depth=3,
                                                               min_samples_leaf=3, random_state=42))]),
    'XGBoost': Pipeline([('scaler', StandardScaler()),
                         ('model', xgb.XGBRegressor(n_estimators=100, max_depth=2,
                                                    learning_rate=0.1, reg_alpha=1.0,
                                                    reg_lambda=2.0, random_state=42, verbosity=0))]),
}

print("Running repeated K-Fold for violin plot data...")
stability_results = {}
for name, pipeline in stability_models.items():
    scores = cross_val_score(pipeline, X, y, cv=rkf, scoring='r2', n_jobs=-1)
    stability_results[name] = scores
    print(f"  {name}: Mean R²={scores.mean():.4f}")

print("\nAll models fitted. Generating figures...\n")

# ─── FIGURE 17: SHAP Beeswarm ─────────────────────────────────────────
print("[0/5] Generating fig17 (SHAP beeswarm)...")
fig, ax = plt.subplots(figsize=(12, 7))
# Use X_df if we had it, but X and feature_cols works for summary_plot
shap.summary_plot(shap_values, X, feature_names=feature_cols,
                  show=False, plot_size=None)
# Title removed
plt.tight_layout()
plt.savefig(os.path.join(FIGURES_DIR, 'fig17_shap_beeswarm.jpg'), bbox_inches='tight', dpi=300)
plt.close()

# ─── FIGURE 21: PCA Biplot ───────────────────────────────────────────
print("[0/5] Generating fig21 (PCA biplot)...")
from sklearn.decomposition import PCA
pca = PCA(n_components=2)
X_pca = pca.fit_transform(X_scaled)
var_explained = pca.explained_variance_ratio_
loadings = pd.DataFrame(pca.components_.T, index=feature_cols, columns=['PC1', 'PC2'])

fig, ax = plt.subplots(figsize=(14, 10))
ax.set_facecolor(COLORS['bg'])
cluster_colors = [COLORS['primary'], COLORS['accent'], COLORS['warm'],
                  COLORS['orange'], COLORS['secondary'], COLORS['teal']]

for c in range(best_k):
    mask = cluster_labels == c
    cname = cluster_names[c]
    ax.scatter(X_pca[mask, 0], X_pca[mask, 1],
              c=cluster_colors[c % len(cluster_colors)], s=150, alpha=0.8,
              edgecolors='white', linewidth=2, label=cname, zorder=3)

for i, state in enumerate(state_names):
    ax.annotate(state, (X_pca[i, 0], X_pca[i, 1]),
                fontsize=8, fontweight='bold', alpha=0.8,
                ha='center', va='bottom', xytext=(0, 8), textcoords='offset points')

arrow_scale = 3.0
for i, feat in enumerate(feature_cols):
    ax.annotate('', xy=(loadings.iloc[i, 0] * arrow_scale, loadings.iloc[i, 1] * arrow_scale),
                xytext=(0, 0), arrowprops=dict(arrowstyle='->', color=COLORS['warm'], lw=2))
    ax.text(loadings.iloc[i, 0] * arrow_scale * 1.15,
            loadings.iloc[i, 1] * arrow_scale * 1.15,
            feat.replace('_', '\n'), fontsize=8, color=COLORS['warm'],
            ha='center', va='center', fontweight='bold',
            bbox=dict(boxstyle='round,pad=0.2', facecolor='white', alpha=0.7))

ax.set_xlabel(f'PC1 ({var_explained[0]*100:.1f}% variance explained)', fontsize=13, fontweight='bold')
ax.set_ylabel(f'PC2 ({var_explained[1]*100:.1f}% variance explained)', fontsize=13, fontweight='bold')
# Title removed
ax.legend(fontsize=11, loc='best', framealpha=0.9)
ax.grid(True, alpha=0.2)
ax.axhline(0, color='black', linewidth=0.5, alpha=0.3)
ax.axvline(0, color='black', linewidth=0.5, alpha=0.3)
plt.tight_layout()
plt.savefig(os.path.join(FIGURES_DIR, 'fig21_pca_biplot.jpg'), bbox_inches='tight', dpi=300)
plt.close()


# ═══════════════════════════════════════════════════════════════════════
#  FIGURE 19: SHAP Waterfall — VERTICAL (2, 1)
# ═══════════════════════════════════════════════════════════════════════
print("[1/3] Generating fig19 (SHAP waterfall — vertical)...")
fig, axes = plt.subplots(2, 1, figsize=(10, 14))

max_idx = np.argmax(y)
min_idx = np.argmin(y)

for ax_idx, (state_idx, title_prefix) in enumerate([(max_idx, 'Highest CE'), (min_idx, 'Lowest CE')]):
    ax = axes[ax_idx]
    state = state_names[state_idx]
    sv = shap_values[state_idx]
    base_value = explainer.expected_value

    feat_order = np.argsort(np.abs(sv))
    sv_sorted = sv[feat_order]
    feat_sorted = [feature_cols[i] for i in feat_order]

    colors_wf = [COLORS['accent'] if s > 0 else COLORS['warm'] for s in sv_sorted]
    ax.barh(range(len(feature_cols)), sv_sorted, color=colors_wf,
            edgecolor='white', height=0.6)
    ax.set_yticks(range(len(feature_cols)))
    ax.set_yticklabels(feat_sorted, fontsize=10)
    ax.set_xlabel('SHAP Value (contribution to prediction)', fontsize=11, fontweight='bold')
    ax.set_title(f'{title_prefix}: {state}\n'
                 f'Actual={y[state_idx]:.1f}, Predicted={xgb_for_shap.predict(X[state_idx:state_idx+1])[0]:.1f}, '
                 f'Base={base_value:.1f}',
                 fontsize=12, fontweight='bold')
    ax.axvline(0, color='black', linewidth=0.8)
    ax.grid(axis='x', alpha=0.2)

    for i, s in enumerate(sv_sorted):
        ax.text(s + (0.2 if s >= 0 else -0.2), i, f'{s:+.2f}',
                va='center', ha='left' if s >= 0 else 'right', fontsize=9)

# fig.suptitle('Figure 19: SHAP State Explanations — Why do states score differently?\n'
#              'Green = pushes score UP | Red = pushes score DOWN',
#              fontsize=14, fontweight='bold', y=1.02)
plt.tight_layout()
plt.savefig(os.path.join(FIGURES_DIR, 'fig19_shap_waterfall.jpg'), bbox_inches='tight', dpi=300)
plt.close()
print("  ✅ Saved fig19_shap_waterfall.jpg")


# ═══════════════════════════════════════════════════════════════════════
#  FIGURE 20: Clustering — VERTICAL (3, 1)
# ═══════════════════════════════════════════════════════════════════════
print("[2/3] Generating fig20 (clustering — vertical)...")
fig = plt.figure(figsize=(10, 21))
gs = gridspec.GridSpec(3, 1, hspace=0.35)

# Panel A: Dendrogram
ax1 = fig.add_subplot(gs[0])
dendro = dendrogram(linkage_matrix, labels=state_names, ax=ax1,
                    leaf_rotation=45, leaf_font_size=9,
                    color_threshold=linkage_matrix[-best_k+1, 2])
ax1.set_title('Hierarchical Clustering Dendrogram (Ward Linkage)',
              fontsize=13, fontweight='bold')
ax1.set_ylabel('Distance', fontsize=11)

# Panel B: Scatter
ax2 = fig.add_subplot(gs[1])
cluster_colors = [COLORS['primary'], COLORS['accent'], COLORS['warm'],
                  COLORS['orange'], COLORS['secondary'], COLORS['teal']]
for c in range(best_k):
    mask = cluster_labels == c
    cname = cluster_names[c]
    ax2.scatter(df.loc[mask, 'Digital_Access_Score'],
               df.loc[mask, 'CE_Behavior_Score'],
               c=cluster_colors[c % len(cluster_colors)], s=120, alpha=0.8,
               edgecolors='white', linewidth=1.5, label=cname, zorder=3)
    for idx in np.where(mask)[0]:
        ax2.annotate(state_names[idx],
                     (df.iloc[idx]['Digital_Access_Score'], df.iloc[idx]['CE_Behavior_Score']),
                     fontsize=6, alpha=0.7, ha='center', va='bottom',
                     xytext=(0, 6), textcoords='offset points')

ax2.set_xlabel('Digital Access Score', fontsize=11, fontweight='bold')
ax2.set_ylabel('CE Behavior Score', fontsize=11, fontweight='bold')
ax2.set_title('State Clusters: Digital Access vs CE Behavior', fontsize=12, fontweight='bold')
ax2.legend(fontsize=9, loc='best')
ax2.grid(True, alpha=0.2)

# Panel C: Cluster profiles
ax3 = fig.add_subplot(gs[2])
profile_features = ['Digital_Access_Score', 'CE_Behavior_Score', 'Tele_Density_Percent',
                     'UPI_PerCapita_Transactions', 'SDG_Index_Score']
profile_labels = ['DA Score', 'CE Score', 'Tele-density', 'UPI/Cap', 'SDG Index']

profile_data = {}
for c in range(best_k):
    mask = cluster_labels == c
    profile_data[cluster_names[c]] = [
        df.loc[mask, feat].mean() / df[feat].max() * 100 for feat in profile_features
    ]

x_pos = np.arange(len(profile_labels))
width = 0.8 / best_k
for i, (cname, values) in enumerate(profile_data.items()):
    ax3.bar(x_pos + i * width, values, width, label=cname,
            color=cluster_colors[i % len(cluster_colors)], edgecolor='white', alpha=0.85)

ax3.set_xticks(x_pos + width * (best_k - 1) / 2)
ax3.set_xticklabels(profile_labels, fontsize=9)
ax3.set_ylabel('Normalized Score (% of max)', fontsize=11, fontweight='bold')
ax3.set_title('Cluster Profiles Comparison', fontsize=12, fontweight='bold')
ax3.legend(fontsize=8, loc='upper right')
ax3.grid(axis='y', alpha=0.3)

# fig.suptitle('Figure 20: State Clustering Analysis\n'
#              f'K-Means (k={best_k}) with Ward Hierarchical Dendrogram',
#              fontsize=15, fontweight='bold', y=1.01)
plt.savefig(os.path.join(FIGURES_DIR, 'fig20_clustering.jpg'), bbox_inches='tight', dpi=300)
plt.close()
print("  ✅ Saved fig20_clustering.jpg")


# ═══════════════════════════════════════════════════════════════════════
#  FIGURE 22: Comprehensive ML — VERTICAL (3, 1)
# ═══════════════════════════════════════════════════════════════════════
print("[3/3] Generating fig22 (comprehensive ML — vertical)...")
fig, axes = plt.subplots(3, 1, figsize=(10, 21))

# Panel A: Nested CV R²
ax = axes[0]
models_n = nested_df['Model'].values
r2_n = nested_df['Nested_R2'].values
colors_n = [COLORS['accent'] if r2 > 0 else COLORS['warm'] for r2 in r2_n]
ax.barh(range(len(models_n)), r2_n, color=colors_n, edgecolor='white', height=0.6)
ax.set_yticks(range(len(models_n)))
ax.set_yticklabels(models_n, fontsize=10)
ax.set_xlabel('Nested LOO-CV R²', fontsize=11, fontweight='bold')
ax.set_title('Nested CV\n(Leak-Free)', fontsize=12, fontweight='bold')
ax.axvline(0, color='black', linewidth=0.8)
for i, r2 in enumerate(r2_n):
    ax.text(max(r2, 0) + 0.01, i, f'{r2:.3f}', va='center', fontsize=9)
ax.grid(axis='x', alpha=0.3)

# Panel B: Repeated K-Fold Stability (violin)
ax = axes[1]
labels_rk = list(stability_results.keys())
positions = list(range(len(labels_rk)))

violins = ax.violinplot([stability_results[n] for n in labels_rk],
                        positions=positions, showmeans=True, showmedians=True)
for body in violins['bodies']:
    body.set_facecolor(COLORS['primary'])
    body.set_alpha(0.6)
violins['cmeans'].set_color(COLORS['warm'])
violins['cmedians'].set_color(COLORS['accent'])

ax.set_xticks(positions)
ax.set_xticklabels(labels_rk, fontsize=9, rotation=30, ha='right')
ax.set_ylabel('R² Score', fontsize=11, fontweight='bold')
ax.set_title('Repeated 4-Fold CV\n(100 repeats, R² distribution)', fontsize=12, fontweight='bold')
ax.grid(axis='y', alpha=0.3)
ax.axhline(0, color='black', linewidth=0.8, linestyle='--', alpha=0.5)

# Panel C: Feature Importance comparison
ax = axes[2]
comp_df = pd.DataFrame({
    'Feature': feature_cols,
    'SHAP': mean_shap / mean_shap.sum(),
    'XGBoost': xgb_importance / xgb_importance.sum(),
    'Random Forest': rf_imp / rf_imp.sum(),
})

x_pos = np.arange(len(feature_cols))
width = 0.25
ax.bar(x_pos - width, comp_df['SHAP'], width, label='SHAP', color=COLORS['primary'], alpha=0.85)
ax.bar(x_pos, comp_df['XGBoost'], width, label='XGBoost', color=COLORS['accent'], alpha=0.85)
ax.bar(x_pos + width, comp_df['Random Forest'], width, label='Random Forest', color=COLORS['orange'], alpha=0.85)
ax.set_xticks(x_pos)
ax.set_xticklabels([f.split('_')[0] for f in feature_cols], fontsize=8, rotation=30, ha='right')
ax.set_ylabel('Normalized Importance', fontsize=11, fontweight='bold')
ax.set_title('Feature Importance\n(3 methods compared)', fontsize=12, fontweight='bold')
ax.legend(fontsize=9)
ax.grid(axis='y', alpha=0.3)

# fig.suptitle('Figure 22: Comprehensive ML Validation Summary\n'
#              'Nested CV + Stability Analysis + Multi-Method Feature Importance',
#              fontsize=15, fontweight='bold', y=1.02)
plt.tight_layout()
plt.savefig(os.path.join(FIGURES_DIR, 'fig22_comprehensive_ml.jpg'), bbox_inches='tight', dpi=300)
plt.close()
print("  ✅ Saved fig22_comprehensive_ml.jpg")

print("\n" + "=" * 50)
print("  ✅ All 3 figures regenerated with vertical layouts!")
print("=" * 50)
