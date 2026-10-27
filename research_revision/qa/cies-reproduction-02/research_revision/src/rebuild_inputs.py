"""Build revision inputs from archived public evidence, without touching legacy files."""
from pathlib import Path
import hashlib
import json
import re

import numpy as np
import pandas as pd

REV = Path(__file__).resolve().parents[1]
ROOT = REV.parent
RAW = REV / 'data/raw'
EVIDENCE = REV / 'evidence'
STATES = pd.read_csv(ROOT / 'data/raw/niti_sdg_index_2023_24.csv')['State'].tolist()
GROUPS = [
    ['India', 'Jammu & Kashmir', 'Himachal Pradesh'],
    ['Punjab', 'Haryana', 'Delhi'],
    ['Rajasthan', 'Uttar Pradesh', 'Bihar'],
    ['Assam', 'West Bengal', 'Jharkhand'],
    ['Odisha', 'Chhattisgarh', 'Madhya Pradesh'],
    ['Gujarat', 'Maharashtra', 'Andhra Pradesh'],
    ['Karnataka', 'Kerala', 'Tamil Nadu'],
    ['Chandigarh', 'Uttarakhand', 'Sikkim'],
    ['Arunachal Pradesh', 'Nagaland', 'Manipur'],
    ['Mizoram', 'Tripura', 'Meghalaya'],
    ['Daman & Diu', 'Dadra & Nagar Haveli', 'Goa'],
    ['Lakshadweep', 'Puducherry', 'Andaman & Nicobar Islands'],
    ['Telangana', 'Ladakh'],
]


def table11_or_13(table, first_page, column, output):
    pages = (EVIDENCE / 'mohfw_population_projection_2020_mirror.txt').read_text().split('\f')
    records = []
    for offset, names in enumerate(GROUPS):
        page_number = first_page + offset
        text = pages[page_number - 1]
        assert re.search(r'TABLE\s*[–-]\s*' + str(table) + r'\b', text), page_number
        assert '1st July' in text and '2036' in text, page_number
        match = re.search(r'(?m)^\s*2021\s+((?:[\d.,]+[ \t]*)+)', text)
        assert match, page_number
        values = [float(v.replace(',', '')) for v in match[1].split()]
        assert len(values) == 3 * len(names), (page_number, values)
        for index, name in enumerate(names):
            records.append({'State': name, column: values[index * 3],
                            'Year': 2021, 'Reference_Date': '2021-07-01',
                            'Source_Table': table, 'Source_PDF_Page': page_number})
    pd.DataFrame(records).to_csv(RAW / output, index=False)


