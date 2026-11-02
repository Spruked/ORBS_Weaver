//! Independent, click-through guidance windows. The main Orb remains the sole
//! owner of its own position; these windows only present Motion Runtime state.
use super::*;
use std::collections::HashSet;
use tauri::{PhysicalPosition, WebviewUrl, WebviewWindowBuilder};

pub(super) fn clear(app:&tauri::AppHandle) {
    let state=app.state::<Presentation>();
    if let Ok(_guard)=state.position_gate.lock() {
        for (label,window) in app.webview_windows() {
            if label.starts_with("morb-") { let _=window.close(); }
        }
    }
    if let Ok(token)=vault_token(&state.root) {
        let _=reqwest::blocking::Client::builder().timeout(Duration::from_millis(800)).no_proxy().build()
            .and_then(|client|client.post("http://127.0.0.1:16525/presentation/morbs/clear").bearer_auth(token).send());
    }
}

pub(super) fn render(app:&tauri::AppHandle,entities:&serde_json::Value) {
    let Some(entities)=entities.as_array() else {return};
    let state=app.state::<Presentation>();
    let Ok(_guard)=state.position_gate.lock() else {return};
    if state.docked.load(Ordering::SeqCst) || state.shutting_down.load(Ordering::SeqCst) {return;}
    let mut active=HashSet::new();
    for item in entities.iter().take(4) {
        let (Some(id),Some(x),Some(y),Some(phase))=(item["id"].as_str(),item["x"].as_i64(),item["y"].as_i64(),item["state"].as_str()) else {continue};
        if id.len()!=32 || !id.bytes().all(|b|b.is_ascii_hexdigit()) || !["traveling","pulse","holding"].contains(&phase) {continue;}
        let (Ok(x),Ok(y))=(i32::try_from(x),i32::try_from(y)) else {continue};
        let label=format!("morb-{id}");active.insert(label.clone());
        let window=if let Some(window)=app.get_webview_window(&label) {window} else {
            let Ok(window)=WebviewWindowBuilder::new(app,&label,WebviewUrl::App("index.html".into()))
                .title("MORB guidance").inner_size(40.,40.).decorations(false).transparent(true)
                .shadow(false).resizable(false).always_on_top(true).skip_taskbar(true).visible(false).focused(false).build() else {continue};
            if window.set_ignore_cursor_events(true).is_err() {let _=window.close();continue;}
            window
        };
        if let Ok(size)=window.outer_size() {
            if window.set_position(PhysicalPosition::new(x-size.width as i32/2,y-size.height as i32/2)).is_ok() {
                let _=window.emit("orbot:morb-phase",phase);
                let _=window.show();
            }
        }
    }
    for (label,window) in app.webview_windows() {
        if label.starts_with("morb-") && !active.contains(&label) {let _=window.close();}
    }
}
