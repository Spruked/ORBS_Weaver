import { createAuthClient } from "better-auth/react";

import { AUTH_PROVIDERS } from "./providers";

export const authClient = createAuthClient();

export const {
  signIn,
  signOut,
  signUp,
  useSession,
} = authClient;

export { AUTH_PROVIDERS };