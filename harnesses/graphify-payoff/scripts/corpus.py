"""Freeze the transcript corpus: write sessions.json (plan.md Phase 0 step 1).

Run from the repo root:  python3 -I local/graphify-eval/corpus.py
One record per main transcript with its subagent files, model(s), first and last timestamps, the
first `go mX` prompt, and whether the session is inside the cutoff. Also records the dedup rules the
other scripts rely on and the harness's own cost-state totals for cross-checking token sums.
"""
import json
import os
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import transcripts as T  # noqa: E402


def describe(sid):
    files = T.transcript_files(sid)
    rows = T.entries(files)
    reqs = T.requests(rows)
    ts = [e['timestamp'] for e in rows if e.get('timestamp')]
    real = lambda recs: sorted({r['model'] for r in recs if r['model'] and not r['model'].startswith('<')})
    main_models = real(T.requests([e for e in rows if e['_file'] == sid + '.jsonl']))
    milestone, prompt_ts = T.first_prompt_milestone(rows)
    first_ts = min(ts) if ts else ''
    return {
        'session': sid,
        'files': [os.path.relpath(f, T.PROJECT) for f in files],
        'subagents': len(files) - 1,
        'first_ts': first_ts,
        'last_ts': max(ts) if ts else '',
        'models': real(reqs),
        'main_model': main_models[0] if main_models else None,
        'requests': len(reqs),
        'tool_calls': len(T.tool_calls(rows)),
        'first_go_prompt': milestone,
        'first_go_prompt_ts': prompt_ts,
        'included': bool(first_ts) and first_ts < T.CUTOFF and len(reqs) > 0,
        'cost_state': T.cost_state(rows),
    }


def main():
    cli = subprocess.run(['claude', '--version'], capture_output=True, text=True).stdout.strip()
    corpus = {
        'frozen_at': __import__('datetime').datetime.now().astimezone().isoformat(timespec='seconds'),
        'project_dir': T.PROJECT,
        'claude_code_version': cli,
        'cutoff_rule': f'included = main transcript has at least one API request and its first timestamp is '
                       f'before {T.CUTOFF}; later sessions are the evaluation itself',
        'request_dedup_key': 'requestId (fallback message.id); usage = per-field max over the streamed rows',
        'reminder_dedup_key': 'hook_success attachment with command starting "graphify hook-guard", keyed by '
                              'toolUseID; both the search and the read variant count',
        'subagent_rule': '<session>/subagents/*.jsonl folded into the parent session',
        'weights': T.WEIGHTS,
        'sessions': [describe(sid) for sid in T.session_ids()],
    }
    out = os.path.join(T.HERE, 'sessions.json')
    json.dump(corpus, open(out, 'w'), indent=2)
    inc = [s for s in corpus['sessions'] if s['included']]
    print(f'{len(corpus["sessions"])} transcripts, {len(inc)} included, '
          f'{sum(s["subagents"] for s in inc)} subagent files, {sum(s["tool_calls"] for s in inc)} tool calls')
    for s in corpus['sessions']:
        flag = 'in ' if s['included'] else 'OUT'
        print(f'{flag} {s["session"][:8]} {s["first_ts"][:16]} {s["main_model"] or "-":22} subs={s["subagents"]:2} '
              f'calls={s["tool_calls"]:4} go={s["first_go_prompt"] or "-"}')
    print(f'written: {os.path.relpath(out, T.REPO)}')


if __name__ == '__main__':
    main()