def main():
    records = []
    for row in json.loads((EVIDENCE / 'trai_pib_table.json').read_text()):
        if len(row) == 3 and row[1] in STATES:
            records.append({'State': row[1], 'Tele_Density_Percent': float(row[2]),
                            'Reference_Date': '2024-06-30', 'Source': 'PIB PRID 2086009 annexure; TRAI'})
    assert len(records) == 28
    pd.DataFrame(records).to_csv(RAW / 'trai_teledensity_2024_06.csv', index=False)

    records = []
    for row in json.loads((EVIDENCE / 'cpcb_pib_table.json').read_text()):
        if len(row) == 4 and row[1] in STATES:
            value = None if row[3].strip(' -') == '' else float(row[3].replace(',', ''))
            records.append({'State': row[1], 'EWaste_Processed_Tonnes': value,
                            'Year': '2021-22', 'Source': 'PIB PRID 2004015 Annexure 1; CPCB'})
    pd.DataFrame(records).to_csv(RAW / 'cpcb_ewaste_2021_22.csv', index=False)

    records = []
    for line in (EVIDENCE / 'nsdp_economic_survey_2025_26.txt').read_text().splitlines():
        match = re.match(r'^\s*([A-Za-z &]+?)\s{2,}((?:\d+|NA)(?:\s+(?:\d+|NA)){8})\s*$', line)
        if match and match[1] in STATES:
            values = match[2].split()
            records.append({'State': match[1], 'Per_Capita_NSDP_Rs': float(values[7]),
                            'Year': '2023-24', 'Source': 'Economic Survey 2025-26 Table 1.11A',
                            'Vintage': '2025-08-01'})
    assert len(records) == 28, records
    pd.DataFrame(records).to_csv(RAW / 'nsdp_2023_24.csv', index=False)

    # The complete 28-state values were visually checked against the PIB ranking
    # image archived with this revision. The source CSV is a transcription.
    sdg = pd.read_csv(ROOT / 'data/raw/niti_sdg_index_2023_24.csv')[['State', 'SDG_Index_Score']]
    sdg['Source'] = 'NITI SDG India Index 2023-24; PIB PRID 2032857 overall state ranking image'
    sdg.to_csv(RAW / 'sdg_2023_24.csv', index=False)
    table11_or_13(11, 89, 'Population_Thousands_2021', 'population_2021.csv')
    table11_or_13(13, 115, 'Urban_Percent_2021', 'urban_share_2021.csv')

    data = pd.DataFrame({'State': sorted(STATES)})
    sources = [
        ('trai_teledensity_2024_06.csv', 'Tele_Density_Percent'),
        ('upi_percapita_2024_25.csv', 'UPI_PerCapita_Transactions'),
        ('nsdp_2023_24.csv', 'Per_Capita_NSDP_Rs'),
        ('sdg_2023_24.csv', 'SDG_Index_Score'),
        ('cpcb_ewaste_2021_22.csv', 'EWaste_Processed_Tonnes'),
        ('population_2021.csv', 'Population_Thousands_2021'),
        ('urban_share_2021.csv', 'Urban_Percent_2021'),
    ]
    for filename, value in sources:
        source = pd.read_csv(RAW / filename)
        assert source.State.is_unique, filename
        data = data.merge(source[['State', value]], on='State', how='left', validate='one_to_one')
    numeric = data.select_dtypes(include='number')
    coverage = data[['State']].copy()
    coverage['Missing_Columns'] = numeric.isna().apply(lambda row: '; '.join(row.index[row]), axis=1)
    coverage['Included'] = ~numeric.isna().any(axis=1)
    coverage.to_csv(REV / 'data/sample_coverage.csv', index=False)
    data = data.loc[coverage.Included].copy()
    assert data.State.is_unique and len(data) >= 20
    assert np.isfinite(data.select_dtypes(include='number').values).all()
    assert (data.EWaste_Processed_Tonnes > 0).all()
    data['Population_Mn_2021'] = data.Population_Thousands_2021 / 1000
    data['EWaste_Tonnes_Per_Million'] = data.EWaste_Processed_Tonnes / data.Population_Mn_2021
    data['Log_EWaste_Per_Million'] = np.log1p(data.EWaste_Tonnes_Per_Million)
    data['Log_NSDP'] = np.log(data.Per_Capita_NSDP_Rs)
    data['Log_Population'] = np.log(data.Population_Mn_2021)
    for raw in ['Tele_Density_Percent', 'UPI_PerCapita_Transactions', 'EWaste_Tonnes_Per_Million', 'SDG_Index_Score']:
        data[raw + '_MinMax'] = 100 * (data[raw] - data[raw].min()) / (data[raw].max() - data[raw].min())
    data['Digital_Access_Score'] = (4 * data.Tele_Density_Percent_MinMax + 3 * data.UPI_PerCapita_Transactions_MinMax) / 7
    data['Circularity_Related_Proxy'] = (7 * data.EWaste_Tonnes_Per_Million_MinMax + 8 * data.SDG_Index_Score_MinMax) / 15
    data['DCI_Descriptive'] = data.Digital_Access_Score * data.Circularity_Related_Proxy / 100
    data.to_csv(REV / 'data/revised_state_dataset.csv', index=False, float_format='%.12g')
    old = pd.read_csv(ROOT / 'data/unified_state_dataset.csv')
    audit = old.merge(data, on='State', suffixes=('_Legacy', '_Revised'))
    comparison = []
    for _, row in audit.iterrows():
        for name in ['UPI_PerCapita_Transactions', 'Per_Capita_NSDP_Rs', 'Tele_Density_Percent', 'SDG_Index_Score', 'EWaste_Processed_Tonnes']:
            a, b = row[name + '_Legacy'], row[name + '_Revised']
            comparison.append({'State': row.State, 'Variable': name, 'Legacy': a, 'Revised': b, 'Changed': a != b})
    pd.DataFrame(comparison).to_csv(REV / 'results/input_changes.csv', index=False)
    manifest = [{'file': str(p.relative_to(REV)), 'sha256': hashlib.sha256(p.read_bytes()).hexdigest(), 'bytes': p.stat().st_size}
                for folder in ['evidence', 'data/raw'] for p in sorted((REV / folder).glob('*'))
                if p.is_file() and p.name != 'manifest.json']
    (REV / 'evidence/manifest.json').write_text(json.dumps(manifest, indent=2) + '\n')
    print('Revised complete-case states:', len(data), ', '.join(data.State))
    print('UPI mismatches among legacy states:', sum(r['Changed'] for r in comparison if r['Variable'] == 'UPI_PerCapita_Transactions'))
    print('Excluded:', coverage.loc[~coverage.Included].to_dict('records'))


if __name__ == '__main__':
    main()
