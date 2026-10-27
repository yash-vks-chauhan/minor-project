from pathlib import Path
import json
import pandas as pd

REV = Path(__file__).resolve().parents[1]
OUT = REV / 'manuscript'
stats = json.loads((REV / 'results/statistical_results.json').read_text())
cv = pd.read_csv(REV / 'results/nested_cv_results.csv')
data = pd.read_csv(REV / 'data/revised_state_dataset.csv')
sens = pd.read_csv(REV / 'results/sensitivity_correlations.csv').set_index('specification')


def cvrow(target, features, model):
    return cv[(cv.target == target) & (cv.features == features) & (cv.model == model)].iloc[0]


main = stats['main_association']
adjusted = next(r for r in stats['regressions'] if r['target'] == 'Circularity_Related_Proxy' and r['controls'])
term = next(r for r in adjusted['coefficients'] if r['term'] == 'Digital_Access_Score')
sdg = cvrow('SDG_Index_Score', 'digital', 'ElasticNet')
ew = cvrow('Log_EWaste_Per_Million', 'digital', 'ElasticNet')
macros = dict(SampleN=str(len(data)), MainR=f"{main['pearson_r']:.3f}", MainRho=f"{main['spearman_rho']:.3f}",
              MainP=f"{main['pearson_p']:.6f}", PermutationP=f"{main['permutation_p']:.5f}",
              BootstrapLow=f"{main['bootstrap_percentile_ci'][0]:.3f}", BootstrapHigh=f"{main['bootstrap_percentile_ci'][1]:.3f}",
              AdjustedP=f"{term['p']:.3f}", AdjustedBeta=f"{term['coefficient']:.3f}",
              AdjustedLow=f"{term['ci_low']:.3f}", AdjustedHigh=f"{term['ci_high']:.3f}",
              DigitalSDGRtwo=f'{sdg.R2:.3f}', DigitalEWasteRtwo=f'{ew.R2:.3f}',
              DigitalSDGRMSE=f'{sdg.RMSE:.3f}', DigitalEWasteRMSE=f'{ew.RMSE:.3f}',
              BaselineRtwo=f"{cvrow('SDG_Index_Score','none','TrainingMean').R2:.3f}",
              XGBSDGRtwo=f"{cvrow('SDG_Index_Score','digital','XGBoost').R2:.3f}",
              XGBEWasteRtwo=f"{cvrow('Log_EWaste_Per_Million','digital','XGBoost').R2:.3f}",
              WithoutHaryanaR=f"{stats['without_haryana']['pearson_r']:.3f}",
              DeletionLow=f"{stats['leave_one_state_out_r_range'][0]:.3f}", DeletionHigh=f"{stats['leave_one_state_out_r_range'][1]:.3f}",
              EqualWeightR=f"{sens.loc['Equal weights','pearson_r']:.3f}",
              EWasteOnlyR=f"{sens.loc['E-waste-only outcome','pearson_r']:.3f}",
              EWasteOnlyP=f"{sens.loc['E-waste-only outcome','pearson_p']:.3f}",
              EWasteOnlyRho=f"{sens.loc['E-waste-only outcome','spearman_rho']:.3f}",
              LogEWasteR=f"{sens.loc['Log e-waste-only outcome','pearson_r']:.3f}",
              SDGOnlyR=f"{sens.loc['SDG-only outcome','pearson_r']:.3f}")
(OUT / 'generated_results.tex').write_text('\n'.join('\\newcommand{\\'+k+'}{'+v+'}' for k,v in macros.items())+'\n')
labels = {'Circularity_Related_Proxy':'Combined proxy', 'Log_EWaste_Per_Million':'Log e-waste intensity', 'SDG_Index_Score':'SDG composite'}
lines = [r'\begin{table}[htbp]\centering\small',r'\caption{DAS association per ten points, with HC3 standard errors and t-based inference.}\label{tab:regression}',
         r'\begin{tabular}{llrrr}\toprule Outcome & Log income control & Coefficient & 95\% interval & $p$ \\ \midrule']
for reg in stats['regressions']:
    t=next(x for x in reg['coefficients'] if x['term']=='Digital_Access_Score')
    lines.append(f"{labels[reg['target']]} & {'Yes' if reg['controls'] else 'No'} & {t['coefficient']:.3f} & [{t['ci_low']:.3f}, {t['ci_high']:.3f}] & {t['p']:.4f} \\")
    lines[-1] += '\\'
lines += [r'\bottomrule\end{tabular}\end{table}']
(OUT/'regression_table.tex').write_text('\n'.join(lines)+'\n')
lines=[r'\begin{table}[htbp]\centering\small',r'\caption{Pooled outer leave-one-state-out prediction scores. Inner tuning uses negative MSE.}\label{tab:cv}',
       r'\begin{tabular}{llrrrr}\toprule & & \multicolumn{2}{c}{Log e-waste} & \multicolumn{2}{c}{SDG composite} \\',
       r'Model & Features & $R^2$ & RMSE & $R^2$ & RMSE \\ \midrule']
for model,features in [('TrainingMean','none')]+[(m,f) for f in ['digital','augmented'] for m in ['Ridge','ElasticNet','RandomForest','XGBoost']]:
    a=cvrow('Log_EWaste_Per_Million',features,model);b=cvrow('SDG_Index_Score',features,model)
    lines.append(f'{model} & {features} & {a.R2:.3f} & {a.RMSE:.3f} & {b.R2:.3f} & {b.RMSE:.3f} '+r'\\')
lines += [r'\bottomrule\end{tabular}\end{table}']
(OUT/'cv_table.tex').write_text('\n'.join(lines)+'\n')
lines=[r'\begin{longtable}{lrrrrr}',r'\caption{Revised cohort and descriptive indices.}\\',
       r'\toprule State & UPI/person & E-waste/million & DAS & Proxy & DCI \\ \midrule\endfirsthead',
       r'\toprule State & UPI/person & E-waste/million & DAS & Proxy & DCI \\ \midrule\endhead']
for row in data.itertuples():
    lines.append(f'{row.State} & {row.UPI_PerCapita_Transactions:.0f} & {row.EWaste_Tonnes_Per_Million:.2f} & {row.Digital_Access_Score:.2f} & {row.Circularity_Related_Proxy:.2f} & {row.DCI_Descriptive:.2f} '+r'\\')
lines += [r'\bottomrule\end{longtable}']
(OUT/'state_table.tex').write_text('\n'.join(lines)+'\n')
print('Generated all manuscript numbers and tables from checked results.')
