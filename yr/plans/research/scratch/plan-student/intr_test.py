import time, sys, json
from jupyter_client.manager import start_new_kernel
src = open(sys.argv[1]).read(); setup = src.split("SETUP = r'''")[1].split("'''")[0]
km, kc = start_new_kernel(kernel_name='python3')
def wait(msg_id):
    while True:
        m = kc.get_shell_msg(timeout=60)
        if m['parent_header'].get('msg_id') == msg_id: return m['content']['status']
wait(kc.execute(setup))
a = kc.execute('run_code("""\nimport time\nfor i in range(30):\n    time.sleep(1)\nprint(\'finished\')\n""")', stop_on_error=True)
b = kc.execute("print('END')", stop_on_error=True)   # queued, like Run all
time.sleep(2); km.interrupt_kernel()
print('slow cell:', wait(a), '| queued END cell:', wait(b))
n_err = 0
while True:
    try: m = kc.get_iopub_msg(timeout=2)
    except Exception: break
    if m['msg_type'] == 'error' and m['parent_header'].get('msg_id') == a: n_err += 1
print('error outputs in the slow cell:', n_err)
kc.stop_channels(); km.shutdown_kernel(now=True)
