"""Reproducible exploratory statistics and auditable nested state-held-out models."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import platform
import sys

import numpy as np
import pandas as pd
from scipy import stats
import statsmodels.api as sm
from sklearn.base import clone
from sklearn.ensemble import RandomForestRegressor
from sklearn.linear_model import ElasticNet, Ridge
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import GridSearchCV, KFold, LeaveOneOut
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
import xgboost as xgb

REV = Path(__file__).resolve().parents[1]
OUT = REV / 'results'
SEED = 20261026
DIGITAL = ['Tele_Density_Percent', 'UPI_PerCapita_Transactions']
AUGMENTED = DIGITAL + ['Log_NSDP', 'Urban_Percent_2021', 'Log_Population']
TARGETS = ['Log_EWaste_Per_Million', 'SDG_Index_Score']


def dump(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, allow_nan=False) + '\n')


def correlation(x, y):
    r, p = stats.pearsonr(x, y)
    rho, sp = stats.spearmanr(x, y)
    return dict(n=len(x), pearson_r=float(r), pearson_p=float(p),
                spearman_rho=float(rho), spearman_p=float(sp))


def regression(data, target, controls):
    X = data[['Digital_Access_Score'] + controls].copy()
    X['Digital_Access_Score'] /= 10
    fit = sm.OLS(data[target], sm.add_constant(X)).fit(cov_type='HC3', use_t=True)
    ordinary = sm.OLS(data[target], sm.add_constant(X)).fit()
    ci = fit.conf_int()
    records = [dict(term=name, coefficient=float(fit.params[name]),
                    hc3_se=float(fit.bse[name]), p=float(fit.pvalues[name]),
                    ci_low=float(ci.loc[name, 0]), ci_high=float(ci.loc[name, 1]))
               for name in fit.params.index]
    cook = ordinary.get_influence().cooks_distance[0]
    return dict(target=target, controls=controls, n=len(data), r_squared=float(fit.rsquared),
                coefficients=records, largest_cooks_d=float(cook.max()),
                influential_state=data.iloc[int(cook.argmax())].State,
                shapiro_w=float(stats.shapiro(ordinary.resid).statistic),
                shapiro_p=float(stats.shapiro(ordinary.resid).pvalue))


def run_stats(data):
    rng = np.random.default_rng(SEED)
    x = data.Digital_Access_Score.to_numpy()
    y = data.Circularity_Related_Proxy.to_numpy()
    main = correlation(x, y)
    xc = x - x.mean()
    yc = y - y.mean()
    permutations = np.array([np.dot(xc, rng.permutation(yc)) / np.sqrt(np.dot(xc, xc) * np.dot(yc, yc))
                             for _ in range(19999)])
    main['permutation_p'] = float((1 + (np.abs(permutations) >= abs(main['pearson_r'])).sum()) / 20000)
    boot = []
    for _ in range(10000):
        indices = rng.integers(0, len(x), size=len(x))
        if np.std(x[indices]) and np.std(y[indices]):
            boot.append(float(np.corrcoef(x[indices], y[indices])[0, 1]))
    main['bootstrap_percentile_ci'] = np.quantile(boot, [0.025, 0.975]).tolist()
    main['bootstrap_resamples'] = len(boot)
    deletion = [dict(removed=row.State, **correlation(np.delete(x, i), np.delete(y, i)))
                for i, row in data.iterrows()]
    pd.DataFrame(deletion).to_csv(OUT / 'leave_one_state_out_associations.csv', index=False)
    T, U = data.Tele_Density_Percent_MinMax, data.UPI_PerCapita_Transactions_MinMax
    E, S = data.EWaste_Tonnes_Per_Million_MinMax, data.SDG_Index_Score_MinMax
    loge = data.Log_EWaste_Per_Million
    lognorm = 100 * (loge - loge.min()) / (loge.max() - loge.min())
    sensitivities = []
    for name, dx, cy in [
        ('Equal weights', (T + U) / 2, (E + S) / 2),
        ('Tele-density weighted 75 percent', .75 * T + .25 * U, y),
        ('UPI weighted 75 percent', .25 * T + .75 * U, y),
        ('E-waste-only outcome', x, data.EWaste_Tonnes_Per_Million),
        ('SDG-only outcome', x, data.SDG_Index_Score),
        ('Log e-waste-only outcome', x, loge),
        ('Proxy using log e-waste', x, (7 * lognorm + 8 * S) / 15),
    ]:
        sensitivities.append(dict(specification=name, **correlation(dx, cy)))
    pd.DataFrame(sensitivities).to_csv(OUT / 'sensitivity_correlations.csv', index=False)
    regressions = []
    for target in ['Circularity_Related_Proxy', 'Log_EWaste_Per_Million', 'SDG_Index_Score']:
        for controls in [[], ['Log_NSDP']]:
            regressions.append(regression(data, target, controls))
    audit = dict(seed=SEED, main_association=main, regressions=regressions,
                 without_haryana=next(r for r in deletion if r['removed'] == 'Haryana'),
                 leave_one_state_out_r_range=[min(r['pearson_r'] for r in deletion), max(r['pearson_r'] for r in deletion)],
                 descriptive_index_definition='DAS=(4*Tnorm+3*UPInorm)/7; proxy=(7*EWnorm+8*SDGnorm)/15; DCI=DAS*proxy/100',
                 legacy_baseline_correlation=correlation(
                     pd.read_csv(REV.parent / 'data/unified_state_dataset.csv').Digital_Access_Score,
                     pd.read_csv(REV.parent / 'data/unified_state_dataset.csv').CE_Behavior_Score))
    dump(OUT / 'statistical_results.json', audit)
    data.describe().to_csv(OUT / 'descriptive_statistics.csv')
    print('STATISTICS', json.dumps(main), flush=True)
    for fit in regressions:
        term = next(r for r in fit['coefficients'] if r['term'] == 'Digital_Access_Score')
        print(f"REGRESSION {fit['target']} controls={fit['controls']}: b10={term['coefficient']:.4f}, HC3 p={term['p']:.5f}", flush=True)


def model_specs():
    return {
        'Ridge': (Pipeline([('scale', StandardScaler()), ('model', Ridge())]),
                  {'model__alpha': [.1, 1., 10., 100.]}),
        'ElasticNet': (Pipeline([('scale', StandardScaler()), ('model', ElasticNet(max_iter=30000))]),
                       {'model__alpha': [.01, .1, 1.], 'model__l1_ratio': [.2, .5, .8]}),
        'RandomForest': (Pipeline([('model', RandomForestRegressor(n_estimators=200, random_state=SEED, n_jobs=1))]),
                         {'model__max_depth': [2, 3], 'model__min_samples_leaf': [2, 4]}),
        'XGBoost': (Pipeline([('model', xgb.XGBRegressor(random_state=SEED, n_jobs=1, verbosity=0,
                                                       min_child_weight=3, reg_alpha=1, reg_lambda=2,
                                                       subsample=.8, colsample_bytree=.8))]),
                    {'model__n_estimators': [100, 200], 'model__max_depth': [1, 2], 'model__learning_rate': [.05, .1]}),
    }


def metrics(y, pred):
    return {'R2': float(r2_score(y, pred)), 'RMSE': float(np.sqrt(mean_squared_error(y, pred))),
            'MAE': float(mean_absolute_error(y, pred))}


def run_models(data, n_jobs):
    import shap
    digest = hashlib.sha256()
    for path in [REV / 'data/revised_state_dataset.csv', REV / 'ANALYSIS_PROTOCOL.md', Path(__file__)]:
        digest.update(path.read_bytes())
    run_hash = digest.hexdigest()
    cache = OUT / 'folds'
    cache.mkdir(exist_ok=True)
    all_folds, summary, predictions, shap_rows = [], [], [], []
    for target in TARGETS:
        y = data[target].to_numpy()
        baseline = (y.sum() - y) / (len(y) - 1)
        summary.append(dict(target=target, features='none', model='TrainingMean', **metrics(y, baseline)))
        for i, state in enumerate(data.State):
            predictions.append(dict(target=target, features='none', model='TrainingMean', State=state, actual=float(y[i]), prediction=float(baseline[i])))
        for feature_name, features in [('digital', DIGITAL), ('augmented', AUGMENTED)]:
            X = data[features].to_numpy()
            for name, (pipeline, params) in model_specs().items():
                pred = np.empty(len(data))
                for fold, (train, test) in enumerate(LeaveOneOut().split(X)):
                    path = cache / f'{target}__{feature_name}__{name}__{fold:02}.json'
                    record = json.loads(path.read_text()) if path.exists() else {}
                    if record.get('run_hash') != run_hash:
                        inner = list(KFold(n_splits=4, shuffle=True, random_state=SEED).split(X[train]))
                        grid = GridSearchCV(clone(pipeline), params, cv=inner, scoring='neg_mean_squared_error',
                                            n_jobs=n_jobs, error_score='raise', refit=True)
                        grid.fit(X[train], y[train])
                        assert np.isfinite(grid.cv_results_['mean_test_score']).all()
                        prediction = float(grid.predict(X[test])[0])
                        record = dict(run_hash=run_hash, target=target, features=feature_name, feature_columns=features,
                                      model=name, fold=fold, test_index=int(test[0]), test_state=data.iloc[test[0]].State,
                                      outer_train_indices=train.tolist(), best_params=grid.best_params_,
                                      best_inner_negative_mse=float(grid.best_score_),
                                      inner_scores=[dict(params=p, mean_negative_mse=float(score))
                                                    for p, score in zip(grid.cv_results_['params'], grid.cv_results_['mean_test_score'])],
                                      inner_splits=[dict(train_indices=train[a].tolist(), validation_indices=train[b].tolist()) for a, b in inner],
                                      actual=float(y[test[0]]), prediction=prediction)
                        if name == 'XGBoost':
                            tree = grid.best_estimator_.named_steps['model']
                            exp = shap.TreeExplainer(tree)(X[test])
                            sv = exp.values[0].astype(float)
                            base = float(np.asarray(exp.base_values).reshape(-1)[0])
                            assert np.isclose(base + sv.sum(), prediction, atol=1e-4)
                            record['shap'] = dict(base=base, values=dict(zip(features, sv.tolist())))
                        dump(path, record)
                    pred[test[0]] = record['prediction']
                    all_folds.append(record)
                    predictions.append(dict(target=target, features=feature_name, model=name,
                                            State=record['test_state'], actual=record['actual'], prediction=record['prediction']))
                    if 'shap' in record:
                        for feature, value in record['shap']['values'].items():
                            shap_rows.append(dict(target=target, feature_set=feature_name, State=record['test_state'],
                                                  feature=feature, shap_value=value, base_value=record['shap']['base']))
                summary.append(dict(target=target, features=feature_name, model=name, **metrics(y, pred)))
                print(f'MODEL {target} {feature_name} {name}: {metrics(y, pred)}', flush=True)
                pd.DataFrame(summary).to_csv(OUT / 'nested_cv_results.csv', index=False)
                pd.DataFrame(predictions).to_csv(OUT / 'outer_predictions.csv', index=False)
                pd.DataFrame(shap_rows).to_csv(OUT / 'held_out_shap.csv', index=False)
    dump(OUT / 'nested_cv_audit.json', dict(run_hash=run_hash, seed=SEED, outer='leave-one-state-out',
                                          inner='shuffled four-fold', scoring='neg_mean_squared_error', folds=all_folds))


def run_figures(data):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    plt.rcParams.update({'font.family': 'DejaVu Sans', 'font.size': 10, 'savefig.dpi': 220,
                         'axes.spines.top': False, 'axes.spines.right': False})
    folder = REV / 'figures'
    folder.mkdir(exist_ok=True)
    fig, axes = plt.subplots(1, 2, figsize=(11, 4.6), layout='constrained')
    panels = [('Circularity_Related_Proxy', 'Circularity-related proxy (0-100)'),
              ('Log_EWaste_Per_Million', 'log(1 + e-waste tonnes/million residents)')]
    for ax, (target, label) in zip(axes, panels):
        sc = ax.scatter(data.Digital_Access_Score, data[target], c=data.Log_NSDP, cmap='viridis', s=42)
        for state in ['Haryana', 'Bihar', 'Telangana', 'Uttarakhand', 'Sikkim']:
            r = data.loc[data.State == state].iloc[0]
            ax.annotate(state, (r.Digital_Access_Score, r[target]), xytext=(4, 5), textcoords='offset points', fontsize=8)
        ax.set(xlabel='Digital access score (0-100)', ylabel=label)
        ax.grid(alpha=.15)
    fig.colorbar(sc, ax=axes, label='Log per-capita NSDP')
    fig.savefig(folder / 'association.png')
    plt.close(fig)
    ranked = data.sort_values('DCI_Descriptive')
    fig, ax = plt.subplots(figsize=(7.8, 7.2), layout='constrained')
    ax.barh(ranked.State, ranked.DCI_Descriptive, color='#207c82')
    ax.set(xlabel='Descriptive DCI (sample-relative, 0-100)', ylabel='')
    ax.grid(axis='x', alpha=.15)
    fig.savefig(folder / 'descriptive_dci.png')
    plt.close(fig)
    if (OUT / 'nested_cv_results.csv').exists():
        results = pd.read_csv(OUT / 'nested_cv_results.csv')
        fig, axes = plt.subplots(1, 2, figsize=(10.5, 4.4), layout='constrained')
        for ax, target in zip(axes, TARGETS):
            rows = results[(results.target == target) & (results.model != 'TrainingMean')]
            labels = [f'{r.model} ({r.features})' for r in rows.itertuples()]
            ax.barh(labels, rows.R2, color=['#207c82' if r == 'digital' else '#be7037' for r in rows.features])
            baseline = float(results.loc[(results.target == target) & (results.model == 'TrainingMean'), 'R2'].iloc[0])
            ax.axvline(0, color='black', lw=.8)
            ax.axvline(baseline, color='gray', ls='--', label='Outer training-mean baseline')
            ax.set(title='E-waste (log)' if target == TARGETS[0] else 'SDG composite', xlabel='Pooled outer LOO R-squared')
            ax.legend(fontsize=7)
        fig.savefig(folder / 'nested_cv_comparison.png')
        plt.close(fig)
    print('Figures written', flush=True)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--stage', choices=['stats', 'models', 'figures', 'all'], default='all')
    parser.add_argument('--jobs', type=int, default=2)
    args = parser.parse_args()
    OUT.mkdir(exist_ok=True)
    data = pd.read_csv(REV / 'data/revised_state_dataset.csv').reset_index(drop=True)
    dump(OUT / 'runtime.json', dict(python=sys.version, platform=platform.platform(), seed=SEED,
                                   numpy=np.__version__, pandas=pd.__version__, xgboost=xgb.__version__))
    if args.stage in ['stats', 'all']:
        run_stats(data)
    if args.stage in ['models', 'all']:
        run_models(data, args.jobs)
    if args.stage in ['figures', 'all']:
        run_figures(data)


if __name__ == '__main__':
    main()
