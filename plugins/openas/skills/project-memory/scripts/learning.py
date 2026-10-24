#!/usr/bin/env python3
"""Project-local learning lifecycle; receipts are evidence, never executable authority."""
import argparse
from contextlib import contextmanager
import importlib.util
import json
import os
from pathlib import Path
import re
import sys

SPEC = importlib.util.spec_from_file_location('learning_memory', Path(__file__).with_name('project_memory.py'))
pm = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(pm)

REVIEW_CHECKS = ('supported', 'scoped', 'reusable', 'no_secrets', 'conflicts_resolved')
SKILL_CHECKS = ('supported', 'scoped', 'no_secrets', 'positive_case', 'negative_case', 'behavior_checked')
SECRET_PATTERN = re.compile(r'-----BEGIN [A-Z ]*PRIVATE KEY-----|\bgh[pousr]_[A-Za-z0-9]{20,}|\bgithub_pat_[A-Za-z0-9_]{20,}|\b(?:api[_-]?key|password|authorization)\s*[:=]\s*["\x27]?(?!\$\{)[A-Za-z0-9_/-]{16,}', re.I)


def text(value, limit=1000):
    if not isinstance(value, str) or not value.strip() or len(value) > limit:
        raise ValueError('Expected bounded nonempty text')
    return value.strip()


def strings(value, limit=12):
    if not isinstance(value, list) or not value or len(value) > limit:
        raise ValueError('Expected bounded nonempty list')
    return [text(x, 600) for x in value]


def fingerprint(value):
    return pm.digest(json.dumps(value, sort_keys=True, ensure_ascii=False).encode())[:24]


def tokens(value):
    return set(re.findall(r'[a-z0-9_-]+|[\u4e00-\u9fff]', value.lower()))


def review_report(report, author, checks):
    if not isinstance(report, dict) or report.get('verdict') not in ('approve', 'reject'):
        raise ValueError('Review requires approve/reject')
    reviewer = text(report.get('reviewer'), 120)
    text(report.get('reason'))
    if reviewer == author:
        raise ValueError('Review must use a different reviewer from the author')
    if report['verdict'] == 'approve' and any(report.get('checks', {}).get(k) is not True for k in checks):
        raise ValueError('Approval requires all semantic review checks')
    return {k: report[k] for k in ('verdict', 'reviewer', 'reason')} | {'checks': report.get('checks', {}), 'at': pm.now()}


