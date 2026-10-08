import time, sys
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
        if m['msg_type'] == 'error': outs.append('error:' + m['content']['ename'])
        if m['msg_type'] == 'status' and m['content']['execution_state'] == 'idle': break
    reply = kc.get_shell_msg(timeout=30)
    return reply['content']['status'], outs
run(open('magic_def.py').read())
print('magic, interrupted:', run('%%run_question\nimport time\nwhile True:\n    time.sleep(0.1)', 1.5))
print('magic, normal error:', run('%%run_question\n1/0'))
# queue behaviour: send 3 requests at once like Run all; middle one is a magic error
ids = [kc.execute(c) for c in ['%%run_question\n1/0', '%%run_question\nx = 5\nif x = 5:\n    pass', 'print("after")']]
for _ in ids:
    r = kc.get_shell_msg(timeout=30); print('queued reply:', r['content']['status'])
kc.stop_channels(); km.shutdown_kernel(now=True)
