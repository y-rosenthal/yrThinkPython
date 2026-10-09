import nbformat, nbclient
nb = nbformat.v4.new_notebook()
nb.cells = [nbformat.v4.new_code_cell("import sys; print(sys.getrecursionlimit())"),
 nbformat.v4.new_code_cell("%xmode Context"),
 nbformat.v4.new_code_cell("def recurse():\n    recurse()\nrecurse()")]
c = nbclient.NotebookClient(nb, kernel_name="python3", allow_errors=True); c.execute()
import re
for cell in nb.cells:
    for o in cell.outputs:
        t = o.get("text") or "\n".join(o.get("traceback", []))
        t = re.sub(r"\x1b\[[0-9;]*m","",t)
        print([l for l in t.splitlines() if "skipping" in l or l.strip().isdigit() or "Error" in l][:5])
