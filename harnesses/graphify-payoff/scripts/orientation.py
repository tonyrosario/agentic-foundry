"""M1, M2 and M5 for one session's orientation window (plan.md section 6).

Run from the repo root, for example:
  python3 -I orientation.py --session <id-prefix> --milestone <task> --base <sha> --tick <sha>            # historical
  python3 -I orientation.py --session <id> --milestone <task> --base <sha> --tick <sha> --plan PLAN.md  # a run
The window opens at the first `go <milestone>` prompt. It closes at the first tool call that writes
under app/ (a historical session) or at the Write of PLAN.md (a Phase 2 run, --plan given).
M1 sums the deduplicated usage of every request inside the window, raw and price-weighted; M2 counts
tool calls; M5 is the share of app/ files opened in the window that are in neither the reference
diff nor the plan. --verbose prints each request for hand-checking against the transcript.
"""
import argparse
import json
import os
import re
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import transcripts as T  # noqa: E402

import config as C  # noqa: E402

APP_PATH = C.REL_PATH_RE
SOURCE_FILE = C.SOURCE_REL
WRITE_CMD = re.compile(r'(?:>|>>|\btee\b|sed -i(?: \'\')?)\s*\S*' + SOURCE_FILE)
READ_CMD = re.compile(r'\b(cat|sed -n|head|tail|nl)\b')


def git(*args):
    return subprocess.run(['git', *args], cwd=T.REPO, capture_output=True, text=True).stdout


def reference_files(base, tick):
    changed = [p for p in git('diff', '--name-only', base, tick, '--', C.CODE_ROOT or '.').split()
               if C.FULL_PATH_RE.fullmatch(p)]
    existed = [p for p in changed if subprocess.run(['git', 'cat-file', '-e', f'{base}:{p}'], cwd=T.REPO,
                                                    stderr=subprocess.DEVNULL).returncode == 0]
    strip = lambda ps: {p[len(C.CODE_PREFIX):] for p in ps}
    return strip(changed), strip(existed)


def writes_app(name, inp):
    if name in ('Edit', 'Write', 'NotebookEdit', 'MultiEdit'):
        return bool(APP_PATH.search(inp.get('file_path') or inp.get('notebook_path') or ''))
    if name != 'Bash':
        return False
    cmd = inp.get('command', '')
    # A python heredoc that writes files names them in quotes near a write call; a plain redirect or
    # sed -i names the path after the operator.
    return bool(WRITE_CMD.search(cmd)) or bool(re.search(r'write_text|open\([^)]*[\'"]w', cmd)
                                                and re.search(SOURCE_FILE, cmd))


def opened_paths(name, inp):
    if name in ('Read', 'Edit'):
        return set(APP_PATH.findall(inp.get('file_path') or ''))
    if name == 'Bash' and READ_CMD.search(inp.get('command', '')):
        return set(APP_PATH.findall(inp.get('command', '')))
    return set()


def window(rows, milestone, plan):
    start = end = end_reason = None
    for e in rows:
        content = (e.get('message') or {}).get('content')
        if e.get('type') == 'user' and isinstance(content, str) and re.search(rf'\bgo {milestone}\b', content, re.I):
            start = e.get('timestamp')
            break
    if not start:
        return None, None, 'no `go %s` prompt' % milestone
    for ts, cid, name, inp, out, out_ts in T.tool_calls(rows):
        if ts < start:
            continue
        plan_name = C.PLAN_FILE  # the file the prompt asks for; --plan may point at an archived copy
        if plan and (name == 'Write' and (inp.get('file_path') or '').endswith('/' + plan_name)
                     or name == 'Bash' and re.search(r'(?:>|>>|\btee\b)\s*\S*' + re.escape(plan_name),
                                                     inp.get('command', ''))):
            return start, ts, f'{plan_name} written by {name}'
        if not plan and writes_app(name, inp):
            return start, ts, f'first app write: {name} {inp.get("file_path") or inp.get("command", "")[:120]!r}'
    return start, None, 'window never closed'


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--session', required=True, help='session id or prefix')
    ap.add_argument('--milestone', required=True)
    ap.add_argument('--base', required=True)
    ap.add_argument('--tick', required=True)
    ap.add_argument('--plan', help='PLAN.md path; closes the window at its Write (Phase 2 runs)')
    ap.add_argument('--project', help='transcript project dir (default: this repo\'s)')
    ap.add_argument('--verbose', action='store_true')
    args = ap.parse_args()
    if args.project:
        T.PROJECT = args.project
    sid = next((s for s in T.session_ids() if s.startswith(args.session)), None)
    if not sid:
        sys.exit(f'no session starting with {args.session}')
    rows = T.entries(T.transcript_files(sid))
    start, end, reason = window(rows, args.milestone, args.plan)
    if not end:
        sys.exit(f'{sid[:8]}: {reason}')
    reqs = [r for r in T.requests(rows) if start <= r['ts'] <= end]
    calls = [c for c in T.tool_calls(rows) if start <= c[0] <= end]
    changed, existed = reference_files(args.base, args.tick)
    planned = set(APP_PATH.findall(open(args.plan).read())) if args.plan and os.path.exists(args.plan) else set()
    opened = set()
    for ts, cid, name, inp, out, out_ts in calls:
        opened |= opened_paths(name, inp)
    exploratory = sorted(opened - changed - planned)
    usage = T.sum_usage(reqs)
    result = {
        'session': sid[:8], 'milestone': args.milestone, 'base': args.base, 'tick': args.tick,
        'window': {'start': start, 'end': end, 'closed_by': reason},
        'M1_raw': usage['raw'], 'M1_weighted': usage['weighted'], 'M1_fields': {f: usage[f] for f in T.USAGE_FIELDS},
        'M1_requests': len(reqs), 'models': sorted({r['model'] for r in reqs if r['model']}),
        'M2_tool_calls': len(calls),
        'M5_exploratory_share': round(len(exploratory) / len(opened), 3) if opened else None,
        'M5_opened': len(opened), 'M5_exploratory': exploratory,
        'reference_changed': len(changed), 'reference_existed_at_base': len(existed),
    }
    if args.verbose:
        for r in reqs:
            u = r['usage']
            print(f"{r['ts']} {r['id']} {r['model'][:18]:18} in={u['input_tokens']:>6} cc={u['cache_creation_input_tokens']:>7} "
                  f"cr={u['cache_read_input_tokens']:>8} out={u['output_tokens']:>6}")
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
