"""Research-to-design route; no product implementation or implicit external writes."""
import copy
import json
from pathlib import Path

PHASES = ('market-research', 'product-requirements', 'solution-design',
          'technology-selection', 'architecture-design', 'design-documentation')
DEFAULT_OUTPUTS = dict(zip(PHASES, ('design/01-market.md', 'design/02-requirements.md',
    'design/03-solution.md', 'design/04-technology.md', 'design/05-architecture.md', 'design/DESIGN.md')))
SKILLS = {
    'market-research': ('market-research', 'competitive-analysis', 'technical-research'),
    'product-requirements': ('product-requirements',),
    'solution-design': ('solution-design',),
    'technology-selection': ('technology-selection', 'technical-research'),
    'architecture-design': ('architecture-design', 'technical-diagrams'),
    'design-documentation': ('project-documentation',),
    'design-gate': ('design-review',),
}


def review_schema(base):
    schema = copy.deepcopy(base)
    schema['properties']['revision_from'] = {'type': 'string', 'enum': ['none', *PHASES]}
    schema['required'].append('revision_from')
    return schema


def outputs(task):
    return task.get('design_outputs', DEFAULT_OUTPUTS)


def validate(task, error):
    if task.get('research_mode') not in ('live', 'provided'):
        raise error('research-design requires research_mode=live or provided')
    files = outputs(task)
    if not isinstance(files, dict) or set(files) != set(PHASES):
        raise error('design_outputs must map all six research-design phases')
    for name in files.values():
        if (not isinstance(name, str) or not name or Path(name).is_absolute()
                or Path(name) == Path('.') or '..' in Path(name).parts or Path(name).parts[0] == '.git'
                or Path(name).as_posix() != name or Path(name).suffix.lower() != '.md'):
            raise error('Design outputs must be normalized workspace-relative Markdown files')
    if len(set(files.values())) != len(PHASES) or set(task['scope']) != set(files.values()):
        raise error('research-design scope must contain exactly the six distinct design outputs')
    if task.get('artifacts'):
        raise error('research-design uses inline diagrams; artifact directories are not supported')


def native_searches(path):
    """Count completed native search items, never agent claims in prose."""
    count = 0
    for line in path.read_text().splitlines():
        try:
            event = json.loads(line)
        except ValueError:
            continue
        if (isinstance(event, dict) and event.get('type') == 'item.completed'
                and isinstance(event.get('item'), dict) and event['item'].get('type') == 'web_search'):
            count += 1
    return count


def drive(r, error):
    files = outputs(r.task)
    upstream = {}
    feedback = None
    start = 0
    for attempt in range(r.rounds):
        for phase in PHASES[start:]:
            context = {'stage': phase, 'target_file': files[phase], 'upstream': dict(upstream),
                       'feedback': feedback, 'research_mode': r.task['research_mode'],
                       'instruction': 'Perform the substantive domain work and write the target Markdown file. '
                           'Read actual upstream files. Preserve stable evidence, requirement and decision IDs. '
                           'Mark assumptions and blockers; do not fabricate sources, interviews, tests or approvals. '
                           'No product implementation. Use inline diagrams only.'}
            result = r.stage('tech-writer', phase, json.dumps(context, ensure_ascii=False), {'complete', 'fail'})
            upstream[phase] = {'file': files[phase], 'result': result}
        review = r.stage('red-team', 'design-gate', json.dumps({'artifacts':upstream,
            'instruction':'Review all six actual files and their cross-document consistency. '
                'Approve only if no blocking findings. On needs_fix set revision_from to the earliest affected '
                'phase; all downstream phases will rerun. On approve set revision_from=none. '
                'Review only; design approval is not implementation or market validation.'}, ensure_ascii=False),
            {'approve', 'needs_fix'})
        r.state['design_review'] = review
        r.atomic_record('design-review.json', review)
        r.atomic_record('design-artifacts.json', upstream)
        if review['verdict'] != 'approve':
            start = PHASES.index(review['revision_from'])
            feedback = {'review':review}
        else:
            checks = r.checks(f'design-round-{attempt+1}')
            if any(c['exit_code'] != 0 for c in checks):
                start, feedback = 0, {'host_checks_failed': checks}
            else:
                verification = r.verify(upstream, review, checks)
                if verification['verdict'] == 'pass':
                    r.complete()
                    r.state['verification_subject'] = 'design-artifacts'
                    return
                start, feedback = 0, {'verification':verification}
        # Remove stale downstream results before handing off the next revision.
        upstream = {phase:upstream[phase] for phase in PHASES[:start]}
    raise error('Research/design review or verification round limit', 'review_limit')
