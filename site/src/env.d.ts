/// <reference types="astro/client" />

interface ImportMetaEnv {
  readonly PUBLIC_SUPABASE_URL?: string;
  readonly PUBLIC_SUPABASE_ANON_KEY?: string;
  readonly PUBLIC_GATED_API_BASE?: string;
  // sb-xjf: client-side Sentry DSN, baked into the JS bundle at build time so
  // browser errors reach Sentry. Optional — when unset the @sentry/astro
  // integration is skipped entirely (see astro.config.mjs).
  readonly PUBLIC_SENTRY_DSN?: string;
}

interface ImportMeta {
  readonly env: ImportMetaEnv;
}
