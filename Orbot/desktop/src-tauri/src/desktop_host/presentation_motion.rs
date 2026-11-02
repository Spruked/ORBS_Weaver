//! The only programmatic desktop window-position writer.
use super::*;
use tauri::PhysicalPosition;

#[cfg(windows)]
#[repr(C)]
struct Point { x:i32, y:i32 }
#[cfg(windows)]
#[repr(C)]
struct Rect { left:i32, top:i32, right:i32, bottom:i32 }
#[cfg(windows)]
#[repr(C)]
struct LastInputInfo { cb_size:u32, dw_time:u32 }
#[cfg(windows)]
#[link(name="user32")]
extern "system" {
    fn GetCursorPos(point:*mut Point)->i32;
    fn GetAsyncKeyState(key:i32)->i16;
    fn GetForegroundWindow()->*mut std::ffi::c_void;
    fn GetWindowRect(hwnd:*mut std::ffi::c_void, rect:*mut Rect)->i32;
    fn GetWindowTextLengthW(hwnd:*mut std::ffi::c_void)->i32;
    fn GetWindowTextW(hwnd:*mut std::ffi::c_void, text:*mut u16, max:i32)->i32;
    fn GetWindowThreadProcessId(hwnd:*mut std::ffi::c_void, pid:*mut u32)->u32;
    fn GetLastInputInfo(info:*mut LastInputInfo)->i32;
}
#[cfg(windows)]
#[link(name="kernel32")]
extern "system" { fn GetTickCount()->u32; }
#[cfg(windows)]
#[link(name="kernel32")]
extern "system" {
    fn OpenProcess(access:u32, inherit:i32, pid:u32)->*mut std::ffi::c_void;
    fn QueryFullProcessImageNameW(process:*mut std::ffi::c_void, flags:u32, text:*mut u16, size:*mut u32)->i32;
    fn CloseHandle(handle:*mut std::ffi::c_void)->i32;
}

#[cfg(windows)]
pub(super) fn foreground_activity()->serde_json::Value {
    use std::sync::{Mutex,OnceLock};
    use std::time::{Duration,Instant};
    static CACHE:OnceLock<Mutex<(Instant,serde_json::Value)>>=OnceLock::new();
    let cache=CACHE.get_or_init(||Mutex::new((Instant::now().checked_sub(Duration::from_secs(2)).unwrap_or_else(Instant::now),serde_json::json!({}))));
    if let Ok(value)=cache.lock() {if value.0.elapsed()<Duration::from_millis(500) {return value.1.clone();}}
    use std::path::Path;
    let hwnd=unsafe {GetForegroundWindow()};
    if hwnd.is_null() {return serde_json::json!({});}
    let mut rect=Rect{left:0,top:0,right:0,bottom:0};
    let rect_ok=unsafe {GetWindowRect(hwnd,&mut rect)}!=0 && rect.right>rect.left && rect.bottom>rect.top;
    let n=unsafe {GetWindowTextLengthW(hwnd)}.clamp(0,512);
    let mut title=vec![0u16;n as usize+1];
    let title_len=unsafe {GetWindowTextW(hwnd,title.as_mut_ptr(),title.len() as i32)}.max(0) as usize;
    title.truncate(title_len);
    let mut pid=0u32;unsafe {GetWindowThreadProcessId(hwnd,&mut pid);}
    let handle=unsafe {OpenProcess(0x1000,0,pid)};
    let app=if handle.is_null(){String::new()}else{
        let mut path=vec![0u16;1024];let mut size=path.len() as u32;
        let ok=unsafe {QueryFullProcessImageNameW(handle,0,path.as_mut_ptr(),&mut size)}!=0;
        unsafe {CloseHandle(handle);}
        if ok {Path::new(&String::from_utf16_lossy(&path[..size as usize])).file_name().map(|v|v.to_string_lossy().to_string()).unwrap_or_default()} else {String::new()}
    };
    let mut input=LastInputInfo{cb_size:std::mem::size_of::<LastInputInfo>() as u32,dw_time:0};
    let idle=if unsafe {GetLastInputInfo(&mut input)}!=0 {Some(unsafe {GetTickCount()}.wrapping_sub(input.dw_time))}else{None};
    let value=serde_json::json!({"foreground_app":app,"window_title":String::from_utf16_lossy(&title),
        "foreground_rect":if rect_ok {serde_json::json!({"left":rect.left,"top":rect.top,"right":rect.right,"bottom":rect.bottom})} else {serde_json::Value::Null},
        "idle_ms":idle});
    if let Ok(mut cached)=cache.lock() {*cached=(Instant::now(),value.clone());}
    value
}
#[cfg(not(windows))]
pub(super) fn foreground_activity()->serde_json::Value {serde_json::json!({})}
#[cfg(windows)]
pub(super) fn cursor() -> Option<(i32,i32)> {
    let mut point=Point{x:0,y:0};
    if unsafe {GetCursorPos(&mut point)} != 0 {Some((point.x,point.y))} else {None}
}
#[cfg(not(windows))]
pub(super) fn cursor() -> Option<(i32,i32)> {None}
#[cfg(windows)]
fn pressed()->bool {unsafe {GetAsyncKeyState(1) < 0 || GetAsyncKeyState(2) < 0}}
#[cfg(not(windows))]
fn pressed()->bool {true}

