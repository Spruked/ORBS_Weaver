import { invoke, isTauri } from '@tauri-apps/api/core';

// The native host uses the existing server-side credential. No credential is
// copied into the webview. Both presentation surfaces use this runtime session.
export async function embodimentSession(): Promise<string> {
  if (!isTauri()) throw new Error('Launch Orbot through native Dock Station.');
  return invoke<string>('active_session');
}
