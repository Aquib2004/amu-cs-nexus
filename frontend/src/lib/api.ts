// Base configuration for the frontend API client.
//
// NEXT_PUBLIC_* environment variables are inlined at build time and can be
// set in a local .env.local file. We default to the local backend URL.

export const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";
