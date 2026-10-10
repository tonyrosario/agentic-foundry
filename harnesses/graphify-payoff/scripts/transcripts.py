"""Shared readers for Claude Code transcripts: sessions, deduplicated token usage, hook reminders.

Transcript facts these readers depend on (checked 2026-10-10 on Claude Code's JSONL format):
- One API request is stored as several `assistant` rows (one per content block) that all carry the
  same `requestId` and repeat the same `usage`; usage is therefore summed once per requestId.
- The hook's reminder is stored several times per tool call; the one entry per call is the
  `hook_success` attachment whose `command` starts with `graphify hook-guard`, keyed by `toolUseID`.
- Subagent transcripts live in `<session>/subagents/*.jsonl` and are folded into the parent.
"""
import glob
import json
import os
import re
import sys
from collections import defaultdict

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import config as C  # noqa: E402

PROJECT = C.PROJECT
HERE = C.HERE
REPO = C.REPO
# Sessions that started after this instant are the evaluation itself, not the work being measured.
CUTOFF = C.CUTOFF
# Price weights relative to the model's input price (plan section 6); the output ratio is the
# model's published output/input price.
WEIGHTS = C.WEIGHTS
USAGE_FIELDS = tuple(WEIGHTS)
HOOK_CMD = C.HOOK_CMD
GRAPH_CMD = re.compile(r'(?:^|[;&|(]\s*|\n)\s*(?:cd [^;&]+&&\s*)?graphify (query|path|explain|affected)\b')
UPDATE_CMD = re.compile(r'(?:^|[;&|(]\s*|\n)\s*(?:cd [^;&]+&&\s*)?graphify update\b')


def session_ids():
    return sorted(os.path.basename(p)[:-len('.jsonl')] for p in glob.glob(os.path.join(PROJECT, '*.jsonl')))


def transcript_files(sid):
    main = os.path.join(PROJECT, sid + '.jsonl')
    subs = sorted(glob.glob(os.path.join(PROJECT, sid, 'subagents', '*.jsonl')))
    return [main] + subs


def entries(files):
    """Every JSON row across the files, tagged with its source file, sorted by timestamp."""
    rows = []
    for path in files:
        for line in open(path, encoding='utf-8'):
            try:
                e = json.loads(line)
            except ValueError:
                continue
            e['_file'] = os.path.basename(path)
            rows.append(e)
    rows.sort(key=lambda e: e.get('timestamp') or '')
    return rows


def requests(rows):
    """One record per API request: {id, ts, model, usage} with usage taken as the per-field max over
    the streamed rows that share the requestId."""
    seen = {}
    for e in rows:
        if e.get('type') != 'assistant':
            continue
        msg = e.get('message') or {}
        usage = msg.get('usage')
        if not usage:
            continue
        key = e.get('requestId') or msg.get('id')
        rec = seen.setdefault(key, {'id': key, 'ts': e.get('timestamp') or '', 'model': msg.get('model'),
                                    'usage': dict.fromkeys(USAGE_FIELDS, 0)})
        for f in USAGE_FIELDS:
            rec['usage'][f] = max(rec['usage'][f], usage.get(f) or 0)
    return sorted(seen.values(), key=lambda r: r['ts'])


def sum_usage(recs):
    total = dict.fromkeys(USAGE_FIELDS, 0)
    for r in recs:
        for f in USAGE_FIELDS:
            total[f] += r['usage'][f]
    total['raw'] = sum(total[f] for f in USAGE_FIELDS)
    total['weighted'] = round(sum(total[f] * WEIGHTS[f] for f in USAGE_FIELDS))
    return total


def tool_calls(rows):
    """Tool uses in order with their results: (ts, id, name, input, result_text, result_ts)."""
    uses, results = [], {}
    for e in rows:
        content = (e.get('message') or {}).get('content')
        if not isinstance(content, list):
            continue
        for c in content:
            if c.get('type') == 'tool_use':
                uses.append([e.get('timestamp') or '', c['id'], c.get('name'), c.get('input') or {}, '', ''])
            elif c.get('type') == 'tool_result':
                results[c.get('tool_use_id')] = (result_text(c.get('content')), e.get('timestamp') or '')
    for u in uses:
        u[4], u[5] = results.get(u[1], ('', ''))
    return uses


def result_text(content):
    if isinstance(content, list):
        return ''.join(x.get('text', '') for x in content if isinstance(x, dict))
    return content or ''


def reminders(rows):
    """One record per hook reminder, keyed by toolUseID: (ts, toolUseID, text)."""
    out = {}
    for e in rows:
        att = e.get('attachment')
        if not isinstance(att, dict) or att.get('type') != 'hook_success':
            continue
        if not (att.get('command') or '').startswith(HOOK_CMD):
            continue
        try:
            text = json.loads(att.get('stdout') or '{}').get('hookSpecificOutput', {}).get('additionalContext', '')
        except ValueError:
            text = ''
        if text:
            out.setdefault(att.get('toolUseID'), (e.get('timestamp') or '', att.get('toolUseID'), text))
    return sorted(out.values())


def first_prompt_milestone(rows):
    for e in rows:
        content = (e.get('message') or {}).get('content')
        if e.get('type') == 'user' and isinstance(content, str):
            m = re.search(r'\bgo (m\d+\w*)\b', content, re.I)
            if m:
                return m.group(1).lower(), e.get('timestamp') or ''
    return None, None


def cost_state(rows):
    """The harness's own running totals, used only to validate the per-request sums."""
    last = None
    for e in rows:
        if e.get('type') == 'cost-state' and e['_file'].count('/') == 0:
            last = e
    if not last:
        return None
    by_model = defaultdict(lambda: dict.fromkeys(USAGE_FIELDS, 0))
    for model, u in (last.get('modelUsage') or {}).items():
        by_model[model]['input_tokens'] = u.get('inputTokens', 0)
        by_model[model]['cache_creation_input_tokens'] = u.get('cacheCreationInputTokens', 0)
        by_model[model]['cache_read_input_tokens'] = u.get('cacheReadInputTokens', 0)
        by_model[model]['output_tokens'] = u.get('outputTokens', 0)
    return {'cost_usd': last.get('totalCostUSD'), 'by_model': dict(by_model)}


def load_corpus():
    path = os.path.join(HERE, 'sessions.json')
    return json.load(open(path)) if os.path.exists(path) else None
