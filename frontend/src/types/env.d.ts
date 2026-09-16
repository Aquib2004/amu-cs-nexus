// Custom environment variable types recognised by the frontend.

declare namespace NodeJS {
  interface ProcessEnv {
    // Base URL of the backend REST API. Read at build time for NEXT_PUBLIC vars.
    NEXT_PUBLIC_API_URL?: string;
  }
}
