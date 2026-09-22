#!/usr/bin/env python3
"""Launch the game and retain local diagnostic records for every world in this session."""
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import signal
import subprocess
import sys
from report import LOGS, ROOT, write_reports

def git(*args):
    return subprocess.run(['git',*args],cwd=ROOT,text=True,capture_output=True).stdout.strip()

def event_line(line, match):
    if not match:return None
    # Lua uses a deliberately small pipe-delimited diagnostic protocol.
    for prefix,kind in [('AGES_AI|','ai_decision'),('AGES_VILLAGE|','village_event')]:
        if prefix not in line:continue
        bits=line[line.index(prefix)+len(prefix):].strip().split('|')
        try:
            tick=int(bits[0]);data={}
            for part in bits[1:]:
                key,value=part.split('=',1);data[key]=value
            return dict(schema=1,match=match,tick=tick,kind=kind,data=data)
        except ValueError:return None
    return None

def main():
    args=sys.argv[1:]
    if not args:raise SystemExit('Usage: run.py command [args...]')
    session=LOGS/(datetime.now().strftime('%Y%m%d-%H%M%S-%f')+f'-{os.getpid()}')
    session.mkdir(parents=True)
    meta=dict(schema=1,started_utc=datetime.now(timezone.utc).isoformat(),status='running',command=args,revision=git('rev-parse','HEAD'),dirty=git('status','--short'))
    (session/'session.json').write_text(json.dumps(meta,indent=2))
    (session/'source.diff').write_text(git('diff','HEAD','--','mods/ages','OpenRA.Mods.Common','launch-ages.sh','tools/skirmish'))
    # Preserve the small, exact rule/script inputs as well as the compiled build identity.
    manifest={}
    for source in sorted((ROOT/'mods/ages').rglob('*')):
        if source.is_file() and source.suffix in ('.yaml','.lua','.ftl','.bin','.pal'):
            rel=source.relative_to(ROOT)
            manifest[str(rel)]=hashlib.sha256(source.read_bytes()).hexdigest()
            if source.suffix in ('.yaml','.lua','.ftl'):
                target=session/'source'/rel;target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(source.read_bytes())
    for name in ('OpenRA.Game.dll','OpenRA.Mods.Common.dll'):
        source=ROOT/'bin'/name
        if source.exists():manifest['bin/'+name]=hashlib.sha256(source.read_bytes()).hexdigest()
    (session/'source-manifest.json').write_text(json.dumps(manifest,indent=2))
    env=dict(os.environ,AGES_TELEMETRY='1')
    print(f'Skirmish logs: {session}',flush=True)
    child=None;active_match=None;files={};code=1;last_tick=0
    def forward(sig,_):
        if child and child.poll() is None:
            os.killpg(child.pid,sig)
    signal.signal(signal.SIGINT,forward);signal.signal(signal.SIGTERM,forward)
    try:
        with (session/'engine.log').open('w',buffering=1) as raw:
            child=subprocess.Popen(args,cwd=ROOT,env=env,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True,errors='replace',bufsize=1,start_new_session=True)
            for line in child.stdout:
                raw.write(line)
                record=None
                if line.startswith('AGES_TELEMETRY '):
                    try:
                        record=json.loads(line[len('AGES_TELEMETRY '):])
                        if record['kind']=='match_start':active_match=record['match']
                    except (ValueError,KeyError):pass
                else:
                    print(line,end='',flush=True)
                    record=event_line(line,active_match)
                    if 'Fatal Lua Error:' in line or 'Exception of type' in line:
                        if active_match:
                            record=dict(schema=1,match=active_match,tick=last_tick,kind='engine_error',data=dict(message=line.strip()))
                        else:
                            meta.setdefault('launch_errors',[]).append(line.strip())
                if record:
                    key=record['match']
                    last_tick=record['tick']
                    if key not in files:files[key]=(session/f'match-{key}.jsonl').open('a',buffering=1)
                    files[key].write(json.dumps(record,separators=(',',':'))+'\n')
                    if record['kind'] in ('match_start','snapshot','match_end','engine_error','telemetry_error'):
                        try:write_reports(session)
                        except Exception as error:
                            raw.write('REPORT ERROR: '+str(error)+'\n')
                    if record['kind']=='match_end':active_match=None
            code=child.wait()
    finally:
        for handle in files.values():handle.close()
        meta.update(status='finished',finished_utc=datetime.now(timezone.utc).isoformat(),exit_code=code)
        (session/'session.json').write_text(json.dumps(meta,indent=2));write_reports(session)
        print(f'Match report: {session / "report.md"}',flush=True)
    return code if code>=0 else 128-code
if __name__=='__main__':sys.exit(main())
