"""M6, the graph's overhead per session, from the saved transcripts (plan.md Phase 0 step 0).

Run from the repo root:  python3 -I local/graphify-eval/overhead_census.py
Overhead = hook reminders + graph query output + the CLAUDE.md graphify section (loaded once per
transcript file) + `graphify update` output. Two figures per session:
  once     each overhead token counted once, as plan.md section 6 defines M6;
  carried  the same tokens priced as they are actually paid: written to cache once (x1.25) and read
           back on every later request of the same transcript file (x0.1 each).
Tokens are estimated at CHARS_PER_TOKEN; the calibration column shows the ratio the transcripts
themselves imply (context growth between requests against the characters that entered).
Writes results/overhead-census-<date>.json.
"""
import datetime
import json
import os
import re
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import transcripts as T  # noqa: E402

import config as C  # noqa: E402

CHARS_PER_TOKEN = 4.0
T6 = C.THRESHOLDS['T6']


def tokens(chars):
    return chars / CHARS_PER_TOKEN


def claude_md_section_chars(first_ts):
    commit = subprocess.run(['git', 'log', '-1', f'--before={first_ts}', '--format=%H'], cwd=T.REPO,
                            capture_output=True, text=True).stdout.strip()
    if not commit:
        return 0
    text = subprocess.run(['git', 'show', f'{commit}:{C.INSTRUCTIONS_FILE}'], cwd=T.REPO, capture_output=True,
                          text=True).stdout
    m = re.search(r'^' + re.escape(C.SECTION_HEADING) + r'\n.*?(?=^#{1,2} |\Z)', text, re.S | re.M)
    return len(m.group(0)) if m else 0


def carried_weight(file_reqs, ts):
    """Price multiplier for tokens injected at ts: one cache write, then one cache read per later request."""
    later = sum(1 for r in file_reqs if r['ts'] > ts)
    return T.WEIGHTS['cache_creation_input_tokens'] + T.WEIGHTS['cache_read_input_tokens'] * later


def calibration(rows, reqs):
    """Chars that entered the context per token the context grew, over consecutive same-model requests."""
    main = [r for r in reqs]
    ctx = lambda r: sum(r['usage'][f] for f in ('input_tokens', 'cache_creation_input_tokens',
                                                  'cache_read_input_tokens'))
    incoming = []
    for e in rows:
        content = (e.get('message') or {}).get('content')
        if e.get('type') != 'user':
            continue
        text = content if isinstance(content, str) else T.result_text(
            [c for c in content if c.get('type') == 'text'] +
            [{'text': T.result_text(c.get('content'))} for c in content if c.get('type') == 'tool_result'])
        incoming.append((e.get('timestamp') or '', len(text)))
    chars = grew = 0
    for a, b in zip(main, main[1:]):
        if a['model'] != b['model'] or a['_file'] != b['_file']:
            continue
        d = ctx(b) - ctx(a) - a['usage']['output_tokens']
        c = sum(n for ts, n in incoming if a['ts'] < ts <= b['ts'])
        if d > 0 and c > 0:
            chars += c
            grew += d
    return round(chars / grew, 2) if grew else None


def census(session):
    sid = session['session']
    rows = T.entries(T.transcript_files(sid))
    reqs = T.requests(rows)
    by_file = {}
    for e in rows:
        if e.get('type') == 'assistant':
            by_file.setdefault(e.get('requestId') or (e.get('message') or {}).get('id'), e['_file'])
    for r in reqs:
        r['_file'] = by_file.get(r['id'], sid + '.jsonl')
    file_reqs = lambda f: [r for r in reqs if r['_file'] == f]
    once = carried = 0.0
    rem = T.reminders(rows)
    rem_map = {}
    for e in rows:
        att = e.get('attachment')
        if isinstance(att, dict) and att.get('type') == 'hook_success':
            rem_map[att.get('toolUseID')] = e['_file']
    for ts, tuid, text in rem:
        n = tokens(len(text))
        once += n
        carried += n * carried_weight(file_reqs(rem_map.get(tuid, sid + '.jsonl')), ts)
    call_file = {}
    for e in rows:
        if e.get('type') == 'assistant':
            for c in (e.get('message') or {}).get('content') or []:
                if isinstance(c, dict) and c.get('type') == 'tool_use':
                    call_file[c['id']] = e['_file']
    graph_calls = graph_chars = updates = update_ms = update_chars = 0
    for ts, cid, name, inp, out, out_ts in T.tool_calls(rows):
        if name != 'Bash':
            continue
        cmd = inp.get('command', '')
        f = call_file.get(cid, sid + '.jsonl')
        if T.GRAPH_CMD.search(cmd):
            graph_calls += 1
            graph_chars += len(out)
            once += tokens(len(out))
            carried += tokens(len(out)) * carried_weight(file_reqs(f), out_ts or ts)
        elif T.UPDATE_CMD.search(cmd):
            updates += 1
            update_chars += len(out)
            if ts and out_ts:
                a, b = (datetime.datetime.fromisoformat(x.replace('Z', '+00:00')) for x in (ts, out_ts))
                update_ms += int((b - a).total_seconds() * 1000)
            once += tokens(len(out))
            carried += tokens(len(out)) * carried_weight(file_reqs(f), out_ts or ts)
    section = claude_md_section_chars(session['first_ts'])
    for f in {r['_file'] for r in reqs}:
        fr = file_reqs(f)
        if fr and section:
            once += tokens(section)
            carried += tokens(section) * carried_weight(fr, fr[0]['ts'])
    total = T.sum_usage(reqs)
    return {
        'session': sid[:8], 'date': session['first_ts'][:10], 'model': session['main_model'],
        'requests': len(reqs), 'reminders': len(rem), 'reminder_chars': sum(len(t) for _, _, t in rem),
        'graph_calls': graph_calls, 'graph_chars': graph_chars, 'updates': updates, 'update_ms': update_ms,
        'update_chars': update_chars, 'claude_md_section_chars': section,
        'overhead_once': round(once), 'overhead_carried': round(carried),
        'total_raw': total['raw'], 'total_weighted': total['weighted'],
        'share_once': round(once / total['weighted'], 4) if total['weighted'] else None,
        'share_carried': round(carried / total['weighted'], 4) if total['weighted'] else None,
        'chars_per_token_implied': calibration(rows, reqs),
        'cost_state_matches': check_cost_state(session, reqs),
    }


