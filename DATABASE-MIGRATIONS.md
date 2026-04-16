# Database migrations (maintainer note)

This file is intentionally short and contributor-facing.

If you are an external contributor, you usually do **not** need to run or apply
production database changes. Focus on code/tests/docs PRs unless a maintainer
asks for migration work.

## Migration policy

All schema changes must land as migration files under `supabase/migrations/`
through a pull request.

- Do not apply production DDL manually.
- Do not edit already-applied migration files.
- Add a new migration for every schema change.

## Creating a migration

Use the Supabase CLI to generate a correctly versioned filename:

```bash
supabase migration new <slug>
```

This creates `supabase/migrations/<YYYYMMDDHHMMSS>_<slug>.sql`.

## Review expectations

For migration PRs, include:

1. What schema changed and why.
2. Whether the migration is reversible/backward-compatible.
3. Any data backfill or rollout notes needed by maintainers.

## Related docs

- [`supabase/README.md`](supabase/README.md) — brief migration file index.
- [`SUBMISSIONS.md`](SUBMISSIONS.md) — contributor-facing submission flow.
