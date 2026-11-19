"""Local, escaped HTML receipts; a workflow success is not blanket acceptance."""
from html import escape
import os
from pathlib import Path
import tempfile


def summary(state):
    rows = state.get('acceptance_report', [])
    counts = {key: sum(row.get('status') == key for row in rows)
              for key in ('passed', 'failed', 'pending', 'reviewed', 'reported')}
    if not state.get('done'):
        status = 'failed' if state.get('status') == 'stopped' else 'in_progress'
    elif counts['failed']:
        status = 'failed'
    elif not rows or counts['pending'] or counts['reviewed'] or counts['reported']:
        status = 'needs_manual_review'
    else:
        status = 'automated_checks_passed'
    return {'status': status, 'total': len(rows), **counts,
            'manual_review_required': sum(bool(r.get('manual_review_required')) for r in rows)}


def write_report(output, state):
    """No scripts or external resources; every model/task string is escaped."""
    output = Path(output)
    receipt = summary(state)
    rows = ''.join('<tr><td>{}</td><td>{}</td><td>{}</td><td>{}</td></tr>'.format(
        escape(str(r.get('id', ''))), escape(str(r.get('criterion', ''))),
        escape(str(r.get('status', 'pending'))), escape(str(r.get('host_exit_codes', []))))
        for r in state.get('acceptance_report', []))
    failure = escape(str(state.get('failure') or ''))
    memory = state.get('memory_status', {})
    memory_warning = escape(str(memory.get('warning') or ''))
    body = f'''<!doctype html><html lang="en"><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>OpenAS delivery receipt</title>
<style>body{{font:16px system-ui;max-width:1000px;margin:40px auto;padding:0 20px;color:#172033}}
table{{border-collapse:collapse;width:100%}}td,th{{padding:12px;border:1px solid #d7dce5;text-align:left}}
pre{{white-space:pre-wrap;overflow-wrap:anywhere}}.status{{background:#eef2ff;padding:16px;border-radius:8px}}
</style><h1>OpenAS delivery receipt</h1>
<p class="status">Acceptance: <strong>{escape(receipt['status'])}</strong><br>
Workflow: {escape(str(state.get('status', 'unknown')))} ·
Phase: {escape(str(state.get('next_phase', '')))}</p>
<p>Project memory: {'active' if memory.get('active') else 'disabled'}.
Automated checks cover only the criteria mapped to those checks. Review semantic/business requirements separately.</p>
<p>{memory_warning}</p>
<h2>Task</h2><pre>{escape(str(state.get('task', {}).get('requirement', '')))}</pre>
<h2>Acceptance</h2><table><tr><th>ID</th><th>Criterion</th><th>Status</th><th>Host exit codes</th></tr>{rows}</table>
<h2>Failure / blocker</h2><pre>{failure}</pre>
<p><a href="state.json">State</a> · <a href="acceptance.json">Acceptance evidence</a> ·
<a href="handoff.json">Handoff</a> · <a href="events.jsonl">Event timeline</a></p>
<p>Local receipt. Inspect source and logs before sharing; this report is not a native desktop E2E certificate.</p></html>'''
    fd, name = tempfile.mkstemp(prefix='.report-', dir=output)
    try:
        with os.fdopen(fd, 'w', encoding='utf-8') as stream:
            stream.write(body)
        os.replace(name, output/'report.html')
    finally:
        if os.path.exists(name):
            os.unlink(name)
