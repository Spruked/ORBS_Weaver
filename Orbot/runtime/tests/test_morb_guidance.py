import unittest
import tempfile
from pathlib import Path
from unittest.mock import patch
from fastapi.testclient import TestClient
from runtime.motion import service
from runtime.motion.morb_guidance import MorbGuidance


def frame():
    return {'x':100,'y':100,'orb_x':100,'orb_y':100,
            'monitors':[{'x':0,'y':0,'width':800,'height':600,'scale':1.0},
                        {'x':800,'y':0,'width':800,'height':600,'scale':1.25}]}

class GuidanceTests(unittest.TestCase):
    def test_independent_ids_move_and_pulse_near_targets(self):
        g=MorbGuidance(); ids={g.assign(500,300,now=0),g.assign(900,300,now=0)}
        seen_pulse=set(); previous={}
        for i in range(400):
            for e in g.step(frame(),now=i*.1):
                self.assertIn(e['id'],ids); self.assertEqual(e['color'],'blue')
                if e['state']=='pulse': seen_pulse.add(e['id']); previous[e['id']]=e
        self.assertEqual(seen_pulse,ids)
        self.assertEqual(previous[next(k for k in ids if previous[k]['target']['x']==500)]['x'],525)
        self.assertFalse(g.entities)

    def test_invalid_target_and_clear_remove_entities(self):
        g=MorbGuidance(); g.assign(-1,0,now=0)
        self.assertEqual(g.step(frame(),now=0),[])
        g.assign(300,300,now=1);g.clear();self.assertFalse(g.entities)

    def test_guidance_requires_existing_credential_and_active_presentation(self):
        with tempfile.TemporaryDirectory() as folder:
            token=Path(folder)/'token'; token.write_text('fixture')
            with patch.dict('os.environ', {'ORBOT_VAULT_TOKEN_FILE':str(token)}):
                client=TestClient(service.app)
                self.assertEqual(client.post('/presentation/morbs/assign',json={'x':100,'y':100}).status_code,401)
                with patch.object(service,'last_presentation_step',None):
                    self.assertEqual(client.post('/presentation/morbs/assign',json={'x':100,'y':100},headers={'Authorization':'Bearer fixture'}).status_code,409)
                service.morbs.clear()

    def test_disconnected_display_does_not_cross_gap(self):
        f=frame();f['monitors'][1]['x']=900
        g=MorbGuidance();g.assign(1000,300,now=0)
        for i in range(200):
            for e in g.step(f,now=i*.1): self.assertFalse(800 <= e['x'] < 900)

if __name__=='__main__': unittest.main()
