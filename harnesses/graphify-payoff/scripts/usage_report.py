"""Was the graph used, and did it lead navigation? Read from Claude's saved transcripts.

Run from the repo root:  python3 -I local/graphify-eval/usage_report.py [--since YYYY-MM-DD] [--session ID]
Prints one row per session (subagents folded into their parent) and totals. Only counts and app/
paths are printed; transcript text is never copied out.

For every app source file a session opened (Read, Edit, or cat/sed/head/tail in Bash), the
earliest earlier tool result that named it decides where the lead came from:
  graph   a graphify query/path/explain/affected result
  search  a grep/rg/find/ls/Glob/Grep result
  other   any other result (README, build plan, test output, git log ...)
  none    never named in an earlier result (known from the prompt, summary or memory)
"""
import argparse
import glob
import json
import os
import re
import subprocess
import sys
from collections import Counter, defaultdict

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import transcripts as T  # noqa: E402

PROJECT = T.PROJECT
REPO = T.REPO
GRAPH_CMD = re.compile(r'(?:^|[;&|(]\s*|\n)\s*(?:cd [^;&]+&&\s*)?graphify (query|path|explain|affected)\b')
UPDATE_CMD = re.compile(r'(?:^|[;&|(]\s*|\n)\s*(?:cd [^;&]+&&\s*)?graphify update\b')
SEARCH_CMD = re.compile(r'\b(grep|rg|find|ls|git grep)\b')
READ_CMD = re.compile(r'\b(cat|sed -n|head|tail|nl)\b')
import config as C  # noqa: E402

# A path as the agent or a tool might write it; normalised to the part after the code root.
PATH = C.REL_PATH_RE


def paths_in(text):
    return {m for m in PATH.findall(text or '')}


def result_text(content):
    if isinstance(content, list):
        return ''.join(x.get('text', '') for x in content if isinstance(x, dict))
    return content or ''


def classify(name, inp):
    if name == 'Bash':
        cmd = inp.get('command', '')
        if GRAPH_CMD.search(cmd):
            return 'graph', cmd
        if UPDATE_CMD.search(cmd):
            return 'update', cmd
        if SEARCH_CMD.search(cmd):
            return 'search', cmd
        if READ_CMD.search(cmd):
            return 'read', cmd
        return 'bash', cmd
    if name in ('Grep', 'Glob'):
        return 'search', json.dumps(inp)
    if name in ('Read', 'Edit', 'Write'):
        return name.lower(), inp.get('file_path', '')
    return 'other', ''


def session_events(paths):
    """Tool calls in order across a session and its subagents, with results and reminder count."""
    events, results, first_ts, last_ts, milestone = [], {}, None, '', None
    rows = T.entries(paths)
    reminders = len(T.reminders(rows))
    for e in rows:
        ts = e.get('timestamp') or ''
        if ts and (first_ts is None or ts < first_ts):
            first_ts = ts
        last_ts = max(last_ts, ts)
        content = (e.get('message') or {}).get('content')
        if e.get('type') == 'user' and isinstance(content, str) and milestone is None:
            m = re.search(r'\bgo (m\d+\w*)\b', content, re.I)
            if m:
                milestone = m.group(1).lower()
        if not isinstance(content, list):
            continue
        for c in content:
            if c.get('type') == 'tool_use':
                kind, detail = classify(c['name'], c.get('input', {}))
                events.append((ts, c['id'], kind, detail))
            elif c.get('type') == 'tool_result':
                results[c.get('tool_use_id')] = result_text(c.get('content'))
    events.sort(key=lambda x: x[0])
    return events, results, reminders, first_ts, last_ts, milestone


def committed_files(first_ts, last_ts):
    """App source files in commits made while the session ran (sessions commit with -q, so no hashes)."""
    if not first_ts:
        return set()
    out = subprocess.run(['git', 'log', '--all', f'--since={first_ts}', f'--until={last_ts}', '--format=',
                          '--name-only'], cwd=REPO, capture_output=True, text=True).stdout
    n = len(C.CODE_PREFIX)
    return {p[n:] for p in out.split() if p.startswith(C.CODE_PREFIX) and PATH.fullmatch(p[n:])}


