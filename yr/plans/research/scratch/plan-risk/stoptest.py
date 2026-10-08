"""Queue the stop notebook's cells like Run all, interrupt during the slow run_code cell, report statuses."""
import sys, time, shutil, tempfile, os
import nbformat as nbf
from jupyter_client.manager import start_new_kernel
nb = nbf.read(sys.argv[1], nbf.NO_CONVERT)
codes = [c.source for c in nb.cells if c.cell_type == 'code']
tmp = tempfile.mkdtemp(); shutil.copy('/root/.venvs/yrThinkPython/yr-cache/jupyturtle.py', tmp)
km, kc = start_new_kernel(kernel_name='python3', cwd=tmp)
ids = [kc.execute(src) for src in codes]          # all queued at once, like Run all
time.sleep(6); km.interrupt_kernel()
replies = {}
while len(replies) < len(ids):
    m = kc.get_shell_msg(timeout=120)
    replies[m['parent_header']['msg_id']] = m['content']['status']
for src, i in zip(codes, ids):
    print(replies[i], '|', src.splitlines()[0][:50])
kc.stop_channels(); km.shutdown_kernel(now=True)
