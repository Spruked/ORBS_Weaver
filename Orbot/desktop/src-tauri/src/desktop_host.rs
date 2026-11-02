mod presentation_motion;
mod morbs;
use std::{path::PathBuf, sync::{Arc, Mutex, atomic::{AtomicBool, Ordering}}, time::Duration};
use std::io::Read;
use tauri::{Emitter, Manager, menu::{Menu, MenuItem}, tray::TrayIconBuilder};

pub enum Role { Orbot }
struct Presentation { docked: Arc<AtomicBool>, launch_id: String, root: PathBuf, shutting_down: AtomicBool, renderer_ready: AtomicBool, motion_paused: AtomicBool, voice_state: Mutex<String>, position_gate: Mutex<()> }

fn request(port: u16, path: &str, post: bool, launch_id: &str) -> Result<serde_json::Value, String> {
    let client = reqwest::blocking::Client::builder().timeout(Duration::from_secs(4)).no_proxy().build().map_err(|e|e.to_string())?;
    let url = format!("http://127.0.0.1:{port}{path}");
    let req = if post { client.post(url) } else { client.get(url) };
    let req=if post && (port==16522 || port==16523) { req.bearer_auth(vault_token(&repository_root())?) } else { req };
    req.header("X-Orbot-Desktop", "1").header("X-Orbot-Launch", launch_id).send()
        .and_then(|r|r.error_for_status()).and_then(|r|r.json()).map_err(|e|e.to_string())
}

fn repository_root() -> PathBuf {
    std::env::var_os("ORBOT_REPO_ROOT").map(PathBuf::from).unwrap_or_else(||PathBuf::from(env!("CARGO_MANIFEST_DIR")).parent().unwrap().parent().unwrap().to_path_buf())
}
fn vault_token(root: &std::path::Path) -> Result<String,String> {
    let token_path=std::env::var_os("ORBOT_VAULT_TOKEN_FILE").map(PathBuf::from).unwrap_or_else(||root.join("../orbs_vault_system/.local/host-memory.token"));
    std::fs::read_to_string(token_path).map(|token|token.trim().to_owned()).map_err(|_|"Existing Vault credential unavailable".into())
}
fn memory_call(root: &std::path::Path, path: &str) -> Result<serde_json::Value, String> {
    memory_payload(root,path,serde_json::json!({}))
}
fn memory_payload(root: &std::path::Path, path: &str, payload: serde_json::Value) -> Result<serde_json::Value, String> {
    let token = vault_token(root)?;
    reqwest::blocking::Client::builder().timeout(Duration::from_secs(5)).no_proxy().build().map_err(|e|e.to_string())?
        .post(format!("http://127.0.0.1:16521{path}")).bearer_auth(token.trim()).json(&payload)
        .send().and_then(|r|r.error_for_status()).and_then(|r|r.json()).map_err(|e|e.to_string())
}

fn ready(launch_id: &str) -> Result<(), String> {
    let station = request(16522, "/status", false, launch_id)?;
    if station["application"] != "station" || station["launch_id"] != launch_id || station["lifecycle"]["ready"] != true {
        return Err("Dock has not established lifecycle readiness".into());
    }
    let mut foundation = serde_json::Value::Null;
    for (name,port) in [("communication",16521),("cognition_governance",16524),("motion",16525)] {
        let health = request(port, "/health", false, launch_id)?;
        if health["runtime"] != name || health["ready"] != true || health["execution_authority"] != false {
            return Err(format!("Required runtime {name} is not ready in its expected bounded mode"));
        }
        if name == "communication" {
            if health["process_instance_id"] != station["lifecycle"]["communication_instance"] {
                return Err("Communication instance changed; return to Dock for reconciliation".into());
            }
            foundation = health["professional_foundation"]["sha256"].clone();
            if foundation != station["lifecycle"]["foundation_sha256"] { return Err("Professional foundation changed".into()); }
        } else if name == "cognition_governance" && health["professional_foundation"]["sha256"] != foundation {
            return Err("Cognition foundation mismatch".into());
        }
    }
    Ok(())
}

