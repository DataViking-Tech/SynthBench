# Supabase migrations index

This directory contains SQL migration files tracked in git.

For contributor workflow expectations, see
[`DATABASE-MIGRATIONS.md`](../DATABASE-MIGRATIONS.md).

## Files currently in this directory

- `20260415065524_cf_gate_identity_layer.sql` — legacy reconciliation stub.
- `20260415065540_harden_touch_updated_at.sql` — legacy reconciliation stub.
- `20260415190844_submissions.sql` — submissions table and policies.
- `20260415190854_api_keys.sql` — API keys table and policies.

## Notes

- The two `*_stub`-style entries are retained for migration history
  reconciliation.
- New schema changes should always be added as new files; do not rewrite old
  migration files.
