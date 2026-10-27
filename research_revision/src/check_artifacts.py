"""Check final local artifacts against analysis outputs and venue constraints."""
from pathlib import Path
import hashlib
import json
import re
import subprocess
import unicodedata

import pandas as pd
from pypdf import PdfReader

REV = Path(__file__).resolve().parents[1]


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    stats = json.loads((REV / 'results/statistical_results.json').read_text())
    models = pd.read_csv(REV / 'results/nested_cv_results.csv')
    metadata = json.loads((REV / 'submissions/author_metadata.json').read_text())
    authors=metadata.get('authors_in_submission_order',metadata['authors_in_existing_order'])
    records = json.loads((REV / 'results/submission_format_checks.json').read_text())
    expected = [f"{stats['main_association']['pearson_r']:.3f}",
                f"{stats['main_association']['spearman_rho']:.3f}"]
    reg = next(x for x in stats['regressions']
               if x['target'] == 'Circularity_Related_Proxy' and x['controls'] == ['Log_NSDP'])
    expected.append(f"{next(x['p'] for x in reg['coefficients'] if x['term']=='Digital_Access_Score'):.3f}")
    for target in ['Log_EWaste_Per_Million', 'SDG_Index_Score']:
        result = models[(models.target == target) & (models.features == 'digital') & (models.model == 'ElasticNet')]
        expected.append(f'{result.iloc[0].R2:.3f}')
    paths = [REV / 'manuscript/main.pdf'] + [REV / record['file'] for record in records]
    checked = []
    for path in paths:
        reader = PdfReader(path)
        texts = [page.extract_text() or '' for page in reader.pages]
        # Poppler preserves mathematical decimal spacing better than pypdf.
        text = subprocess.run(['pdftotext', '-layout', str(path), '-'],
                              check=True, capture_output=True, text=True).stdout
        assert all(len(page.strip()) > 50 for page in texts), ('blank or nearly blank page', path)
        assert '\ufffd' not in text and '\x00' not in text, ('invalid extracted character', path)
        for number in expected:
            assert number in text, (path, 'missing expected result', number)
        if path == REV / 'manuscript/main.pdf':
            flattened = ' '.join(unicodedata.normalize('NFKC',text).split())
            for author in authors:
                assert author['name'] in flattened and author['email'] in flattened, ('missing master author',author['name'])
            first_page=' '.join(unicodedata.normalize('NFKC',texts[0]).split())
            positions=[first_page.find(author['name']) for author in authors]
            assert min(positions)>=0 and positions==sorted(positions), 'incorrect author order in master'
            assert 'Corresponding author: Yash Chauhan' in flattened
            for declaration in ['funding_statement','competing_interests_statement']:
                if metadata.get(declaration):
                    assert metadata[declaration] in flattened, ('missing confirmed declaration',declaration)
        if '02-weave' in str(path):
            for author in authors:
                assert author['name'].lower() not in text.lower()
                assert author['email'].lower() not in text.lower()
            for identifier in ['srmist.edu.in', 'SRM Institute', 'Kattankulathur']:
                assert identifier.lower() not in text.lower()
            assert not reader.metadata.get('/Author')
        checked.append(dict(file=str(path.relative_to(REV)), pages=len(reader.pages), sha256=sha(path)))
    for record in records:
        source = (REV / record['file']).with_suffix('.md')
        body = source.read_text().strip().split('\n\n', 1)[1].split('## References')[0]
        count = len(re.findall(r'\S+', re.sub(r'[#*]', '', body)))
        assert record['body_words'] == count
        assert record['limits'][0] <= count <= record['limits'][1]
    for venue in ['01-ioce2027', '04-urban-eplanning2027']:
        path = REV / 'submissions' / venue / 'abstract_body.txt'
        assert not path.read_text().startswith('Digital Access')
        title = (path.parent / 'abstract.md').read_text().splitlines()[0][2:]
        assert title not in path.read_text()
    # The evidence manifest deliberately excludes itself, avoiding a self-hash cycle.
    for record in json.loads((REV / 'evidence/manifest.json').read_text()):
        assert sha(REV / record['file']) == record['sha256'], record['file']
    digest = hashlib.sha256()
    for path in [REV / 'data/revised_state_dataset.csv', REV / 'ANALYSIS_PROTOCOL.md', REV / 'src/analyze.py']:
        digest.update(path.read_bytes())
    audit = json.loads((REV / 'results/nested_cv_audit.json').read_text())
    assert digest.hexdigest() == audit['run_hash'], 'model outputs are stale for the current data/protocol/code'
    log = (REV / 'manuscript/main.log').read_text()
    assert 'Overfull' not in log and 'Underfull' not in log, 'resolve manuscript layout warnings'
    result = dict(status='PASS', artifacts=checked, required_result_strings=expected,
                  checks=['expected numeric results in every PDF', 'no blank PDF pages',
                          'no invalid extracted characters', 'anonymous WEAVE content and author metadata',
                          'word limits', 'body-only form text', 'evidence hashes',
                          'current data/protocol/code model hash', 'clean manuscript layout log',
                          'all three authors and confirmed declarations in master',
                          'confirmed author order and Yash correspondence in master'],
                  visual_review='Required separately; automatic checks do not certify page layout.',
                  submission_status=json.loads((REV / 'submissions/01-ioce2027/browser_progress.json').read_text())['status'])
    (REV / 'results/artifact_checks.json').write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
