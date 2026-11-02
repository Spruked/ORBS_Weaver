"""Bounded, presentation-only desktop gliding in physical screen pixels.

MotionRuntime selects and integrates targets. The native host is the only
programmatic window-position writer. No desktop action or permit is issued.
"""
from __future__ import annotations
import math
import random
import time
from threading import RLock


def clamp(x, lo, hi):
    return min(hi, max(lo, x))


def inside(point, rect):
    x,y=point; left,top,right,bottom=rect
    return left-0.01 <= x <= right+0.01 and top-0.01 <= y <= bottom+0.01


def safe_rectangle(m, halfw, halfh):
    return (m['x']+halfw, m['y']+halfh, m['x']+m['width']-halfw, m['y']+m['height']-halfh)


def crossing(a,b,halfw,halfh):
    # Adjacent displays share an edge; reject corners, gaps, and narrow joins.
    al,at,ar,ab=a['x'],a['y'],a['x']+a['width'],a['y']+a['height']
    bl,bt,br,bb=b['x'],b['y'],b['x']+b['width'],b['y']+b['height']
    if ar == bl or br == al:
        low=max(at,bt)+halfh; high=min(ab,bb)-halfh
        if low>high:return None
        edge=ar if ar==bl else al; sign=1 if ar==bl else -1
        return ('x',edge,sign,low,high,halfw)
    if ab == bt or bb == at:
        low=max(al,bl)+halfw; high=min(ar,br)-halfw
        if low>high:return None
        edge=ab if ab==bt else at; sign=1 if ab==bt else -1
        return ('y',edge,sign,low,high,halfh)
    return None


def visible(center, monitors, halfw, halfh):
    if any(inside(center,safe_rectangle(m,halfw,halfh)) for m in monitors):return True
    for i,a in enumerate(monitors):
        for b in monitors[i+1:]:
            join=crossing(a,b,halfw,halfh)
            if not join:continue
            axis,edge,_,low,high,half=join
            along,across=(center[0],center[1]) if axis=='x' else (center[1],center[0])
            if edge-half <= along <= edge+half and low <= across <= high:return True
    return False


def segment_hits_rect(start, end, rect):
    """Liang-Barsky segment/rectangle intersection for work-area clearance."""
    left, top, right, bottom = rect
    x0, y0 = start
    dx, dy = end[0]-x0, end[1]-y0
    low, high = 0.0, 1.0
    for p, q in ((-dx, x0-left), (dx, right-x0), (-dy, y0-top), (dy, bottom-y0)):
        if abs(p) < 1e-9:
            if q < 0:
                return False
            continue
        ratio = q/p
        if p < 0:
            if ratio > high: return False
            low = max(low, ratio)
        else:
            if ratio < low: return False
            high = min(high, ratio)
    return low <= high


def work_route(start, end, rect):
    """Return a shortest clear polyline around a foreground-work rectangle."""
    if not segment_hits_rect(start, end, rect):
        return [end]
    left, top, right, bottom = rect
    margin = 8.0
    nodes = [start, (left-margin, top-margin), (right+margin, top-margin),
             (right+margin, bottom+margin), (left-margin, bottom+margin), end]
    goal = len(nodes)-1
    distances = [math.inf]*len(nodes)
    previous = [None]*len(nodes)
    pending = set(range(len(nodes)))
    distances[0] = 0.0
    while pending:
        current = min(pending, key=lambda index: distances[index])
        pending.remove(current)
        if current == goal or not math.isfinite(distances[current]):
            break
        for neighbor, point in enumerate(nodes):
            if neighbor not in pending or neighbor == current:
                continue
            if segment_hits_rect(nodes[current], point, rect):
                continue
            distance = distances[current] + math.dist(nodes[current], point)
            if distance < distances[neighbor]:
                distances[neighbor] = distance
                previous[neighbor] = current
                pending.add(neighbor)
    if not math.isfinite(distances[goal]):
        return None
    path = []
    current = goal
    while current != 0:
        path.append(nodes[current])
        current = previous[current]
        if current is None:
            return None
    path.reverse()
    return path


