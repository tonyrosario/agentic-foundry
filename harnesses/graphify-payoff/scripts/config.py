"""Harness configuration: everything repo-specific lives in harness.json, next to this file or at
$HARNESS_CONFIG. Python scripts `import config as C`; shell scripts call `python3 -I config.py get <key>`.
"""
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
CONFIG_PATH = os.environ.get('HARNESS_CONFIG') or os.path.join(HERE, 'harness.json')
with open(CONFIG_PATH, encoding='utf-8') as f:
    RAW = json.load(f)


def _abs(path):
    return path if os.path.isabs(path) else os.path.normpath(os.path.join(os.path.dirname(CONFIG_PATH), path))


def slug(path):
    """Claude Code names a project's transcript folder after its absolute path."""
    return re.sub(r'[/._]', '-', os.path.abspath(path))


REPO = _abs(RAW['repo'])
CODE_ROOT = RAW.get('code_root', '').strip('/')
CODE_PREFIX = CODE_ROOT + '/' if CODE_ROOT else ''
CODE_DIR = os.path.join(REPO, CODE_ROOT) if CODE_ROOT else REPO
SOURCE_DIRS = tuple(RAW['source_dirs'])
SOURCE_EXTS = tuple(RAW['source_exts'])
PROJECT = RAW.get('transcripts_project_dir') or os.path.join(
    os.environ.get('CLAUDE_CONFIG_DIR', os.path.expanduser('~/.claude')), 'projects', slug(REPO))
CUTOFF = RAW.get('corpus_cutoff', '9999')
WEIGHTS = RAW['weights']
THRESHOLDS = RAW['thresholds']
HOOK_CMD = RAW['graph']['hook_command_prefix']
SECTION_HEADING = RAW['graph']['instructions_section_heading']
INSTRUCTIONS_FILE = RAW['graph'].get('instructions_file', 'CLAUDE.md')
GRAPH_OUT = RAW['graph'].get('graph_out', (CODE_PREFIX + 'graphify-out'))
ARM_N_REMOVE = RAW['graph'].get('arm_N_remove', [])
ARM_D_NOTE = RAW['graph'].get('arm_D_note', '')
# For a repo that no longer (or never) mandates the graph: a commit whose hook settings and
# instructions section arm G installs, so G means "mandated" rather than "whatever the base had".
ARM_G_RESTORE = RAW['graph'].get('arm_G_restore') or {}
# Literal [old, new] substitutions arm N applies to the instructions file after the section is
# stripped, for mentions of the graph that live outside the section (an on-demand repo has these).
ARM_N_EDITS = RAW['graph'].get('arm_N_edits', [])
MODEL = RAW['runs']['model']
CAP_USD = RAW['runs']['cap_usd']
PROMPT = RAW['runs']['prompt']
PLAN_FILE = RAW['runs'].get('plan_file', 'PLAN.md')
QUESTIONS_FILE = _abs(RAW['graph'].get('questions_file', 'questions.json'))
TASKS = RAW['tasks']

_dirs = '|'.join(re.escape(d) for d in SOURCE_DIRS)
# Longest extension first: with `ts|tsx`, a search would stop at `.ts` inside `foo.tsx`.
_exts = '|'.join(re.escape(e) for e in sorted(SOURCE_EXTS, key=len, reverse=True))
SOURCE_REL = rf'(?:{_dirs})/[\w./-]+\.(?:{_exts})'
# A source path as an agent or a tool might write it, captured relative to the code root (agents
# often `cd` into the code root and use relative paths).
REL_PATH_RE = re.compile(rf'(?<![\w.-])(?:[\w./-]*?/)?({SOURCE_REL})')
# A source path relative to the repository root, as git prints it.
FULL_PATH_RE = re.compile(rf'({re.escape(CODE_PREFIX)}{SOURCE_REL})')
SOURCE_ROOTS = tuple(CODE_PREFIX + d for d in SOURCE_DIRS)


def main():
    if len(sys.argv) < 3 or sys.argv[1] != 'get':
        sys.exit('usage: config.py get <key>')
    key = sys.argv[2]
    if key == 'tasks':
        for name, t in TASKS.items():
            print(name, t['base'], t['tick'])
        return
    if key == 'arm_N_remove':
        print('\n'.join(ARM_N_REMOVE))
        return
    if key == 'arm_N_edits':
        print(json.dumps(ARM_N_EDITS))
        return
    value = {'repo': REPO, 'code_root': CODE_ROOT, 'graph_out': GRAPH_OUT, 'hook_command_prefix': HOOK_CMD,
             'instructions_file': INSTRUCTIONS_FILE, 'instructions_section_heading': SECTION_HEADING,
             'arm_D_note': ARM_D_NOTE, 'arm_G_restore_commit': ARM_G_RESTORE.get('commit', ''),
             'arm_G_restore_files': ' '.join(ARM_G_RESTORE.get('files', [])), 'model': MODEL, 'cap_usd': CAP_USD, 'prompt': PROMPT,
             'project': PROJECT}[key]
    print(value)


if __name__ == '__main__':
    main()