class Learning:
    def __init__(self, root):
        self.memory = pm.Memory(root)
        self.root = self.memory.root
        self.directory = self.memory.directory / 'learning'
        self.file = self.directory / 'state.json'
        if self.root not in self.directory.parents:
            raise ValueError('Learning storage must remain inside the consumer project')
        self.local(self.file)

    def local(self, path):
        path = Path(path)
        if self.root not in path.parents or any(p.is_symlink() for p in (path, *path.parents) if p != self.root and self.root in p.parents):
            raise ValueError('Learning paths must be project-local without symlinks')
        return path

    def read(self):
        if not self.file.exists():
            return {'version': 1, 'observations': {}, 'lessons': {}, 'skills': {}, 'active': {}, 'outcomes': {}, 'audit': []}
        data = json.loads(self.file.read_text())
        if data.get('version') != 1 or any(not isinstance(data.get(k), dict) for k in ('observations', 'lessons', 'skills', 'active', 'outcomes')) or not isinstance(data.get('audit'), list):
            raise ValueError('Invalid learning store; refusing overwrite')
        return data

    @contextmanager
    def transaction(self):
        self.local(self.file)
        self.local(self.directory / '.lock')
        self.directory.mkdir(parents=True, exist_ok=True)
        with (self.directory / '.lock').open('a') as lock:
            pm.fcntl.flock(lock, pm.fcntl.LOCK_EX)
            data = self.read()
            yield data
            pm.Memory.atomic(self.file, data)

    def receipt(self, folder, value):
        ident = fingerprint(value)
        path = self.directory / folder / (ident + '.json')
        self.local(path)
        if not path.exists():
            pm.Memory.atomic(path, value)
        elif json.loads(path.read_text()) != value:
            raise ValueError('Receipt collision or tampering')
        return ident, self.memory.evidence(str(path.relative_to(self.root)), '')

    @staticmethod
    def event(data, kind, ident, **extra):
        data['audit'].append({'at': pm.now(), 'event': kind, 'id': ident, **extra})

    def capture(self, run, run_key):
        """Automatic bounded host observations, including failed runs; never raw prose/logs."""
        observation = {
            'run_key': pm.digest(text(run_key, 4096).encode()),
            'requirement_sha256': pm.digest(run.get('task', {}).get('requirement', '').encode()),
            'status': run.get('status') if run.get('status') in ('verified', 'stopped', 'reviewed') else 'unknown',
            'done': run.get('done') is True,
            'failure_kind': re.sub(r'[^a-z_-]', '', str(run.get('failure', {}).get('kind', '')))[:80],
            'baseline_exit_codes': [x.get('exit_code') for x in run.get('baseline_checks', [])],
            'final_exit_codes': [x.get('exit_code') for x in run.get('final_checks', run.get('last_checks', []))],
            'recoveries': len(run.get('recoveries', [])),
            'initial_snapshot_sha256': fingerprint(run.get('initial_snapshot', {})),
            'final_snapshot_sha256': fingerprint(run.get('final_snapshot', run.get('checkpoint_snapshot', {}))),
        }
        for field in ('baseline_exit_codes', 'final_exit_codes'):
            if len(observation[field]) > 100 or any(type(x) is not int for x in observation[field]):
                raise ValueError('Invalid host exit codes')
        ident, evidence = self.receipt('observations', observation)
        with self.transaction() as data:
            if ident not in data['observations']:
                data['observations'][ident] = {'id': ident, 'value': observation, 'evidence': evidence}
                self.event(data, 'captured', ident)
        return data['observations'][ident]

    def propose(self, proposal):
        fields = ('key', 'scope', 'statement', 'trigger', 'cause', 'limitations', 'author')
        item = {k: text(proposal.get(k), 600 if k != 'statement' else 1000) for k in fields}
        item['procedure'] = strings(proposal.get('procedure'))
        item['validation'] = strings(proposal.get('validation'))
        item['tags'] = strings(proposal.get('tags'))
        item['observation_ids'] = strings(proposal.get('observation_ids'))
        item['evidence'] = proposal.get('evidence')
        if SECRET_PATTERN.search(json.dumps(item, ensure_ascii=False)):
            raise ValueError('Possible credential material in lesson; redact before proposing')
        if not self.memory.valid(item):
            raise ValueError('Lesson requires current project-file evidence')
        with self.transaction() as data:
            for ident in item['observation_ids']:
                observation = data['observations'].get(ident)
                if not observation or not self.memory.valid({'evidence': [observation['evidence']]}):
                    raise ValueError('Missing or stale observation')
                if observation['evidence'] not in item['evidence']:
                    item['evidence'] = [*item['evidence'], observation['evidence']]
            ident = fingerprint(item)
            if ident in data['lessons']:
                return data['lessons'][ident]
            similar = []
            a = tokens(item['statement'])
            for other in data['lessons'].values():
                b = tokens(other['statement'])
                if other['scope'] == item['scope'] and a and len(a & b) / len(a | b) >= .65:
                    similar.append(other['id'])
            item.update(id=ident, status='candidate', similar=similar, created=pm.now(), review=None)
            # Same key/scope is a conflict even when wording differs; never overwrite.
            if self.conflicts(data, item):
                item['status'] = 'conflict'
            data['lessons'][ident] = item
            self.event(data, 'proposed', ident)
        return item

    @staticmethod
    def conflicts(data, item):
        return [x['id'] for x in data['lessons'].values() if x['id'] != item['id'] and x['key'] == item['key'] and x['scope'] == item['scope'] and x['status'] == 'accepted']

    def lesson_valid(self, item):
        return self.memory.valid(item)

    def review(self, ident, report):
        with self.transaction() as data:
            item = data['lessons'][ident]
            if item['status'] not in ('candidate', 'conflict'):
                raise ValueError('Only pending lessons can be reviewed')
            reviewed = review_report(report, item['author'], REVIEW_CHECKS)
            if reviewed['verdict'] == 'approve':
                if not self.lesson_valid(item):
                    raise ValueError('Stale lesson evidence')
                if self.conflicts(data, item):
                    raise ValueError('Retire conflicting lesson before approval')
                # Link the complete procedure, not just its one-line summary, into evidence.
                payload = {k: item[k] for k in ('trigger', 'cause', 'procedure', 'validation', 'limitations')}
                _, detail = self.receipt('lessons', payload)
                record = self.memory.propose(item['key'], 'lesson', item['statement'], item['tags'], [*item['evidence'], detail], item['scope'])
                if record['status'] in ('candidate', 'conflict'):
                    record = self.memory.review(record['id'], 'approve', reviewed['reviewer'], reviewed['reason'])
                if record['status'] != 'accepted':
                    raise ValueError('Memory conflict or retired record; inspect memory before retry')
                item['memory_id'] = record['id']
                item['status'] = 'accepted'
            else:
                item['status'] = 'rejected'
            item['review'] = reviewed
            self.event(data, item['status'], ident)
        return item

    def retire(self, ident, reason):
        reason = text(reason)
        with self.transaction() as data:
            item = data['lessons'][ident]
            if item.get('memory_id'):
                self.memory.retire(item['memory_id'], reason)
            item['status'] = 'retired'
            self.event(data, 'retired', ident, reason=reason)
        return item

    def ready_lesson(self, data, ident):
        item = data['lessons'][ident]
        record = next((r for r in self.memory.inspect() if r['id'] == item.get('memory_id')), None)
        if item['status'] != 'accepted' or not self.lesson_valid(item) or not record or record['status'] != 'accepted' or not record['evidence_valid']:
            raise ValueError('Skill requires accepted, current lessons')
        return item

    def draft(self, name, lesson_ids, author):
        if not re.fullmatch(r'[a-z][a-z0-9-]{0,62}', name):
            raise ValueError('Invalid skill name')
        text(author, 120)
        with self.transaction() as data:
            lessons = [self.ready_lesson(data, ident) for ident in dict.fromkeys(lesson_ids)]
            if not lessons:
                raise ValueError('At least one accepted lesson is required')
            scopes = {x['scope'] for x in lessons}
            if len(scopes) != 1:
                raise ValueError('Skill sources must have one scope')
            description = '；'.join(x['trigger'] for x in lessons)[:600]
            body = f'---\nname: {name}\ndescription: {json.dumps(description, ensure_ascii=False)}\n---\n\n# {name}\n\n'
            body += '仅在以下项目条件成立时使用；当前用户任务、源码和授权优先。\n\n'
            for item in lessons:
                body += f"## {item['key']}\n\n触发条件：{item['trigger']}\n\n已审查经验：{item['statement']}\n\n原因及前提：{item['cause']}\n\n"
                body += '\n'.join(f'{i}. {step}' for i, step in enumerate(item['procedure'], 1)) + '\n\n'
                body += '验证：\n\n' + '\n'.join('- ' + step for step in item['validation']) + '\n\n'
                body += f"适用边界：{item['limitations']}\n\n"
            payload = {'name': name, 'lesson_ids': [x['id'] for x in lessons], 'author': author, 'body': body}
            ident = fingerprint(payload)
            path = self.directory / 'skills' / name / ident / 'SKILL.md'
            self.local(path)
            if path.exists() and path.read_text() != body:
                raise ValueError('Existing skill artifact changed')
            if not path.exists():
                path.parent.mkdir(parents=True, exist_ok=True)
                fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
                with os.fdopen(fd, 'w') as stream:
                    stream.write(body)
            if ident not in data['skills']:
                data['skills'][ident] = {k: v for k, v in payload.items() if k != 'body'} | {
                    'id': ident, 'scope': lessons[0]['scope'], 'path': str(path.relative_to(self.root)),
                    'sha256': pm.digest(body.encode()), 'status': 'candidate', 'review': None,
                    'evaluations': [], 'suspended': False, 'created': pm.now()}
                self.event(data, 'skill-drafted', ident)
        return data['skills'][ident]

    def valid_skill(self, data, skill):
        try:
            raw = self.memory.source(skill['path']).read_bytes()
            return pm.digest(raw) == skill['sha256'] and all(self.ready_lesson(data, ident) for ident in skill['lesson_ids'])
        except (OSError, ValueError, KeyError):
            return False

    def evaluate(self, ident, report_path):
        """Import a trusted external trial receipt, bound to exact skill bytes and sources."""
        report_path = str(report_path)
        report = json.loads(self.memory.source(report_path).read_text())
        with self.transaction() as data:
            skill = data['skills'][ident]
            if not self.valid_skill(data, skill) or report.get('skill_sha256') != skill['sha256']:
                raise ValueError('Skill or trial version is stale')
            cases = report.get('cases')
            if not isinstance(cases, list) or len(cases) < 2:
                raise ValueError('Positive and negative trials required')
            if not {True, False} <= {c.get('expected_applicable') for c in cases}:
                raise ValueError('Positive and negative trials required')
            evidence = self.memory.evidence(report_path, '', sources=strings(report.get('sources'), 50))
            passed = all(type(c.get('expected_applicable')) is bool and c.get('actual_applicable') is c['expected_applicable']
                         and c.get('passed') is True and bool(c.get('checks'))
                         and all(type(code) is int and code == 0 for code in c['checks']) for c in cases)
            eid = fingerprint(evidence)
            entry = {'id': eid, 'passed': passed, 'evidence': [evidence], 'at': pm.now()}
            if not any(x['id'] == eid for x in skill['evaluations']):
                skill['evaluations'].append(entry)
                # New evaluation invalidates old semantic acceptance.
                skill['review'] = None
                skill['status'] = 'candidate'
                if data['active'].get(skill['name']) == ident:
                    del data['active'][skill['name']]
                self.event(data, 'evaluated', ident, passed=passed)
        return entry

    def approve_skill(self, ident, report):
        with self.transaction() as data:
            skill = data['skills'][ident]
            reviewed = review_report(report, skill['author'], SKILL_CHECKS)
            if reviewed['verdict'] == 'approve':
                if not self.valid_skill(data, skill) or not skill['evaluations']:
                    raise ValueError('Current skill and trial evidence required')
                evaluation = skill['evaluations'][-1]
                if not evaluation['passed'] or not self.memory.valid(evaluation):
                    raise ValueError('Latest trial failed or is stale')
                if skill['suspended']:
                    stopped = [x['at'] for x in data['audit'] if x['id'] == ident and x['event'] in ('disabled', 'auto-suspended')]
                    if stopped and evaluation['at'] <= max(stopped):
                        raise ValueError('Suspended skill needs a fresh trial before reinstatement')
                    skill['suspended'] = False
            skill['review'] = reviewed
            skill['status'] = 'approved' if reviewed['verdict'] == 'approve' else 'rejected'
            if reviewed['verdict'] == 'reject' and data['active'].get(skill['name']) == ident:
                del data['active'][skill['name']]
            self.event(data, 'skill-' + skill['status'], ident)
        return skill

    def eligible(self, data, skill):
        return (skill['status'] == 'approved' and not skill['suspended'] and self.valid_skill(data, skill)
                and skill['evaluations'] and skill['evaluations'][-1]['passed']
                and self.memory.valid(skill['evaluations'][-1]))

    def activate(self, ident, reason, rollback=False):
        reason = text(reason)
        with self.transaction() as data:
            skill = data['skills'][ident]
            if not self.eligible(data, skill):
                raise ValueError('Only reviewed, evaluated, current, unsuspended skill can activate')
            previous = data['active'].get(skill['name'])
            if previous == ident:
                return skill
            if rollback and not any(x['event'] in ('activated', 'rollback') and x['id'] == ident for x in data['audit']):
                raise ValueError('Rollback target was never activated')
            data['active'][skill['name']] = ident
            self.event(data, 'rollback' if rollback else 'activated', ident, previous=previous, reason=reason)
        return skill

    def disable(self, ident, reason):
        with self.transaction() as data:
            skill = data['skills'][ident]
            skill['suspended'] = True
            if data['active'].get(skill['name']) == ident:
                del data['active'][skill['name']]
            self.event(data, 'disabled', ident, reason=text(reason))
        return skill

    def context(self, query, limit=3, budget=8000):
        data = self.read()
        chosen = []
        used = 0
        for ident in data['active'].values():
            skill = data['skills'][ident]
            if not self.eligible(data, skill):
                continue
            body = self.memory.source(skill['path']).read_text()
            if not tokens(query) & tokens(body):
                continue
            if used + len(body) > budget:
                continue
            chosen.append({'id': ident, 'name': skill['name'], 'sha256': skill['sha256'], 'content': body})
            used += len(body)
            if len(chosen) >= limit:
                break
        return chosen

    def outcome(self, ident, observation_id, useful=None):
        if useful is not None and type(useful) is not bool:
            raise ValueError('useful must be boolean or null')
        with self.transaction() as data:
            skill = data['skills'][ident]
            observation = data['observations'][observation_id]
            if not self.memory.valid({'evidence': [observation['evidence']]}):
                raise ValueError('Observation is stale')
            oid = fingerprint([ident, observation_id])
            if oid in data['outcomes']:
                entry = data['outcomes'][oid]
                if useful is None or entry['useful'] is useful:
                    return entry
                entry['useful'] = useful
                self.event(data, 'feedback-updated', ident, observation_id=observation_id, useful=useful)
            else:
                value = observation['value']
                success = (value['status'] == 'verified' and value['done'] and bool(value['final_exit_codes'])
                           and all(x == 0 for x in value['final_exit_codes']))
                if value['status'] not in ('verified', 'stopped'):
                    success = None
                entry = {'id': oid, 'skill_id': ident, 'observation_id': observation_id,
                         'success': success, 'useful': useful, 'at': pm.now()}
                data['outcomes'][oid] = entry
            history = [x for x in data['outcomes'].values() if x['skill_id'] == ident]
            # Conservative circuit breaker: task failures are correlation, not causal proof.
            if len(history) >= 3 and all(x['success'] is False or x['useful'] is False for x in history[-3:]):
                skill['suspended'] = True
                if data['active'].get(skill['name']) == ident:
                    del data['active'][skill['name']]
                self.event(data, 'auto-suspended', ident, reason='Three consecutive negative observations; investigate causality before re-enabling')
            self.event(data, 'outcome', ident, observation_id=observation_id)
        return entry

    def inspect(self):
        data = self.read()
        metrics = {}
        for ident in data['skills']:
            outcomes = [x for x in data['outcomes'].values() if x['skill_id'] == ident]
            metrics[ident] = {'observed_tasks': len(outcomes), 'successful_tasks': sum(x['success'] is True for x in outcomes),
                              'unclassified_tasks': sum(x['success'] is None for x in outcomes),
                              'useful_feedback': sum(x['useful'] is True for x in outcomes),
                              'negative_feedback': sum(x['useful'] is False for x in outcomes),
                              'note': 'Context delivery and task outcomes are correlation, not proof of skill use or benefit'}
        return {**data, 'lesson_validity': {k: self.lesson_valid(v) for k, v in data['lessons'].items()},
                'skill_eligibility': {k: bool(self.eligible(data, v)) for k, v in data['skills'].items()}, 'metrics': metrics}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', required=True, type=Path)
    sub = parser.add_subparsers(dest='command', required=True)
    sub.add_parser('inspect')
    p = sub.add_parser('capture'); p.add_argument('run', type=Path)
    p = sub.add_parser('propose'); p.add_argument('proposal', type=Path)
    for command in ('review', 'review-skill'):
        p = sub.add_parser(command); p.add_argument('id'); p.add_argument('report', type=Path)
    for command in ('retire', 'activate', 'rollback', 'disable'):
        p = sub.add_parser(command); p.add_argument('id'); p.add_argument('--reason', required=True)
    p = sub.add_parser('draft'); p.add_argument('name'); p.add_argument('--lessons', nargs='+', required=True); p.add_argument('--author', required=True)
    p = sub.add_parser('evaluate'); p.add_argument('id'); p.add_argument('report', help='Project-relative trial report')
    p = sub.add_parser('context'); p.add_argument('query')
    p = sub.add_parser('outcome'); p.add_argument('id'); p.add_argument('observation_id'); p.add_argument('--useful', choices=('yes', 'no'))
    args = parser.parse_args()
    try:
        learning = Learning(args.root)
        command = args.command
        if command == 'inspect': result = learning.inspect()
        elif command == 'capture': result = learning.capture(json.loads(args.run.read_text()), str(args.run.resolve()))
        elif command == 'propose': result = learning.propose(json.loads(args.proposal.read_text()))
        elif command == 'review': result = learning.review(args.id, json.loads(args.report.read_text()))
        elif command == 'review-skill': result = learning.approve_skill(args.id, json.loads(args.report.read_text()))
        elif command == 'draft': result = learning.draft(args.name, args.lessons, args.author)
        elif command == 'evaluate': result = learning.evaluate(args.id, args.report)
        elif command == 'context': result = learning.context(args.query)
        elif command == 'outcome': result = learning.outcome(args.id, args.observation_id, None if args.useful is None else args.useful == 'yes')
        elif command in ('activate', 'rollback'): result = learning.activate(args.id, args.reason, rollback=command == 'rollback')
        else: result = getattr(learning, command)(args.id, args.reason)
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0
    except (OSError, ValueError, KeyError, TypeError, StopIteration) as exc:
        print(f'Learning operation failed: {type(exc).__name__}; inspect input and evidence.', file=sys.stderr)
        return 2


if __name__ == '__main__':
    sys.exit(main())
