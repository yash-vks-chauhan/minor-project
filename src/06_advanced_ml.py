"""
=============================================================================
 ADVANCED ML ANALYSIS v1 — SHAP, XGBoost, Clustering, Nested CV, PCA
 Research: Digital Inclusion as a Driver of Circular Economy Behavior in India
 Author: Yash Chauhan
 Date: February 2026
=============================================================================
 This script adds 6 advanced ML analyses that significantly strengthen
 the research paper's predictive and interpretive claims:

 ANALYSIS 1: XGBoost Regression (state-of-the-art gradient boosting)
 ANALYSIS 2: Nested LOO-CV with GridSearch (leak-free hyperparameter tuning)
 ANALYSIS 3: Repeated K-Fold CV (stable R² estimates with confidence bands)
 ANALYSIS 4: SHAP Explainability (per-state, per-feature explanations)
 ANALYSIS 5: K-Means Clustering (natural state groupings)
 ANALYSIS 6: PCA Visualization (2D state landscape)
=============================================================================
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import seaborn as sns
from scipy import stats
from scipy.cluster.hierarchy import dendrogram, linkage, fcluster
import os
import warnings
warnings.filterwarnings('ignore')

# ─── sklearn imports ──────────────────────────────────────────────────
from sklearn.linear_model import Ridge, Lasso, ElasticNet
from sklearn.svm import SVR
from sklearn.ensemble import (
    RandomForestRegressor, GradientBoostingRegressor, StackingRegressor
)
from sklearn.model_selection import (
    LeaveOneOut, RepeatedKFold, cross_val_predict,
    cross_val_score, GridSearchCV
)
from sklearn.metrics import (
    mean_squared_error, mean_absolute_error, r2_score
)
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA

# ─── XGBoost & SHAP ──────────────────────────────────────────────────
import xgboost as xgb
import shap

# ─── Configuration ────────────────────────────────────────────────────
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, 'data')
RESULTS_DIR = os.path.join(BASE_DIR, 'results')
FIGURES_DIR = os.path.join(BASE_DIR, 'figures')
os.makedirs(RESULTS_DIR, exist_ok=True)
os.makedirs(FIGURES_DIR, exist_ok=True)

# Publication-quality plot settings
plt.rcParams.update({
    'figure.dpi': 300,
    'savefig.dpi': 300,
    'font.family': 'sans-serif',
    'font.size': 11,
    'axes.titlesize': 14,
    'axes.labelsize': 12,
    'xtick.labelsize': 10,
    'ytick.labelsize': 10,
    'legend.fontsize': 10,
    'axes.spines.top': False,
    'axes.spines.right': False,
})

COLORS = {
    'primary': '#2563EB',
    'secondary': '#7C3AED',
    'accent': '#059669',
    'warm': '#DC2626',
    'orange': '#EA580C',
    'teal': '#0D9488',
    'slate': '#475569',
    'bg': '#FAFBFC',
    'grid': '#E2E8F0',
    'gold': '#D97706',
}

print("=" * 70)
print("  ADVANCED ML ANALYSIS v1")
print("  SHAP · XGBoost · Nested CV · Clustering · PCA")
print("=" * 70)

# ─── Load Data ────────────────────────────────────────────────────────
df = pd.read_csv(os.path.join(DATA_DIR, 'unified_state_dataset.csv'))
print(f"\n  Loaded: {len(df)} states, {len(df.columns)} features")

target_col = 'CE_Behavior_Score'
y = df[target_col].values
state_names = df['State'].values

# Full feature set (same as 05_predictive_modeling.py)
feature_cols = [
    'Tele_Density_Percent', 'UPI_PerCapita_Transactions',
    'Per_Capita_NSDP_Rs', 'Literacy_Rate_Percent',
    'Urban_Percent', 'Population_Mn'
]
feature_labels = [
    'Tele-density\n(TRAI)', 'UPI/Capita\n(NPCI)', 'NSDP/Cap\n(RBI)',
    'Literacy\n(Census)', 'Urbanization\n(Census)', 'Population\n(Census)'
]

X = df[feature_cols].values
X_df = df[feature_cols]

print(f"  Features: {feature_cols}")
print(f"  Target: {target_col}")


# ═══════════════════════════════════════════════════════════════════════
#  ANALYSIS 1: XGBOOST REGRESSION
#  State-of-the-art gradient boosting — the most cited ML model in
#  research papers. Conservative hyperparameters for small n.
# ═══════════════════════════════════════════════════════════════════════
print(f"\n{'━' * 70}")
print("  ANALYSIS 1: XGBoost Regression")
print("  The most widely-used ML model in applied research")
print(f"{'━' * 70}")

# XGBoost with conservative hyperparameters for n=16
xgb_model = xgb.XGBRegressor(
    n_estimators=100,
    max_depth=2,
    learning_rate=0.1,
    min_child_weight=3,
    subsample=0.8,
    colsample_bytree=0.8,
    reg_alpha=1.0,       # L1 regularization (helps with small n)
    reg_lambda=2.0,       # L2 regularization
    random_state=42,
    verbosity=0
)

# LOO-CV prediction
loo = LeaveOneOut()
y_pred_xgb = cross_val_predict(xgb_model, X, y, cv=loo)
r2_xgb = r2_score(y, y_pred_xgb)
rmse_xgb = np.sqrt(mean_squared_error(y, y_pred_xgb))
mae_xgb = mean_absolute_error(y, y_pred_xgb)
r_xgb, p_xgb = stats.pearsonr(y, y_pred_xgb)

print(f"\n  XGBoost LOO-CV Results:")
print(f"    R²:   {r2_xgb:.4f}")
print(f"    RMSE: {rmse_xgb:.2f}")
print(f"    MAE:  {mae_xgb:.2f}")
print(f"    r:    {r_xgb:.4f} (p={p_xgb:.4f}) {'✅ Significant' if p_xgb < 0.05 else '⚠️'}")

# Fit on full data for feature importance / SHAP
xgb_model.fit(X, y)
xgb_importance = xgb_model.feature_importances_

print(f"\n  XGBoost Feature Importance:")
for feat, imp in sorted(zip(feature_cols, xgb_importance), key=lambda x: -x[1]):
    bar = '█' * int(imp * 40)
    print(f"    {feat:35s} {imp:.4f}  {bar}")


# ═══════════════════════════════════════════════════════════════════════
#  ANALYSIS 2: NESTED LOO-CV WITH GRIDSEARCH
#  Problem: In 05_predictive_modeling.py, hyperparameters were fixed.
#  This means the "best model" might be best only for those params.
#  Solution: Nested CV — inner loop tunes params, outer loop evaluates.
#  This is the gold standard for small-sample ML evaluation.
# ═══════════════════════════════════════════════════════════════════════
print(f"\n{'━' * 70}")
print("  ANALYSIS 2: Nested LOO-CV with GridSearch")
print("  Leak-free hyperparameter tuning (inner CV inside outer LOO)")
print(f"{'━' * 70}")

# Define models with param grids
nested_models = {
    'Ridge': {
        'pipeline': Pipeline([('scaler', StandardScaler()), ('model', Ridge())]),
        'params': {'model__alpha': [0.01, 0.1, 0.5, 1.0, 5.0, 10.0, 50.0]}
    },
    'Lasso': {
        'pipeline': Pipeline([('scaler', StandardScaler()), ('model', Lasso(max_iter=10000))]),
        'params': {'model__alpha': [0.01, 0.05, 0.1, 0.5, 1.0, 5.0]}
    },
    'ElasticNet': {
        'pipeline': Pipeline([('scaler', StandardScaler()), ('model', ElasticNet(max_iter=10000))]),
        'params': {
            'model__alpha': [0.01, 0.1, 0.5, 1.0, 5.0],
            'model__l1_ratio': [0.1, 0.3, 0.5, 0.7, 0.9]
        }
    },
    'SVR': {
        'pipeline': Pipeline([('scaler', StandardScaler()), ('model', SVR(kernel='rbf'))]),
        'params': {
            'model__C': [0.1, 1.0, 10.0, 50.0],
            'model__epsilon': [0.1, 0.5, 1.0],
            'model__gamma': ['scale', 'auto']
        }
    },
    'Random Forest': {
        'pipeline': Pipeline([('scaler', StandardScaler()),
                              ('model', RandomForestRegressor(random_state=42, n_jobs=-1))]),
        'params': {
            'model__n_estimators': [100, 300, 500],
            'model__max_depth': [2, 3, 4],
            'model__min_samples_leaf': [2, 3, 4]
        }
    },
    'XGBoost': {
        'pipeline': Pipeline([('scaler', StandardScaler()),
                              ('model', xgb.XGBRegressor(random_state=42, verbosity=0))]),
        'params': {
            'model__n_estimators': [50, 100, 200],
            'model__max_depth': [2, 3],
            'model__learning_rate': [0.05, 0.1, 0.2],
            'model__reg_alpha': [0, 0.5, 1.0],
            'model__reg_lambda': [1.0, 2.0]
        }
    },
}

nested_results = []

for name, config in nested_models.items():
    # Outer loop: LOO-CV
    y_pred_nested = np.zeros(len(y))

    for train_idx, test_idx in loo.split(X):
        X_train, X_test = X[train_idx], X[test_idx]
        y_train, y_test = y[train_idx], y[test_idx]

        # Inner loop: GridSearch with LOO on the training set
        inner_cv = LeaveOneOut()
        grid = GridSearchCV(
            config['pipeline'], config['params'],
            cv=inner_cv, scoring='r2', n_jobs=-1, refit=True
        )
        grid.fit(X_train, y_train)
        y_pred_nested[test_idx] = grid.predict(X_test)

    r2_nested = r2_score(y, y_pred_nested)
    rmse_nested = np.sqrt(mean_squared_error(y, y_pred_nested))
    mae_nested = mean_absolute_error(y, y_pred_nested)
    r_nested, p_nested = stats.pearsonr(y, y_pred_nested)

    nested_results.append({
        'Model': name,
        'Nested_R2': r2_nested,
        'RMSE': rmse_nested,
        'MAE': mae_nested,
        'Pearson_r': r_nested,
        'Pearson_p': p_nested,
    })

    sig = '✅' if p_nested < 0.05 else '⚠️'
    print(f"  {name:20s}  Nested R²={r2_nested:+.4f}  RMSE={rmse_nested:.2f}  r={r_nested:.3f} {sig}")

nested_df = pd.DataFrame(nested_results).sort_values('Nested_R2', ascending=False)
best_nested = nested_df.iloc[0]
print(f"\n  🏆 Best (Nested CV): {best_nested['Model']} — R²={best_nested['Nested_R2']:.4f}")
print(f"  → This is the MOST RELIABLE R² estimate (no data leakage at all)")


# ═══════════════════════════════════════════════════════════════════════
#  ANALYSIS 3: REPEATED K-FOLD CV (Stability Analysis)
#  LOO-CV can have high variance. Repeated K-Fold (100 repeats × 4 folds)
#  gives 400 different train/test splits → stable R² with CI.
# ═══════════════════════════════════════════════════════════════════════
print(f"\n{'━' * 70}")
print("  ANALYSIS 3: Repeated K-Fold CV (Stability Analysis)")
print("  100 repeats × 4 folds = 400 different train/test splits")
print(f"{'━' * 70}")

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

stability_results = {}
stability_summary = []

for name, pipeline in stability_models.items():
    scores = cross_val_score(pipeline, X, y, cv=rkf, scoring='r2')
    stability_results[name] = scores

    ci_low, ci_high = np.percentile(scores, [2.5, 97.5])
    stability_summary.append({
        'Model': name,
        'Mean_R2': scores.mean(),
        'Std_R2': scores.std(),
        'CI_Low': ci_low,
        'CI_High': ci_high,
        'Median_R2': np.median(scores),
        'Min_R2': scores.min(),
        'Max_R2': scores.max(),
    })

    print(f"  {name:20s}  Mean R²={scores.mean():.4f} ± {scores.std():.4f}  "
          f"95% CI=[{ci_low:.3f}, {ci_high:.3f}]")

stability_df = pd.DataFrame(stability_summary).sort_values('Mean_R2', ascending=False)
best_stable = stability_df.iloc[0]
print(f"\n  🏆 Most Stable: {best_stable['Model']} — Mean R²={best_stable['Mean_R2']:.4f}")


# ═══════════════════════════════════════════════════════════════════════
#  ANALYSIS 4: SHAP EXPLAINABILITY
#  SHAP (SHapley Additive exPlanations) provides:
#    - Global feature importance (unbiased, unlike RF importance)
#    - Per-state explanations (why Bihar scores low, why Karnataka high)
#    - Feature interaction effects
#  This is the #1 requested analysis by ML paper reviewers.
# ═══════════════════════════════════════════════════════════════════════
print(f"\n{'━' * 70}")
print("  ANALYSIS 4: SHAP Explainability Analysis")
print("  Model-agnostic feature attribution (Shapley values)")
print(f"{'━' * 70}")

# Fit XGBoost on full data for SHAP analysis
xgb_for_shap = xgb.XGBRegressor(
    n_estimators=100, max_depth=2, learning_rate=0.1,
    min_child_weight=3, reg_alpha=1.0, reg_lambda=2.0,
    random_state=42, verbosity=0
)
xgb_for_shap.fit(X, y)

# SHAP values
explainer = shap.TreeExplainer(xgb_for_shap)
shap_values = explainer.shap_values(X)
shap_df = pd.DataFrame(shap_values, columns=feature_cols, index=state_names)

# Global feature importance (mean |SHAP|)
mean_shap = np.abs(shap_values).mean(axis=0)
print(f"\n  SHAP Feature Importance (mean |SHAP value|):")
for feat, shap_imp in sorted(zip(feature_cols, mean_shap), key=lambda x: -x[1]):
    bar = '█' * int(shap_imp * 4)
    print(f"    {feat:35s} {shap_imp:.4f}  {bar}")

# Per-state breakdown for top/bottom states
print(f"\n  Per-State SHAP Breakdown (top 3 and bottom 3 by CE Score):")
df_sorted = df.sort_values(target_col, ascending=False)
for state in list(df_sorted['State'].head(3)) + list(df_sorted['State'].tail(3)):
    idx = list(state_names).index(state)
    ce_score = y[idx]
    top_feat = sorted(zip(feature_cols, shap_values[idx]), key=lambda x: -abs(x[1]))[:3]
    print(f"\n    {state} (CE={ce_score:.1f}):")
    for feat, sv in top_feat:
        direction = '↑' if sv > 0 else '↓'
        print(f"      {direction} {feat}: {sv:+.2f}")


# ── SHAP FIGURES ──────────────────────────────────────────────────────

# Figure 17: SHAP Beeswarm Plot
print(f"\n  Generating SHAP figures...")
fig, ax = plt.subplots(figsize=(12, 7))
shap.summary_plot(shap_values, X_df, feature_names=feature_cols,
                  show=False, plot_size=None)
# plt.title('Figure 17: SHAP Feature Impact on CE Behavior Score\n'
#           'Each dot = one state; color = feature value (red=high, blue=low)',
#           fontsize=13, fontweight='bold', pad=15)
plt.tight_layout()
plt.savefig(os.path.join(FIGURES_DIR, 'fig17_shap_beeswarm.jpg'), bbox_inches='tight', dpi=300)
plt.close()

# Figure 18: SHAP Bar Plot (mean absolute SHAP values)
fig, ax = plt.subplots(figsize=(10, 6))
sorted_idx = np.argsort(mean_shap)
colors_shap = [COLORS['primary'] if i >= len(mean_shap) - 3 else COLORS['slate']
               for i in range(len(mean_shap))]
ax.barh(range(len(feature_cols)), mean_shap[sorted_idx],
        color=[colors_shap[i] for i in sorted_idx],
        edgecolor='white', height=0.6, alpha=0.85)
ax.set_yticks(range(len(feature_cols)))
ax.set_yticklabels([feature_cols[i] for i in sorted_idx], fontsize=10)
ax.set_xlabel('Mean |SHAP Value| (Impact on CE Behavior Score)', fontsize=12, fontweight='bold')
# ax.set_title('Figure 18: SHAP Global Feature Importance\n'
#              'Unbiased feature attribution via Shapley values (XGBoost)',
#              fontsize=13, fontweight='bold')
for i, idx in enumerate(sorted_idx):
    ax.text(mean_shap[idx] + 0.1, i, f'{mean_shap[idx]:.2f}', va='center', fontsize=9)
ax.grid(axis='x', alpha=0.3)
plt.tight_layout()
plt.savefig(os.path.join(FIGURES_DIR, 'fig18_shap_importance.jpg'), bbox_inches='tight', dpi=300)
plt.close()

# Figure 19: SHAP Waterfall for Highest and Lowest CE States
fig, axes = plt.subplots(2, 1, figsize=(10, 14))

# Find highest and lowest CE states
max_idx = np.argmax(y)
min_idx = np.argmin(y)

for ax_idx, (state_idx, title_prefix) in enumerate([(max_idx, 'Highest CE'), (min_idx, 'Lowest CE')]):
    ax = axes[ax_idx]
    state = state_names[state_idx]
    sv = shap_values[state_idx]
    base_value = explainer.expected_value

    # Sort by absolute SHAP
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
#              fontsize=14, fontweight='bold', y=1.04)
plt.tight_layout()
plt.savefig(os.path.join(FIGURES_DIR, 'fig19_shap_waterfall.jpg'), bbox_inches='tight', dpi=300)
plt.close()


# ═══════════════════════════════════════════════════════════════════════
#  ANALYSIS 5: K-MEANS CLUSTERING
#  Identify natural groupings of states based on their digital and CE
#  profiles. Useful for policy recommendations.
# ═══════════════════════════════════════════════════════════════════════
print(f"\n{'━' * 70}")
print("  ANALYSIS 5: K-Means Clustering (State Groupings)")
print("  Identifying natural Digital-CE typologies")
print(f"{'━' * 70}")

# Scale features for clustering
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

# Find optimal k using silhouette score
from sklearn.metrics import silhouette_score

silhouette_scores = []
K_range = range(2, min(8, len(df)))
for k in K_range:
    km = KMeans(n_clusters=k, random_state=42, n_init=20)
    labels = km.fit_predict(X_scaled)
    sil = silhouette_score(X_scaled, labels)
    silhouette_scores.append(sil)
    print(f"    k={k}: Silhouette Score = {sil:.4f}")

best_k = list(K_range)[np.argmax(silhouette_scores)]
print(f"\n  Optimal k = {best_k} (highest silhouette score)")

# Fit final clustering
km_final = KMeans(n_clusters=best_k, random_state=42, n_init=20)
cluster_labels = km_final.fit_predict(X_scaled)

# Name clusters based on their characteristics
cluster_profiles = []
for c in range(best_k):
    mask = cluster_labels == c
    states_in_cluster = state_names[mask]
    mean_da = df.loc[mask, 'Digital_Access_Score'].mean()
    mean_ce = df.loc[mask, 'CE_Behavior_Score'].mean()
    mean_dci = df.loc[mask, 'DCI'].mean()
    cluster_profiles.append({
        'Cluster': c,
        'States': ', '.join(states_in_cluster),
        'n_States': len(states_in_cluster),
        'Mean_DA': mean_da,
        'Mean_CE': mean_ce,
        'Mean_DCI': mean_dci,
    })

# Sort clusters by DCI to assign meaningful names
cp_df = pd.DataFrame(cluster_profiles).sort_values('Mean_DCI', ascending=False)
cluster_names = {}
name_options = ['Digital Leaders', 'Emerging States', 'Developing States', 'Lagging States',
                'Transitioning States', 'Growth States']
for i, (_, row) in enumerate(cp_df.iterrows()):
    cname = name_options[i] if i < len(name_options) else f'Group {i+1}'
    cluster_names[row['Cluster']] = cname

print(f"\n  State Typologies ({best_k} clusters):")
for _, row in cp_df.iterrows():
    cname = cluster_names[row['Cluster']]
    print(f"\n    {cname} (n={row['n_States']}):")
    print(f"      Mean DA={row['Mean_DA']:.1f}, CE={row['Mean_CE']:.1f}, DCI={row['Mean_DCI']:.1f}")
    print(f"      States: {row['States']}")

# Add cluster labels to dataframe
df['Cluster'] = cluster_labels
df['Cluster_Name'] = df['Cluster'].map(cluster_names)

# Hierarchical clustering dendrogram
linkage_matrix = linkage(X_scaled, method='ward')

# Figure 20: Clustering Visualization
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

# Panel B: Scatter (Digital Access vs CE Behavior by cluster)
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

# Panel C: Cluster profiles radar-like comparison (bar chart)
ax3 = fig.add_subplot(gs[2])
profile_features = ['Digital_Access_Score', 'CE_Behavior_Score', 'Tele_Density_Percent',
                     'UPI_PerCapita_Transactions', 'SDG_Index_Score']
profile_labels = ['DA Score', 'CE Score', 'Tele-density', 'UPI/Cap', 'SDG Index']

# Normalize for comparison
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
#              fontsize=15, fontweight='bold', y=1.02)
plt.savefig(os.path.join(FIGURES_DIR, 'fig20_clustering.jpg'), bbox_inches='tight', dpi=300)
plt.close()


# ═══════════════════════════════════════════════════════════════════════
#  ANALYSIS 6: PCA VISUALIZATION
#  Project all states into 2D space based on their feature profiles.
#  Shows how states relate to each other in the digital-CE landscape.
# ═══════════════════════════════════════════════════════════════════════
print(f"\n{'━' * 70}")
print("  ANALYSIS 6: PCA Visualization (2D State Landscape)")
print(f"{'━' * 70}")

# PCA on scaled features
pca = PCA(n_components=2)
X_pca = pca.fit_transform(X_scaled)

var_explained = pca.explained_variance_ratio_
print(f"\n  PC1 explains {var_explained[0]*100:.1f}% of variance")
print(f"  PC2 explains {var_explained[1]*100:.1f}% of variance")
print(f"  Total:       {sum(var_explained)*100:.1f}%")

# PCA loadings
loadings = pd.DataFrame(
    pca.components_.T, index=feature_cols, columns=['PC1', 'PC2']
)
print(f"\n  PCA Loadings:")
for feat in feature_cols:
    print(f"    {feat:35s} PC1={loadings.loc[feat,'PC1']:+.3f}  PC2={loadings.loc[feat,'PC2']:+.3f}")

# Figure 21: PCA Biplot
fig, ax = plt.subplots(figsize=(14, 10))
ax.set_facecolor(COLORS['bg'])

# Plot states (colored by cluster)
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

# Plot feature loading arrows
arrow_scale = 3.0
for i, feat in enumerate(feature_cols):
    ax.annotate('', xy=(loadings.iloc[i, 0] * arrow_scale, loadings.iloc[i, 1] * arrow_scale),
                xytext=(0, 0),
                arrowprops=dict(arrowstyle='->', color=COLORS['warm'], lw=2))
    ax.text(loadings.iloc[i, 0] * arrow_scale * 1.15,
            loadings.iloc[i, 1] * arrow_scale * 1.15,
            feat.replace('_', '\n'), fontsize=8, color=COLORS['warm'],
            ha='center', va='center', fontweight='bold',
            bbox=dict(boxstyle='round,pad=0.2', facecolor='white', alpha=0.7))

ax.set_xlabel(f'PC1 ({var_explained[0]*100:.1f}% variance explained)', fontsize=13, fontweight='bold')
ax.set_ylabel(f'PC2 ({var_explained[1]*100:.1f}% variance explained)', fontsize=13, fontweight='bold')
# ax.set_title('Figure 21: PCA Biplot — State Positioning in Digital-CE Landscape\n'
#              'Arrows show feature loading directions; clusters colored by K-Means',
#              fontsize=14, fontweight='bold')
ax.legend(fontsize=11, loc='best', framealpha=0.9)
ax.grid(True, alpha=0.2)
ax.axhline(0, color='black', linewidth=0.5, alpha=0.3)
ax.axvline(0, color='black', linewidth=0.5, alpha=0.3)

plt.tight_layout()
plt.savefig(os.path.join(FIGURES_DIR, 'fig21_pca_biplot.jpg'), bbox_inches='tight', dpi=300)
plt.close()


# ═══════════════════════════════════════════════════════════════════════
#  COMPARATIVE SUMMARY: FIGURE 22
#  Side-by-side comparison: Fixed CV vs Nested CV vs Repeated K-Fold
# ═══════════════════════════════════════════════════════════════════════
print(f"\n{'━' * 70}")
print("  COMPREHENSIVE MODEL COMPARISON")
print(f"{'━' * 70}")

fig, axes = plt.subplots(3, 1, figsize=(10, 21))

# Panel A: Nested CV R² comparison
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

# Panel B: Repeated K-Fold Stability (violin/box)
ax = axes[1]
positions = []
labels_rk = []
for i, (name, scores) in enumerate(stability_results.items()):
    positions.append(i)
    labels_rk.append(name)

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

# Panel C: SHAP vs XGBoost vs RF Feature Importance
ax = axes[2]
# Random Forest importance
rf_for_compare = RandomForestRegressor(n_estimators=500, max_depth=3,
                                        min_samples_leaf=3, random_state=42)
rf_for_compare.fit(X, y)
rf_imp = rf_for_compare.feature_importances_

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
#              fontsize=15, fontweight='bold', y=1.04)
plt.tight_layout()
plt.savefig(os.path.join(FIGURES_DIR, 'fig22_comprehensive_ml.jpg'), bbox_inches='tight', dpi=300)
plt.close()


# ═══════════════════════════════════════════════════════════════════════
#  SAVE ALL RESULTS
# ═══════════════════════════════════════════════════════════════════════
print(f"\n{'━' * 70}")
print("  SAVING ALL RESULTS")
print(f"{'━' * 70}")

# CSVs
nested_df.to_csv(os.path.join(RESULTS_DIR, 'nested_cv_results.csv'), index=False)
stability_df.to_csv(os.path.join(RESULTS_DIR, 'repeated_kfold_stability.csv'), index=False)
shap_df.round(3).to_csv(os.path.join(RESULTS_DIR, 'shap_values_per_state.csv'))

cluster_output = df[['State', 'Digital_Access_Score', 'CE_Behavior_Score', 'DCI',
                      'Cluster', 'Cluster_Name']].copy()
cluster_output.to_csv(os.path.join(RESULTS_DIR, 'state_clusters.csv'), index=False)

# Comprehensive report
with open(os.path.join(RESULTS_DIR, 'advanced_ml_report.txt'), 'w') as f:
    f.write("=" * 80 + "\n")
    f.write("  ADVANCED ML ANALYSIS REPORT\n")
    f.write("  Research: Digital Inclusion × Circular Economy Behavior in India\n")
    f.write("  Date: February 2026\n")
    f.write("=" * 80 + "\n\n")

    f.write("─" * 80 + "\n")
    f.write("ANALYSIS 1: XGBoost Regression\n")
    f.write("─" * 80 + "\n")
    f.write(f"LOO-CV R²:  {r2_xgb:.4f}\n")
    f.write(f"RMSE:       {rmse_xgb:.4f}\n")
    f.write(f"MAE:        {mae_xgb:.4f}\n")
    f.write(f"Pearson r:  {r_xgb:.4f} (p={p_xgb:.6f})\n\n")

    f.write("─" * 80 + "\n")
    f.write("ANALYSIS 2: Nested LOO-CV (Leak-Free Hyperparameter Tuning)\n")
    f.write("─" * 80 + "\n")
    f.write(nested_df.to_string(index=False) + "\n")
    f.write(f"\nBest: {best_nested['Model']} — Nested R²={best_nested['Nested_R2']:.4f}\n")
    f.write(f"This is the MOST RELIABLE performance estimate.\n\n")

    f.write("─" * 80 + "\n")
    f.write("ANALYSIS 3: Repeated K-Fold CV (100 repeats × 4 folds)\n")
    f.write("─" * 80 + "\n")
    f.write(stability_df.to_string(index=False) + "\n")
    f.write(f"\nMost Stable: {best_stable['Model']} — Mean R²={best_stable['Mean_R2']:.4f}\n\n")

    f.write("─" * 80 + "\n")
    f.write("ANALYSIS 4: SHAP Explainability\n")
    f.write("─" * 80 + "\n")
    f.write("Global Feature Importance (mean |SHAP|):\n")
    for feat, sv in sorted(zip(feature_cols, mean_shap), key=lambda x: -x[1]):
        f.write(f"  {feat:35s} {sv:.4f}\n")
    f.write(f"\nPer-State SHAP Values saved to: results/shap_values_per_state.csv\n\n")

    f.write("─" * 80 + "\n")
    f.write(f"ANALYSIS 5: K-Means Clustering (k={best_k})\n")
    f.write("─" * 80 + "\n")
    for _, row in cp_df.iterrows():
        cname = cluster_names[row['Cluster']]
        f.write(f"\n{cname} (n={row['n_States']}):\n")
        f.write(f"  Mean DA={row['Mean_DA']:.1f}, CE={row['Mean_CE']:.1f}, DCI={row['Mean_DCI']:.1f}\n")
        f.write(f"  States: {row['States']}\n")

    f.write(f"\n\n{'─' * 80}\n")
    f.write("ANALYSIS 6: PCA\n")
    f.write("─" * 80 + "\n")
    f.write(f"PC1: {var_explained[0]*100:.1f}% variance explained\n")
    f.write(f"PC2: {var_explained[1]*100:.1f}% variance explained\n")
    f.write(f"Total: {sum(var_explained)*100:.1f}%\n\n")
    f.write("Loadings:\n")
    f.write(loadings.to_string() + "\n")

    f.write(f"\n\n{'=' * 80}\n")
    f.write("FIGURES GENERATED:\n")
    f.write("  fig17_shap_beeswarm.jpg     — SHAP beeswarm plot\n")
    f.write("  fig18_shap_importance.jpg   — SHAP global feature importance\n")
    f.write("  fig19_shap_waterfall.jpg    — SHAP per-state explanations\n")
    f.write("  fig20_clustering.jpg        — K-Means + dendrogram + profiles\n")
    f.write("  fig21_pca_biplot.jpg        — PCA biplot with loadings\n")
    f.write("  fig22_comprehensive_ml.jpg  — Side-by-side ML comparison\n")
    f.write("=" * 80 + "\n")

print(f"\n  Saved: results/nested_cv_results.csv")
print(f"  Saved: results/repeated_kfold_stability.csv")
print(f"  Saved: results/shap_values_per_state.csv")
print(f"  Saved: results/state_clusters.csv")
print(f"  Saved: results/advanced_ml_report.txt")
print(f"  Saved: figures/fig17-22 (6 new figures)")

print("\n" + "=" * 70)
print("  ✅ ADVANCED ML ANALYSIS COMPLETE")
print(f"  📊 6 analyses | 6 new figures | 5 result files")
print("=" * 70)
