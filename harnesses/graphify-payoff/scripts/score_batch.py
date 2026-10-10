"""Score a Phase 2 batch and apply plan.md section 7 for arms G and N (plan.md Phase 3 steps 1 and 3).

Run from the repo root:  python3 -I local/graphify-eval/score_batch.py <runs-dir> [--out results/<name>.json]
For every <runs-dir>/<milestone>/rep*/runs.jsonl row it computes M1, M2, M5 (orientation.py) and
M3, M4, M7 unadjusted (plan_score.py), then per-milestone medians and ranges, then the rules in
order. Excluded runs (no PLAN.md, non-zero exit, budget cap, leakage hit) are listed with reasons.
"""
import glob
import json
import os
import re
import statistics
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import transcripts as T  # noqa: E402

import config as C  # noqa: E402

BASES = {name: (t['base'], t['tick']) for name, t in C.TASKS.items()}
T1, T2, T3, T4 = (C.THRESHOLDS[k] for k in ('T1', 'T2', 'T3', 'T4'))
LEAK = re.compile(r'--all\b|reflog|git fetch|graphify-eval', re.I)


def project_dir(clone):
    return os.path.join(os.path.dirname(T.PROJECT), C.slug(clone))


def run_tool(script, *args):
    out = subprocess.run([sys.executable, '-I', os.path.join(T.HERE, script), *args], capture_output=True, text=True)
    if out.returncode:
        return {'error': (out.stderr or out.stdout).strip()[-300:]}
    return json.loads(out.stdout)


def leakage(project, sid):
    path = os.path.join(project, sid + '.jsonl')
    hits = []
    for ts, cid, name, inp, out, out_ts in T.tool_calls(T.entries([path])):
        text = json.dumps(inp)
        if LEAK.search(text):
            hits.append(text[:120])
    return hits


def score_run(ms, row):
    base, tick = BASES[ms]
    clone, sid = row['clone'], row['session_id']
    # run_pair.sh copies the plan beside runs.jsonl; the clone itself is removed after scoring.
    plan = os.path.join(os.path.dirname(clone), f'PLAN-{row["arm"]}.md')
    if not os.path.exists(plan):
        plan = os.path.join(clone, 'PLAN.md')
    rec = {'milestone': ms, 'arm': row['arm'], 'session': sid[:8], 'cost_usd': row.get('cost_usd'),
           'turns': row.get('turns'), 'duration_s': round((row.get('duration_ms') or 0) / 1000)}
    reasons = []
    if row.get('exit'):
        reasons.append(f'exit {row["exit"]}')
    if not row.get('plan_written') or not os.path.exists(plan):
        reasons.append('no PLAN.md')
    if row.get('subtype') not in (None, 'success'):
        reasons.append(f'subtype {row.get("subtype")}')
    project = project_dir(clone)
    if os.path.exists(os.path.join(project, sid + '.jsonl')):
        hits = leakage(project, sid)
        if hits:
            reasons.append('leakage: ' + '; '.join(hits[:2]))
    else:
        reasons.append('transcript missing')
    if not reasons:
        o = run_tool('orientation.py', '--project', project, '--session', sid, '--milestone', ms,
                     '--base', base, '--tick', tick, '--plan', plan)
        p = run_tool('plan_score.py', '--plan', plan, '--base', base, '--tick', tick)
        for d in (o, p):
            if 'error' in d:
                reasons.append(d['error'])
        if not reasons:
            rec.update({'M1': o['M1_weighted'], 'M1_raw': o['M1_raw'], 'M2': o['M2_tool_calls'],
                        'M5': o['M5_exploratory_share'], 'M3': p['M3_file_recall'], 'M4': p['M4_reuse_recall'],
                        'M7': p['M7_precision'], 'plan_paths': p['plan_paths'], 'M3_missed': p['M3_missed']})
    rec['excluded'] = reasons
    return rec


def summarise(scored):
    per = {}
    for ms in BASES:
        per[ms] = {}
        for arm in ('G', 'N'):
            vals = [r for r in scored if r['milestone'] == ms and r['arm'] == arm and not r['excluded']]
            if len(vals) < 2:
                per[ms][arm] = {'n': len(vals), 'unscored': True}
                continue
            s = {'n': len(vals)}
            for m in ('M1', 'M2', 'M3', 'M4', 'M5', 'M7'):
                xs = [v[m] for v in vals if v[m] is not None]
                s[m] = {'median': statistics.median(xs), 'min': min(xs), 'max': max(xs)}
            per[ms][arm] = s
    return per


