"""
=============================================================================
 STATISTICAL ANALYSIS v3 — 100% VERIFIED REAL DATA
 Research: Digital Inclusion as a Driver of Circular Economy Behavior in India
 Author: Yash Chauhan
 Date: February 2026
=============================================================================
 6 Analyses using ONLY verified government data:
   1. OLS Regression (Primary Hypothesis)
   2. Multiple Regression with Controls
   3. Random Forest Feature Importance
   4. Threshold/Piecewise Regression
   5. Mediation Analysis (Baron & Kenny)
   6. Robustness Checks
=============================================================================
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import statsmodels.api as sm
from statsmodels.stats.diagnostic import het_breuschpagan
from statsmodels.stats.outliers_influence import variance_inflation_factor
from scipy import stats
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import LeaveOneOut, cross_val_score
from sklearn.metrics import r2_score
import os
import warnings
warnings.filterwarnings('ignore')

# ─── Configuration ────────────────────────────────────────────────────
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, 'data')
RESULTS_DIR = os.path.join(BASE_DIR, 'results')
FIGURES_DIR = os.path.join(BASE_DIR, 'figures')
os.makedirs(RESULTS_DIR, exist_ok=True)
os.makedirs(FIGURES_DIR, exist_ok=True)

print("=" * 70)
print("  STATISTICAL ANALYSIS v3 — 100% VERIFIED REAL DATA")
print("  Digital Inclusion × Circular Economy Behavior")
print("=" * 70)

# ─── Load Data ────────────────────────────────────────────────────────
df = pd.read_csv(os.path.join(DATA_DIR, 'unified_state_dataset.csv'))
print(f"\n  Loaded: {len(df)} states, {len(df.columns)} features")
print(f"  Sources: TRAI, RBI, NITI Aayog, NPCI/Dataful, CPCB, Census 2011")
print(f"  Columns: {list(df.select_dtypes(include=[np.number]).columns)}")

# ═══════════════════════════════════════════════════════════════════════
#  ANALYSIS 1: OLS REGRESSION — PRIMARY HYPOTHESIS (H1)
#  H1: Higher Digital Access Score → Higher CE Behavior Score
# ═══════════════════════════════════════════════════════════════════════
print("\n" + "━" * 70)
print("  ANALYSIS 1: OLS Regression — Primary Hypothesis (H1)")
print("  H1: Digital Access Score → CE Behavior Score")
print("━" * 70)

X = sm.add_constant(df['Digital_Access_Score'])
y = df['CE_Behavior_Score']
model1 = sm.OLS(y, X).fit()
print(model1.summary2())

with open(os.path.join(RESULTS_DIR, 'ols_primary_results.txt'), 'w') as f:
    f.write("ANALYSIS 1: OLS Regression — Primary Hypothesis\n")
    f.write("=" * 60 + "\n")
    f.write(f"100% VERIFIED REAL DATA | {len(df)} states\n\n")
    f.write(f"Sources: TRAI Q2 2024, RBI HoS Table 9, NITI Aayog SDG 2023-24,\n")
    f.write(f"         NPCI/Dataful UPI 2024-25, CPCB E-Waste 2021-22, Census 2011\n\n")
    f.write(str(model1.summary2()))
    f.write(f"\n\nPearson r:  {np.sqrt(model1.rsquared):.4f}")
    f.write(f"\nR-squared:  {model1.rsquared:.4f}")
    f.write(f"\nAdj R²:     {model1.rsquared_adj:.4f}")
    f.write(f"\nβ₁:         {model1.params.iloc[1]:.4f}")
    f.write(f"\np-value:    {model1.pvalues.iloc[1]:.6f}\n")

# ═══════════════════════════════════════════════════════════════════════
#  ANALYSIS 2: Multiple Regression with Controls
# ═══════════════════════════════════════════════════════════════════════
print("\n" + "━" * 70)
print("  ANALYSIS 2: Multiple Regression with Controls")
print("━" * 70)

control_features = ['Digital_Access_Score', 'Per_Capita_NSDP_Rs',
                     'Urban_Percent', 'Literacy_Rate_Percent', 'Population_Mn']

X2 = sm.add_constant(df[control_features])
model2 = sm.OLS(y, X2).fit()
print(model2.summary2())

# VIF
print("\n  Variance Inflation Factors:")
vif_data = pd.DataFrame()
vif_data['Feature'] = control_features
vif_data['VIF'] = [variance_inflation_factor(X2.values, i+1) for i in range(len(control_features))]
for _, r in vif_data.iterrows():
    print(f"    {r['Feature']:30s} VIF = {r['VIF']:.2f}")

with open(os.path.join(RESULTS_DIR, 'multiple_regression_results.txt'), 'w') as f:
    f.write("ANALYSIS 2: Multiple Regression with Controls\n")
    f.write("=" * 60 + "\n")
    f.write(f"100% VERIFIED REAL DATA | {len(df)} states\n\n")
    f.write(str(model2.summary2()))
    f.write(f"\n\nVariance Inflation Factors:\n")
    f.write(vif_data.to_string(index=False))

# ═══════════════════════════════════════════════════════════════════════
#  ANALYSIS 3: Random Forest Feature Importance
# ═══════════════════════════════════════════════════════════════════════
print("\n" + "━" * 70)
print("  ANALYSIS 3: Random Forest Feature Importance")
print("━" * 70)

feature_cols = [
    'Tele_Density_Percent', 'UPI_PerCapita_Transactions',
    'Per_Capita_NSDP_Rs', 'SDG_Index_Score',
    'Literacy_Rate_Percent', 'Urban_Percent',
    'EWaste_PerCapita', 'Population_Mn'
]

X_rf = df[feature_cols].values
y_rf = df['CE_Behavior_Score'].values

rf = RandomForestRegressor(n_estimators=500, max_depth=4, min_samples_leaf=3,
                           random_state=42, n_jobs=-1)
rf.fit(X_rf, y_rf)

importances = rf.feature_importances_
sorted_idx = np.argsort(importances)[::-1]

print(f"\n  Feature Importances (Random Forest):")
for i in sorted_idx:
    bar = '█' * int(importances[i] * 50)
    print(f"    {feature_cols[i]:35s} {importances[i]:.4f}  {bar}")

# LOO Cross-validation
loo = LeaveOneOut()
cv_scores_rf = cross_val_score(rf, X_rf, y_rf, cv=loo, scoring='r2')
print(f"\n  RF LOO-CV R²: {np.mean(cv_scores_rf):.4f} ± {np.std(cv_scores_rf):.4f}")

# Feature importance plot
fig, ax = plt.subplots(figsize=(10, 6))
ax.barh(range(len(sorted_idx)), importances[sorted_idx],
        color=['#2563EB' if i > 2 else '#059669' for i, _ in enumerate(sorted_idx)],
        edgecolor='white')
ax.set_yticks(range(len(sorted_idx)))
ax.set_yticklabels([feature_cols[i] for i in sorted_idx])
ax.set_xlabel('Feature Importance', fontsize=12, fontweight='bold')
# ax.set_title('Random Forest Feature Importance for CE Behavior Score\n'
#              f'(R² = {r2_score(y_rf, rf.predict(X_rf)):.3f}, LOO-CV = {np.mean(cv_scores_rf):.3f})',
#              fontsize=13, fontweight='bold')
plt.tight_layout()
plt.savefig(os.path.join(FIGURES_DIR, 'fig9_feature_importance.jpg'), bbox_inches='tight', dpi=300)
plt.close()

with open(os.path.join(RESULTS_DIR, 'feature_importance.txt'), 'w') as f:
    f.write("ANALYSIS 3: Random Forest Feature Importance\n")
    f.write("=" * 60 + "\n")
    f.write(f"100% VERIFIED REAL DATA | {len(df)} states\n\n")
    f.write(f"RF R² (training): {r2_score(y_rf, rf.predict(X_rf)):.4f}\n")
    f.write(f"RF LOO-CV R²: {np.mean(cv_scores_rf):.4f} ± {np.std(cv_scores_rf):.4f}\n\n")
    for i in sorted_idx:
        f.write(f"  {feature_cols[i]:35s} {importances[i]:.4f}\n")

# ═══════════════════════════════════════════════════════════════════════
#  ANALYSIS 4: Threshold / Piecewise Regression
# ═══════════════════════════════════════════════════════════════════════
print("\n" + "━" * 70)
print("  ANALYSIS 4: Threshold / Piecewise Regression")
print("━" * 70)

# Test for different threshold values
best_r2 = -1
best_threshold = None

td_values = df['Tele_Density_Percent'].sort_values().values
for threshold in td_values[2:-2]:
    df['TD_Below'] = np.minimum(df['Tele_Density_Percent'], threshold)
    df['TD_Above'] = np.maximum(df['Tele_Density_Percent'] - threshold, 0)

    X_pw = sm.add_constant(df[['TD_Below', 'TD_Above']])
    model_pw = sm.OLS(y, X_pw).fit()

    if model_pw.rsquared > best_r2:
        best_r2 = model_pw.rsquared
        best_threshold = threshold

print(f"  Best threshold: {best_threshold:.2f}% tele-density")
print(f"  R² at threshold: {best_r2:.4f}")

df['TD_Below'] = np.minimum(df['Tele_Density_Percent'], best_threshold)
df['TD_Above'] = np.maximum(df['Tele_Density_Percent'] - best_threshold, 0)
X_pw_final = sm.add_constant(df[['TD_Below', 'TD_Above']])
model_pw_final = sm.OLS(y, X_pw_final).fit()
print(model_pw_final.summary2())

with open(os.path.join(RESULTS_DIR, 'threshold_analysis.txt'), 'w') as f:
    f.write("ANALYSIS 4: Threshold/Piecewise Regression\n")
    f.write("=" * 60 + "\n")
    f.write(f"100% VERIFIED REAL DATA | {len(df)} states\n\n")
    f.write(f"Best threshold: {best_threshold:.2f}% tele-density\n")
    f.write(f"R² at threshold: {best_r2:.4f}\n\n")
    f.write(str(model_pw_final.summary2()))

# ═══════════════════════════════════════════════════════════════════════
#  ANALYSIS 5: Mediation Analysis (Baron & Kenny)
# ═══════════════════════════════════════════════════════════════════════
print("\n" + "━" * 70)
print("  ANALYSIS 5: Mediation Analysis (Baron & Kenny)")
print("  X: Tele-density (TRAI) → M: UPI Per Capita (NPCI) → Y: CE Behavior")
print("━" * 70)

X_med = df['Tele_Density_Percent']
M_med = df['UPI_PerCapita_Transactions']
Y_med = df['CE_Behavior_Score']

# Step 1 — c path
model_c = sm.OLS(Y_med, sm.add_constant(X_med)).fit()
# Step 2 — a path
model_a = sm.OLS(M_med, sm.add_constant(X_med)).fit()
# Step 3 — b and c' paths
model_b = sm.OLS(Y_med, sm.add_constant(pd.DataFrame({'X': X_med, 'M': M_med}))).fit()

a = model_a.params.iloc[1]
b = model_b.params['M']
c = model_c.params.iloc[1]
c_prime = model_b.params['X']
indirect = a * b

se_indirect = np.sqrt(a**2 * model_b.bse['M']**2 + b**2 * model_a.bse.iloc[1]**2)
sobel_z = indirect / se_indirect
sobel_p = 2 * (1 - stats.norm.cdf(abs(sobel_z)))

print(f"\n  Step 1 (c path): X → Y:   β={c:.4f}, p={model_c.pvalues.iloc[1]:.4f}")
print(f"  Step 2 (a path): X → M:   β={a:.4f}, p={model_a.pvalues.iloc[1]:.4f}")
print(f"  Step 3 (b path): M → Y|X: β={b:.4f}, p={model_b.pvalues['M']:.4f}")
print(f"  Step 3 (c' path): X → Y|M: β={c_prime:.4f}, p={model_b.pvalues['X']:.4f}")
print(f"\n  Indirect effect (a × b): {indirect:.4f}")
print(f"  Sobel test: z={sobel_z:.4f}, p={sobel_p:.4f}")

if model_c.pvalues.iloc[1] < 0.05 and model_a.pvalues.iloc[1] < 0.05 and model_b.pvalues['M'] < 0.05:
    if model_b.pvalues['X'] >= 0.05:
        med_type = "Full mediation detected"
    else:
        med_type = "Partial mediation detected"
else:
    med_type = "No significant mediation detected"
print(f"  Mediation type: {med_type}")

with open(os.path.join(RESULTS_DIR, 'mediation_analysis.txt'), 'w') as f:
    f.write("ANALYSIS 5: Mediation Analysis (Baron & Kenny)\n")
    f.write("=" * 60 + "\n")
    f.write(f"100% VERIFIED REAL DATA | {len(df)} states\n\n")
    f.write(f"X: Tele-density (TRAI Q2 2024)\n")
    f.write(f"M: UPI Per Capita (NPCI/Dataful 2024-25)\n")
    f.write(f"Y: CE Behavior Score (Composite)\n\n")
    f.write(f"Path c (total):   β={c:.4f}, p={model_c.pvalues.iloc[1]:.4f}\n")
    f.write(f"Path a (X→M):     β={a:.4f}, p={model_a.pvalues.iloc[1]:.4f}\n")
    f.write(f"Path b (M→Y|X):   β={b:.4f}, p={model_b.pvalues['M']:.4f}\n")
    f.write(f"Path c' (direct): β={c_prime:.4f}, p={model_b.pvalues['X']:.4f}\n\n")
    f.write(f"Indirect effect: {indirect:.4f}\n")
    f.write(f"Sobel z: {sobel_z:.4f}, p={sobel_p:.4f}\n")
    f.write(f"Mediation type: {med_type}\n")

# ═══════════════════════════════════════════════════════════════════════
#  ANALYSIS 6: Robustness Checks
# ═══════════════════════════════════════════════════════════════════════
print("\n" + "━" * 70)
print("  ANALYSIS 6: Robustness Checks")
print("━" * 70)

# Standardized beta
beta_std = model1.params.iloc[1] * df['Digital_Access_Score'].std() / df['CE_Behavior_Score'].std()

# Non-parametric correlations
rho, p_rho = stats.spearmanr(df['Digital_Access_Score'], df['CE_Behavior_Score'])
tau, p_tau = stats.kendalltau(df['Digital_Access_Score'], df['CE_Behavior_Score'])

# Breusch-Pagan
bp_lm, bp_p, _, _ = het_breuschpagan(model1.resid, model1.model.exog)

# Durbin-Watson
from statsmodels.stats.stattools import durbin_watson
dw = durbin_watson(model1.resid)

# Cook's distance
influence = model1.get_influence()
cooks_d = influence.cooks_distance[0]
threshold = 4 / len(df)
influential = df.loc[cooks_d > threshold, 'State'].tolist()

print(f"\n  Standardized β: {beta_std:.4f}")
print(f"  Spearman ρ: {rho:.4f} (p={p_rho:.4f})")
print(f"  Kendall τ:  {tau:.4f} (p={p_tau:.4f})")
print(f"  Breusch-Pagan: LM={bp_lm:.4f}, p={bp_p:.4f}")
print(f"  Durbin-Watson: {dw:.4f}")
print(f"  Influential states (Cook's D > {threshold:.3f}): {influential}")

with open(os.path.join(RESULTS_DIR, 'robustness_checks.txt'), 'w') as f:
    f.write("ANALYSIS 6: Robustness Checks\n")
    f.write("=" * 60 + "\n")
    f.write(f"100% VERIFIED REAL DATA | {len(df)} states\n\n")
    f.write(f"Standardized β: {beta_std:.4f}\n")
    f.write(f"Spearman ρ:     {rho:.4f} (p={p_rho:.4f})\n")
    f.write(f"Kendall τ:      {tau:.4f} (p={p_tau:.4f})\n")
    f.write(f"Breusch-Pagan:  LM={bp_lm:.4f}, p={bp_p:.4f}\n")
    f.write(f"Durbin-Watson:  {dw:.4f}\n")
    f.write(f"Influential:    {influential}\n")

# ═══════════════════════════════════════════════════════════════════════
#  MODEL COMPARISON TABLE
# ═══════════════════════════════════════════════════════════════════════
print("\n" + "━" * 70)
print("  MODEL COMPARISON SUMMARY")
print("━" * 70)

comparison = pd.DataFrame({
    'Model': [
        'Simple OLS (DA → CE)',
        'Multiple OLS (with controls)',
        'Random Forest',
        'Piecewise Regression',
        'Mediation (Baron & Kenny)'
    ],
    'R_Squared': [
        model1.rsquared,
        model2.rsquared,
        r2_score(y_rf, rf.predict(X_rf)),
        model_pw_final.rsquared,
        model_b.rsquared
    ],
    'Adj_R2_or_CV': [
        model1.rsquared_adj,
        model2.rsquared_adj,
        np.mean(cv_scores_rf),
        model_pw_final.rsquared_adj,
        model_b.rsquared_adj
    ],
    'Key_Finding': [
        f'β={model1.params.iloc[1]:.3f}, p={model1.pvalues.iloc[1]:.4f}',
        f'Adj R²={model2.rsquared_adj:.3f}, DA p={model2.pvalues.iloc[1]:.4f}',
        f'Top: {feature_cols[sorted_idx[0]]}, LOO-CV={np.mean(cv_scores_rf):.3f}',
        f'Threshold={best_threshold:.1f}%',
        f'Indirect={indirect:.3f}, Sobel z={sobel_z:.3f}, p={sobel_p:.4f}'
    ]
})

comparison.to_csv(os.path.join(RESULTS_DIR, 'model_comparison.csv'), index=False)
print(comparison.to_string(index=False))

print("\n" + "=" * 70)
print("  ✅ STATISTICAL ANALYSIS v3 COMPLETE — 100% VERIFIED REAL DATA")
print(f"  📁 Results saved to: {RESULTS_DIR}")
print(f"  📁 Figures saved to: {FIGURES_DIR}")
print("=" * 70)
for f in sorted(os.listdir(RESULTS_DIR)):
    print(f"  • results/{f}")
