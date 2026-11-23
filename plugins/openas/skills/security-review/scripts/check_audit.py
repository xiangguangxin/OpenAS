#!/usr/bin/env python3
"""Read-only audit-record consistency validation; does not perform security audits."""
import argparse
import json
from pathlib import Path
import sys


def text_field(row, name):
    value = row.get(name)
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f'Missing nonempty text: {name}')
    return value


def text_list(row, name):
    values = row.get(name)
    if not isinstance(values, list) or not values or any(not isinstance(v, str) or not v.strip() for v in values):
        raise ValueError(f'Missing nonempty text list: {name}')
    return values


def unique_rows(rows, label):
    if not isinstance(rows, list) or any(not isinstance(row, dict) for row in rows):
        raise ValueError(f'Invalid {label} records')
    by_id = {}
    for row in rows:
        identity = text_field(row, 'id')
        if identity in by_id:
            raise ValueError(f'Duplicate {label} ID: {identity}')
        by_id[identity] = row
    return by_id


def validate(data):
    if not isinstance(data, dict) or type(data.get('version')) is not int or data['version'] != 1:
        raise ValueError('Expected audit record version 1')
    text_field(data, 'source_ref')
    text_list(data, 'scope')
    if data.get('run_status') not in ('complete', 'incomplete'):
        raise ValueError('Expected complete or incomplete run_status')
    if data['run_status'] == 'incomplete':
        text_field(data, 'incomplete_reason')
    elif 'incomplete_reason' in data:
        raise ValueError('Complete run must not retain an incomplete_reason')
    units = unique_rows(data.get('coverage'), 'coverage')
    if not units:
        raise ValueError('Coverage must explicitly enumerate at least one unit')
    for unit in units.values():
        for field in ('surface', 'boundary', 'attack_class'):
            text_field(unit, field)
        if unit.get('status') not in ('planned', 'checked', 'blocked', 'out_of_scope'):
            raise ValueError('Unknown coverage status')
        if unit['status'] == 'checked':
            text_list(unit, 'evidence')
        else:
            text_field(unit, 'reason')
        if data['run_status'] == 'complete' and unit['status'] in ('planned', 'blocked'):
            raise ValueError('Complete run contains unresolved coverage')
    findings = unique_rows(data.get('findings'), 'finding')
    fingerprints = set()
    counts = dict(confirmed=0, needs_validation=0, rejected=0)
    for finding in findings.values():
        for field in ('fingerprint', 'unit_id', 'location', 'boundary', 'prerequisites', 'impact'):
            text_field(finding, field)
        fingerprint = finding['fingerprint']
        if fingerprint in fingerprints:
            raise ValueError('Duplicate finding fingerprint')
        fingerprints.add(fingerprint)
        unit = units.get(finding['unit_id'])
        if unit is None or unit['status'] == 'out_of_scope':
            raise ValueError('Finding must reference an in-scope coverage unit')
        if finding['boundary'] != unit['boundary']:
            raise ValueError('Finding and coverage boundary disagree')
        text_list(finding, 'evidence')
        status = finding.get('status')
        if not isinstance(status, str) or status not in counts:
            raise ValueError('Unknown finding status')
        counts[status] += 1
        if status == 'confirmed':
            if unit['status'] != 'checked':
                raise ValueError('Confirmed finding requires a checked unit')
            if finding.get('severity') not in ('critical', 'high', 'medium', 'low', 'informational'):
                raise ValueError('Confirmed finding requires calibrated severity')
            for field in ('author', 'verified_by', 'fix', 'regression_plan'):
                text_field(finding, field)
            if finding['author'].strip().casefold() == finding['verified_by'].strip().casefold():
                raise ValueError('Self-review cannot be recorded as independent verification')
            text_list(finding, 'verification_evidence')
        else:
            if 'severity' in finding:
                raise ValueError('Unconfirmed records must not carry severity')
            if status == 'needs_validation':
                text_field(finding, 'blocker')
                text_field(finding, 'validation_plan')
            else:
                text_field(finding, 'reason')
    return {'valid': True, 'run_status': data['run_status'], 'coverage_units': len(units),
            **counts, 'authority': 'record consistency only; not evidence authenticity or security acceptance'}


def unique_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f'Duplicate JSON key: {key}')
        result[key] = value
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('record', type=Path)
    args = parser.parse_args()
    try:
        result = validate(json.loads(args.record.read_text(encoding='utf-8'), object_pairs_hook=unique_object))
    except (OSError, ValueError, TypeError) as exc:
        print(str(exc), file=sys.stderr)
        return 1
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == '__main__':
    sys.exit(main())
