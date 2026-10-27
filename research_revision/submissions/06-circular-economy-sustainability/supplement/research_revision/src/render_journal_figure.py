"""Render the journal's vector figure from the unchanged 22-state dataset."""
from pathlib import Path
import argparse
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import pandas as pd

REV = Path(__file__).resolve().parents[1]


def render(data_path, output):
    data = pd.read_csv(data_path)
    assert len(data) == 22 and data.State.is_unique
    output = Path(output)
    output.mkdir(parents=True, exist_ok=True)
    plt.rcParams.update({'font.family': 'DejaVu Sans', 'font.size': 8,
                         'axes.spines.top': False, 'axes.spines.right': False,
                         'pdf.fonttype': 42, 'ps.fonttype': 42})
    fig, axes = plt.subplots(1, 2, figsize=(174 / 25.4, 88 / 25.4), layout='constrained')
    panels = [('Circularity_Related_Proxy', 'Circularity-related proxy (0-100)'),
              ('Log_EWaste_Per_Million', 'log(1 + e-waste tonnes/million residents)')]
    for panel, (ax, (target, label)) in enumerate(zip(axes, panels)):
        sc = ax.scatter(data.Digital_Access_Score, data[target], c=data.Log_NSDP,
                        cmap='viridis', s=23, edgecolor='black', linewidth=.25)
        for state in ['Haryana', 'Bihar', 'Telangana', 'Uttarakhand', 'Sikkim']:
            row = data.loc[data.State == state].iloc[0]
            offset, align = (3, 4), 'left'
            if state == 'Uttarakhand':
                offset, align = (-4, 7), 'right'
            elif state == 'Haryana':
                offset = (3, 7)
            elif state == 'Telangana':
                offset, align = (-4, 26 if panel == 0 else 20), 'right'
            elif state == 'Sikkim' and panel == 0:
                offset, align = (-4, -10), 'right'
            ax.annotate(state, (row.Digital_Access_Score, row[target]),
                        xytext=offset, textcoords='offset points', fontsize=8,
                        horizontalalignment=align,
                        arrowprops={'arrowstyle':'-', 'lw':.5, 'color':'#555555'}
                        if state == 'Telangana' else None)
        ax.text(.03, .96, f'({chr(97 + panel)})', transform=ax.transAxes,
                va='top', fontweight='bold')
        ax.set(xlabel='Digital access score (0-100)', ylabel=label)
        ax.margins(x=.12, y=.15)
        ax.grid(color='#dddddd', linewidth=.4)
        ax.set_axisbelow(True)
    fig.colorbar(sc, ax=axes, label='Log per-capita NSDP', fraction=.04)
    fig.savefig(output / 'Fig1.pdf', metadata={'Title': 'Digital access and separate circularity-related outcomes', 'Author': 'Yash Chauhan; Suresh Kumar Chelliah; Shreya Srivastava'})
    fig.savefig(output / 'Fig1.eps')
    plt.close(fig)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--data', type=Path, default=REV / 'data/revised_state_dataset.csv')
    parser.add_argument('--output', type=Path, default=REV / 'figures/journal')
    args = parser.parse_args()
    render(args.data, args.output)
