"""Transient visual guidance; this module does not perform desktop actions."""
import math
import threading
import time
import uuid

def covered_segment(start, end, monitors):
    """Reject any travel segment through gaps, even gaps narrower than a tick."""
    intervals=[]
    for m in monitors:
        low, high=0., 1.
        for origin, delta, a, b in ((start[0],end[0]-start[0],m['x'],m['x']+m['width']),
                                     (start[1],end[1]-start[1],m['y'],m['y']+m['height'])):
            if abs(delta)<1e-9:
                if not a <= origin <= b: low,high=1.,0.;break
            else:
                t1,t2=(a-origin)/delta,(b-origin)/delta
                low=max(low,min(t1,t2));high=min(high,max(t1,t2))
        if low<=high: intervals.append((low,high))
    cursor=0.
    for lo,hi in sorted(intervals):
        if lo>cursor+1e-9: return False
        cursor=max(cursor,hi)
    return cursor>=1.-1e-9

class MorbGuidance:
    def __init__(self):
        self.lock = threading.RLock()
        self.entities = {}

    def assign(self, x, y, now=None):
        """Queue an owner-supplied physical desktop coordinate, not a verified action."""
        with self.lock:
            if len(self.entities) >= 4:
                raise ValueError('All guidance presentations are occupied')
            identifier = uuid.uuid4().hex
            self.entities[identifier] = dict(id=identifier, target=(x, y), state='queued',
                created=time.monotonic() if now is None else now, position=None, velocity=(0., 0.), last=None)
            return identifier

    def clear(self):
        with self.lock:
            self.entities.clear()

    def step(self, frame, now=None):
        now = time.monotonic() if now is None else now
        with self.lock:
            results = []
            for key, e in list(self.entities.items()):
                monitors = frame['monitors']
                tx, ty = e['target']
                monitor = next((m for m in monitors if m['x'] <= tx < m['x']+m['width'] and m['y'] <= ty < m['y']+m['height']), None)
                if not monitor or now-e['created'] > 45:
                    del self.entities[key]; continue
                if e['position'] is None:
                    e['position'] = (frame['x']+frame['orb_x'], frame['y']+frame['orb_y'])
                    e['last'] = now
                # Offset from the specified point; the overlay itself never clicks.
                margin = 25 * monitor['scale']
                dx = max(monitor['x']+margin, min(monitor['x']+monitor['width']-margin, tx+margin))
                dy = max(monitor['y']+margin, min(monitor['y']+monitor['height']-margin, ty+margin))
                px, py = e['position']; distance = math.hypot(dx-px, dy-py)
                if e['state'] == 'queued': e['state'] = 'traveling'
                if e['state'] == 'traveling':
                    dt = max(0., min(.15, now-e['last']))
                    speed = min(280., distance*2.)
                    desired = ((dx-px)/max(distance, 1)*speed, (dy-py)/max(distance, 1)*speed)
                    alpha = 1-math.exp(-dt/.25)
                    vx, vy = e['velocity']
                    vx += (desired[0]-vx)*alpha; vy += (desired[1]-vy)*alpha
                    nx, ny = px+vx*dt, py+vy*dt
                    # Do not guide into gaps between displays.
                    if covered_segment((px,py),(nx,ny),monitors):
                        e['position']=(nx,ny); e['velocity']=(vx,vy)
                    else:
                        e['state']='blocked'; e['settled']=now
                    if distance < 3:
                        e['position']=(dx,dy); e['velocity']=(0.,0.); e['state']='pulse'; e['settled']=now
                elif e['state']=='pulse' and now-e['settled']>=1:
                    e['state']='holding'
                elif e['state'] in ('holding','blocked') and now-e['settled']>=3:
                    del self.entities[key];continue
                e['last']=now
                if e['state'] != 'blocked':
                    results.append({'id':key,'x':round(e['position'][0]),'y':round(e['position'][1]),
                                    'state':e['state'],'color':'blue','target':{'x':tx,'y':ty}})
            return results
