import { authClient } from "./client";

/**
 * Authentication is opt-in during early Orbot development.
 *
 * Set:
 * VITE_AUTH_ENABLED=true
 *
 * when the real Better Auth flow is configured.
 */
const authEnabled =
  import.meta.env.VITE_AUTH_ENABLED === "true";

export type AppUser = {
  id: string;
  displayName: string | null;
  primaryEmail: string | null;
  profileImageUrl: string | null;
  isDevFallback: boolean;
};

export const DEV_USER: AppUser = {
  id: "dev-user",
  displayName: "Dev User",
  primaryEmail: "dev@example.com",
  profileImageUrl: null,
  isDevFallback: true,
};

export type CurrentUserState = {
  user: AppUser | null;
  isPending: boolean;
};

export function useCurrentUserState(): CurrentUserState {
  if (!authEnabled) {
    return {
      user: DEV_USER,
      isPending: false,
    };
  }

  // authEnabled is a module-level constant and therefore does not
  // change during the lifetime of the application.
  // eslint-disable-next-line react-hooks/rules-of-hooks
  const { data, isPending } =
    authClient.useSession();

  const sessionUser = data?.user;

  return {
    user: sessionUser
      ? {
          id: sessionUser.id,
          displayName:
            sessionUser.name ?? null,
          primaryEmail:
            sessionUser.email ?? null,
          profileImageUrl:
            sessionUser.image ?? null,
          isDevFallback: false,
        }
      : null,

    isPending,
  };
}

export function useCurrentUser(): AppUser | null {
  return useCurrentUserState().user;
}