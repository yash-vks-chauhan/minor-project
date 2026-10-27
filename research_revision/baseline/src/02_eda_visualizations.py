"""
=============================================================================
 EXPLORATORY DATA ANALYSIS (EDA) v3 — 100% VERIFIED REAL DATA
 Research: Digital Inclusion as a Driver of Circular Economy Behavior in India
 Author: Yash Chauhan
 Date: February 2026
=============================================================================
 ALL DATA loaded from verified CSV sources:
   TRAI, RBI, NITI Aayog, NPCI/Dataful, CPCB, Census 2011
=============================================================================
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import seaborn as sns
from scipy import stats
import os
import warnings
warnings.filterwarnings('ignore')

# ─── Configuration ────────────────────────────────────────────────────
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, 'data')
FIG_DIR = os.path.join(BASE_DIR, 'figures')
os.makedirs(FIG_DIR, exist_ok=True)

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
    'figure.figsize': (10, 7),
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
}

print("=" * 70)
print("  EXPLORATORY DATA ANALYSIS v3 — 100% VERIFIED REAL DATA")
print("  Digital Inclusion × Circular Economy Behavior")
print("=" * 70)

# ─── Load Data ────────────────────────────────────────────────────────
df = pd.read_csv(os.path.join(DATA_DIR, 'unified_state_dataset.csv'))
upi = pd.read_csv(os.path.join(DATA_DIR, 'upi_monthly_trends.csv'))
upi['Date'] = pd.to_datetime(upi['Date'])

print(f"\n  Loaded: {len(df)} states, {len(df.columns)} features")
print(f"  Loaded: {len(upi)} months of UPI data")
print(f"  Columns: {list(df.select_dtypes(include=[np.number]).columns)}")

# ─── FIGURE 1: Correlation Heatmap ───────────────────────────────────
print("\n[1/8] Generating correlation heatmap...")

key_cols = [
    'Tele_Density_Percent', 'UPI_PerCapita_Transactions',
    'Per_Capita_NSDP_Rs', 'SDG_Index_Score',
    'Literacy_Rate_Percent', 'Urban_Percent',
    'EWaste_PerCapita', 'EWaste_Processed_Tonnes',
    'Digital_Access_Score', 'CE_Behavior_Score', 'DCI'
]

short_labels = [
    'Tele-density', 'UPI/Capita',
    'NSDP/Cap', 'SDG Index',
    'Literacy', 'Urbanization',
    'E-Waste/Cap', 'E-Waste (T)',
    'Digital Access', 'CE Behavior', 'DCI'
]

corr_data = df[key_cols].corr()

fig, ax = plt.subplots(figsize=(13, 10))
mask = np.triu(np.ones_like(corr_data, dtype=bool), k=1)
cmap = sns.diverging_palette(250, 15, s=85, l=45, n=12, as_cmap=True)
sns.heatmap(corr_data, mask=mask, cmap=cmap, center=0,
            annot=True, fmt='.2f', linewidths=0.8,
            xticklabels=short_labels, yticklabels=short_labels,
            square=True, cbar_kws={'shrink': 0.75, 'label': 'Pearson Correlation'})
# ax.set_title('Figure 1: Correlation Matrix — Digital Inclusion & Circular Economy Variables\n'
#              '(Sources: TRAI, RBI, NITI Aayog, NPCI, CPCB, Census 2011)',
#              fontsize=13, fontweight='bold', pad=20)
plt.tight_layout()
plt.savefig(os.path.join(FIG_DIR, 'fig1_correlation_heatmap.jpg'), bbox_inches='tight')
plt.close()

# ─── FIGURE 2: Digital Access vs CE Behavior ─────────────────────────
print("[2/8] Generating Digital Access vs CE Behavior scatter...")

fig, ax = plt.subplots(figsize=(12, 8))
ax.set_facecolor(COLORS['bg'])

income_colors = {'Low': COLORS['warm'], 'Medium': COLORS['orange'], 'High': COLORS['primary']}
for group in ['Low', 'Medium', 'High']:
    mask_g = df['Income_Group'] == group
    ax.scatter(df.loc[mask_g, 'Digital_Access_Score'],
              df.loc[mask_g, 'CE_Behavior_Score'],
              c=income_colors[group], s=df.loc[mask_g, 'Population_Mn'] * 3,
              alpha=0.7, edgecolors='white', linewidth=1.5,
              label=f'{group} Income', zorder=3)

for _, row in df.iterrows():
    ax.annotate(row['State'], (row['Digital_Access_Score'], row['CE_Behavior_Score']),
                fontsize=7, alpha=0.75, ha='center', va='bottom',
                xytext=(0, 8), textcoords='offset points')

slope, intercept, r_value, p_value, std_err = stats.linregress(
    df['Digital_Access_Score'], df['CE_Behavior_Score']
)
x_line = np.linspace(df['Digital_Access_Score'].min(), df['Digital_Access_Score'].max(), 100)
y_line = slope * x_line + intercept
ax.plot(x_line, y_line, '--', color=COLORS['slate'], linewidth=2, alpha=0.8,
        label=f'OLS Fit (R²={r_value**2:.3f}, p={p_value:.4f})')

ax.set_xlabel('Digital Access Score (Composite)', fontsize=13, fontweight='bold')
ax.set_ylabel('Circular Economy Behavior Score', fontsize=13, fontweight='bold')
# ax.set_title('Figure 2: Digital Inclusion vs. Circular Economy Behavior\n'
#              '(Bubble size = Population; Color = Per Capita NSDP group)',
#              fontsize=14, fontweight='bold')
ax.legend(loc='best', framealpha=0.9, fontsize=10)
ax.grid(True, alpha=0.3, color=COLORS['grid'])
plt.tight_layout()
plt.savefig(os.path.join(FIG_DIR, 'fig2_digital_vs_ce_scatter.jpg'), bbox_inches='tight')
plt.close()

# ─── FIGURE 3: DCI Ranking ───────────────────────────────────────────
print("[3/8] Generating DCI ranking chart...")

df_sorted = df.sort_values('DCI', ascending=True)

fig, ax = plt.subplots(figsize=(12, 10))
colors = plt.cm.RdYlGn(np.linspace(0.15, 0.85, len(df_sorted)))
bars = ax.barh(range(len(df_sorted)), df_sorted['DCI'], color=colors,
               edgecolor='white', linewidth=0.8, height=0.7)

ax.set_yticks(range(len(df_sorted)))
ax.set_yticklabels(df_sorted['State'], fontsize=10)
ax.set_xlabel('Digital Circularity Index (DCI)', fontsize=13, fontweight='bold')
# ax.set_title('Figure 3: State-wise Digital Circularity Index (DCI) Ranking\n'
#              '(100% Verified Data: TRAI, RBI, NITI Aayog, NPCI, CPCB)', fontsize=14, fontweight='bold')

for i, (val, state) in enumerate(zip(df_sorted['DCI'], df_sorted['State'])):
    ax.text(val + 0.3, i, f'{val:.1f}', va='center', fontsize=9, fontweight='bold')

mean_dci = df['DCI'].mean()
ax.axvline(x=mean_dci, color=COLORS['warm'], linestyle='--', linewidth=2, alpha=0.7)
ax.text(mean_dci + 0.5, len(df_sorted) - 1.5, f'Mean DCI: {mean_dci:.1f}',
        color=COLORS['warm'], fontsize=10, fontweight='bold')

ax.grid(axis='x', alpha=0.3)
plt.tight_layout()
plt.savefig(os.path.join(FIG_DIR, 'fig3_dci_ranking.jpg'), bbox_inches='tight')
plt.close()

# ─── FIGURE 4: Distribution Analysis ─────────────────────────────────
print("[4/8] Generating distribution analysis...")

fig, axes = plt.subplots(2, 3, figsize=(16, 10))
dist_vars = [
    ('Digital_Access_Score', 'Digital Access Score'),
    ('CE_Behavior_Score', 'CE Behavior Score'),
    ('DCI', 'Digital Circularity Index'),
    ('Tele_Density_Percent', 'Tele-density %\n(TRAI Q2 2024)'),
    ('SDG_Index_Score', 'SDG Index Score\n(NITI Aayog 2023-24)'),
    ('UPI_PerCapita_Transactions', 'UPI Per Capita Txns\n(NPCI/Dataful 2024-25)')
]

for ax, (col, title) in zip(axes.flat, dist_vars):
    data = df[col].dropna()
    ax.hist(data, bins=8, color=COLORS['primary'], alpha=0.7, edgecolor='white', density=True)

    kde_x = np.linspace(data.min(), data.max(), 100)
    kde = stats.gaussian_kde(data)
    ax.plot(kde_x, kde(kde_x), color=COLORS['warm'], linewidth=2)

    stat_val, p_val = stats.shapiro(data)

    ax.set_title(title, fontsize=11, fontweight='bold')
    ax.set_ylabel('Density')
    ax.text(0.95, 0.95, f'μ={data.mean():.1f}\nσ={data.std():.1f}\nW={stat_val:.3f}',
            transform=ax.transAxes, ha='right', va='top', fontsize=8,
            bbox=dict(boxstyle='round,pad=0.3', facecolor='white', alpha=0.8))

# fig.suptitle('Figure 4: Distribution Analysis of Key Variables (100% Verified Data)',
#              fontsize=14, fontweight='bold', y=1.02)
plt.tight_layout()
plt.savefig(os.path.join(FIG_DIR, 'fig4_distributions.jpg'), bbox_inches='tight')
plt.close()

# ─── FIGURE 5: Box Plots by Digital Access Category ──────────────────
print("[5/8] Generating box plots by digital access category...")

fig, axes = plt.subplots(1, 3, figsize=(16, 6))
box_vars = [
    ('CE_Behavior_Score', 'CE Behavior Score'),
    ('SDG_Index_Score', 'SDG Index Score'),
    ('EWaste_PerCapita', 'E-Waste Per Capita')
]

for ax, (col, title) in zip(axes, box_vars):
    categories = df['Digital_Access_Category'].dropna().unique()
    order = sorted(categories, key=lambda x: float(x.split('(')[1].split(')')[0].replace('<','0').replace('>','100').split('-')[0]))
    valid_cats = [cat for cat in order if cat in df['Digital_Access_Category'].values]
    if valid_cats:
        palette_map = {}
        for i, cat in enumerate(valid_cats):
            if i == 0: palette_map[cat] = COLORS['warm']
            elif i == 1: palette_map[cat] = COLORS['orange']
            else: palette_map[cat] = COLORS['accent']

        bp = sns.boxplot(data=df, x='Digital_Access_Category', y=col,
                         order=valid_cats, ax=ax,
                         palette=[palette_map.get(c, COLORS['slate']) for c in valid_cats],
                         width=0.6, linewidth=1.5)
        sns.stripplot(data=df, x='Digital_Access_Category', y=col,
                      order=valid_cats, ax=ax, color=COLORS['slate'], size=5, alpha=0.5, jitter=True)
        ax.set_title(title, fontsize=12, fontweight='bold')
        ax.set_xlabel('Digital Access Category', fontsize=11)
        ax.set_ylabel(title, fontsize=11)

        groups = [df.loc[df['Digital_Access_Category'] == cat, col].dropna() for cat in valid_cats]
        groups = [g for g in groups if len(g) > 0]
        if len(groups) >= 2:
            f_stat, p_val = stats.f_oneway(*groups)
            ax.text(0.5, 0.02, f'ANOVA: F={f_stat:.2f}, p={p_val:.4f}',
                    transform=ax.transAxes, ha='center', fontsize=9,
                    bbox=dict(boxstyle='round,pad=0.3', facecolor='lightyellow', alpha=0.8))

# fig.suptitle('Figure 5: Circular Economy Metrics by Digital Access Level',
#              fontsize=14, fontweight='bold', y=1.02)
plt.tight_layout()
plt.savefig(os.path.join(FIG_DIR, 'fig5_boxplots_digital_access.jpg'), bbox_inches='tight')
plt.close()

# ─── FIGURE 6: UPI Growth Trends ─────────────────────────────────────
print("[6/8] Generating UPI growth trends...")

fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 10))

ax1.fill_between(upi['Date'], upi['Volume_Mn'], alpha=0.15, color=COLORS['primary'])
ax1.plot(upi['Date'], upi['Volume_Mn'], 'o-', color=COLORS['primary'],
         linewidth=2.5, markersize=7, markerfacecolor='white', markeredgewidth=2)
ax1.set_ylabel('Transaction Volume (Millions)', fontsize=12, fontweight='bold')
ax1.set_title('UPI Monthly Transaction Volume (NPCI Data)', fontsize=13, fontweight='bold')
ax1.grid(True, alpha=0.3)

ax2.fill_between(upi['Date'], upi['Value_Cr'], alpha=0.15, color=COLORS['accent'])
ax2.plot(upi['Date'], upi['Value_Cr'], 's-', color=COLORS['accent'],
         linewidth=2.5, markersize=7, markerfacecolor='white', markeredgewidth=2)
ax2.set_ylabel('Transaction Value (₹ Crores)', fontsize=12, fontweight='bold')
ax2.set_xlabel('Month', fontsize=12, fontweight='bold')
ax2.set_title('UPI Monthly Transaction Value (NPCI Data)', fontsize=13, fontweight='bold')
ax2.grid(True, alpha=0.3)

plt.tight_layout(h_pad=3)
plt.savefig(os.path.join(FIG_DIR, 'fig6_upi_trends.jpg'), bbox_inches='tight')
plt.close()

# ─── FIGURE 7: Component Regression Panels ───────────────────────────
print("[7/8] Generating component regression panels...")

fig, axes = plt.subplots(2, 2, figsize=(14, 12))
regression_pairs = [
    ('Tele_Density_Percent', 'SDG_Index_Score', 'Tele-density % (TRAI)', 'SDG Index Score (NITI Aayog)'),
    ('UPI_PerCapita_Transactions', 'EWaste_PerCapita', 'UPI per Capita (NPCI)', 'E-Waste per Capita (CPCB)'),
    ('Literacy_Rate_Percent', 'CE_Behavior_Score', 'Literacy Rate (Census 2011)', 'CE Behavior Score'),
    ('Per_Capita_NSDP_Rs', 'Digital_Access_Score', 'Per Capita NSDP (RBI)', 'Digital Access Score')
]

for ax, (x_col, y_col, x_label, y_label) in zip(axes.flat, regression_pairs):
    x_data = df[x_col]
    y_data = df[y_col]
    ax.scatter(x_data, y_data, c=COLORS['primary'], s=80, alpha=0.6,
              edgecolors='white', linewidth=1)

    slope, intercept, r, p, se = stats.linregress(x_data, y_data)
    x_pred = np.linspace(x_data.min(), x_data.max(), 100)
    y_pred = slope * x_pred + intercept
    ax.plot(x_pred, y_pred, '--', color=COLORS['warm'], linewidth=2)

    ax.set_xlabel(x_label, fontsize=11, fontweight='bold')
    ax.set_ylabel(y_label, fontsize=11, fontweight='bold')
    ax.set_title(f'{x_label} vs {y_label}', fontsize=10, fontweight='bold')
    ax.text(0.05, 0.95, f'R²={r**2:.3f}\np={p:.4f}\nβ={slope:.4f}',
            transform=ax.transAxes, va='top', fontsize=9,
            bbox=dict(boxstyle='round,pad=0.3', facecolor='white', alpha=0.8))
    ax.grid(True, alpha=0.2)

# fig.suptitle('Figure 7: Component-Level Regression Analysis\n'
#              'Digital Inclusion Indicators vs. Circular Economy Metrics',
#              fontsize=14, fontweight='bold', y=1.02)
plt.tight_layout()
plt.savefig(os.path.join(FIG_DIR, 'fig7_regression_panels.jpg'), bbox_inches='tight')
plt.close()

# ─── FIGURE 8: UPI Adoption vs SDG Score ─────────────────────────────
print("[8/8] Generating UPI vs SDG Score analysis...")

fig, ax = plt.subplots(figsize=(12, 7))

scatter = ax.scatter(df['UPI_PerCapita_Transactions'], df['SDG_Index_Score'],
                     c=df['Per_Capita_NSDP_Rs'] / 1000, cmap='RdYlGn', s=120, alpha=0.8,
                     edgecolors='white', linewidth=1.5, zorder=3)

for _, row in df.iterrows():
    ax.annotate(row['State'],
                (row['UPI_PerCapita_Transactions'], row['SDG_Index_Score']),
                fontsize=7, alpha=0.75, ha='center', va='bottom',
                xytext=(0, 8), textcoords='offset points')

slope, intercept, r, p, se = stats.linregress(
    df['UPI_PerCapita_Transactions'], df['SDG_Index_Score']
)
x_line = np.linspace(df['UPI_PerCapita_Transactions'].min(),
                     df['UPI_PerCapita_Transactions'].max(), 100)
y_line = slope * x_line + intercept
ax.plot(x_line, y_line, '--', color=COLORS['warm'], linewidth=2,
        label=f'OLS Fit (R²={r**2:.3f}, p={p:.4f})')

# LOWESS smoothing
from statsmodels.nonparametric.smoothers_lowess import lowess
smoothed = lowess(df['SDG_Index_Score'], df['UPI_PerCapita_Transactions'], frac=0.6)
ax.plot(smoothed[:, 0], smoothed[:, 1], '-', color=COLORS['accent'], linewidth=3,
        label='LOWESS Fit', zorder=2)

cbar = plt.colorbar(scatter, ax=ax, label='Per Capita NSDP (₹ thousands)', shrink=0.8)

ax.set_xlabel('UPI Transactions per Capita (NPCI/Dataful 2024-25)', fontsize=13, fontweight='bold')
ax.set_ylabel('SDG Index Score (NITI Aayog 2023-24)', fontsize=13, fontweight='bold')
# ax.set_title('Figure 8: Digital Payment Adoption vs. SDG Performance\n'
#              '(Color = Per Capita NSDP from RBI 2023-24)',
#              fontsize=14, fontweight='bold')
ax.legend(loc='upper left', fontsize=11)
ax.grid(True, alpha=0.2)

plt.tight_layout()
plt.savefig(os.path.join(FIG_DIR, 'fig8_upi_vs_sdg.jpg'), bbox_inches='tight')
plt.close()

print("\n" + "=" * 70)
print("  ✅ EDA v3 COMPLETE — 8 publication-ready figures (100% verified data)")
print(f"  📁 Figures saved to: {FIG_DIR}")
print("=" * 70)
for f in sorted(os.listdir(FIG_DIR)):
    if f.startswith('fig') and f.endswith('.jpg'):
        print(f"  • {f}")
