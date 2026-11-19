"""Data-driven minimal skill bundles, tier floors and host-evidence gates."""
import hashlib
import ast
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TIERS = ('light', 'standard', 'heavy')
RISKS = {'unknown', 'security', 'public-api', 'data-migration', 'production-incident',
         'performance-critical', 'concurrency'}
CARRIERS = {'code', 'markdown', 'office', 'browser', 'desktop', 'diagram'}


def unique_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result: raise ValueError('Duplicate machine metadata key: '+key)
        result[key] = value
    return result


def load_policy(root=ROOT):
    return json.loads((Path(root)/'references/task-routing.json').read_text(encoding='utf-8'), object_pairs_hook=unique_object)


def validate_registry(root=ROOT):
    root = Path(root)
    policy = load_policy(root)
    skills = {p.parent.name for p in (root/'skills').glob('*/SKILL.md')}
    roles = {p.stem for p in (root/'agents').glob('*.md')}
    if policy.get('version') != 1 or set(policy.get('bundles', {})) != {'feature', 'bugfix', 'refactor', 'documentation'}:
        raise ValueError('Routing registry requires four supported task bundles')
    catalog = policy.get('skills')
    if not isinstance(catalog, dict) or set(catalog) != skills:
        raise ValueError('Skill catalog must cover every packaged skill exactly once')
    for name, entry in catalog.items():
        if (not isinstance(entry, dict) or set(entry) != {'owner', 'category', 'activation', 'when'}
                or entry['owner'] not in roles or entry['activation'] not in {'core', 'conditional', 'specialized'}
                or not isinstance(entry['when'], str) or not entry['when'].strip()
                or not isinstance(entry['category'], str) or not entry['category'].strip()):
            raise ValueError(f'Incomplete skill metadata or unknown role: {name}')
    for kind, bundle in policy['bundles'].items():
        if set(bundle) != {'base', 'standard', 'heavy', 'roles'} or any(r not in roles for r in bundle['roles']):
            raise ValueError(f'Invalid role references for bundle: {kind}')
        for level in ('base', 'standard', 'heavy'):
            values = bundle[level]
            if not isinstance(values, list) or len(set(values)) != len(values) or any(v not in skills for v in values):
                raise ValueError(f'Invalid skill references for bundle: {kind}/{level}')
        if not 1 <= len(bundle['base']) <= 3:
            raise ValueError('Default bundle must contain one to three skills')
    if set(policy.get('extensions', {})) != (RISKS - {'unknown'}) | (CARRIERS - {'code', 'markdown'}):
        raise ValueError('Routing extension coverage mismatch')
    for condition, names in policy['extensions'].items():
        if not isinstance(names, list) or any(n not in skills for n in names):
            raise ValueError(f'Unknown conditional skill: {condition}')
    for path in (root/'workflows').glob('*.py'):
        for node in ast.walk(ast.parse(path.read_text(encoding='utf-8'))):
            if (isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute)
                    and node.func.attr in {'stage', 'call'} and node.args
                    and isinstance(node.args[0], ast.Constant) and isinstance(node.args[0].value, str)
                    and node.args[0].value not in roles):
                raise ValueError(f'Unknown workflow role reference in {path.name}: {node.args[0].value}')
    return {'bundles': len(policy['bundles']), 'catalog_skills': len(catalog), 'roles': len(roles)}