def analyse(paths):
    events, results, reminders, first_ts, last_ts, milestone = session_events(paths)
    kinds = Counter(k for _, _, k, _ in events)
    seen_by = {}  # path -> first source that named it
    lead = Counter()
    graph_named, opened = set(), set()
    hedged = truncated = 0
    for _, cid, kind, detail in events:
        out = results.get(cid, '')
        # A Bash search or query that also cats files opens them, led by what came before this call.
        if kind in ('read', 'edit', 'write') or kind in ('search', 'graph') and READ_CMD.search(detail):
            for p in paths_in(detail):
                if p not in opened:
                    opened.add(p)
                    lead[seen_by.get(p, 'none')] += 1
        if kind == 'graph':
            hedged += bool(re.search(r'\b(grep|cat|ls|sed|find|rg)\b', GRAPH_CMD.sub('', detail)))
            truncated += 'TRUNCATED' in out
            named = paths_in(out)
            graph_named |= named
        source = {'graph': 'graph', 'search': 'search'}.get(kind, 'other')
        for p in paths_in(out):
            seen_by.setdefault(p, source)
    # Sessions can overlap in time; only one that ran git commit itself owns the window's commits.
    commits = any(kind != 'other' and 'git commit' in detail for _, _, kind, detail in events)
    committed = committed_files(first_ts, last_ts) if commits else set()
    return {
        'date': (first_ts or '')[:10],
        'milestone': milestone or '-',
        'calls': len(events),
        'graph': kinds['graph'],
        'hedged': hedged,
        'truncated': truncated,
        'updates': kinds['update'],
        'reminders': reminders,
        'search': kinds['search'],
        'opened': len(opened),
        'lead': lead,
        'committed': len(committed),
        'committed_named_by_graph': len(committed & graph_named),
    }


def sessions(since, only):
    corpus = T.load_corpus()
    included = {s['session'] for s in corpus['sessions'] if s['included']} if corpus else None
    for main in sorted(glob.glob(os.path.join(PROJECT, '*.jsonl'))):
        sid = os.path.basename(main)[:-len('.jsonl')]
        if only and not sid.startswith(only):
            continue
        if included is not None and sid not in included and not only:
            continue
        subs = sorted(glob.glob(os.path.join(PROJECT, sid, 'subagents', '*.jsonl')))
        row = analyse([main] + subs)
        if row['calls'] and row['date'] >= since:
            row['session'] = sid[:8]
            yield row


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--since', default='')
    ap.add_argument('--session', default='')
    args = ap.parse_args()
    rows = sorted(sessions(args.since, args.session), key=lambda r: r['date'])
    cols = ['date', 'session', 'milestone', 'calls', 'graph', 'hedged', 'truncated', 'updates', 'reminders',
            'search', 'opened', 'lead:graph', 'lead:search', 'lead:other', 'lead:none', 'committed', 'cmt∩graph']
    print('\t'.join(cols))
    total = Counter()
    for r in rows:
        vals = [r['date'], r['session'], r['milestone'], r['calls'], r['graph'], r['hedged'], r['truncated'],
                r['updates'], r['reminders'], r['search'], r['opened'], r['lead']['graph'], r['lead']['search'],
                r['lead']['other'], r['lead']['none'], r['committed'], r['committed_named_by_graph']]
        print('\t'.join(str(v) for v in vals))
        for c, v in zip(cols[3:], vals[3:]):
            total[c] += v
    print('\t'.join(['TOTAL', f'{len(rows)} sessions', ''] + [str(total[c]) for c in cols[3:]]))
    opened = total['opened'] or 1
    print(f"\nfirst opens led by: graph {total['lead:graph'] / opened:.0%}, search {total['lead:search'] / opened:.0%}, "
          f"other output {total['lead:other'] / opened:.0%}, none {total['lead:none'] / opened:.0%}")
    if total['committed']:
        print(f"committed app files a graph query had named in the same session: "
              f"{total['cmt∩graph']}/{total['committed']}")
    print(f"graph calls per 100 tool calls: {100 * total['graph'] / max(total['calls'], 1):.1f}; "
          f"reminders per graph call: {total['reminders'] / max(total['graph'], 1):.0f}")


if __name__ == '__main__':
    main()
