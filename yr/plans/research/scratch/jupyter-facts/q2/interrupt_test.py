"""What happens to execute_reply status when the user interrupts code running inside run_code variants."""
import time, re
from jupyter_client.manager import start_new_kernel
ANSI = re.compile(r'\x1b\[[0-9;]*m')
km, kc = start_new_kernel(kernel_name='python3')
SETUP = '''
import sys
def run_exec_catch(code):
    try:
        exec(code, globals())
    except Exception:
        get_ipython().showtraceback()
def run_nested(code):
    get_ipython().run_cell(code, store_history=False)
'''
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
        elif t == 'stream': outs.append('stream:' + m['content']['text'].strip())
        elif t == 'status' and m['content']['execution_state'] == 'idle': break
    reply = kc.get_shell_msg(timeout=30)
    return reply['content']['status'], outs
print('setup', run(SETUP))
print('exec+catch, interrupted :', run('run_exec_catch("import time\\ntime.sleep(10)")', 1.5))
print('nested run_cell, interrupted:', run('run_nested("import time\\ntime.sleep(10)")', 1.5))
print('plain cell, interrupted     :', run('import time\ntime.sleep(10)', 1.5))
kc.stop_channels(); km.shutdown_kernel(now=True)