// The exact union handles adjacent displays, negative coordinates and
// overlapping/mirrored monitors without accepting gaps.
fn covered(x:i32,y:i32,w:u32,h:u32,rectangles:&[(i64,i64,i64,i64)])->bool {
    let (left,top,right,bottom)=(x as i64,y as i64,x as i64+w as i64,y as i64+h as i64);
    let mut edges=vec![left,right];
    for &(l,_,r,_) in rectangles {if l>left&&l<right {edges.push(l);} if r>left&&r<right {edges.push(r);}}
    edges.sort_unstable();edges.dedup();
    for pair in edges.windows(2) {
        let (l,r)=(pair[0],pair[1]);let mut ys:Vec<_>=rectangles.iter()
            .filter(|&&(a,_,b,_)|a<=l&&b>=r).map(|&(_,t,_,b)|(t.max(top),b.min(bottom)))
            .filter(|(t,b)|t<b).collect();
        ys.sort_unstable();let mut cursor=top;
        for (t,b) in ys {if t>cursor {break;}cursor=cursor.max(b);}
        if cursor<bottom{return false;}
    }
    true
}

fn apply_position(app:&tauri::AppHandle,x:i32,y:i32,manual:bool,expected:Option<PhysicalPosition<i32>>,expected_size:Option<tauri::PhysicalSize<u32>>)->Result<(),String> {
    let state=app.state::<Presentation>();
    let _guard=state.position_gate.lock().map_err(|e|e.to_string())?;
    if state.docked.load(Ordering::SeqCst) || (!manual && (state.motion_paused.load(Ordering::SeqCst)||pressed())) {return Ok(());}
    let window=app.get_webview_window("orb").ok_or("Orb window unavailable")?;
    let size=window.outer_size().map_err(|e|e.to_string())?;
    if expected_size.is_some_and(|old|old!=size) || expected.is_some_and(|old|window.outer_position().ok()!=Some(old)) {return Ok(());}
    let screens=window.available_monitors().map_err(|e|e.to_string())?;
    let rectangles:Vec<_>=screens.iter().map(|m|{
        let p=m.position();let s=m.size();(p.x as i64,p.y as i64,p.x as i64+s.width as i64,p.y as i64+s.height as i64)
    }).collect();
    if covered(x,y,size.width,size.height,&rectangles) {window.set_position(PhysicalPosition::new(x,y)).map_err(|e|e.to_string())?;}
    Ok(())
}

