import { createMiddleware } from "@tanstack/react-start";

/**
 * Provider-neutral authentication middleware.
 *
 * Protect server functions that access private
 * or per-user data with this middleware.
 *
 * The verified user id is added to:
 *
 * context.userId
 */
export const authMiddleware = createMiddleware({
  type: "function",
}).server(async ({ next }) => {
  const { requireUserId } =
    await import("./verify.server");

  const userId = await requireUserId();

  return next({
    context: {
      userId,
    },
  });
});