def check_cost_state(session, reqs):
    """Our deduplicated sums over the harness's own totals for the main model. Only the three large
    fields are comparable: the harness counts `inputTokens` differently, and that field is under 1% of
    the weighted total. Secondary (subagent) models are not compared because the harness's cost-state
    can carry usage from resumed sessions."""
    cs = session.get('cost_state')
    model = session.get('main_model')
    if not cs or model not in cs['by_model']:
        return None
    mine = dict.fromkeys(T.USAGE_FIELDS, 0)
    for r in reqs:
        if r['model'] == model:
            for f in T.USAGE_FIELDS:
                mine[f] += r['usage'][f]
    theirs = cs['by_model'][model]
    return {f: round(mine[f] / theirs[f], 3) for f in
            ('cache_creation_input_tokens', 'cache_read_input_tokens', 'output_tokens') if theirs[f]}


def main():
    corpus = T.load_corpus()
    if not corpus:
        sys.exit('run corpus.py first')
    rows = [census(s) for s in corpus['sessions'] if s['included']]
    cols = ['date', 'session', 'requests', 'reminders', 'graph_calls', 'updates', 'update_ms', 'overhead_once',
            'overhead_carried', 'total_weighted', 'share_once', 'share_carried', 'chars_per_token_implied']
    print('\t'.join(cols))
    for r in rows:
        print('\t'.join(str(r[c]) for c in cols))
    tw = sorted(r['total_weighted'] for r in rows)
    median = tw[len(tw) // 2]
    once = sum(r['overhead_once'] for r in rows)
    carried = sum(r['overhead_carried'] for r in rows)
    total = sum(r['total_weighted'] for r in rows)
    summary = {
        'sessions': len(rows), 'chars_per_token_assumed': CHARS_PER_TOKEN,
        'reminders': sum(r['reminders'] for r in rows), 'graph_calls': sum(r['graph_calls'] for r in rows),
        'updates': sum(r['updates'] for r in rows), 'update_wall_s': round(sum(r['update_ms'] for r in rows) / 1000),
        'overhead_once_tokens': once, 'overhead_carried_weighted': carried,
        'total_weighted_tokens': total, 'median_session_weighted': median,
        'overhead_once_per_session': round(once / len(rows)), 'overhead_carried_per_session': round(carried / len(rows)),
        'share_once_of_total': round(once / total, 4), 'share_carried_of_total': round(carried / total, 4),
        'share_once_per_session_vs_median': round(once / len(rows) / median, 4),
        'share_carried_per_session_vs_median': round(carried / len(rows) / median, 4),
        'T6': T6,
    }
    for k, v in summary.items():
        print(f'{k:36} {v}')
    checked = [r for r in rows if r['cost_state_matches']]
    bad = {r['session']: r['cost_state_matches'] for r in checked
           if any(abs(v - 1) > 0.06 for v in r['cost_state_matches'].values())}
    summary['cost_state_within_6pct'] = f'{len(checked) - len(bad)}/{len(checked)}'
    summary['median_share_once'] = __import__('statistics').median(r['share_once'] for r in rows)
    summary['median_share_carried'] = __import__('statistics').median(r['share_carried'] for r in rows)
    print(f'cost-state cross-check (main model, cache and output fields): {summary["cost_state_within_6pct"]} '
          f'within 6%' + (f'; off: {json.dumps(bad)[:400]}' if bad else ''))
    print(f'median per-session share: once {summary["median_share_once"]}, carried {summary["median_share_carried"]}')
    out = os.path.join(T.HERE, 'results', f'overhead-census-{datetime.date.today().isoformat()}.json')
    json.dump({'summary': summary, 'sessions': rows}, open(out, 'w'), indent=2)
    print(f'written: {os.path.relpath(out, T.REPO)}')


if __name__ == '__main__':
    main()
