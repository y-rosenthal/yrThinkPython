# Simulate a frontend that queues all execute_requests at once (as a Run all does),
# relying on ipykernel's stop_on_error queue abort. Kernel = the venv's python.
import sys, queue as Q
from jupyter_client.manager import start_new_kernel
cells = [
 "import sys\ndef run_code(code):\n    try:\n        exec(code, globals())\n    except Exception:\n        get_ipython().showtraceback()\n"
 "def run_code2(code):\n    r = get_ipython().run_cell(code, store_history=False)\n    if isinstance(r.error_in_exec, KeyboardInterrupt): raise r.error_in_exec\n",
 'run_code("""\nx = 5\nif x = 5:\n    print(1)\n""")',
 "print('reached: after showtraceback SyntaxError')",
 'run_code("""\nprint(undefined_name)\n""")',
 "print('reached: after showtraceback NameError')",
 'run_code2("""\nprint(1/0)\n""")',
 "print('reached: after nested run_cell ZeroDivisionError')",
 "1/0",
 "print('SHOULD BE ABORTED')",
]
km, kc = start_new_kernel(kernel_name='python3')
try:
    ids = [kc.execute(c) for c in cells]   # queue them all, no waiting
    replies = {}
    while len(replies) < len(ids):
        m = kc.get_shell_msg(timeout=30)
        replies[m['parent_header']['msg_id']] = m['content']['status']
    outs = {i: [] for i in ids}
    while True:
        try: m = kc.get_iopub_msg(timeout=2)
        except Q.Empty: break
        pid = m['parent_header'].get('msg_id')
        if pid in outs and m['msg_type'] in ('stream','error','execute_result'):
            c = m['content']
            outs[pid].append((m['msg_type'], c.get('text', c.get('ename','')).strip()[:60]))
    for n,(c,i) in enumerate(zip(cells, ids)):
        print(n, repr(c[:40]), '->', replies[i], outs[i])
finally:
    kc.stop_channels(); km.shutdown_kernel(now=True)
