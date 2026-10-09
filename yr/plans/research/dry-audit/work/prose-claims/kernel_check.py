"""Check the notebook-only claims in a real Jupyter kernel."""
import nbformat, nbclient
cells = ["import sys\nsys.getrecursionlimit()",
         "def f(n):\n    return f(n + 1)\ndepth = 0\ndef g(n):\n    global depth\n    depth = n\n    g(n + 1)\ntry:\n    g(0)\nexcept RecursionError as e:\n    print(depth, e)",
         "def greet():\n    print('Hello')\n\ngreet",
         "None",
         "import math\nmath.pi"]
nb = nbformat.v4.new_notebook(cells=[nbformat.v4.new_code_cell(c) for c in cells])
nbclient.NotebookClient(nb, timeout=60, kernel_name='python3').execute()
for c in nb.cells:
    print('---', c.source.splitlines()[-1], '->', [o.get('data', {}).get('text/plain') or o.get('text') for o in c.outputs])
