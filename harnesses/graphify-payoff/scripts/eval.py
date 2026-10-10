"""Score the code graph against source: is it correct, fresh, and does a query find the answer?

Run from the repo root after `graphify update app`:  python3 -I local/graphify-eval/eval.py
Appends a summary line to results.jsonl and writes full detail to results/<date>-<commit>.json.
Reads only app/ source, git metadata and app/graphify-out/. Never runs a graph rebuild.
"""
import datetime
import json
import os
import re
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.normpath(os.path.join(HERE, '..', '..'))
sys.path.insert(0, HERE)
from source_imports import import_edges, importers_of, source_files  # noqa: E402

import config as C  # noqa: E402

GRAPH = os.environ.get('GRAPH_EVAL_GRAPH') or os.path.join(REPO, C.GRAPH_OUT, 'graph.json')
IMPORT_RELATIONS = {'imports', 'imports_from', 're_exports', 'dynamic_import'}
CALL_RELATIONS = {'calls', 'indirect_call', 'method', 'references'}
SRC_RE = re.compile(r'src=(' + re.escape(C.CODE_PREFIX) + r'[^\s\]]+)')
PATH_RE = C.FULL_PATH_RE


def git(*args):
    return subprocess.run(['git', *args], cwd=REPO, capture_output=True, text=True).stdout.strip()


def graphify(*args):
    run = subprocess.run(['graphify', *args], cwd=REPO, capture_output=True, text=True, timeout=60)
    return run.stdout + run.stderr


def evidence_holds(evidence):
    for path, pattern in evidence.items():
        full = os.path.join(REPO, path)
        if not os.path.isfile(full) or not re.search(pattern, open(full, encoding='utf-8').read()):
            return f'{path} no longer matches /{pattern}/'
    return None


def load_graph():
    g = json.load(open(GRAPH))
    nodes = {n['id']: n for n in g['nodes']}
    return g, nodes


def file_of(node):
    return (node or {}).get('source_file') or None


def score_imports(g, nodes):
    """TS-to-TS import recall over the whole codebase; CSS-module imports reported apart."""
    truth = import_edges()
    found = set()
    for e in g['links']:
        if e['relation'] not in IMPORT_RELATIONS:
            continue
        a, b = file_of(nodes.get(e['source'])), file_of(nodes.get(e['target']))
        if a and b and a != b:
            found.add((a, b))
    ts = {k: v for k, v in truth.items() if not k[1].endswith('.css')}
    css = [k for k in truth if k[1].endswith('.css')]
    hit = {k for k in ts if k in found}
    roots = C.SOURCE_ROOTS
    graph_ts = {(a, b) for (a, b) in found if a.startswith(roots) and b.startswith(roots)
                and a.endswith(('.ts', '.tsx')) and b.endswith(('.ts', '.tsx'))}
    extra = graph_ts - set(ts)
    # The graph resolves `export { x } from './y'` through to y; one barrel hop is correct, not a false edge.
    via_reexport = {(a, b) for (a, b) in extra if any((a, c) in truth and (c, b) in truth for (_, c) in truth if _ == a)}
    false_pos = sorted(extra - via_reexport)
    by_root, by_kind = {}, {}
    for (a, b), kind in ts.items():
        for bucket, key in ((by_root, a.split('/')[1]), (by_kind, kind)):
            t = bucket.setdefault(key, [0, 0])
            t[0] += (a, b) in hit
            t[1] += 1
    return {
        'recall': round(len(hit) / len(ts), 3) if ts else None,
        'expected': len(ts),
        'found': len(hit),
        'precision': round(len(hit) / (len(hit) + len(false_pos)), 3) if hit or false_pos else None,
        'resolved_through_reexport': len(via_reexport),
        'unexplained_edges': false_pos[:25] and [f'{a} -> {b}' for a, b in false_pos[:25]],
        'unexplained_count': len(false_pos),
        'css_imports_in_source': len(css),
        'css_imports_in_graph': sum(k in found for k in css),
        'by_root': {k: f'{v[0]}/{v[1]}' for k, v in sorted(by_root.items())},
        'by_kind': {k: f'{v[0]}/{v[1]}' for k, v in sorted(by_kind.items())},
        'missed': sorted(f'{a} -> {b} ({k})' for (a, b), k in ts.items() if (a, b) not in hit)[:25],
    }


