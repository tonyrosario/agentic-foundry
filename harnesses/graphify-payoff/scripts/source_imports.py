"""Ground truth for import edges, read straight from the source in app/.

Independent of graphify: a regex over import/export/dynamic-import specifiers,
resolved relative to the importing file. Bare package imports are ignored.
"""
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import config as C  # noqa: E402

APP = C.CODE_DIR
ROOTS = C.SOURCE_DIRS
EXTS = tuple('.' + e for e in C.SOURCE_EXTS if e not in ('css',))
SPEC = re.compile(
    r"""(?:^|\n)\s*(?:import|export)\s+(type\s+)?(?:[^'";]*?\s+from\s+)?['"]([^'"]+)['"]"""
    r"""|import\(\s*['"]([^'"]+)['"]\s*\)""",
    re.S,
)
RESOLVE = ('', '.ts', '.tsx', '.css', '/index.ts', '/index.tsx')


def source_files():
    for root in ROOTS:
        for dirpath, dirnames, filenames in os.walk(os.path.join(APP, root)):
            dirnames[:] = [d for d in dirnames if d not in ('node_modules', 'dist')]
            for name in filenames:
                if name.endswith(EXTS) and not name.endswith('.d.ts'):
                    yield os.path.relpath(os.path.join(dirpath, name), os.path.dirname(APP))


def _resolve(importer, spec):
    if not spec.startswith('.'):
        return None
    base = os.path.normpath(os.path.join(os.path.dirname(importer), spec))
    for suffix in RESOLVE:
        candidate = base + suffix
        if os.path.isfile(os.path.join(os.path.dirname(APP), candidate)):
            return candidate
    return None


def import_edges():
    """{(importer, imported): 'type' | 'value'} with repo-relative paths (app/...)."""
    edges = {}
    for path in source_files():
        text = open(os.path.join(os.path.dirname(APP), path), encoding='utf-8').read()
        for m in SPEC.finditer(text):
            spec = m.group(2) or m.group(3)
            target = _resolve(path, spec) if spec else None
            if target and target != path:
                kind = 'type' if m.group(1) else 'value'
                if edges.get((path, target)) != 'value':
                    edges[(path, target)] = kind
    return edges


def importers_of(target):
    return sorted(src for (src, dst) in import_edges() if dst == target)


if __name__ == '__main__':
    edges = import_edges()
    print(len(edges), 'import edges;', sum(1 for k in edges.values() if k == 'type'), 'type-only')
    for t in sorted({dst for (_, dst) in edges})[:4]:
        print(t, '<-', importers_of(t))
