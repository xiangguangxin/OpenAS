#!/usr/bin/env python3
"""Evidence-backed project memory. JSON storage with atomic writes and portable process locking."""
import argparse
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path
import importlib.util

_SUPPORT_SPEC = importlib.util.spec_from_file_location("openas_runtime_support", Path(__file__).with_name("runtime_support.py"))
support = importlib.util.module_from_spec(_SUPPORT_SPEC)
_SUPPORT_SPEC.loader.exec_module(support)
import hashlib
import json
import re
import tempfile
import os


def now():
    return datetime.now(timezone.utc).isoformat()


def digest(data):
    return hashlib.sha256(data).hexdigest()


def pointer(doc, path):
    if path == '':
        return doc
    if not isinstance(path, str) or not path.startswith('/'):
        raise ValueError('Evidence must use a JSON pointer')
    for part in path[1:].split('/'):
        part = part.replace('~1', '/').replace('~0', '~')
        doc = doc[int(part)] if isinstance(doc, list) else doc[part]
    return doc


TRANSITIONS = {
    None: {'proposed': 'candidate'},
    'candidate': {'accepted': 'accepted', 'conflict': 'conflict', 'rejected': 'rejected', 'retired': 'retired'},
    'conflict': {'accepted': 'accepted', 'conflict': 'conflict', 'rejected': 'rejected', 'retired': 'retired'},
    'accepted': {'retired': 'retired'}, 'rejected': {'retired': 'retired'}, 'retired': {},
}


def relative_path(value):
    return (isinstance(value, str) and bool(value) and not Path(value).is_absolute()
            and '..' not in Path(value).parts and value != '.')


def validate_evidence(evidence):
    if not isinstance(evidence, list) or not evidence:
        raise ValueError('Nonempty evidence records required')
    for item in evidence:
        if (not isinstance(item, dict) or not {'path', 'sha256', 'pointer', 'value'} <= set(item)
                or not relative_path(item['path']) or not isinstance(item['sha256'], str)
                or not re.fullmatch(r'[0-9a-f]{64}', item['sha256'])
                or not isinstance(item['pointer'], str) or (item['pointer'] and not item['pointer'].startswith('/'))
                or re.search(r'~(?![01])', item['pointer'])):
            raise ValueError('Incomplete or invalid memory evidence')
        if 'sources' in item:
            if not isinstance(item['sources'], list) or not item['sources']:
                raise ValueError('Nonempty source dependencies required')
            for source in item['sources']:
                if (not isinstance(source, dict) or not relative_path(source.get('path'))
                        or not isinstance(source.get('sha256'), str) or not re.fullmatch(r'[0-9a-f]{64}', source['sha256'])):
                    raise ValueError('Invalid source dependency')
    json.dumps(evidence, allow_nan=False)


def validate_store(data):
    if (not isinstance(data, dict) or type(data.get('version')) is not int or data['version'] != 1
            or not isinstance(data.get('records'), list) or not isinstance(data.get('audit'), list)):
        raise ValueError('Invalid memory store; do not overwrite')
    records = {}
    for record in data['records']:
        if (not isinstance(record, dict) or not isinstance(record.get('id'), str)
                or not re.fullmatch(r'[0-9a-f]{20}', record['id']) or record['id'] in records
                or record.get('kind') not in ('fact', 'decision', 'lesson')
                or not isinstance(record.get('status'), str) or record['status'] not in TRANSITIONS
                or any(not isinstance(record.get(k), str) or not record[k].strip() for k in ('key', 'scope', 'statement', 'created', 'updated'))
                or not isinstance(record.get('tags'), list) or any(not isinstance(t, str) for t in record['tags'])):
            raise ValueError('Invalid memory record or duplicate ID')
        validate_evidence(record.get('evidence'))
        content = {key: record[key] for key in ('key', 'scope', 'kind', 'statement', 'tags', 'evidence')}
        if digest(json.dumps(content, sort_keys=True, ensure_ascii=False, allow_nan=False).encode())[:20] != record['id']:
            raise ValueError('Memory content changed without a new proposal ID')
        review = record.get('review')
        if record['status'] in ('accepted', 'conflict', 'rejected') and (
                not isinstance(review, dict) or any(not isinstance(review.get(k), str) or not review[k].strip()
                                                     for k in ('reviewer', 'reason', 'at'))
                or review.get('verdict') != ('reject' if record['status'] == 'rejected' else 'approve')):
            raise ValueError('Memory status lacks matching review evidence')
        records[record['id']] = record
    status = {}
    for event in data['audit']:
        if (not isinstance(event, dict) or not isinstance(event.get('id'), str) or event['id'] not in records
                or not isinstance(event.get('at'), str) or not event['at']):
            raise ValueError('Invalid memory audit reference')
        ident, name = event['id'], event.get('event')
        if not isinstance(name, str) or name not in TRANSITIONS[status.get(ident)]:
            raise ValueError('Illegal memory status transition')
        if name != 'proposed' and (not isinstance(event.get('reason'), str) or not event['reason'].strip()):
            raise ValueError('Memory transition lacks an audit reason')
        status[ident] = TRANSITIONS[status.get(ident)][name]
    if any(status.get(ident) != record['status'] for ident, record in records.items()):
        raise ValueError('Memory status does not match lifecycle audit')
    json.dumps(data, allow_nan=False)
    return {'records': len(records), 'audit_events': len(data['audit'])}