def score_calls(questions, g, nodes):
    out = []
    for q in questions:
        stale = evidence_holds(q['evidence'])
        if stale:
            out.append({'id': q['id'], 'stale': stale})
            continue
        targets = []
        for e in g['links']:
            if e['relation'] not in CALL_RELATIONS:
                continue
            s, t = nodes.get(e['source'], {}), nodes.get(e['target'], {})
            label = (t.get('label') or '').lstrip('.').removesuffix('()')
            if file_of(s) == q['caller'] and label == q['symbol']:
                targets.append(file_of(t))
        wrong = sorted({t for t in targets if t in q['not_targets']})
        right = q['target'] is None and bool(targets) or q['target'] in targets
        out.append({'id': q['id'], 'found': right, 'wrong_target': wrong,
                    'targets_seen': sorted({str(t) for t in targets})})
    return out


def score_retrieval(questions):
    out = []
    for q in questions:
        stale = evidence_holds(q['evidence']) or next(
            (f'{p} is gone' for p in q['expect'] if not os.path.isfile(os.path.join(REPO, p))), None)
        if stale:
            out.append({'id': q['id'], 'stale': stale})
            continue
        text = graphify('query', q['question'])
        files = []
        for p in SRC_RE.findall(text) + PATH_RE.findall(text):
            if p not in files:
                files.append(p)
        ranks = [files.index(p) + 1 for p in q['expect'] if p in files]
        row = {
            'id': q['id'],
            'expected_found': f'{len(ranks)}/{len(q["expect"])}',
            'first_rank': min(ranks) if ranks else None,
            'files_returned': len(files),
            'chars': len(text),
            'truncated': 'TRUNCATED' in text,
            'missing': [p for p in q['expect'] if p not in files],
            'returned_sample': files[:8],
        }
        if q.get('expect_none'):
            row['passed'] = 'No matching nodes' in text or not files
        else:
            row['passed'] = len(ranks) == len(q['expect'])
        out.append(row)
    return out


def score_affected(questions):
    out = []
    for q in questions:
        if not os.path.isfile(os.path.join(REPO, q['file'])):
            out.append({'id': q['id'], 'stale': f'{q["file"]} is gone'})
            continue
        module = os.path.basename(q['file']).split('.')[0]
        symbol = q['node'].removesuffix('()')
        names_symbol = re.compile(r'import\s+(?!type\b)[^;]*\b' + re.escape(symbol) + r'\b[^;]*from\s+[\'"][^\'"]*/'
                                  + re.escape(module) + r'[\'"]', re.S)
        # Importers that take the symbol itself; a type-only import of the module is not affected.
        expected = [p for p in importers_of(q['file'])
                    if names_symbol.search(open(os.path.join(REPO, p), encoding='utf-8').read())]
        text = graphify('affected', q['node'])
        named = set(SRC_RE.findall(text) + PATH_RE.findall(text))
        hit = [p for p in expected if p in named]
        out.append({'id': q['id'], 'expected_importers': len(expected), 'found': len(hit),
                    'missing': [p for p in expected if p not in hit], 'chars': len(text)})
    return out


def freshness(g, nodes):
    built = g.get('built_at_commit') or ''
    changed = git('diff', '--name-only', f'{built}..HEAD', '--', C.CODE_ROOT or '.') if built else 'unknown'
    dirty = git('status', '--porcelain', '--', *C.SOURCE_ROOTS)
    graph_files = {file_of(n) for n in nodes.values() if file_of(n)}
    gone = git('log', '--diff-filter=DR', '--name-status', '--format=', '--', *C.SOURCE_ROOTS)
    old_paths = set()
    for line in gone.splitlines():
        parts = line.split('\t')
        if len(parts) >= 2:
            old_paths.add(parts[1])
    old_paths = {p for p in old_paths if not os.path.exists(os.path.join(REPO, p))}
    ghosts = sorted(old_paths & graph_files)
    current = set(source_files())
    uncovered = sorted(current - graph_files)
    return {
        'built_at_commit': built[:7],
        'head': git('rev-parse', '--short', 'HEAD'),
        'app_files_changed_since_build': [p for p in changed.splitlines() if p] if built else 'unknown',
        'uncommitted_app_changes': bool(dirty),
        'deleted_or_renamed_paths_checked': len(old_paths),
        'ghost_files_in_graph': ghosts,
        'source_files': len(current),
        'source_files_without_nodes': len(uncovered),
        'uncovered_sample': uncovered[:15],
    }


