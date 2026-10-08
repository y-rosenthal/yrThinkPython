import sys, json, nbformat as nbf
from nbclient import NotebookClient
from pathlib import Path
here = Path(__file__).parent
for p in sorted((here/'nbs').glob('chap0*_review.ipynb')):
    nb = nbf.read(p, nbf.NO_CONVERT)
    NotebookClient(nb, timeout=300, kernel_name='python3', allow_errors=True,
                   resources={'metadata': {'path': str(here/'run')}}).execute()
    nbf.write(nb, here/'run'/(p.stem + '.executed.ipynb'))
    print('done', p.name)
