"""Regenerate jb/soln_overlay.json from Allen Downey's ThinkPythonSolutions notebooks.

Downey builds his website from the notebooks in AllenDowney/ThinkPythonSolutions (soln/), not
from the chapters/ notebooks, which are generated from them with outputs, display tags and
solutions stripped. This fork builds from chapters/, so it takes two things from his notebooks,
matched by cell id, and keeps them in soln_overlay.json:

- display tags (remove-input, remove-cell, section_* labels, ...), which prep_notebooks.py
  adds to the copies in jb/ at build time, so pages show and hide the same things as his site;
- his solution code for the '# Solution goes here' cells, which execute_notebooks.py runs (in a
  scratch copy, never shown) so the exercise test cells can draw their example pictures.

chapters/ itself is never modified. Run this after syncing with upstream (see the sync-upstream
skill), from the repo root or jb/:

    python jb/update_overlay.py
"""
import json
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
URL = 'https://raw.githubusercontent.com/AllenDowney/ThinkPythonSolutions/v3/soln/{name}'
KEEP = {'remove-cell', 'remove-input', 'remove-output', 'hide-cell', 'hide-input', 'hide-output',
        'raises-exception'}


def keep(tag):
    return tag in KEEP or tag.startswith(('section', 'chapter'))


def main():
    overlay = {}
    for chap in sorted((ROOT / 'chapters').glob('chap[01][0-9].ipynb')):
        with urllib.request.urlopen(URL.format(name=chap.name)) as r:
            soln = json.load(r)
        cells = {c['id']: c for c in json.loads(chap.read_text(encoding='utf-8'))['cells']}
        tags, solutions = {}, {}
        for c in soln['cells']:
            mine = cells.get(c.get('id'))
            if mine is None:
                continue
            t = [t for t in c['metadata'].get('tags', []) if keep(t)]
            if t:
                tags[c['id']] = t
            if mine['cell_type'] == 'code' and ''.join(mine['source']).startswith('# Solution'):
                src = ''.join(c['source'])
                if src.strip() and not src.startswith('# Solution goes here'):
                    solutions[c['id']] = src
        overlay[chap.stem] = {'tags': tags, 'solutions': solutions}
        print(f'{chap.stem}: {len(tags)} tagged cells, {len(solutions)} solutions '
              f'({len(cells)} cells, {len(set(cells) & {c.get("id") for c in soln["cells"]})} matched)')
    out = ROOT / 'jb' / 'soln_overlay.json'
    out.write_text(json.dumps(overlay, indent=1, ensure_ascii=False, sort_keys=True) + '\n', encoding='utf-8')
    print(f'wrote {out.relative_to(ROOT)}')


if __name__ == '__main__':
    main()
