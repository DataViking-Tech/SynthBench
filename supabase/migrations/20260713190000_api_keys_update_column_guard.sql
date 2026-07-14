-- sb-t61h follow-up: enforce column-level immutability on api_keys UPDATE.
--
-- The `api_keys_revoke_own` policy (20260415190854_api_keys.sql) is documented
-- as "restricted to revocation", but RLS `USING`/`WITH CHECK` only gate WHICH
-- ROWS a user may touch — not WHICH COLUMNS. A signed-in user can therefore
-- PATCH their own key row via PostgREST to:
--   • clear `revoked_at` (un-revoke a key they previously killed),
--   • extend `expires_at`,
--   • escalate `scope` read → both,
--   • overwrite `key_hash` / `key_prefix` (point the row at a new secret).
--
-- RLS can't express "only revoked_at may change", so we add a BEFORE UPDATE
-- trigger that enforces it. The only mutation an ordinary (authenticated) user
-- may make is a one-way `revoked_at` NULL → non-NULL transition, with every
-- other column byte-for-byte unchanged. Re-issuing a key means INSERTing a new
-- row, exactly as the original design intended.
--
-- The Worker (service_role) must stay able to touch `last_used_at` on every
-- successful auth, so the trigger no-ops for the privileged roles. Unlike RLS,
-- triggers are NOT bypassed by service_role, so this exemption is explicit.
-- Migrations run as the table owner (postgres / supabase_admin), also exempt.

create or replace function public.enforce_api_keys_update_columns()
returns trigger
language plpgsql
-- Hardened search_path (mirrors the touch_updated_at hardening): the function
-- references no unqualified objects, so an empty search_path is safe and blocks
-- search-path injection.
set search_path = ''
as $$
begin
  -- Privileged roles (the Worker's service_role, and admin/owner roles used by
  -- migrations) are exempt: they legitimately update last_used_at and perform
  -- maintenance. RLS already scopes the authenticated path to auth.uid() =
  -- user_id, so this trigger only has to constrain that role's column set.
  if current_user in ('service_role', 'supabase_admin', 'postgres') then
    return new;
  end if;

  -- Ordinary users may ONLY revoke: a one-way NULL → non-NULL flip of
  -- revoked_at. Anything that leaves revoked_at null (incl. no-op updates) or
  -- touches an already-revoked row is rejected.
  if new.revoked_at is null then
    raise exception
      'api_keys: authenticated users may only revoke a key (set revoked_at); other updates are not permitted'
      using errcode = 'check_violation';
  end if;
  if old.revoked_at is not null then
    raise exception
      'api_keys: key is already revoked; further updates are not permitted'
      using errcode = 'check_violation';
  end if;

  -- revoked_at is NULL → non-NULL. Guarantee nothing else changed, so a
  -- revoke PATCH can't smuggle a scope escalation or key_hash swap alongside.
  if new.id is distinct from old.id
     or new.user_id is distinct from old.user_id
     or new.name is distinct from old.name
     or new.key_hash is distinct from old.key_hash
     or new.key_prefix is distinct from old.key_prefix
     or new.scope is distinct from old.scope
     or new.expires_at is distinct from old.expires_at
     or new.created_at is distinct from old.created_at
     or new.last_used_at is distinct from old.last_used_at then
    raise exception
      'api_keys: only revoked_at may be changed by the key owner'
      using errcode = 'check_violation';
  end if;

  return new;
end;
$$;

drop trigger if exists enforce_api_keys_update_columns on public.api_keys;
create trigger enforce_api_keys_update_columns
  before update on public.api_keys
  for each row
  execute function public.enforce_api_keys_update_columns();