// Size and position are changed under the same gate as autonomous motion and drag.
pub(super) fn resize(app:&tauri::AppHandle,diameter:f64,panel:bool)->Result<f64,String> {
    if !diameter.is_finite() { return Err("Invalid appearance size".into()); }
    let state=app.state::<Presentation>();
    let _guard=state.position_gate.lock().map_err(|e|e.to_string())?;
    let window=app.get_webview_window("orb").ok_or("Orb window unavailable")?;
    let scale=window.scale_factor().map_err(|e|e.to_string())?;
    let old=window.outer_size().map_err(|e|e.to_string())?;
    let old_pos=window.outer_position().map_err(|e|e.to_string())?;
    let old_d=(old.width as f64/scale-20.).max(1.);
    if state.docked.load(Ordering::SeqCst) || pressed() {return Ok(old_d);}
    let monitors=window.available_monitors().map_err(|e|e.to_string())?;
    let center_x=old_pos.x as f64+old.width as f64/2.;
    let center_y=old_pos.y as f64+(10.+old_d/2.)*scale;
    let monitor=monitors.iter().min_by_key(|m| {
        let p=m.position();let z=m.size();
        let dx=(center_x-(p.x as f64+z.width as f64/2.)).abs();
        let dy=(center_y-(p.y as f64+z.height as f64/2.)).abs();
        (dx*dx+dy*dy) as u64
    }).ok_or("No monitor available")?;
    let extra=if panel {180.} else {0.};
    let fit=(monitor.size().width as f64/scale-20.).min(monitor.size().height as f64/scale-20.-extra);
    if fit<80. {return Err("Display is too small for the Orb and controls".into());}
    let d=diameter.clamp(80.,350.).min(fit);
    let mut width=((d+20.)*scale).round() as u32;
    // Preserve the existing center exactly through integer pixel rounding.
    if width%2 != old.width%2 { width=width.saturating_sub(1); }
    let height=((d+20.+extra)*scale).round() as u32;
    let rectangles:Vec<_>=monitors.iter().map(|m|{let p=m.position();let s=m.size();(p.x as i64,p.y as i64,p.x as i64+s.width as i64,p.y as i64+s.height as i64)}).collect();
    let mut x=(center_x-width as f64/2.).round() as i32;
    let mut y=(center_y-(10.+d/2.)*scale).round() as i32;
    if !covered(x,y,width,height,&rectangles) {
        let p=monitor.position();let z=monitor.size();
        x=x.clamp(p.x,p.x+z.width as i32-width as i32);
        y=y.clamp(p.y,p.y+z.height as i32-height as i32);
    }
    let desired=tauri::PhysicalSize::new(width,height);
    if desired!=old || x!=old_pos.x || y!=old_pos.y {
        window.set_size(desired).map_err(|e|e.to_string())?;
        if let Err(e)=window.set_position(PhysicalPosition::new(x,y)) {
            let _=window.set_size(old);return Err(e.to_string());
        }
    }
    Ok(width as f64/scale-20.)
}

pub(super) fn drag(app:&tauri::AppHandle,offset_x:f64,offset_y:f64)->Result<(),String> {
    let window=app.get_webview_window("orb").ok_or("Orb window unavailable")?;
    let scale=window.scale_factor().map_err(|e|e.to_string())?;
    let size=window.outer_size().map_err(|e|e.to_string())?;
    if !offset_x.is_finite()||!offset_y.is_finite()||offset_x<0.||offset_y<0.||offset_x*scale>size.width as f64||offset_y*scale>size.height as f64 {return Err("Invalid drag offset".into());}
    let (x,y)=cursor().ok_or("Cursor position unavailable")?;
    apply_position(app,(x as f64-offset_x*scale).round() as i32,(y as f64-offset_y*scale).round() as i32,true,None,None)
}

