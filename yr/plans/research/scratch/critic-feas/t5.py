import nbformat as nbf, re
from nbclient import NotebookClient
src=open('t2.py').read()
COLAB_SIM=src.split("COLAB_SIM = r'''")[1].split("'''")[0]
COLAB_SIM=COLAB_SIM.replace("    if isinstance(stb, ColabTraceback): stb = stb.stb", "    import sys as _s; open('/tmp/claude-0/-home-user-yrThinkPython/6571a165-f8cc-5e43-8b74-c00357a4a6f6/scratchpad/ultra/critic-feas/dbg.txt','a').write(repr(type(stb))+' '+repr(ColabTraceback)+chr(10))\n    if isinstance(stb, ColabTraceback): stb = stb.stb")
cells=[COLAB_SIM, 'import nosuchmodule_first']
nb=nbf.v4.new_notebook(cells=[nbf.v4.new_code_cell(c) for c in cells])
NotebookClient(nb,timeout=60,kernel_name='python3',allow_errors=True).execute()
for i,c in enumerate(nb.cells):
    for o in c.outputs: print(i,o.output_type, (o.get('text') or o.get('evalue'))[:300])
