"""M3, M4 and M7 for one run's PLAN.md against the reference milestone (plan.md section 6, unadjusted).

Run from the repo root:
  python3 -I local/graphify-eval/plan_score.py --plan <PLAN.md> --base c5178f0 --tick 9738747
Reference files (M3 denominator): app/ source files the milestone changed that existed at the base.
Reuse set (M4 denominator): modules that the milestone's new or changed files import, resolved from
the tick commit's sources, that existed at the base. A plan item counts when it names the path, or,
as a fallback that is reported, only the basename. M7 is the share of app/ items the plan names
that are in either set. The blind grader's accepted items (Phase 3) are added with --accept.
"""
import argparse
import json
import os
import posixpath
import re
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import transcripts as T  # noqa: E402

import config as C  # noqa: E402

SOURCE = C.FULL_PATH_RE
NAMED = C.REL_PATH_RE
BASENAME = re.compile(r'(?<![\w/])([A-Z][\w]+|use[A-Z]\w+|[a-z][\w]+)\.(?:tsx?|css)\b')
IMPORT = re.compile(r'(?:import|export)\s[^;]*?from\s+[\'"](\.[^\'"]+)[\'"]|import\s*\(\s*[\'"](\.[^\'"]+)[\'"]')
EXTS = ('.ts', '.tsx', '/index.ts', '/index.tsx', '')


def git(*args):
    return subprocess.run(['git', *args], cwd=T.REPO, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL,
                          text=True).stdout


def exists_at(commit, path):
    return subprocess.run(['git', 'cat-file', '-e', f'{commit}:{path}'], cwd=T.REPO,
                          stderr=subprocess.DEVNULL).returncode == 0


def resolve(src, spec, commit):
    base = posixpath.normpath(posixpath.join(posixpath.dirname(src), spec))
    for ext in EXTS:
        if ext == '' and not base.endswith(('.ts', '.tsx', '.css')):
            continue
        if exists_at(commit, base + ext):
            return base + ext
    return None


def reference(base, tick):
    changed = [p for p in git('diff', '--name-only', base, tick, '--', C.CODE_ROOT or '.').split() if SOURCE.fullmatch(p)]
    existed = {p for p in changed if exists_at(base, p)}
    reuse = set()
    for p in changed:
        for m in IMPORT.finditer(git('show', f'{tick}:{p}')):
            target = resolve(p, m.group(1) or m.group(2), tick)
            if target and exists_at(base, target):
                reuse.add(target)
    return existed, reuse, set(changed)


def plan_items(text):
    by_path = {C.CODE_PREFIX + p for p in NAMED.findall(text)}
    by_name = set(BASENAME.findall(text)) - {posixpath.basename(p).rsplit('.', 1)[0] for p in by_path}
    return by_path, by_name


def hits(reference_set, by_path, by_name):
    exact = {p for p in reference_set if p in by_path}
    loose = {p for p in reference_set - exact if posixpath.basename(p).rsplit('.', 1)[0] in by_name}
    return exact, loose


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--plan', required=True)
    ap.add_argument('--base', required=True)
    ap.add_argument('--tick', required=True)
    ap.add_argument('--accept', help='JSON list of plan items the blind grader accepted as valid')
    args = ap.parse_args()
    existed, reuse, changed = reference(args.base, args.tick)
    text = open(args.plan, encoding='utf-8').read()
    by_path, by_name = plan_items(text)
    m3_exact, m3_loose = hits(existed, by_path, by_name)
    m4_exact, m4_loose = hits(reuse, by_path, by_name)
    # Files the milestone created count as valid plan items too (M7 is precision over everything named).
    valid = changed | reuse
    accepted = set(json.load(open(args.accept))) if args.accept else set()
    named = by_path
    precise = {p for p in named if p in valid or p in accepted}
    result = {
        'plan': args.plan, 'base': args.base, 'tick': args.tick,
        'reference_files': len(existed), 'reference_new_files': len(changed - existed), 'reuse_modules': len(reuse),
        'plan_paths': len(by_path), 'new_files_named_exactly': sorted((changed - existed) & by_path),
        'plan_basenames_only': sorted(by_name),
        'M3_file_recall': round((len(m3_exact) + len(m3_loose)) / len(existed), 3) if existed else None,
        'M4_reuse_recall': round((len(m4_exact) + len(m4_loose)) / len(reuse), 3) if reuse else None,
        'M7_precision': round(len(precise) / len(named), 3) if named else None,
        'M3_by_basename_only': sorted(m3_loose), 'M4_by_basename_only': sorted(m4_loose),
        'M3_missed': sorted(existed - m3_exact - m3_loose), 'M4_missed': sorted(reuse - m4_exact - m4_loose),
        'named_outside_reference': sorted(named - valid - accepted),
        'accepted_by_grader': sorted(accepted),
    }
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