class PresentationMotion:
    def __init__(self, rng=None):
        self.lock=RLock(); self.rng=rng or random.Random(); self.reset()
    def reset(self):
        self.position=None; self.velocity=[0.,0.]; self.waypoints=[]; self.last_time=None
        self.last_cursor=None; self.release_at=0.; self.signature=None; self.visits=0
        self.previous_monitor=None; self.destination_monitor=None; self.authority='ambient'; self.guided_target=None
        self.work_targets=[]; self.work_rect=None; self.work_pad=0.; self.work_monitor=None
        self.work_index=-1; self.work_laps=0
        self.last_result={'state':'waiting_for_embodiment'}
    def set_authority(self, authority, target=None):
        if authority not in ('ambient','hold','guided'):
            raise ValueError('Unknown presentation state')
        if authority=='guided' and (not isinstance(target, (tuple, list)) or len(target)!=2
                                    or not all(isinstance(v, (int,float)) and math.isfinite(v) for v in target)):
            raise ValueError('Guided positioning requires a finite desktop coordinate')
        with self.lock:
            self.authority=authority
            self.guided_target=tuple(map(float,target)) if authority=='guided' else None
            self.velocity=[0.,0.]
            self.waypoints=[]
            if authority=='ambient': self.release_at=0.
    def set_work_path(self, rect, pad, targets, preferred_monitor):
        # Window rectangles fluctuate by a few physical pixels while Windows
        # animates/focuses. Avoid resetting the patrol waypoint for that noise.
        signature=(tuple(round(v/24) for v in rect), round(float(pad)/12),
                   tuple((round(t['x']/24),round(t['y']/24),t['monitor']) for t in targets), preferred_monitor)
        with self.lock:
            old=(tuple(round(v/24) for v in self.work_rect) if self.work_rect else None,
                 round(self.work_pad/12),tuple((round(t[0]/24),round(t[1]/24),t[2]) for t in self.work_targets),self.work_monitor)
            if old == signature:
                return
            previous_index=self.work_index
            self.work_rect=tuple(map(float,rect));self.work_pad=float(pad)
            self.work_targets=[(float(t['x']),float(t['y']),int(t['monitor'])) for t in targets]
            self.work_monitor=preferred_monitor
            self.work_index=previous_index if previous_index < len(self.work_targets) else -1
            self.waypoints=[]
    def clear_work_path(self):
        with self.lock:
            self.work_targets=[];self.work_rect=None;self.work_pad=0.;self.work_monitor=None
            self.work_index=-1;self.waypoints=[]
    def _monitor(self,p,monitors):
        for i,m in enumerate(monitors):
            if inside(p,(m['x'],m['y'],m['x']+m['width'],m['y']+m['height'])):return i
        return min(range(len(monitors)),key=lambda i:(p[0]-(monitors[i]['x']+monitors[i]['width']/2))**2+(p[1]-(monitors[i]['y']+monitors[i]['height']/2))**2)
    def _choose(self, p, monitors, halfw, halfh):
        idx=self._monitor(p,monitors);m=monitors[idx]
        local=[(i,target) for i,target in enumerate(self.work_targets) if target[2]==idx]
        if local:
            ordered=sorted(local,key=lambda item:item[0])
            if self.work_index < 0:
                start=min(range(len(ordered)),key=lambda n:math.dist(p,ordered[n][1][:2]))
            else:
                start=next((n for n,(i,_) in enumerate(ordered) if i>self.work_index),0)
            clear_rect=None
            if self.work_rect:
                l,t,r,b=self.work_rect;pad=self.work_pad
                clear_rect=(l-pad,t-pad,r+pad,b+pad)
            chosen=None
            for offset in range(len(ordered)):
                i,target=ordered[(start+offset)%len(ordered)]
                candidate=target[:2]
                if math.dist(p,candidate)<80: continue
                route=work_route(p,candidate,clear_rect) if clear_rect else [candidate]
                if route:
                    chosen=(i,target,route);break
            if chosen is None and self.work_rect:
                l,t,r,b=self.work_rect;pad=self.work_pad
                # If a foreground window moved over the Orb, take the shortest
                # clear exit; otherwise stay on this work monitor's safe lane.
                if l-pad <= p[0] <= r+pad and t-pad <= p[1] <= b+pad:
                    i,target=min(local,key=lambda item:math.dist(p,item[1][:2]))
                    chosen=(i,target,[target[:2]])
            if chosen is not None:
                i,target,route=chosen
                if self.work_index>=0 and i<=self.work_index: self.work_laps+=1
                self.work_index=i;self.waypoints=route;self.destination_monitor=idx
                return
        candidates=[(j,crossing(m,n,halfw,halfh)) for j,n in enumerate(monitors) if j!=idx]
        candidates=[(j,c) for j,c in candidates if c]
        # Visit adjacent monitors; alternate after each arrival. Other choices
        # are random within reachable physical desktop space.
        if candidates:
            j,join=candidates[self.rng.randrange(len(candidates))]
            axis,edge,sign,low,high,half=join
            coord=clamp(p[1] if axis=='x' else p[0],low+min(40,(high-low)/4),high-min(40,(high-low)/4))
            near=edge-sign*(half+20);far=edge+sign*(half+45)
            left,top,right,bottom=safe_rectangle(monitors[j],halfw,halfh)
            inset=min(80,max(0,(right-left)/4),max(0,(bottom-top)/4))
            interior=(self.rng.uniform(left+inset,right-inset),self.rng.uniform(top+inset,bottom-inset))
            if axis=='x':self.waypoints=[(near,coord),(far,coord),interior]
            else:self.waypoints=[(coord,near),(coord,far),interior]
            self.destination_monitor=j
        else:
            left,top,right,bottom=safe_rectangle(m,halfw,halfh)
            inset=min(80,max(0,(right-left)/4),max(0,(bottom-top)/4))
            self.waypoints=[(self.rng.uniform(left+inset,right-inset),self.rng.uniform(top+inset,bottom-inset))]
            self.destination_monitor=idx
    def step(self, data, now=None):
        with self.lock:
            now=time.monotonic() if now is None else now
            ms=data['monitors'];w=data['width'];h=data['height'];halfw=w/2;halfh=h/2
            if not ms or any(m['width']<w or m['height']<h for m in ms):
                self.reset();return {'state':'blocked','reason':'Display is too small for the window','execution_authority':False}
            p=(data['x']+halfw,data['y']+halfh)
            signature=tuple((m['x'],m['y'],m['width'],m['height']) for m in ms)
            if signature != self.signature or self.position is None:
                self.position=list(p);self.velocity=[0.,0.];self.waypoints=[];self.signature=signature;self.last_time=now
            elapsed=now-(self.last_time if self.last_time is not None else now)
            if elapsed>0.5:self.velocity=[0.,0.];self.waypoints=[]
            dt=clamp(elapsed,0.01,0.15);self.last_time=now
            if math.hypot(p[0]-self.position[0],p[1]-self.position[1])>2:
                self.position=list(p);self.velocity=[0.,0.];self.waypoints=[]
            cur=data['cursor'];cx=data['x']+data['orb_x'];cy=data['y']+data['orb_y'];radius=data['orb_radius']
            dx=cx-cur['x'];dy=cy-cur['y'];distance=math.hypot(dx,dy);gap=max(0.,distance-radius)
            cursor_speed=0.
            if self.last_cursor:
                old=math.hypot(cx-self.last_cursor[0],cy-self.last_cursor[1]);cursor_speed=(old-distance)/dt
            self.last_cursor=(cur['x'],cur['y'])
            # Hold the orb still while it can be clicked or dragged.
            interacting=data['interaction'] or (gap<=14 and self.authority!='guided')
            if interacting:
                self.release_at=now+1.;self.velocity=[0.,0.];self.waypoints=[]
            if interacting or now<self.release_at:
                self.last_result={'state':'interaction_hold','x':data['x'],'y':data['y'],'execution_authority':False}
                return self.last_result
            if self.authority=='hold':
                self.last_result={'state':'hold','authority':'hold','x':data['x'],'y':data['y'],
                    'gaze':self._gaze(cx,cy,cur['x'],cur['y']),'execution_authority':False}
                return self.last_result
            if not visible(self.position,ms,halfw,halfh):
                # Display scale/layout may change after an owner drag or hotplug.
                # Recover through the same native writer, never an off-screen path.
                regions=[safe_rectangle(m,halfw,halfh) for m in ms]
                options=[(clamp(self.position[0],r[0],r[2]),clamp(self.position[1],r[1],r[3])) for r in regions]
                nearest=min(options,key=lambda p:(p[0]-self.position[0])**2+(p[1]-self.position[1])**2)
                self.position=list(nearest);self.velocity=[0.,0.];self.waypoints=[]
                self.last_result={'state':'recovering','x':round(nearest[0]-halfw),'y':round(nearest[1]-halfh),
                    'writer':'orbot_native_host','execution_authority':False}
                return self.last_result
            if self.authority=='guided' and self.guided_target:
                target_monitor=self._monitor(self.guided_target,ms)
                current_monitor=self._monitor(self.position,ms)
                self.destination_monitor=target_monitor
                if current_monitor!=target_monitor:
                    target_rect=safe_rectangle(ms[target_monitor],halfw,halfh)
                    goal=(clamp(self.guided_target[0],target_rect[0],target_rect[2]),
                          clamp(self.guided_target[1],target_rect[1],target_rect[3]))
                    if not self.waypoints:
                        frontier=[(current_monitor,[])];seen={current_monitor};route=None
                        while frontier and route is None:
                            index,path=frontier.pop(0)
                            for neighbor,monitor in enumerate(ms):
                                if neighbor not in seen and crossing(ms[index],monitor,halfw,halfh):
                                    next_path=path+[neighbor]
                                    if neighbor==target_monitor:route=next_path;break
                                    seen.add(neighbor);frontier.append((neighbor,next_path))
                        next_monitor=route[0] if route else None
                        join=crossing(ms[current_monitor],ms[next_monitor],halfw,halfh) if next_monitor is not None else None
                        if join:
                            axis,edge,sign,low,high,half=join
                            coord=clamp(goal[1] if axis=='x' else goal[0],low+min(40,(high-low)/4),high-min(40,(high-low)/4))
                            near=edge-sign*(half+20);far=edge+sign*(half+45)
                            if next_monitor==target_monitor:step_goal=goal
                            else:
                                rect=safe_rectangle(ms[next_monitor],halfw,halfh)
                                step_goal=(clamp(goal[0],rect[0],rect[2]),clamp(goal[1],rect[1],rect[3]))
                            self.waypoints=[(near,coord),(far,coord),step_goal] if axis=='x' else [(coord,near),(coord,far),step_goal]
                        else:
                            self.last_result={'state':'guided_blocked','authority':'guided','x':data['x'],'y':data['y'],
                                'reason':'Target display is not directly adjacent','execution_authority':False}
                            return self.last_result
                    target=self.waypoints[0]
                else:
                    self.waypoints=[(clamp(self.guided_target[0],*safe_rectangle(ms[target_monitor],halfw,halfh)[::2]),
                                     clamp(self.guided_target[1],safe_rectangle(ms[target_monitor],halfw,halfh)[1],safe_rectangle(ms[target_monitor],halfw,halfh)[3]))]
                    target=self.waypoints[0]
            elif not self.waypoints:self._choose(self.position,ms,halfw,halfh)
            while len(self.waypoints)>1 and math.hypot(self.waypoints[0][0]-self.position[0],self.waypoints[0][1]-self.position[1])<8:
                self.waypoints.pop(0)
            target=self.waypoints[0];vx=target[0]-self.position[0];vy=target[1]-self.position[1];d=math.hypot(vx,vy)
            if d<5:
                if self.authority=='guided' and self.guided_target:
                    arrived=self._monitor(self.position,ms)==self._monitor(self.guided_target,ms)
                    self.position=list(target);self.velocity=[0.,0.];self.waypoints=[]
                    self.last_result={'state':'guided_arrived' if arrived else 'guided_waypoint_arrived','authority':'guided','x':round(target[0]-halfw),'y':round(target[1]-halfh),
                        'gaze':self._gaze(cx,cy,cur['x'],cur['y']),'execution_authority':False}
                    return self.last_result
                self.waypoints=[]; self.visits+=1; self._choose(self.position,ms,halfw,halfh);target=self.waypoints[0];vx=target[0]-self.position[0];vy=target[1]-self.position[1];d=math.hypot(vx,vy)
            speed=min(220. if self.authority=='guided' else 85.,d*(1.5 if self.authority=='guided' else 1.2))
            if self.authority=='ambient' and d>=5: speed=max(10.,speed)
            desired=[vx/max(d,1)*speed,vy/max(d,1)*speed]
            nudge=0.
            if 14<gap<170 and distance>0:
                strength=clamp((170-gap)/(170-60),0,1)
                nudge=60*strength*clamp(max(0,cursor_speed)/80+0.2,0,1)
                if self.authority=='guided': nudge*=0.25
                desired[0]+=dx/distance*nudge;desired[1]+=dy/distance*nudge
            vmag=math.hypot(*desired)
            speed_cap=220. if self.authority=='guided' else 85.
            if vmag>speed_cap:desired=[v*speed_cap/vmag for v in desired]
            # Adapt FieldMotion's acceleration cap and damping to elapsed time,
            # with the website's exponential velocity smoothing.
            alpha=1-math.exp(-dt/(0.24 if self.authority=='guided' else 0.45))
            dv=[(desired[i]-self.velocity[i])*alpha for i in (0,1)];dm=math.hypot(*dv);limit=(120 if self.authority=='guided' else 90)*dt
            if dm>limit:dv=[v*limit/dm for v in dv]
            self.velocity=[self.velocity[i]+dv[i] for i in (0,1)]
            proposed=[self.position[i]+self.velocity[i]*dt for i in (0,1)]
            if not visible(proposed,ms,halfw,halfh):
                self.velocity=[0.,0.];self.waypoints=[];proposed=self.position[:]
            self.position=proposed;mon=self._monitor(self.position,ms)
            self.last_result={'state':'gliding','authority':self.authority,'x':round(proposed[0]-halfw),'y':round(proposed[1]-halfh),
                'velocity':{'x':round(self.velocity[0],2),'y':round(self.velocity[1],2)},
                'nudge_speed':round(nudge,2),'monitor_index':mon,'destination_monitor':self.destination_monitor,
                'destination':{'x':round(target[0]),'y':round(target[1])},'arrivals':self.visits,
                'gaze':self._gaze(cx,cy,cur['x'],cur['y']),
                'writer':'orbot_native_host','execution_authority':False}
            return self.last_result

    @staticmethod
    def _gaze(center_x,center_y,cursor_x,cursor_y):
        dx=cursor_x-center_x;dy=cursor_y-center_y;distance=math.hypot(dx,dy)
        t=clamp((distance-30.)/(220.-30.),0.,1.)
        reach=t*t*(3.-2.*t)
        if distance<1:return {'x':0.,'y':0.}
        return {'x':clamp(dx/distance*reach,-1.,1.),'y':clamp(dy/distance*reach,-1.,1.)}
