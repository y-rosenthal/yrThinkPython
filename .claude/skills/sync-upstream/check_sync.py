#!/usr/bin/env python3
"""After merging upstream (Allen Downey's ThinkPython), prove that nothing of the fork was lost and all of his
changes arrived. Stdlib + git only.

    check_sync.py [--before REF] [--upstream REF]

Compares three versions with the working tree (the merge result):
  BASE      the last common commit of the fork and upstream (git merge-base BEFORE UPSTREAM)
  BEFORE    the fork before the merge (default: HEAD while a merge is in progress; else the first parent of the
            newest merge of UPSTREAM on this branch; else v3)
Files edited after that merge commit are checked as the merge left them, and listed as notes.
  UPSTREAM  Downey's version (default upstream/v3)

Rules (the fork's sync policy, .claude/skills/sync-upstream/SKILL.md):
  1. Fork files stay: every file of BEFORE that the fork added or changed still exists.
  2. Fork edits stay: in each notebook, every cell the fork added or changed (BEFORE differs from BASE) has the fork's
     text and tags; a cell the fork removed stays removed. In other text files, every line the fork added is there.
  3. Downey's changes arrive: every cell he added or changed (and the fork did not) has his text; a cell he removed is
     gone; every file he added exists; a file the fork never changed equals his version; binary files equal his.
  4. Colab links are the fork's (fork_colab_links.py --check): links are compared with both repositories' names made
     the same, so a rewritten link is not a difference.
  5. The fork's own pages are untouched by the merge: yr/, solutions/, author-guide/ equal BEFORE.
A cell that both the fork and Downey changed keeps the fork's text and is listed as "both changed": read his
change and apply it by hand if it is a correction you want.
Exit status 1 if a rule is broken.
"""
import difflib
import json
import re
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(HERE))
import fork_colab_links  # noqa: E402

FORK_PAGES = ('yr/', 'solutions/', 'author-guide/')
BINARY = ('.zip', '.png', '.jpg', '.jpeg', '.gif', '.pdf', '.svg')


def git(*args, binary=False):
    r = subprocess.run(['git', '-C', str(ROOT), *args], capture_output=True)
    if r.returncode:
        return None
    return r.stdout if binary else r.stdout.decode('utf-8', 'replace')


def files_at(ref):
    return set((git('ls-tree', '-r', '--name-only', ref) or '').split('\n')) - {''}


def norm(text):
    """Text with repository names made the same, so a link rewritten to the fork is not a difference."""
    return fork_colab_links.same_repo(text)


def cells(text):
    if text is None:
        return None
    try:
        nb = json.loads(text)
    except json.JSONDecodeError:
        return None
    out = {}
    for i, c in enumerate(nb.get('cells', [])):
        src = ''.join(c['source']) if isinstance(c['source'], list) else c['source']
        out[c.get('id') or f'#{i}'] = (norm(src), tuple(sorted(c.get('metadata', {}).get('tags', []))))
    return out


def worktree(path, binary=False):
    p = ROOT / path
    if not p.exists():
        return None
    data = p.read_bytes()                       # bytes, so line endings compare exactly as git stores them
    return data if binary else data.decode('utf-8', 'replace')


def find_merge(upstream):
    """The newest merge commit on HEAD's first-parent line whose second parent is in UPSTREAM, or None."""
    for line in (git('rev-list', '--first-parent', '--parents', '-n', '50', 'HEAD') or '').split('\n'):
        ids = line.split()
        if len(ids) > 2 and git('merge-base', '--is-ancestor', ids[2], upstream) is not None:
            return ids[0]
    return None


def default_before(merge):
    if (ROOT / '.git' / 'MERGE_HEAD').exists():
        return 'HEAD'
    return f'{merge}^1' if merge else 'v3'


def check_notebook(path, b, f, u, a, problems, notes):
    base, fork, up, after = cells(b), cells(f), cells(u), cells(a)
    if after is None:
        problems.append(f'2: {path}: not a valid notebook after the merge')
        return
    base, fork, up = base or {}, fork or {}, up or {}
    for cid in set(base) | set(fork) | set(up) | set(after):
        in_b, in_f, in_u, in_a = cid in base, cid in fork, cid in up, cid in after
        fork_changed = (in_f != in_b) or (in_f and in_b and fork[cid] != base[cid])
        up_changed = (in_u != in_b) or (in_u and in_b and up[cid] != base[cid])
        if fork_changed:
            want_present, want = in_f, fork.get(cid)
            if up_changed and (in_u, up.get(cid)) != (in_f, fork.get(cid)):
                notes.append(f'both changed: {path} cell {cid}: kept the fork\'s version; read his change')
            rule = '2'
        elif up_changed:
            want_present, want, rule = in_u, up.get(cid), '3'
        else:
            want_present, want, rule = in_b, base.get(cid), '3'
        if want_present and not in_a:
            problems.append(f'{rule}: {path} cell {cid} is missing ' + ('(a fork edit was lost)' if rule == '2'
                                                                        else '(Downey\'s cell did not arrive)'))
        elif not want_present and in_a and cid not in fork:
            problems.append(f'{rule}: {path} cell {cid} should be gone (removed by ' +
                            ('the fork)' if rule == '2' else 'Downey)'))
        elif want_present and in_a and after[cid] != want:
            what = 'the fork\'s text or tags were lost' if rule == '2' else 'Downey\'s change did not arrive'
            problems.append(f'{rule}: {path} cell {cid}: {what}')