class Memory:
    def __init__(self, root, directory=None):
        self.root = Path(root).resolve()
        candidate = Path(directory).absolute() if directory else self.root/'.openas/memory'
        if any(p.is_symlink() for p in (candidate, *candidate.parents)):
            raise ValueError('Memory directory must not traverse symlinks')
        self.directory = Path(directory).resolve() if directory else (self.root/'.openas/memory').resolve()
        if not self.root.is_dir():
            raise ValueError('Consumer project root must be an existing directory')
        for location in (self.root, self.directory):
            if any((parent/'.claude-plugin/plugin.json').is_file() for parent in (location, *location.parents)):
                raise ValueError('Memory belongs to the consumer project, not the plugin directory')
        self.file = self.directory/'records.json'

    @contextmanager
    def transaction(self):
        self.directory.mkdir(parents=True, exist_ok=True)
        with (self.directory/'.lock').open('a+', encoding='utf-8') as lock, support.locked(lock):
            data = self.read()
            yield data
            validate_store(data)
            self.atomic(self.file, data)

    def read(self):
        if not self.file.exists():
            return {'version':1, 'records':[], 'audit':[]}
        data = json.loads(self.file.read_text(encoding='utf-8'))
        validate_store(data)
        return data

    @staticmethod
    def atomic(path, data):
        path.parent.mkdir(parents=True, exist_ok=True)
        fd, name = tempfile.mkstemp(dir=path.parent, prefix='.memory-')
        try:
            with os.fdopen(fd, 'w', encoding='utf-8') as f:
                json.dump(data,f,ensure_ascii=False,indent=2,allow_nan=False)
                f.write('\n'); f.flush(); os.fsync(f.fileno())
            os.replace(name,path)
        finally:
            if os.path.exists(name): os.unlink(name)

    def source(self, relative):
        p = (self.root/relative).resolve()
        if Path(relative).is_absolute() or p == self.root or self.root not in p.parents:
            raise ValueError('Evidence must be a project-relative file')
        return p

    def evidence(self, relative, at, sources=None):
        p = self.source(relative)
        raw=p.read_bytes()
        result = {'path':relative,'sha256':digest(raw),'pointer':at,'value':pointer(json.loads(raw),at)}
        if sources is not None:
            if not isinstance(sources, list) or not sources or any(not isinstance(s, str) or not s for s in sources):
                raise ValueError('sources must be a nonempty list of project-relative files')
            result['sources'] = [{'path': s, 'sha256': digest(self.source(s).read_bytes())} for s in sources]
        return result

    def valid(self, record):
        try:
            validate_evidence(record['evidence'])
            return bool(record['evidence']) and all(
                json.dumps(self.evidence(e['path'], e['pointer'],
                              sources=[s['path'] for s in e['sources']] if 'sources' in e else None), sort_keys=True, allow_nan=False)
                == json.dumps(e, sort_keys=True, allow_nan=False)
                for e in record['evidence'])
        except (OSError,ValueError,KeyError,TypeError,IndexError):
            return False

    def propose(self, key, kind, statement, tags, evidence, scope='project'):
        if kind not in ('fact','decision','lesson') or not all(isinstance(x,str) and x.strip() for x in (key,statement,scope)):
            raise ValueError('Valid key, scope, kind and statement required')
        if len(statement)>2000 or not evidence or not isinstance(tags,list) or any(not isinstance(t,str) for t in tags):
            raise ValueError('Bounded statement, tags and evidence required')
        r={'key':key,'scope':scope,'kind':kind,'statement':statement,'tags':tags,'evidence':evidence}
        if not self.valid(r): raise ValueError('Missing, changed or mismatched evidence')
        ident=digest(json.dumps(r,sort_keys=True,ensure_ascii=False).encode())[:20]
        with self.transaction() as data:
            existing=next((x for x in data['records'] if x['id']==ident),None)
            if existing:return existing
            r.update(id=ident,status='candidate',created=now(),updated=now(),review=None)
            data['records'].append(r)
            data['audit'].append({'at':now(),'id':ident,'event':'proposed'})
        return r

    def review(self, ident, verdict, reviewer, reason):
        if verdict not in ('approve','reject') or not reviewer.strip() or not reason.strip():
            raise ValueError('Review requires verdict, reviewer and reason')
        with self.transaction() as data:
            r=next(x for x in data['records'] if x['id']==ident)
            if r['status'] not in ('candidate','conflict'):raise ValueError('Only candidates/conflicts can be reviewed')
            if not self.valid(r):raise ValueError('Evidence is stale or missing')
            conflicts=[x for x in data['records'] if x['status']=='accepted' and x['scope']==r['scope'] and x['key']==r['key'] and x['id']!=ident]
            r['status']='rejected' if verdict=='reject' else ('conflict' if conflicts else 'accepted')
            r['review']={'reviewer':reviewer,'reason':reason,'verdict':verdict,'at':now()}
            r['updated']=now()
            data['audit'].append({'at':now(),'id':ident,'event':r['status'],'reason':reason})
        return r

    def retire(self, ident, reason):
        if not reason.strip():raise ValueError('Retirement reason required')
        with self.transaction() as data:
            r=next(x for x in data['records'] if x['id']==ident)
            if r['status'] == 'retired': return r
            r.update(status='retired',updated=now())
            data['audit'].append({'at':now(),'id':ident,'event':'retired','reason':reason})
        return r

    def query(self, query, limit=5, budget=5000):
        if not query.strip() or limit<1 or budget<1:return []
        tokens=set(re.findall(r'[a-z0-9_-]+|[\u4e00-\u9fff]',query.lower()))
        matches=[]
        for r in self.read()['records']:
            if r['status']!='accepted' or not self.valid(r):continue
            hay=(r['key']+' '+r['statement']+' '+' '.join(r['tags'])).lower()
            score=sum(t in hay for t in tokens)
            if score:matches.append((score,r['updated'],r))
        chosen=[];size=0
        for _,_,r in sorted(matches,key=lambda x:(x[0],x[1]),reverse=True):
            item={k:r[k] for k in ('id','kind','statement','evidence','review')}
            encoded=json.dumps(item,ensure_ascii=False)
            if size+len(encoded)>budget:continue
            chosen.append(item);size+=len(encoded)
            if len(chosen)>=limit:break
        return chosen

    def inspect(self):
        return [{**r,'evidence_valid':self.valid(r)} for r in self.read()['records']]

    def harvest(self, run):
        # Only canonical host fields create automatic facts. No prose is promoted here.
        if run.get('done') is not True or run.get('status')!='verified':
            raise ValueError('Only verified runs can be harvested')
        checks=run.get('final_checks')
        if not checks or any(not isinstance(c,dict) or c.get('exit_code')!=0 for c in checks):
            raise ValueError('Verified run lacks successful host checks')
        receipt={'done':True,'status':'verified','final_exit_codes':[c['exit_code'] for c in checks],
                 'initial_snapshot':run.get('initial_snapshot',{}),'final_snapshot':run.get('final_snapshot',{}),
                 'phase_verdicts':[{ 'phase':x.get('phase'), 'verdict':x.get('result',{}).get('verdict')} for x in run.get('history',run.get('phases',[]))]}
        raw=json.dumps(receipt,sort_keys=True,ensure_ascii=False).encode();rid=digest(raw)[:20]
        path=self.directory/'evidence'/f'{rid}.json'
        self.atomic(path,receipt)
        relative=str(path.relative_to(self.root))
        r=self.propose('run/'+rid,'fact',f'运行记录 {rid}：宿主记录为 verified；{len(checks)} 条最终验收命令退出码均为 0。仅适用于该次记录，不代表所有任务正确。',
                       ['harness','verified','验收'],[self.evidence(relative,'/status'),self.evidence(relative,'/final_exit_codes')])
        if r['status']=='candidate':r=self.review(r['id'],'approve','host-field-validator','Statement is generated only from verified host status and exit-code fields; no semantic claims inferred.')
        return r

    def checkpoint(self, run):
        item={'updated':now(),'status':run.get('status'),'done':run.get('done',False),
              'task_scope':run.get('task',{}).get('scope',[]),
              'requirement_sha256':digest(run.get('task',{}).get('requirement','').encode()),
              'completed_phases':[x.get('phase') for x in run.get('history',[]) if x.get('status')=='completed'],
              'error':run.get('error'), 'next_step':'inspect evidence; no automatic resume'}
        self.atomic(self.directory/'current-task.json',item)
        return item


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--root',type=Path,required=True,help='Consumer project root; never the plugin directory')
    sub=p.add_subparsers(dest='command',required=True)
    a=sub.add_parser('query');a.add_argument('text')
    sub.add_parser('inspect')
    a=sub.add_parser('harvest');a.add_argument('run',type=Path)
    a=sub.add_parser('propose');a.add_argument('proposal',type=Path)
    a=sub.add_parser('review');a.add_argument('id');a.add_argument('--verdict',choices=['approve','reject'],required=True);a.add_argument('--reviewer',required=True);a.add_argument('--reason',required=True)
    a=sub.add_parser('retire');a.add_argument('id');a.add_argument('--reason',required=True)
    args=p.parse_args();m=Memory(args.root)
    if args.command=='query':result=m.query(args.text)
    elif args.command=='inspect':result=m.inspect()
    elif args.command=='harvest':result=m.harvest(json.loads(args.run.read_text(encoding='utf-8')))
    elif args.command=='propose':result=m.propose(**json.loads(args.proposal.read_text(encoding='utf-8')))
    elif args.command=='review':result=m.review(args.id,args.verdict,args.reviewer,args.reason)
    else:result=m.retire(args.id,args.reason)
    print(json.dumps(result,ensure_ascii=False,indent=2))


if __name__=='__main__':main()
