"""Planted-defect check for eval.py (plan.md Phase 0 step 4): damage a copy of the graph three ways
and say which the scorer must flag. Imported by eval.py when run with --plant."""
import os

import config as C
from eval import CALL_RELATIONS, IMPORT_RELATIONS, REPO, file_of, git
from source_imports import import_edges


def plant_defects(g, nodes, questions):
    """Damage a copy of the graph three ways and return what the scorer must flag for each."""
    truth = import_edges()
    dropped = next(e for e in g['links'] if e['relation'] in IMPORT_RELATIONS
                   and (file_of(nodes.get(e['source'])), file_of(nodes.get(e['target']))) in truth
                   and not file_of(nodes.get(e['target'])).endswith('.css'))
    pair = (file_of(nodes[dropped['source']]), file_of(nodes[dropped['target']]))
    # Two files can be joined by several import edges (one per symbol); the defect is the pair vanishing.
    g['links'] = [e for e in g['links'] if not (e['relation'] in IMPORT_RELATIONS and
                  (file_of(nodes.get(e['source'])), file_of(nodes.get(e['target']))) == pair)]
    q = next(q for q in questions['calls'] if q['not_targets'])
    wrong_file = q['not_targets'][0]
    decoy = next((n for n in nodes.values() if file_of(n) == wrong_file
                  and (n.get('label') or '').lstrip('.').removesuffix('()') == q['symbol']), None)
    if decoy is None:
        decoy = {'id': f'planted::{wrong_file}::{q["symbol"]}', 'label': q['symbol'], 'source_file': wrong_file}
        g['nodes'].append(decoy)
        nodes[decoy['id']] = decoy
    retargeted = 0
    for e in g['links']:
        s, t = nodes.get(e['source'], {}), nodes.get(e['target'], {})
        if e['relation'] in CALL_RELATIONS and file_of(s) == q['caller'] and \
                (t.get('label') or '').lstrip('.').removesuffix('()') == q['symbol']:
            e['target'] = decoy['id']
            retargeted += 1
    if not retargeted:
        caller = next(n for n in nodes.values() if file_of(n) == q['caller'])
        g['links'].append({'source': caller['id'], 'target': decoy['id'], 'relation': 'calls'})
    gone = git('log', '--diff-filter=D', '--name-only', '--format=', '--', *C.SOURCE_ROOTS).split()
    ghost = next(p for p in gone if not os.path.exists(os.path.join(REPO, p)))
    g['nodes'].append({'id': f'planted::{ghost}', 'label': os.path.basename(ghost), 'source_file': ghost})
    nodes[f'planted::{ghost}'] = g['nodes'][-1]
    return {
        'dropped_import': f'{file_of(nodes[dropped["source"]])} -> {file_of(nodes[dropped["target"]])}',
        'wrong_call': {'question': q['id'], 'decoy_file': wrong_file},
        'ghost_file': ghost,
    }


def check_planted(planted, report):
    imports, calls, fresh = report['imports'], report['calls'], report['freshness']
    call = next(c for c in calls if c['id'] == planted['wrong_call']['question'])
    return {
        'dropped_import_flagged': imports['recall'] is not None and imports['recall'] < 1
        and any(m.startswith(planted['dropped_import']) for m in imports['missed']),
        'wrong_call_flagged': planted['wrong_call']['decoy_file'] in call.get('wrong_target', []),
        'ghost_file_flagged': planted['ghost_file'] in fresh['ghost_files_in_graph'],
    }
