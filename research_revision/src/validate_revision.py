"""Independent checks of source anchors, revision arithmetic, and CV separation."""
from pathlib import Path
import hashlib
import json

import numpy as np
import pandas as pd
from sklearn.metrics import mean_squared_error, r2_score

REV = Path(__file__).resolve().parents[1]


def main():
    data = pd.read_csv(REV / 'data/revised_state_dataset.csv')
    assert len(data) == 22 and data.State.nunique() == 22
    anchors = {
        'Andhra Pradesh': ('UPI_PerCapita_Transactions', 122),
        'Haryana': ('EWaste_Processed_Tonnes', 245015.82),
        'Kerala': ('UPI_PerCapita_Transactions', 112),
        'Tamil Nadu': ('UPI_PerCapita_Transactions', 107),
        'Sikkim': ('Population_Thousands_2021', 678),
        'Bihar': ('Population_Thousands_2021', 123695),
        'Punjab': ('Per_Capita_NSDP_Rs', 205374),
        'West Bengal': ('UPI_PerCapita_Transactions', 51),
    }
    for state, (column, expected) in anchors.items():
        assert np.isclose(data.set_index('State').loc[state, column], expected), (state, column)
    assert np.allclose(data.EWaste_Tonnes_Per_Million,
                       data.EWaste_Processed_Tonnes / (data.Population_Thousands_2021 / 1000))
    for raw in ['Tele_Density_Percent', 'UPI_PerCapita_Transactions', 'EWaste_Tonnes_Per_Million', 'SDG_Index_Score']:
        normalized = data[raw + '_MinMax']
        assert np.isclose(normalized.min(), 0) and np.isclose(normalized.max(), 100)
    # Explicitly recompute from only the independent component columns.
    expected_das = 4/7 * data.Tele_Density_Percent_MinMax + 3/7 * data.UPI_PerCapita_Transactions_MinMax
    expected_proxy = 7/15 * data.EWaste_Tonnes_Per_Million_MinMax + 8/15 * data.SDG_Index_Score_MinMax
    assert np.allclose(data.Digital_Access_Score, expected_das)
    assert np.allclose(data.Circularity_Related_Proxy, expected_proxy)
    coverage = pd.read_csv(REV / 'data/sample_coverage.csv')
    assert len(coverage) == 28
    assert set(coverage.loc[~coverage.Included, 'State']) == {'Arunachal Pradesh', 'Goa', 'Manipur', 'Meghalaya', 'Nagaland', 'Uttar Pradesh'}
    audit = json.loads((REV / 'results/nested_cv_audit.json').read_text())
    folds = audit['folds']
    assert len(folds) == 2 * 2 * 4 * len(data)
    for record in folds:
        test = record['test_index']
        outer = set(record['outer_train_indices'])
        assert outer == set(range(len(data))) - {test}
        valid = []
        for split in record['inner_splits']:
            train = set(split['train_indices'])
            validation = set(split['validation_indices'])
            assert not train.intersection(validation)
            assert train.union(validation) == outer
            assert test not in train and test not in validation
            valid.extend(validation)
        assert set(valid) == outer and len(valid) == len(outer)
        assert all(np.isfinite(s['mean_negative_mse']) for s in record['inner_scores'])
        assert np.isfinite(record['prediction'])
        if 'shap' in record:
            assert np.isclose(record['shap']['base'] + sum(record['shap']['values'].values()), record['prediction'], atol=1e-4)
    predictions = pd.read_csv(REV / 'results/outer_predictions.csv')
    summary = pd.read_csv(REV / 'results/nested_cv_results.csv')
    for (target, features, model), group in predictions.groupby(['target', 'features', 'model']):
        assert len(group) == len(data) and group.State.nunique() == len(data)
        row = summary[(summary.target == target) & (summary.features == features) & (summary.model == model)].iloc[0]
        assert np.isclose(row.R2, r2_score(group.actual, group.prediction))
        assert np.isclose(row.RMSE, np.sqrt(mean_squared_error(group.actual, group.prediction)))
        if model == 'TrainingMean':
            expected = (group.actual.sum() - group.actual) / (len(group) - 1)
            assert np.allclose(expected, group.prediction)
    original_manifest = json.loads((REV / 'baseline/manifest.json').read_text())
    original_science_files = [r for r in original_manifest if not r['path'].startswith('output/research/')]
    for record in original_science_files:
        path = REV.parent / record['path']
        assert hashlib.sha256(path.read_bytes()).hexdigest() == record['sha256'], record['path']
    result = dict(status='PASS', states=len(data), audited_outer_fits=len(folds),
                  inner_folds_audited=sum(len(r['inner_splits']) for r in folds),
                  prediction_groups=len(summary), original_science_files_preserved=len(original_science_files),
                  checks=['source anchors', 'population units', 'actual min-max normalization',
                          'no income term in descriptive indices', 'explicit missing-state exclusion',
                          'outer holdout isolation', 'disjoint inner splits', 'finite tuning scores',
                          'one prediction per state', 'metrics recomputation', 'training-mean baseline',
                          'held-out SHAP additivity', 'unchanged original scientific files'])
    (REV / 'results/validation.json').write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