def rules(per):
    scored = [ms for ms in per if not per[ms]['G'].get('unscored') and not per[ms]['N'].get('unscored')]
    if len(scored) < 2:
        return {'outcome': 'inconclusive', 'why': f'only {len(scored)} scored milestones'}
    rows = {}
    for ms in scored:
        g, n = per[ms]['G'], per[ms]['N']
        nm = n['M1']['median']
        rows[ms] = {
            'M1_saving': round((nm - g['M1']['median']) / nm, 3),
            'G_range_share': round((g['M1']['max'] - g['M1']['min']) / nm, 3),
            'N_range_share': round((n['M1']['max'] - n['M1']['min']) / nm, 3),
            'gap_share': round(abs(g['M1']['median'] - nm) / nm, 3),
            **{f'd{m}': round(g[m]['median'] - n[m]['median'], 3) for m in ('M3', 'M4', 'M7')},
        }
    noisy = sum(1 for r in rows.values() if r['G_range_share'] > r['gap_share']) > len(rows) / 2
    recall_ok = lambda r: r['dM3'] >= -T3 and r['dM4'] >= -T3 and r['dM7'] >= -T3
    a_wins = sum(1 for r in rows.values() if r['M1_saving'] >= T1) >= 2 and all(recall_ok(r) for r in rows.values())
    b_tradeoff = sum(1 for r in rows.values() if (r['dM3'] >= T4 or r['dM4'] >= T4) and r['dM7'] >= -T3) >= 2
    if noisy:
        outcome = 'inconclusive (rule 1: G range wider than the G-N gap on a majority of milestones)'
    elif a_wins:
        outcome = 'A (rule 2)'
    elif b_tradeoff:
        outcome = 'B (rule 3b: G finds more at higher cost)'
    elif sum(1 for r in rows.values() if r['M1_saving'] >= T1 or r['dM3'] >= T4 or r['dM4'] >= T4) < 2:
        outcome = 'C (rule 4: G beats N on neither cost nor recall on 2 of 3)'
    else:
        outcome = 'unresolved (rule 6)'
    return {'outcome': outcome, 'per_milestone': rows,
            'thresholds': {'T1': T1, 'T2': T2, 'T3': T3, 'T4': T4, 'arm_D': 'not run (plan change 2026-10-10)'}}


def main():
    runs_dir = sys.argv[1]
    out_path = sys.argv[sys.argv.index('--out') + 1] if '--out' in sys.argv else None
    scored = []
    for ms in BASES:
        # run_batch.sh writes <ms>/rep<n>/; an archived batch may be flattened to <ms>-rep<n>/.
        logs = glob.glob(os.path.join(runs_dir, ms, 'rep*', 'runs.jsonl')) + glob.glob(os.path.join(runs_dir, f'{ms}-rep*', 'runs.jsonl'))
        for log in sorted(logs):
            for line in open(log):
                row = json.loads(line)
                if 'arm' in row:
                    rec = score_run(ms, row)
                    rec['rep'] = os.path.basename(os.path.dirname(log))
                    scored.append(rec)
    per = summarise(scored)
    verdict = rules(per)
    report = {'runs': scored, 'per_milestone_arm': per, 'rules': verdict,
              'excluded': [(r['milestone'], r['rep'], r['arm'], r['excluded']) for r in scored if r['excluded']]}
    cols = ('milestone', 'rep', 'arm', 'M1', 'M2', 'M3', 'M4', 'M7', 'M5', 'cost_usd', 'duration_s')
    print('\t'.join(cols))
    for r in scored:
        print('\t'.join(str(r.get(c, '')) for c in cols) + ('\tEXCLUDED ' + '; '.join(r['excluded']) if r['excluded'] else ''))
    print(json.dumps({'per_milestone_arm': per, 'rules': verdict}, indent=1))
    if out_path:
        json.dump(report, open(out_path, 'w'), indent=2)
        print('written', out_path)


if __name__ == '__main__':
    main()
