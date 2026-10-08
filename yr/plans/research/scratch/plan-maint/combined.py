import re, shutil, sys, tempfile, glob
import nbformat as nbf
from nbclient import NotebookClient
TEXT = re.compile(r'```text\n(.*?)```', re.S)
for p in sorted(glob.glob('new3/chap0*_review.ipynb')):
    nb = nbf.read(p, as_version=4)
    with tempfile.TemporaryDirectory() as tmp:
        shutil.copy('/root/.venvs/yrThinkPython/yr-cache/jupyturtle.py', tmp)
        NotebookClient(nb, kernel_name='python3', allow_errors=True, timeout=600, resources={'metadata': {'path': tmp}}).execute()
    nbf.write(nb, p.replace('new3/', 'new3/executed_'))
    # answers: cells between '#### Answer' and next heading
    ans_texts, cur, n_res, fails = None, [], 0, []
    groups = []
    for c in nb.cells:
        if c.cell_type == 'markdown' and re.match(r'\s*#{1,3} ', c.source):
            groups.append([]); 
        if groups: groups[-1].append(c)
    for g in groups:
        texts = [t.strip() for c in g if c.cell_type == 'markdown' for t in TEXT.findall(c.source)]
        for c in g:
            if c.cell_type == 'code' and c.source.startswith('%%run_question'):
                parts = []
                for o in c.outputs:
                    if o.output_type == 'stream' and o.name == 'stdout': parts.append(o.text)
                    elif o.output_type == 'execute_result':
                        n_res += 1; parts.append(o.data['text/plain'] + '\n')
                shown = ''.join(parts).strip()
                if shown and shown not in texts:
                    fails.append((g[0].source.splitlines()[0], shown[:80]))
    print(p, 'execute_results:', n_res, 'combined-display mismatches:', fails or 'none')