pub(super) fn start(app:tauri::AppHandle) {
    let gaze_app=app.clone();
    std::thread::spawn(move || {
        let mut previous=(2.0f64,2.0f64);
        loop {
            std::thread::sleep(Duration::from_millis(16));
            let state=gaze_app.state::<Presentation>();
            if state.shutting_down.load(Ordering::SeqCst) {break;}
            if state.docked.load(Ordering::SeqCst) {continue;}
            let Some(window)=gaze_app.get_webview_window("orb") else {break};
            let (Ok(pos),Ok(size),Ok(scale),Some((cx,cy)))=(window.outer_position(),window.outer_size(),window.scale_factor(),cursor()) else {continue};
            let center_x=pos.x as f64+size.width as f64/2.0;
            let center_y=pos.y as f64+size.height as f64/2.0;
            let dx=cx as f64-center_x;let dy=cy as f64-center_y;let distance=(dx*dx+dy*dy).sqrt();
            let t=((distance/scale-30.0)/(220.0-30.0)).clamp(0.0,1.0);let reach=t*t*(3.0-2.0*t);
            let gaze=if distance<1.0 {serde_json::json!({"x":0.0,"y":0.0})} else {serde_json::json!({"x":(dx/distance*reach).clamp(-1.0,1.0),"y":(dy/distance*reach).clamp(-1.0,1.0)})};
            let next=(gaze["x"].as_f64().unwrap_or(0.0),gaze["y"].as_f64().unwrap_or(0.0));
            if (next.0-previous.0).abs()>0.002||(next.1-previous.1).abs()>0.002 {
                previous=next;let _=gaze_app.emit("orbot:gaze",gaze);
            }
        }
    });
    std::thread::spawn(move || {
        let client=match reqwest::blocking::Client::builder().timeout(Duration::from_millis(800)).no_proxy().build(){Ok(c)=>c,Err(_)=>return};
        loop {
            // Keep physical window steps close to a display frame. At the
            // Poll at display cadence so the 120 px/s roaming cap moves in small steps.
            std::thread::sleep(Duration::from_millis(16));
            let state=app.state::<Presentation>();
            if state.shutting_down.load(Ordering::SeqCst) {break;}
            if state.docked.load(Ordering::SeqCst) || state.motion_paused.load(Ordering::SeqCst) {continue;}
            let Some(window)=app.get_webview_window("orb") else {break};
            let (Ok(pos),Ok(size),Ok(scale),Ok(monitors),Some((cx,cy)))=(window.outer_position(),window.outer_size(),window.scale_factor(),window.available_monitors(),cursor()) else {continue};
            let screens:Vec<_>=monitors.iter().map(|m|serde_json::json!({"x":m.position().x,"y":m.position().y,"width":m.size().width,"height":m.size().height,"scale":m.scale_factor()})).collect();
            let activity=foreground_activity();
            let voice_state=state.voice_state.lock().map(|v|v.clone()).unwrap_or_else(|_|"blocked".into());
            let payload=serde_json::json!({"x":pos.x,"y":pos.y,"width":size.width,"height":size.height,
                "orb_x":size.width as f64/2.0,"orb_y":size.width as f64/2.0,"orb_radius":(size.width as f64-20.0*scale)/2.0,
                "cursor":{"x":cx,"y":cy},"interaction":pressed(),"monitors":screens,
                "foreground_app":activity["foreground_app"],"window_title":activity["window_title"],
                "foreground_rect":activity["foreground_rect"],"idle_ms":activity["idle_ms"],"voice_state":voice_state});
            let Ok(token)=vault_token(&state.root) else {continue};
            let Ok(response)=client.post("http://127.0.0.1:16525/presentation/step").bearer_auth(token).json(&payload).send().and_then(|r|r.error_for_status()) else {continue};
            let Ok(next)=response.json::<serde_json::Value>() else {continue};
            morbs::render(&app,&next["morbs"]);
            if let Some(gaze)=next.get("gaze") {let _=app.emit("orbot:gaze",gaze.clone());}
            let _=app.emit("orbot:motion",serde_json::json!({"state":next["state"],"authority":next["authority"],"velocity":next["velocity"]}));
            if let Some(attention)=next.get("attention") {let _=app.emit("orbot:attention",attention.clone());}
            if next["attention"]["return_to_dock"]==true {
                // Dock recall changes only presentation; the Dock-owned runtime
                // and active cognitive session remain alive.
                let _=recall(&app);
                continue;
            }
            if !["gliding","recovering","guided_arrived","guided_waypoint_arrived"].contains(&next["state"].as_str().unwrap_or("")) || next["execution_authority"]!=false {continue;}
            let (Some(x),Some(y))=(next["x"].as_i64(),next["y"].as_i64()) else {continue};
            let (Ok(x),Ok(y))=(i32::try_from(x),i32::try_from(y)) else {continue};
            // Recall, explicit pause, and owner drag take precedence.
            if x!=pos.x || y!=pos.y {let _=apply_position(&app,x,y,false,Some(pos),Some(size));}
        }
    });
}

#[cfg(test)]
mod tests {
    use super::covered;
    #[test]
    fn window_must_be_covered_by_display_union() {
        let screens=[(-1920,0,0,1080),(0,0,1920,1080)];
        assert!(covered(-110,100,220,210,&screens));
        assert!(!covered(1850,100,220,210,&screens));
        let gap=[(-1920,0,-5,1080),(5,0,1920,1080)];
        assert!(!covered(-110,100,220,210,&gap));
    }
}
