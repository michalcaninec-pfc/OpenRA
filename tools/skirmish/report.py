#!/usr/bin/env python3
"""Read local match JSONL, including an incomplete last line after a crash."""
import argparse
from collections import Counter, defaultdict
import json
import os
from pathlib import Path
import time

ROOT = Path(__file__).resolve().parents[2]
LOGS = ROOT / 'Support/SkirmishLogs'

def records(path):
    result = []
    if path.exists():
        for line in path.read_text(errors='replace').splitlines():
            try:
                result.append(json.loads(line))
            except (ValueError, TypeError):
                pass
    return result

def stamp(tick):
    seconds = int(tick) // 25
    return f'{seconds // 60:02d}:{seconds % 60:02d}'

def report_match(path, session_done=False):
    rows = records(path)
    start = next((r for r in rows if r['kind'] == 'match_start'), None)
    if not start:
        return ''
    snaps = [r for r in rows if r['kind'] == 'snapshot']
    ends = [r for r in rows if r['kind'] == 'match_end']
    last_tick = max(r.get('tick', 0) for r in rows)
    status = ends[-1]['data']['reason'] if ends else ('interrupted / no match_end' if session_done else 'running / no match_end yet')
    lines = [f"# {start['data']['map']}", '', f"Match `{start['match']}` · {stamp(last_tick)} game time · {status}", '',
             'Local diagnostic data includes both players and may reveal information hidden by fog. Times use 25 simulation ticks/second; wall-clock speed may differ.', '']
    bots = {p['id'] for p in start['data']['players'] if p.get('bot')}
    names = {p['id']: p['name'] for p in start['data']['players']}
    if snaps:
        lines += ['| Player | Cash + stored ore | Earned / spent (engine) | Army value | Unit kills / losses | Outcome |',
                  '|---|---:|---:|---:|---:|---|']
        for p in snaps[-1]['data']['players']:
            lines.append(f"| {names.get(p['id'], p['id'])} ({'AI' if p['id'] in bots else 'human'}) | {p['cash']} + {p['resources']} | {p['earned']} / {p['spent']} | {p['army_value']} | {p['killed']} / {p['lost']} | {p['outcome']} |")
        lines += ['', 'Final composition and production:', '']
        for p in snaps[-1]['data']['players']:
            counts = ', '.join(f'{k}×{v}' for k,v in sorted(p['counts'].items()) if k not in ('player','world'))
            queues = [f"{q['type']}: "+','.join(i['type']+(' [paused]' if i['paused'] else '') for i in q['items']) for q in p['queues'] if q['items']]
            lines += [f"- {p['id']}: {counts}", f"  Production: {'; '.join(queues) or 'empty'}"]
    alerts = set()
    economic_streak = defaultdict(int)
    idle_streak = defaultdict(int)
    motion = {}
    stuck = defaultdict(int)
    peak_idle = defaultdict(int)
    battles = defaultdict(list)
    for snap in snaps:
        data = snap['data']
        for p in data['players']:
            if p['id'] not in bots:
                continue
            empty = not any(q['items'] for q in p['queues'] if q['enabled'])
            economic_streak[p['id']] = economic_streak[p['id']]+1 if empty and (p['cash'] or 0)+(p['resources'] or 0)>=1000 else 0
            if economic_streak[p['id']]>=3:
                alerts.add(f"{p['id']}: >=1,000 available with empty enabled production queues for 3 snapshots; inspect economy/tech prerequisites.")
            troops = [a for a in data['actors'] if a['owner']==p['id'] and a['mobile'] and a['combat']]
            idle = sum(a['idle'] for a in troops)
            peak_idle[p['id']] = max(peak_idle[p['id']], idle)
            idle_streak[p['id']] = idle_streak[p['id']]+1 if len(troops)>=4 and idle>=len(troops)/2 else 0
            if idle_streak[p['id']]>=3:
                alerts.add(f"{p['id']}: at least half of a 4+ unit combat force idle across 3 snapshots; could be intentional guarding or a squad assignment issue.")
        for a in data['actors']:
            key = a['id']
            moving = any('Move' in label for label in a['activity'])
            stuck[key] = stuck[key]+1 if moving and motion.get(key)==a['cell'] else 0
            if stuck[key]>=3 and a['owner'] in bots:
                alerts.add(f"{a['owner']}: {a['type']} #{key} stayed at {a['cell']} across 4 samples while a Move activity was active; possible obstruction, not a proven pathfinding bug.")
            motion[key] = a['cell']
    ai = [r for r in rows if r['kind']=='ai_decision']
    reasons = Counter(r['data'].get('reason','') for r in ai if r['data'].get('event')=='candidate')
    for event in ai:
        d=event['data']
        if d.get('event')!='dispatch' or not d.get('units'):continue
        ids={int(i) for i in d['units'].split(',')}
        tx,ty=int(d['target_x']),int(d['target_y'])
        later=[r for r in snaps if event['tick']<r['tick']<=event['tick']+1000]
        arrived=set()
        for r in later:
            for a in r['data']['actors']:
                if a['id'] in ids and a['cell'] and (a['cell'][0]-tx)**2+(a['cell'][1]-ty)**2<=31:
                    arrived.add(a['id'])
        if later and later[-1]['tick']-event['tick']>=750 and not arrived:
            alerts.add(f"{stamp(event['tick'])} {d['player']} dispatched units {sorted(ids)} to {d['village']}, but none was observed inside its capture area within 30+ game seconds. Check casualties, pathing and native squad redirection.")
    payouts = Counter()
    timeline = []
    seen_tech = set()
    for r in rows:
        d=r['data']; kind=r['kind']; at=stamp(r['tick'])
        if kind=='actor_removed' and d.get('dead') and d.get('cell'):
            battles[(r['tick']//250,d['owner'])].append(d)
        if kind=='cheat_order':
            timeline.append(f"{at} CHEAT {d['player']}: {d['order']} (amount={d['amount']})")
        elif kind=='actor_added' and d['type'] in ('gunpowder.age','modern.age'):
            key=(d['owner'],d['type'])
            if key not in seen_tech:
                timeline.append(f"{at} TECHNOLOGY {d['owner']}: {d['type']}");seen_tech.add(key)
        elif kind=='ai_decision' and d.get('event')=='dispatch':
            timeline.append(f"{at} AI {d['player']} {d['action']} {d['village']}: {d['count']} troops (army={d['army']}, available={d['available']}, budget={d['budget']}, units={d.get('units','unrecorded')})")
        elif kind=='village_event' and d['event']=='capture':
            timeline.append(f"{at} VILLAGE {d['village']}: {d['owner']}")
        elif kind=='village_event' and d['event']=='payout':
            payouts[d['owner']]+=int(d['amount'])
    lines += ['', '## Diagnostic leads (heuristics, not conclusions)', '']
    lines += ['- '+s for s in sorted(alerts)] or ['- No sustained warning detected in available samples. A short or interrupted match may not contain enough data.']
    lines += [f"- Peak idle combat units: {dict(peak_idle)}", f"- Village AI candidate reasons: {dict(reasons)}", f"- Village income, recorded separately from engine Earned: {dict(payouts)}"]
    for (bucket,owner),losses in sorted(battles.items()):
        counts=Counter(a['type'] for a in losses)
        x=round(sum(a['cell'][0] for a in losses)/len(losses));y=round(sum(a['cell'][1] for a in losses)/len(losses))
        timeline.append(f"{stamp(bucket*250)} LOSSES {owner}: {dict(counts)} around cell ({x},{y})")
    timeline.sort(key=lambda line: tuple(map(int,line.split()[0].split(':'))))
    lines += ['', '## Timeline', ''] + ['- '+s for s in timeline]
    if not timeline:
        lines.append('- No tech, capture, dispatch or cheat events recorded yet.')
    errors=[r for r in rows if r['kind'] in ('telemetry_error','engine_error')]
    if errors:
        lines += ['', 'RECORDED ERRORS: '+str(errors)]
    lines += ['', 'Snapshots contain actor IDs, positions, health, current activity chains and exposed targets. Actor removal is not necessarily death (transport, capture or transformation can also remove actors). Sampling cannot prove every action between snapshots.', '']
    return '\n'.join(lines)

def write_reports(session):
    meta_path=session/'session.json'
    meta=json.loads(meta_path.read_text()) if meta_path.exists() else {}
    summaries=[]
    latest_result=''
    def started(path):
        rows=records(path)
        return next((r['data'].get('utc','') for r in rows if r['kind']=='match_start'),'')
    for path in sorted(session.glob('match-*.jsonl'),key=started):
        result=report_match(path, meta.get('status')=='finished')
        if result:
            target=path.with_suffix('.md');tmp=target.with_suffix(f'.{os.getpid()}.tmp');tmp.write_text(result);tmp.replace(target)
            summaries.append(f'- [{target.name}]({target.name})')
            latest_result=result
    text='# Skirmish session\n\n'+f"Revision: `{meta.get('revision','unknown')}` · status: {meta.get('status','unknown')} · exit code: {meta.get('exit_code','pending')}\n\n"+'\n'.join(summaries or ['No match telemetry received yet. See engine.log for launch errors.'])+'\n'
    if meta.get('launch_errors'):text+='\nLaunch errors: '+str(meta['launch_errors'])+'\n'
    tmp=session/f'report.{os.getpid()}.tmp';tmp.write_text(text);tmp.replace(session/'report.md')
    if session.parent.resolve()==LOGS.resolve():
        sessions=sorted(p for p in LOGS.iterdir() if p.is_dir())
        if sessions and session==sessions[-1]:
            latest=LOGS/f'latest.{os.getpid()}.tmp'
            latest.write_text(f'Session: [{session.name}]({session.name}/report.md)\n\n'+(latest_result or text))
            latest.replace(LOGS/'latest.md')

def main():
    parser=argparse.ArgumentParser();parser.add_argument('session',nargs='?');parser.add_argument('--latest',action='store_true');parser.add_argument('--follow',action='store_true');args=parser.parse_args()
    while True:
        if args.session:
            session=Path(args.session).resolve()
        else:
            dirs=sorted(p for p in LOGS.glob('*') if p.is_dir())
            if not dirs:
                print('No recorded skirmishes yet.');return
            session=dirs[-1]
        write_reports(session)
        print(session/'report.md',flush=True)
        if not args.follow:break
        time.sleep(5)
if __name__=='__main__':main()