def main():
    questions = json.load(open(C.QUESTIONS_FILE))
    g, nodes = load_graph()
    if '--plant' in sys.argv:
        from plant import check_planted, plant_defects
        planted = plant_defects(g, nodes, questions)
        report = {'planted': planted, 'freshness': freshness(g, nodes), 'imports': score_imports(g, nodes),
                  'calls': score_calls(questions['calls'], g, nodes)}
        report['flagged'] = check_planted(planted, report)
        name = f'planted-{datetime.date.today().isoformat()}-{report["freshness"]["head"]}.json'
        os.makedirs(os.path.join(HERE, 'results'), exist_ok=True)
        json.dump(report, open(os.path.join(HERE, 'results', name), 'w'), indent=2)
        print(json.dumps({'planted': planted, 'flagged': report['flagged']}, indent=2))
        print(f'detail: local/graphify-eval/results/{name}')
        sys.exit(0 if all(report['flagged'].values()) else 1)
    report = {
        'run_at': datetime.datetime.now().isoformat(timespec='seconds'),
        'graphify': graphify('--version').strip().splitlines()[-1],
        'nodes': len(g['nodes']),
        'edges': len(g['links']),
        'freshness': freshness(g, nodes),
        'imports': score_imports(g, nodes),
        'calls': score_calls(questions['calls'], g, nodes),
        'retrieval': score_retrieval(questions['retrieval']),
        'affected': score_affected(questions['affected']),
    }
    calls = [c for c in report['calls'] if 'stale' not in c]
    ret = [r for r in report['retrieval'] if 'stale' not in r]
    aff = [a for a in report['affected'] if 'stale' not in a]
    summary = {
        'run_at': report['run_at'],
        'head': report['freshness']['head'],
        'built_at': report['freshness']['built_at_commit'],
        'stale_graph': bool(report['freshness']['app_files_changed_since_build'])
        or report['freshness']['uncommitted_app_changes'],
        'nodes': report['nodes'],
        'import_recall': report['imports']['recall'],
        'import_precision': report['imports']['precision'],
        'css_imports_in_graph': f"{report['imports']['css_imports_in_graph']}/{report['imports']['css_imports_in_source']}",
        'calls_found': f'{sum(c["found"] for c in calls)}/{len(calls)}',
        'calls_wrong_target': sum(bool(c['wrong_target']) for c in calls),
        'retrieval_passed': f'{sum(r["passed"] for r in ret)}/{len(ret)}',
        'retrieval_truncated': sum(r['truncated'] for r in ret),
        'retrieval_mean_chars': round(sum(r['chars'] for r in ret) / len(ret)) if ret else None,
        'affected_importers_found': f'{sum(a["found"] for a in aff)}/{sum(a["expected_importers"] for a in aff)}',
        'ghost_files': len(report['freshness']['ghost_files_in_graph']),
        'uncovered_source_files': report['freshness']['source_files_without_nodes'],
        'stale_questions': sum('stale' in x for x in report['calls'] + report['retrieval'] + report['affected']),
    }
    report['summary'] = summary
    os.makedirs(os.path.join(HERE, 'results'), exist_ok=True)
    name = f'{report["run_at"][:10]}-{summary["head"]}.json'
    json.dump(report, open(os.path.join(HERE, 'results', name), 'w'), indent=2)
    with open(os.path.join(HERE, 'results.jsonl'), 'a') as f:
        f.write(json.dumps(summary) + '\n')
    for k, v in summary.items():
        print(f'{k:26} {v}')
    print(f'detail: local/graphify-eval/results/{name}')


if __name__ == '__main__':
    main()
