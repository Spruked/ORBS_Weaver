export type AuthProvider = {
  providerId: "google" | "github";
  label: string;
};

export const AUTH_PROVIDERS: readonly AuthProvider[] = [
  {
    providerId: "google",
    label: "Google",
  },
  {
    providerId: "github",
    label: "GitHub",
  },
] as const;