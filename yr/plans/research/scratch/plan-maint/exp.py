"""Execute an original page and its converted version; compare per-question outputs.
usage: exp.py ORIG NEW JUPYTURTLE
Reports: reply statuses 'error' in NEW (would stop Run all), outputs outside Answers in NEW,
per-question output differences (stdout / error line / execute_result / display kinds),
and two candidate reverse checks:
  R1 every ```text block in an Answer of a question that has run cells equals some run output
     (stdout exactly, or contains an error line, or equals an execute_result)
  R2 every error-looking last line in those text blocks has its exception name produced by a run cell
"""
import re, shutil, sys, tempfile
from pathlib import Path
import nbformat as nbf
from nbclient import NotebookClient

TEXT = re.compile(r'```text\n(.*?)```', re.S)
ANSI = re.compile(r'\x1b\[[0-9;]*m')
ERRLINE = re.compile(r'^([A-Z]\w*(?:Error|Exception|Interrupt|Exit))\b')


def execute(path, jt):
    nb = nbf.read(path, as_version=4)
    status = {}
    with tempfile.TemporaryDirectory() as tmp:
        shutil.copy(jt, tmp)
        client = NotebookClient(nb, timeout=600, kernel_name='python3', allow_errors=True,
                                resources={'metadata': {'path': tmp}})
        client.on_cell_executed = lambda cell, cell_index, execute_reply: status.__setitem__(
            cell_index, execute_reply['content']['status'])
        client.execute()
    return nb, status


def err_line(o):
    v = re.sub(r' \([^()]*, line \d+\)$', '', ANSI.sub('', o.get('evalue', '')))
    return f"{o['ename']}: {v}"


def outs(c):
    r = []
    for o in c.outputs:
        if o.output_type == 'stream' and o.name == 'stdout':
            r.append(('stdout', o.text.strip()))
        elif o.output_type == 'stream':
            r.append(('stderr', o.text.strip()[:60]))
        elif o.output_type == 'error':
            r.append(('error', err_line(o)))
        elif o.output_type == 'execute_result':
            r.append(('result', o.data.get('text/plain', '')))
        else:
            r.append((o.output_type, ','.join(sorted(o.get('data', {})))))
    # merge consecutive stdout chunks
    m = []
    for k, v in r:
        if m and k == 'stdout' and m[-1][0] == 'stdout':
            m[-1] = ('stdout', (m[-1][1] + '\n' + v).strip())
        else:
            m.append((k, v))
    return m


def groups(cells):
    gs, cur = [], None
    for i, c in enumerate(cells):
        if c.cell_type == 'markdown' and c.source.lstrip().startswith('### '):
            cur = []; gs.append(cur)
        elif c.cell_type == 'markdown' and c.source.lstrip().startswith(('# ', '## ')):
            cur = None
        if cur is not None:
            cur.append((i, c))
    return gs


def main(orig, new, jt):
    o_nb, _ = execute(orig, jt)
    n_nb, st = execute(new, jt)
    print(f'== {Path(new).name}')
    bad = [i for i, s in st.items() if s != 'ok']
    print('  reply status != ok (Run all would stop):', bad or 'none')
    # visibility: outputs in cells not inside an Answer section
    hidden, inside = set(), False
    for i, c in enumerate(n_nb.cells):
        if c.cell_type == 'markdown' and re.match(r'\s*#### Answer\s*$', c.source):
            inside = True; continue
        if c.cell_type == 'markdown' and re.match(r'\s*#{1,4} ', c.source):
            inside = False
        if inside:
            hidden.add(i)
    vis = [i for i, c in enumerate(n_nb.cells) if c.cell_type == 'code' and c.outputs and i not in hidden
           and 'setup' not in c.metadata.get('tags', [])]
    print('  outputs visible outside Answers (setup excluded):', vis or 'none')
    og, ng = groups(o_nb.cells), groups(n_nb.cells)
    assert len(og) == len(ng)
    diffs = r1 = r2 = 0
    for a, b in zip(og, ng):
        title = b[0][1].source.splitlines()[0]
        o_out = [x for i, c in a if c.cell_type == 'code' and c.source.strip() != '# Your code here'
                 and not (not c.outputs) for x in outs(c)]
        run = [(i, c) for i, c in b if c.cell_type == 'code' and c.source.lstrip().startswith(('run_code(', '# Part', '%%run_question'))]
        n_out = [x for i, c in run for x in outs(c)]
        if o_out != n_out:
            diffs += 1
            print(f'  DIFF {title}\n     orig {o_out}\n     new  {n_out}')
        if run:
            ans = ''.join(c.source for i, c in b if c.cell_type == 'markdown' and i in hidden)
            texts = [t.strip() for t in TEXT.findall(ans)]
            produced_names = {v.split(':')[0] for k, v in n_out if k == 'error'}
            for t in texts:
                ok = any((k == 'stdout' and v == t) or (k == 'error' and v in t) or (k == 'result' and v == t)
                         for k, v in n_out)
                if not ok:
                    r1 += 1
                    print(f'  R1 unbacked text block in {title}: {t[:70]!r}')
                last = t.strip().splitlines()[-1] if t.strip() else ''
                m = ERRLINE.match(last)
                if m and m.group(1) not in produced_names:
                    r2 += 1
                    print(f'  R2 error name {m.group(1)} not produced in {title}')
    print(f'  questions with output differences: {diffs}; R1 misses: {r1}; R2 misses: {r2}')


if __name__ == '__main__':
    main(*sys.argv[1:])