def added_lines(old, new):
    old_set = set((old or '').split('\n'))
    return [line for line in (new or '').split('\n') if line.strip() and line not in old_set]


def main(argv):
    opt = lambda name, default: argv[argv.index(name) + 1] if name in argv else default  # noqa: E731
    upstream = opt('--upstream', 'upstream/v3')
    merge = None if (ROOT / '.git' / 'MERGE_HEAD').exists() else find_merge(upstream)
    before = opt('--before', default_before(merge))
    # Files edited after the merge commit (on purpose, on the sync branch) are checked as the merge left them; the
    # edits are listed for a person to read.
    # (committed edits only: uncommitted changes in the working tree are always checked)
    later = set((git('diff', '--name-only', merge, 'HEAD') or '').split('\n')) - {''} if merge else set()
    later -= set((git('diff', '--name-only', 'HEAD') or '').split('\n'))
    base = (git('merge-base', before, upstream) or '').strip()
    if not base:
        sys.exit(f'no common commit for {before} and {upstream}')
    print(f'base {base[:7]}, before {before} ({(git("rev-parse", "--short", before) or "").strip()}), '
          f'upstream {upstream}, after = ' + (f'the merge commit {merge[:7]} and the working tree' if merge
                                               else 'the working tree'))
    fb, ff, fu = files_at(base), files_at(before), files_at(upstream)
    problems, notes = [], []
    for path in sorted(fb | ff | fu):
        b_has, f_has, u_has = path in fb, path in ff, path in fu
        binary = path.lower().endswith(BINARY)
        b = git('show', f'{base}:{path}', binary=binary) if b_has else None
        f = git('show', f'{before}:{path}', binary=binary) if f_has else None
        u = git('show', f'{upstream}:{path}', binary=binary) if u_has else None
        if path in later and (ROOT / path).exists():
            a = git('show', f'{merge}:{path}', binary=binary)
            notes.append(f'{path}: changed after the merge commit (checked as the merge left it; read the later edit)')
        else:
            a = worktree(path, binary)
        fork_changed = f_has != b_has or (f_has and b_has and f != b)
        up_changed = u_has != b_has or (u_has and b_has and u != b)
        if fork_changed and f_has and a is None:
            problems.append(f'1: {path}: a file of the fork is missing')
            continue
        if path.startswith(FORK_PAGES) and f_has and a != f:
            problems.append(f'5: {path}: one of the fork\'s own pages changed in the merge')
            continue
        if a is not None and not binary and f is not None and u is not None and a == f == u:
            continue
        if not fork_changed:
            if up_changed and not u_has:
                if a is not None:
                    notes.append(f'{path}: Downey deleted it; it is still here')
                continue
            if up_changed and a is None:
                problems.append(f'3: {path}: Downey\'s file did not arrive')
                continue
            if a is None:
                continue
            if binary:
                if a != (u if u_has else b):
                    problems.append(f'3: {path}: differs from Downey\'s version')
            elif path.endswith('.ipynb'):
                check_notebook(path, b, f, u, a, problems, notes)
            elif norm(a) != norm(u if u_has else b):
                problems.append(f'3: {path}: differs from Downey\'s version (the fork never changed it)')
            continue
        # the fork changed this file
        if binary or not up_changed:
            if not binary and not path.endswith('.ipynb') and a is not None and norm(a) != norm(f):
                notes.append(f'{path}: changed on this branch after the merge')
            continue
        if path.endswith('.ipynb'):
            check_notebook(path, b, f, u, a, problems, notes)
            continue
        here = {norm(y) for y in (a or '').split('\n')}
        lost = [x for x in added_lines(b, f) if norm(x) not in here]
        missing = [x for x in added_lines(b, u) if norm(x) not in here]
        his_new = [norm(y) for y in added_lines(b, u) if norm(y) in here]
        for x in lost[:5]:
            if any(difflib.SequenceMatcher(None, norm(x), y).ratio() > 0.8 for y in his_new):
                notes.append(f'{path}: a fork line was replaced by Downey\'s newer version of it: {x.strip()[:70]!r}')
            else:
                problems.append(f'2: {path}: a line the fork added is gone: {x.strip()[:90]!r}')
        for x in missing[:5]:
            notes.append(f'both changed: {path}: a line Downey added is not here: {x.strip()[:90]!r}')
    changed, colab_problems = fork_colab_links.run(check=True)
    problems.extend(f'4: {rel}: has Colab links to Downey\'s repository (run fork_colab_links.py)' for rel in changed)
    problems.extend(f'4: {p}' for p in colab_problems)
    for n in notes:
        print('  note:', n)
    if problems:
        print(f'{len(problems)} problem(s):')
        for p in problems:
            print('  -', p)
        return 1
    print('OK: nothing of the fork was lost, all of Downey\'s changes are here, every Colab link is the fork\'s')
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
