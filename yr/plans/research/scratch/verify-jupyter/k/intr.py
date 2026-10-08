import time, threading
from jupyter_client.manager import start_new_kernel
km, kc = start_new_kernel(kernel_name='python3')
def run(code, interrupt_after=None):
    msg_id = kc.execute(code)
    if interrupt_after:
        time.sleep(interrupt_after); km.interrupt_kernel()
    outs = []
    while True:
        m = kc.get_iopub_msg(timeout=30)
        if m['parent_header'].get('msg_id') != msg_id: continue
        t = m['msg_type']
        if t == 'error': outs.append('error:' + m['content']['ename'])
        if t == 'stream': outs.append('stream:' + m['content']['text'].strip()[:60])
        if t == 'status' and m['content']['execution_state'] == 'idle': break
    rep = kc.get_shell_msg(timeout=30)
    while rep['parent_header'].get('msg_id') != msg_id:
        rep = kc.get_shell_msg(timeout=30)
    return rep['content']['status'], outs
run("import sys, IPython; print(sys.version.split()[0], IPython.__version__)")
print(run("import IPython; print(IPython.__version__)"))
print('nested run_cell, interrupted:', run("get_ipython().run_cell('import time\\ntime.sleep(5)', store_history=False)", 1.0))
print('nested run_cell + reraise KI:', run("r = get_ipython().run_cell('import time\\ntime.sleep(5)', store_history=False)\nif isinstance(r.error_in_exec, KeyboardInterrupt): raise r.error_in_exec", 1.0))
print('exec+catch Exception, interrupted:', run("try:\n    exec('import time\\ntime.sleep(5)')\nexcept Exception:\n    get_ipython().showtraceback()", 1.0))
print('plain, interrupted:', run("import time\ntime.sleep(5)", 1.0))
# queued-cell abort after error reply
kc.stop_channels(); km.shutdown_kernel(now=True)
