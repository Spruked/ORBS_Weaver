import os
import random
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from fastapi.testclient import TestClient
from runtime.motion.presentation import PresentationMotion, visible
from runtime.motion.service import app


def frame(x=800, y=300):
    return {'x':x,'y':y,'width':220,'height':210,'orb_x':110,'orb_y':100,'orb_radius':90,
            'cursor':{'x':50,'y':900},'interaction':False,
            'monitors':[{'x':0,'y':0,'width':1920,'height':1080,'scale':1.0},
                        {'x':1920,'y':0,'width':1920,'height':1080,'scale':1.0}]}


class PresentationMotionTests(unittest.TestCase):
    def test_autonomous_motion_crosses_adjacent_monitors_without_leaving_union(self):
        motion=PresentationMotion(random.Random(1));data=frame(x=1500);crossed=False;reached_interior=False
        for step in range(500):
            result=motion.step(data,now=100+step*.1)
            if result['state']=='gliding':
                data['x'],data['y']=result['x'],result['y']
                self.assertTrue(visible((data['x']+110,data['y']+105),data['monitors'],110,105))
                self.assertLessEqual((result['velocity']['x']**2+result['velocity']['y']**2)**.5,120.1)
                crossed |= data['x'] >= 1920
                reached_interior |= data['x'] >= 2300
        self.assertTrue(crossed)
        self.assertTrue(reached_interior)

    def test_nudge_uses_orb_boundary_and_holds_for_direct_click(self):
        motion=PresentationMotion(random.Random(1));data=frame()
        motion.step(data,now=100)
        data['cursor']={'x':data['x']+110-130,'y':data['y']+100}
        result=motion.step(data,now=100.1)
        self.assertGreater(result['nudge_speed'],0)
        self.assertLessEqual(result['nudge_speed'],60)
        data['cursor']={'x':data['x']+110,'y':data['y']+100}
        held=motion.step(data,now=100.2)
        self.assertEqual(held['state'],'interaction_hold')
        self.assertEqual((held['x'],held['y']),(data['x'],data['y']))

    def test_gaps_are_not_treated_as_adjacent_and_negative_coordinates_work(self):
        data=frame(x=-1200);data['monitors']=[{'x':-1920,'y':-100,'width':1920,'height':1080,'scale':1.25},
            {'x':200,'y':-100,'width':1920,'height':1080,'scale':1.0}]
        motion=PresentationMotion(random.Random(1))
        for step in range(150):
            result=motion.step(data,now=100+step*.1)
            if result['state']=='gliding':
                data['x'],data['y']=result['x'],result['y']
                self.assertLessEqual(data['x']+220,0)

    def test_geometry_change_recovers_window_to_a_visible_monitor(self):
        data=frame(x=-100,y=-40)
        data['cursor']={'x':1200,'y':900}
        result=PresentationMotion(random.Random(1)).step(data,now=100)
        self.assertEqual(result['state'],'recovering')
        self.assertTrue(visible((result['x']+110,result['y']+105),data['monitors'],110,105))

    def test_resume_after_idle_starts_with_bounded_acceleration(self):
        data=frame();motion=PresentationMotion(random.Random(1))
        for step in range(20):
            result=motion.step(data,now=100+step*.1)
            data['x'],data['y']=result['x'],result['y']
        resumed=motion.step(data,now=110)
        self.assertLessEqual((resumed['velocity']['x']**2+resumed['velocity']['y']**2)**.5,21.1)

    def test_explicit_hold_freezes_and_ambient_resumes(self):
        data=frame();motion=PresentationMotion(random.Random(1));motion.set_authority('hold')
        held=motion.step(data,now=100)
        self.assertEqual(held['state'],'hold')
        self.assertEqual((held['x'],held['y']),(data['x'],data['y']))
        motion.set_authority('ambient')
        moving=motion.step(data,now=100.1)
        self.assertEqual(moving['authority'],'ambient')
        self.assertIn(moving['state'],('gliding','interaction_hold'))

    def test_guided_target_moves_through_adjacent_monitor_and_gaze_is_independent(self):
        data=frame(x=1500);data['cursor']={'x':1800,'y':500}
        motion=PresentationMotion(random.Random(1));motion.set_authority('guided',(2050,420))
        results=[]
        for step in range(300):
            result=motion.step(data,now=100+step*.1);results.append(result)
            if result.get('x') is not None:data['x'],data['y']=result['x'],result['y']
            if result['state']=='guided_arrived':break
        self.assertTrue(any(r['state']=='gliding' and r['authority']=='guided' for r in results))
        self.assertTrue(any(r['x']>=1920 for r in results))
        self.assertTrue(all(r['authority']=='guided' for r in results))
        self.assertGreater(results[0]['gaze']['x'],0)

    def test_gaze_points_to_cursor_with_smooth_website_range(self):
        gaze=PresentationMotion._gaze(100,100,400,100)
        self.assertAlmostEqual(gaze['x'],1.0)
        self.assertAlmostEqual(gaze['y'],0.0)

    def test_only_existing_credential_can_request_visual_steps(self):
        with tempfile.TemporaryDirectory() as directory:
            token=Path(directory)/'token';token.write_text('fixture')
            with patch.dict(os.environ,{'ORBOT_VAULT_TOKEN_FILE':str(token)}):
                client=TestClient(app)
                self.assertEqual(client.post('/presentation/step',json=frame()).status_code,401)
                result=client.post('/presentation/step',json=frame(),headers={'Authorization':'Bearer fixture'})
                self.assertEqual(result.status_code,200)
                self.assertFalse(result.json()['execution_authority'])
                self.assertEqual(client.post('/commands',json={'permit_id':'invented'}).status_code,503)
                self.assertEqual(client.post('/presentation/authority',json={'authority':'hold'}).status_code,401)
                self.assertEqual(client.post('/presentation/authority',json={'authority':'hold'},headers={'Authorization':'Bearer fixture'}).status_code,200)
