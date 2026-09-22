import json
from pathlib import Path
import tempfile
import unittest
from report import records, report_match, write_reports
from run import event_line

class Reports(unittest.TestCase):
    def test_truncated_tail_keeps_complete_events(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'events.jsonl';p.write_text('{"kind":"one"}\n{"partial"')
            self.assertEqual(records(p),[{'kind':'one'}])

    def test_structured_lua_is_bound_to_active_match_only(self):
        line='Lua debug: AGES_AI|375|event=candidate|reason=cooldown|player=Multi1'
        self.assertIsNone(event_line(line,None))
        r=event_line(line,'abc')
        self.assertEqual(r['match'],'abc');self.assertEqual(r['tick'],375)
        self.assertEqual(r['data']['reason'],'cooldown')
        self.assertIsNone(event_line('AGES_AI|invalid','abc'))

    def test_multiple_matches_and_interrupted_session(self):
        with tempfile.TemporaryDirectory() as d:
            session=Path(d);(session/'session.json').write_text('{"status":"finished"}')
            for ident in ('one','two'):
                start=dict(schema=1,match=ident,tick=0,kind='match_start',data=dict(map=ident,players=[]))
                rows=[start]
                if ident=='one':rows.append(dict(match=ident,tick=250,kind='match_end',data=dict(reason='game_over')))
                (session/f'match-{ident}.jsonl').write_text('\n'.join(map(json.dumps,rows)))
            write_reports(session)
            self.assertIn('game_over',(session/'match-one.md').read_text())
            self.assertIn('interrupted',(session/'match-two.md').read_text())
            self.assertIn('match-one.md',(session/'report.md').read_text())
            self.assertIn('match-two.md',(session/'report.md').read_text())

    def test_battle_and_cash_cheat_are_reported(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'match.jsonl'
            rows=[dict(match='x',tick=0,kind='match_start',data=dict(map='Test',players=[])),
                  dict(match='x',tick=275,kind='actor_removed',data=dict(dead=True,type='pikeman',owner='Multi1',cell=[12,13])),
                  dict(match='x',tick=280,kind='cheat_order',data=dict(player='Multi0',order='DevGiveCash',amount=5000))]
            p.write_text('\n'.join(map(json.dumps,rows)))
            text=report_match(p)
            self.assertIn('LOSSES Multi1',text);self.assertIn('CHEAT Multi0',text)

    def test_dispatch_warning_distinguishes_observed_arrival(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'match.jsonl'
            rows=[dict(match='x',tick=0,kind='match_start',data=dict(map='Test',players=[])),
                  dict(match='x',tick=25,kind='ai_decision',data=dict(event='dispatch',player='Multi1',
                       village='Eastmere',action='capture',count='1',army='2',available='2',budget='1',
                       units='42',target_x='50',target_y='50')),
                  dict(match='x',tick=1000,kind='snapshot',data=dict(players=[],actors=[
                       dict(id=42,type='pikeman',owner='Multi1',cell=[1,1],activity=[])]))]
            p.write_text('\n'.join(map(json.dumps,rows)))
            self.assertIn('none was observed inside',report_match(p))
            rows[-1]['data']['actors'][0]['cell']=[50,50]
            p.write_text('\n'.join(map(json.dumps,rows)))
            self.assertNotIn('none was observed inside',report_match(p))

if __name__=='__main__':unittest.main()