def plan(task, policy=None):
    policy = policy or load_policy()
    kind, requested = task.get('task_kind'), task.get('rigor', 'auto')
    scope = task.get('scope')
    risks, carrier = task.get('risk_factors', ['unknown']), task.get('carrier', 'code')
    modules = task.get('module_count', 1)
    if (kind not in policy['bundles'] or requested not in (*TIERS, 'auto')
            or not isinstance(scope, list) or not scope or any(not isinstance(p, str) or not p.strip() for p in scope)
            or not isinstance(risks, list) or any(r not in RISKS for r in risks)
            or any(Path(p).is_absolute() or '..' in Path(p).parts or Path(p) == Path('.') for p in scope)
            or len(set(scope)) != len(scope)
            or carrier not in CARRIERS or type(modules) is not int or modules < 1):
        raise ValueError('Invalid task kind, rigor, explicit scope, risks or carrier')
    floor, reasons = 'light', ['single-file bounded change']
    if len(scope) > 1 or modules > 1 or 'unknown' in risks or carrier in {'office', 'browser', 'desktop'}:
        floor, reasons = 'standard', ['multiple files/modules, uncertain risk or stateful/visual carrier']
    if set(risks) - {'unknown'} or len(scope) > 10 or modules > 3:
        floor, reasons = 'heavy', ['sensitive risk, broad scope or cross-cutting change']
    if requested != 'auto' and TIERS.index(requested) < TIERS.index(floor):
        raise ValueError(f'Requested rigor {requested} is below the required {floor} floor')
    tier = floor if requested == 'auto' else requested
    route = 'repair' if kind == 'bugfix' else 'documentation' if kind == 'documentation' else 'direct' if tier == 'light' else 'development'
    if 'workflow' in task and task['workflow'] != route:
        raise ValueError(f'Workflow conflicts with selected rigor; expected {route}')
    bundle = policy['bundles'][kind]
    selected = list(bundle['base'])
    if tier != 'light': selected += bundle['standard']
    if tier == 'heavy': selected += bundle['heavy']
    for trigger in [*risks, carrier]: selected += policy['extensions'].get(trigger, [])
    selected = list(dict.fromkeys(selected))
    writer = 'tech-writer' if kind == 'documentation' else 'developer'
    roles = [writer] if tier == 'light' else (['tech-writer', 'red-team', 'verifier'] if kind == 'documentation'
                                               else ['cto', 'red-team', 'tech-writer', 'developer', 'verifier'])
    if tier == 'heavy' and 'cto' not in roles: roles.insert(0, 'cto')
    for risk, role in (('security', 'security-reviewer'), ('performance-critical', 'performance-engineer')):
        if risk in risks: roles.append(role)
    identity = hashlib.sha256(json.dumps(policy, sort_keys=True).encode() + b'\0' + Path(__file__).read_bytes()).hexdigest()
    return {'version': 1, 'kind': kind, 'tier': tier, 'minimum_tier': floor, 'workflow': route,
            'skills': selected, 'roles': roles, 'reasons': reasons, 'policy_sha256': identity,
            'required_evidence': ['scope', 'host_checks'] + (['failing_baseline'] if kind == 'bugfix' else [])
                + (['independent_review', 'independent_verification'] if tier != 'light' else [])
                + (['impact_analysis', 'design_review'] if tier == 'heavy' else []),
            'conditional_triggers': [r for r in [*risks, carrier] if r in policy['extensions']]}


def check_evidence(state):
    """Validate a trusted host receipt's completeness, not its cryptographic authenticity."""
    route = state.get('rigor_plan')
    if not isinstance(route, dict) or route != plan(state.get('task', {})):
        raise ValueError('Missing or stale rigor plan')
    checks = state.get('final_checks')
    if (not isinstance(state.get('workspace'), str) or not state['workspace'].strip()
            or not isinstance(state.get('final_snapshot'), dict) or not checks or not isinstance(checks, list)
            or any(not isinstance(c, dict) or type(c.get('exit_code')) is not int or c['exit_code'] != 0
                   or not isinstance(c.get('argv'), list) or not c['argv']
                   or any(not isinstance(a, str) or not a for a in c['argv']) for c in checks)):
        raise ValueError('Missing successful host command evidence or object snapshot')
    if any(not isinstance(item, dict) or not isinstance(item.get('sha256'), str)
           or not re.fullmatch(r'[0-9a-f]{64}', item['sha256']) for item in state['final_snapshot'].values()):
        raise ValueError('Object snapshot lacks file fingerprints')
    if route['kind'] == 'bugfix' and not any(type(c.get('exit_code')) is int and c['exit_code'] != 0
                                           for c in state.get('baseline_checks', [])):
        raise ValueError('Bug fix requires a failing host baseline')
    steps = state.get('steps', [])
    def has(role, phase, verdict):
        return any(s.get('role') == role and s.get('phase') == phase
                   and s.get('result', {}).get('verdict') == verdict
                   and bool(s['result'].get('evidence')) for s in steps)
    if route['tier'] != 'light':
        if not any(has('red-team', p, 'approve') for p in ('code-review', 'document-review', 'operations-review')):
            raise ValueError('Missing independent implementation/document review evidence')
        result = state.get('verification', {})
        if not has('verifier', 'verification', 'pass') or result.get('verdict') != 'pass':
            raise ValueError('Missing independent acceptance evidence')
    if route['tier'] == 'heavy':
        if not has('cto', 'impact-analysis', 'complete') or not has('red-team', 'rigor-design-review', 'approve'):
            raise ValueError('Heavy rigor requires impact analysis and design review')
        for risk, role in (('security', 'security-reviewer'), ('performance-critical', 'performance-engineer')):
            if risk in route['conditional_triggers'] and not has(role, 'risk-review-'+risk, 'approve'):
                raise ValueError(f'Missing conditional risk review: {risk}')
    mappings = state['task'].get('acceptance_checks')
    if (not isinstance(mappings, list) or len(mappings) != len(state['task']['acceptance'])
            or any(not isinstance(row, list) or not row or any(type(i) is not int or not 0 <= i < len(checks) for i in row)
                   for row in mappings)):
        raise ValueError('Every acceptance criterion requires explicit host check mappings')
    return {'passed': True, 'tier': route['tier'], 'evidence': route['required_evidence'],
            'policy_sha256': route['policy_sha256'], 'authority': 'trusted-host-record; not an authenticity certificate'}