fn recall(app: &tauri::AppHandle) -> Result<(),String> {
    let state=app.state::<Presentation>();
    let window=app.get_webview_window("orb").ok_or("Orb window unavailable")?;
    {
        let _guard=state.position_gate.lock().map_err(|e|e.to_string())?;
        let previous=state.docked.swap(true, Ordering::SeqCst);
        if let Err(error)=window.hide() {state.docked.store(previous,Ordering::SeqCst);return Err(error.to_string());}
    }
    morbs::clear(app);
    let _=app.emit("orbot:docked", ());
    request(16522,"/show",true,&state.launch_id)?;
    Ok(())
}

#[tauri::command]
async fn resize_presentation(app:tauri::AppHandle, diameter:f64, panel:bool)->Result<f64,String> {
    tauri::async_runtime::spawn_blocking(move ||presentation_motion::resize(&app,diameter,panel)).await.map_err(|e|e.to_string())?
}
#[tauri::command]
async fn manual_drag_move(app:tauri::AppHandle,offset_x:f64,offset_y:f64)->Result<(),String> {
    tauri::async_runtime::spawn_blocking(move ||presentation_motion::drag(&app,offset_x,offset_y)).await.map_err(|e|e.to_string())?
}
#[tauri::command]
async fn dock_to_station(app: tauri::AppHandle) -> Result<(),String> {
    tauri::async_runtime::spawn_blocking(move ||recall(&app)).await.map_err(|e|e.to_string())?
}
#[tauri::command]
async fn active_session(app: tauri::AppHandle) -> Result<String,String> {
    let root=app.state::<Presentation>().root.clone();
    tauri::async_runtime::spawn_blocking(move || {
        let value=memory_call(&root,"/sessions/embodiment")?;
        value["session_id"].as_str().map(str::to_owned).ok_or("Session contract unavailable".into())
    }).await.map_err(|e|e.to_string())?
}
#[tauri::command]
async fn voice_event(app: tauri::AppHandle, event: serde_json::Value) -> Result<(),String> {
    if let Some(value)=event.get("state").and_then(|v|v.as_str()) {
        if let Ok(mut state)=app.state::<Presentation>().voice_state.lock() {*state=value.to_owned();}
    }
    let root=app.state::<Presentation>().root.clone();
    tauri::async_runtime::spawn_blocking(move ||memory_payload(&root,"/voice/events",event).map(|_|())).await.map_err(|e|e.to_string())?
}
#[tauri::command]
async fn attention_offer(app:tauri::AppHandle, application:String, window_title:String, stable_seconds:u64)->Result<serde_json::Value,String> {
    let root=app.state::<Presentation>().root.clone();
    let state=app.state::<Presentation>();
    if state.voice_state.lock().map(|v|v.as_str()!="listening").unwrap_or(true) || state.docked.load(Ordering::SeqCst) {
        return Err("Orbot is not available for a spoken attention offer".into());
    }
    tauri::async_runtime::spawn_blocking(move || {
        let session=memory_call(&root,"/sessions/embodiment")?;
        let session_id=session["session_id"].as_str().ok_or("Active Orbot session unavailable")?;
        let body=serde_json::json!({"session_id":session_id,"application":application,"window_title":window_title,"stable_seconds":stable_seconds});
        let token=vault_token(&root)?;
        reqwest::blocking::Client::builder().timeout(Duration::from_secs(120)).no_proxy().build().map_err(|e|e.to_string())?
            .post("http://127.0.0.1:16521/attention/offer").bearer_auth(token).json(&body)
            .send().and_then(|r|r.error_for_status()).and_then(|r|r.json()).map_err(|e|e.to_string())
    }).await.map_err(|e|e.to_string())?
}
#[tauri::command]
async fn attention_feedback(app:tauri::AppHandle,declined:bool)->Result<(),String> {
    let root=app.state::<Presentation>().root.clone();
    tauri::async_runtime::spawn_blocking(move || {
        let token=vault_token(&root)?;
        reqwest::blocking::Client::builder().timeout(Duration::from_secs(3)).no_proxy().build().map_err(|e|e.to_string())?
            .post("http://127.0.0.1:16525/presentation/attention/feedback").bearer_auth(token).json(&serde_json::json!({"declined":declined}))
            .send().and_then(|r|r.error_for_status()).map(|_|()).map_err(|e|e.to_string())
    }).await.map_err(|e|e.to_string())?
}
#[tauri::command]
async fn presentation_preferences(app:tauri::AppHandle)->Result<serde_json::Value,String> {
    let root=app.state::<Presentation>().root.clone();
    tauri::async_runtime::spawn_blocking(move ||{
        reqwest::blocking::Client::builder().timeout(Duration::from_secs(3)).no_proxy().build().map_err(|e|e.to_string())?
            .get("http://127.0.0.1:16521/presentation/preferences").bearer_auth(vault_token(&root)?).send().and_then(|r|r.error_for_status()).and_then(|r|r.json()).map_err(|e|e.to_string())
    }).await.map_err(|e|e.to_string())?
}
#[tauri::command]
async fn save_presentation_preferences(app:tauri::AppHandle,value:serde_json::Value,expected_entry_id:Option<String>)->Result<serde_json::Value,String> {
    let root=app.state::<Presentation>().root.clone();
    tauri::async_runtime::spawn_blocking(move ||memory_payload(&root,"/presentation/preferences",serde_json::json!({"value":value,"expected_entry_id":expected_entry_id})))
        .await.map_err(|e|e.to_string())?
}
#[tauri::command]
async fn set_motion_authority(authority:String)->Result<(),String> {
    if !matches!(authority.as_str(),"ambient"|"hold"|"guided") {return Err("Unknown presentation state".into());}
    let target=if authority=="guided" {let (x,y)=presentation_motion::cursor().ok_or("Windows cursor position unavailable")?;Some((x.saturating_add(150),y.saturating_add(100)))} else {None};
    tauri::async_runtime::spawn_blocking(move || {
        let token=vault_token(&repository_root())?;
        let mut body=serde_json::json!({"authority":authority});
        if let Some((x,y))=target {body["target"]=serde_json::json!({"x":x,"y":y});}
        reqwest::blocking::Client::builder().timeout(Duration::from_secs(3)).no_proxy().build().map_err(|e|e.to_string())?
            .post("http://127.0.0.1:16525/presentation/authority").bearer_auth(token).json(&body)
            .send().and_then(|r|r.error_for_status()).map(|_|()).map_err(|e|e.to_string())
    }).await.map_err(|e|e.to_string())?
}
#[tauri::command]
async fn microphone_preferences(app:tauri::AppHandle)->Result<serde_json::Value,String> {
    let root=app.state::<Presentation>().root.clone();
    tauri::async_runtime::spawn_blocking(move ||{
        reqwest::blocking::Client::builder().timeout(Duration::from_secs(5)).no_proxy().build().map_err(|e|e.to_string())?
            .get("http://127.0.0.1:16521/voice/preferences").bearer_auth(vault_token(&root)?).send().and_then(|r|r.error_for_status()).and_then(|r|r.json()).map_err(|e|e.to_string())
    }).await.map_err(|e|e.to_string())?
}
#[tauri::command]
async fn cancel_voice(app: tauri::AppHandle, session_id:String, turn_id:String) -> Result<(),String> {
    let root=app.state::<Presentation>().root.clone();
    tauri::async_runtime::spawn_blocking(move ||memory_payload(&root,"/voice/cancel",serde_json::json!({"session_id":session_id,"turn_id":turn_id})).map(|_|())).await.map_err(|e|e.to_string())?
}
#[tauri::command]
fn renderer_ready(app: tauri::AppHandle) { app.state::<Presentation>().renderer_ready.store(true,Ordering::SeqCst); }
#[tauri::command]
fn shutdown_complete(app: tauri::AppHandle) -> Result<(),String> {
    if !app.state::<Presentation>().shutting_down.load(Ordering::SeqCst) { return Err("Dock has not requested shutdown".into()); }
    app.exit(0); Ok(())
}

