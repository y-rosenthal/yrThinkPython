import sys, nbformat as nbf
a = nbf.read(sys.argv[1], as_version=4); b = nbf.read(sys.argv[2], as_version=4)
def norm(nb):
    out=[]
    for c in nb.cells:
        md = {k:v for k,v in c.metadata.items() if k!='id'}
        out.append((c.cell_type, c.source, sorted(md.items(), key=str)))
    return out
na, nb2 = norm(a), norm(b)
print(sys.argv[1].split('/')[-1], 'cells', len(na), len(nb2), 'identical-ignoring-ids' if na==nb2 else 'DIFFERENT')
if na!=nb2:
    for i,(x,y) in enumerate(zip(na,nb2)):
        if x!=y: print(' first diff at', i, repr(x[1][:80]), repr(y[1][:80])); break
