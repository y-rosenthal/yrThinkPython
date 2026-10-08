import nbformat as nbf
from nbclient import NotebookClient
COLAB_SIM = r'''
# minimal copy of colabtools _shell_customizations ImportError handling + Shell._showtraceback unwrapping
import sys
ip = get_ipython()
class ColabTraceback:
    def __init__(self, stb, error_details): self.stb = stb; self.error_details = error_details
class FormattedTracebackError(Exception):
    def __init__(self, message, stb, details):
        super().__init__(message); self._colab_traceback = ColabTraceback(stb, details)
    def _render_traceback_(self): return self._colab_traceback
def handle_error(shell, etype, exception, tb, tb_offset=None):
    stb = shell.InteractiveTB.structured_traceback(etype, exception, tb, tb_offset=tb_offset)
    stb += ['', 'NOTE: If your import is failing due to a missing package...']
    wrapped = FormattedTracebackError(str(exception), stb, {'actions': []})
    return shell.showtraceback(exc_tuple=(etype, wrapped, tb))
ip.set_custom_exc((ImportError,), handle_error)
_orig = type(ip)._showtraceback
def colab_showtraceback(self, etype, evalue, stb):
    if isinstance(stb, ColabTraceback): stb = stb.stb
    return _orig(self, etype, evalue, stb)
import types
type(ip)._showtraceback = colab_showtraceback
'''
FALLBACK_B = r'''
import sys
def run_code(code):
    ip = get_ipython()
    ip._showtraceback = lambda et, ev, stb: print(ip.InteractiveTB.stb2text(stb), file=sys.stderr)
    try:
        result = ip.run_cell(code, store_history=False)
    finally:
        del ip._showtraceback
    if isinstance(result.error_in_exec, KeyboardInterrupt):
        raise KeyboardInterrupt
'''
RC_A=open('t1.py').read().split("RUN_CODE = '''")[1].split("'''")[0]
cells=[COLAB_SIM, RC_A, 'import nosuchmodule_first', 'print(type(get_ipython()), type(get_ipython())._showtraceback)', 'run_code(r"""\nimport nosuchmodule_xyz\n""")', 'import nosuchmodule_abc', "print('end')"]
nb=nbf.v4.new_notebook(cells=[nbf.v4.new_code_cell(c) for c in cells])
st={}
NotebookClient(nb,timeout=60,kernel_name='python3',allow_errors=True,on_cell_executed=lambda cell,cell_index,execute_reply: st.__setitem__(cell_index,execute_reply['content']['status'])).execute()
import re; A=re.compile(r'\x1b\[[0-9;]*m')
for i,c in enumerate(nb.cells):
    print('--- cell',i,st.get(i))
    for o in c.outputs:
        if o.output_type=='stream': print('  stream',o.name,repr(A.sub('',o.text)[:3000]))
        elif o.output_type=='error': print('  error',o.ename,A.sub('',o.evalue)[:200]); print('   ',A.sub('','\n'.join(o.traceback))[-400:].replace('\n','\n    '))