pub fn run(_role: Role) {
    // Direct execution never exposes an independently launched floating Orb.
    let launch_id=match std::env::var("ORBOT_DOCK_LAUNCH") { Ok(id) if !id.is_empty()=>id, _=>{ eprintln!("Launch Orbot through Dock Station.");return; } };
    let station=match request(16522,"/status",false,&launch_id) { Ok(value)=>value, Err(_)=>return };
    if station["application"]!="station" || station["launch_id"]!=launch_id { return; }
    let root=std::env::var_os("ORBOT_REPO_ROOT").map(PathBuf::from).unwrap_or_else(||PathBuf::from(env!("CARGO_MANIFEST_DIR")).parent().unwrap().parent().unwrap().to_path_buf());
    let docked=Arc::new(AtomicBool::new(true));
    tauri::Builder::default()
        .on_permission_request(|webview,kind| {
            use tauri::webview::{PermissionKind,PermissionResponse};
            let local=webview.url().ok().is_some_and(|url|matches!(url.host_str(),Some("tauri.localhost"|"localhost"|"127.0.0.1")));
            if webview.label()=="orb" && local && kind==PermissionKind::Autoplay {PermissionResponse::Allow} else {PermissionResponse::Default}
        })
        .manage(Presentation{docked:docked.clone(),launch_id:launch_id.clone(),root,shutting_down:AtomicBool::new(false),renderer_ready:AtomicBool::new(false),motion_paused:AtomicBool::new(false),voice_state:Mutex::new("idle".into()),position_gate:Mutex::new(())})
        .invoke_handler(tauri::generate_handler![dock_to_station,active_session,shutdown_complete,renderer_ready,voice_event,cancel_voice,attention_offer,attention_feedback,microphone_preferences,manual_drag_move,resize_presentation,presentation_preferences,save_presentation_preferences,set_motion_authority])
        .setup(move |app| {
            // Config is invisible too: no initial floating-window flash.
            app.get_webview_window("orb").ok_or("Orb missing")?.hide()?;
            let show=MenuItem::with_id(app,"station","Show Dock Station",true,None::<&str>)?;
            let release=MenuItem::with_id(app,"release","Release through Dock",true,None::<&str>)?;
            let dock=MenuItem::with_id(app,"dock","Recall to Dock",true,None::<&str>)?;
            let pause=MenuItem::with_id(app,"motion_pause","Pause movement",true,None::<&str>)?;
            let resume=MenuItem::with_id(app,"motion_resume","Resume movement",true,None::<&str>)?;
            let quit=MenuItem::with_id(app,"quit","Quit through Dock",true,None::<&str>)?;
            let menu=Menu::with_items(app,&[&show,&release,&dock,&pause,&resume,&quit])?;
            TrayIconBuilder::new().icon(tauri::image::Image::from_bytes(include_bytes!("orbot.png"))?).tooltip("Orbot — managed by Dock Station")
                .menu(&menu).on_menu_event(|app,event| {
                    let handle=app.clone();let action=event.id.as_ref().to_string();
                    std::thread::spawn(move || {
                        let state=handle.state::<Presentation>();
                        match action.as_str() {
                            "station"=>{let _=request(16522,"/show",true,&state.launch_id);},
                            "release"=>{let _=request(16522,"/release",true,&state.launch_id);},
                            "dock"=>{let _=recall(&handle);},
                            "motion_pause"=>{if let Ok(_guard)=state.position_gate.lock(){state.motion_paused.store(true,Ordering::SeqCst);}},
                            "motion_resume"=>{state.motion_paused.store(false,Ordering::SeqCst);},
                            "quit"=>{let _=request(16522,"/shutdown",true,&state.launch_id);}, _=>{}
                        }
                    });
                }).build(app)?;
            presentation_motion::start(app.handle().clone());
            let server=tiny_http::Server::http(("127.0.0.1",16523)).map_err(|e|std::io::Error::other(e.to_string()))?;
            let handle=app.handle().clone();let state=docked.clone();let owner=launch_id.clone();
            std::thread::spawn(move ||for mut request_in in server.incoming_requests() {
                let allowed=request_in.headers().iter().any(|h|h.field.equiv("X-Orbot-Desktop")&&h.value.as_str()=="1") &&
                    request_in.headers().iter().any(|h|h.field.equiv("X-Orbot-Launch")&&h.value.as_str()==owner);
                if !allowed {let _=request_in.respond(tiny_http::Response::empty(403));continue;}
                let post=request_in.method()==&tiny_http::Method::Post;
                if post {
                    let expected=vault_token(&handle.state::<Presentation>().root).map(|token|format!("Bearer {token}"));
                    let authorized=expected.ok().is_some_and(|expected|request_in.headers().iter().any(|h|h.field.equiv("Authorization")&&h.value.as_str()==expected));
                    if !authorized {let _=request_in.respond(tiny_http::Response::empty(401));continue;}
                }
                let result:Result<(),String>=match(request_in.url(),post) {
                    ("/status",false)=>Ok(()),
                    ("/dock",true)=>recall(&handle),
                    ("/undock",true)=>ready(&owner).and_then(|_| {
                        handle.get_webview_window("orb").ok_or("Orb unavailable".into()).and_then(|w|{
                            w.show().and_then(|_|w.set_focus()).map_err(|e|e.to_string())?;
                            state.store(false,Ordering::SeqCst);let _=handle.emit("orbot:released",());Ok(())
                        })
                    }),
                    ("/motion/pause",true)=>{let p=handle.state::<Presentation>();let outcome=match p.position_gate.lock(){Ok(_guard)=>{p.motion_paused.store(true,Ordering::SeqCst);Ok(())},Err(e)=>Err(e.to_string())};outcome},
                    ("/motion/resume",true)=>{handle.state::<Presentation>().motion_paused.store(false,Ordering::SeqCst);Ok(())},
                    ("/voice/input-device",true)=>{
                        let mut body=String::new();
                        let result=request_in.as_reader().take(4096).read_to_string(&mut body).map_err(|e|e.to_string())
                            .and_then(|_|serde_json::from_str::<serde_json::Value>(&body).map_err(|e|e.to_string()));
                        result.and_then(|value|{
                            memory_payload(&handle.state::<Presentation>().root,"/voice/preferences",value.clone())?;
                            handle.emit("orbot:input-device",value).map_err(|e|e.to_string())
                        })
                    },
                    ("/voice/refresh_devices",true)|( "/voice/start",true)|( "/voice/pause",true)|( "/voice/cancel",true)=>{
                        if request_in.url()!="/voice/start" {let _=memory_payload(&handle.state::<Presentation>().root,"/voice/cancel",serde_json::json!({}));}
                        handle.emit("orbot:voice-control",request_in.url().trim_start_matches("/voice/")).map_err(|e|e.to_string())
                    },
                    ("/shutdown",true)=>{handle.state::<Presentation>().shutting_down.store(true,Ordering::SeqCst);let _=handle.emit("orbot:shutdown",());Ok(())},
                    _=>Err("Unknown presentation operation".into())
                };
                let response=match result {
                    Ok(())=>tiny_http::Response::from_string(serde_json::json!({"application":"orb","launch_id":owner,
                        "docked":state.load(Ordering::SeqCst),"motion_paused":handle.state::<Presentation>().motion_paused.load(Ordering::SeqCst),"position":handle.get_webview_window("orb").and_then(|w|w.outer_position().ok()).map(|p|serde_json::json!({"x":p.x,"y":p.y})),"renderer_ready":handle.state::<Presentation>().renderer_ready.load(Ordering::SeqCst),"visible":handle.get_webview_window("orb").map(|w|w.is_visible().unwrap_or(false))}).to_string()),
                    Err(error)=>tiny_http::Response::from_string(serde_json::json!({"error":error}).to_string()).with_status_code(503)
                };
                let _=request_in.respond(response);
            });
            Ok(())
        })
        .on_window_event(|window,event|if window.label()=="orb" { if let tauri::WindowEvent::CloseRequested{api,..}=event {
            api.prevent_close();let handle=window.app_handle().clone();std::thread::spawn(move ||{let _=recall(&handle);});
        }})
        .run(tauri::generate_context!()).expect("Unable to run Dock-managed Orbot host");
}

#[cfg(test)]
mod tests {
    #[test]
    fn initial_window_cannot_float() {
        let config:serde_json::Value=serde_json::from_str(include_str!("../tauri.conf.json")).unwrap();
        assert_eq!(config["app"]["windows"][0]["visible"],false);
    }
}
