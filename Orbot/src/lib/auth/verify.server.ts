import { getRequest } from "@tanstack/react-start/server";

import { auth } from "./server";

const authEnabled =
  (
    process.env.AUTH_ENABLED ??
    process.env.VITE_AUTH_ENABLED ??
    "false"
  ).toLowerCase() === "true";

const databaseConfigured =
  Boolean(process.env.DATABASE_URL?.trim());

/**
 * Real authentication is considered configured only when:
 *
 * 1. auth has explicitly been enabled, and
 * 2. a database connection exists.
 */
export const authConfigured =
  authEnabled && databaseConfigured;

export const DEV_USER_ID = "dev-user";

export class UnauthorizedError extends Error {
  readonly status = 401;

  constructor() {
    super("Unauthorized");
    this.name = "UnauthorizedError";
  }
}

export type VerifiedUser = {
  id: string;
  email: string | null;
};

export async function getSessionUser(
  providedHeaders?: Headers,
): Promise<VerifiedUser | null> {
  if (!authConfigured) {
    return null;
  }

  let headers = providedHeaders;

  if (!headers) {
    const request = getRequest();

    if (!request) {
      return null;
    }

    headers = request.headers;
  }

  const session = await auth.api.getSession({
    headers,
  });

  if (!session?.user) {
    return null;
  }

  return {
    id: session.user.id,
    email: session.user.email ?? null,
  };
}

export async function requireUserId(
  headers?: Headers,
): Promise<string> {
  if (!authConfigured) {
    /**
     * Never permit a shared development identity
     * against a real configured database.
     */
    if (databaseConfigured) {
      throw new Error(
        "Authentication is disabled while DATABASE_URL is configured. " +
          "Refusing to use the shared development user.",
      );
    }

    return DEV_USER_ID;
  }

  const user = await getSessionUser(headers);

  if (!user) {
    throw new UnauthorizedError();
  }

  return user.id;
}