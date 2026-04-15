"""Cloudflare R2 upload helper for gated-tier publish artifacts (sb-sjs).

Per-question/run/config JSONs for datasets whose redistribution policy is not
``full`` ship to a private Cloudflare R2 bucket instead of landing in
``site/public/data/``. The Worker proxy (sb-cf4) reads from the same bucket
after Supabase JWT validation; the data-layer half lives here.

R2 exposes an S3-compatible API. We use ``boto3`` against R2's
``<account>.r2.cloudflarestorage.com`` endpoint. Credentials are read from
the environment so CI can source them from Doppler / GH Actions secrets
without code changes:

    R2_ACCOUNT_ID         Cloudflare account ID (subdomain of endpoint)
    R2_ACCESS_KEY_ID      R2 API token's access key
    R2_SECRET_ACCESS_KEY  R2 API token's secret
    R2_BUCKET             Bucket name (e.g. synthbench-data-prod)

When any of these are missing, callers should treat that as a signal to fall
back to local writes (the publish CLI does this automatically). ``boto3`` is
an optional dependency declared under ``synthbench[r2]``; importing this
module never imports boto3 — that only happens when an ``R2Uploader`` is
constructed without an injected client (i.e. real uploads).
"""

from __future__ import annotations

import json
import os
from dataclasses import dataclass
from typing import Mapping, Protocol


class R2ConfigError(RuntimeError):
    """Raised when R2 configuration or its required dependency is unavailable."""


_REQUIRED_ENV_VARS = (
    "R2_ACCOUNT_ID",
    "R2_ACCESS_KEY_ID",
    "R2_SECRET_ACCESS_KEY",
    "R2_BUCKET",
)


@dataclass(frozen=True)
class R2Config:
    """Resolved R2 connection details."""

    account_id: str
    access_key_id: str
    secret_access_key: str
    bucket: str

    @property
    def endpoint_url(self) -> str:
        return f"https://{self.account_id}.r2.cloudflarestorage.com"

    @classmethod
    def from_env(cls, env: Mapping[str, str] | None = None) -> "R2Config":
        env = env if env is not None else os.environ
        missing = [name for name in _REQUIRED_ENV_VARS if not env.get(name)]
        if missing:
            raise R2ConfigError(
                "Missing required R2 environment variables: " + ", ".join(missing)
            )
        return cls(
            account_id=env["R2_ACCOUNT_ID"],
            access_key_id=env["R2_ACCESS_KEY_ID"],
            secret_access_key=env["R2_SECRET_ACCESS_KEY"],
            bucket=env["R2_BUCKET"],
        )


def env_has_r2_config(env: Mapping[str, str] | None = None) -> bool:
    """True iff every required R2 env var is set to a non-empty value."""
    env = env if env is not None else os.environ
    return all(env.get(name) for name in _REQUIRED_ENV_VARS)


class _S3Client(Protocol):
    def put_object(
        self, *, Bucket: str, Key: str, Body: bytes, ContentType: str
    ) -> object: ...


def _build_default_client(config: R2Config) -> _S3Client:
    try:
        import boto3
    except ImportError as e:
        raise R2ConfigError(
            "boto3 is required for R2 uploads. Install via "
            "`pip install synthbench[r2]` or set --no-r2 to use local writes."
        ) from e
    return boto3.client(
        "s3",
        endpoint_url=config.endpoint_url,
        aws_access_key_id=config.access_key_id,
        aws_secret_access_key=config.secret_access_key,
        region_name="auto",
    )


class R2Uploader:
    """Idempotent JSON uploader to a Cloudflare R2 bucket.

    Re-uploading the same key path overwrites the prior object; bucket
    versioning (enabled at provisioning time) preserves history server-side
    for rollback.
    """

    def __init__(
        self,
        config: R2Config,
        *,
        client: _S3Client | None = None,
    ):
        self._config = config
        self._client = client if client is not None else _build_default_client(config)
        self._object_count = 0

    @classmethod
    def from_env(cls, env: Mapping[str, str] | None = None) -> "R2Uploader":
        return cls(R2Config.from_env(env))

    @property
    def bucket(self) -> str:
        return self._config.bucket

    @property
    def object_count(self) -> int:
        """Number of put_json calls made through this uploader."""
        return self._object_count

    def put_json(self, key: str, payload: object) -> None:
        """Upload ``payload`` as minified JSON to ``key`` in the bucket.

        Mirrors the publish step's ``_write_minified`` serialization so R2
        objects byte-match what the local writer would have produced.
        """
        body = json.dumps(payload, separators=(",", ":"), sort_keys=False).encode(
            "utf-8"
        )
        self._client.put_object(
            Bucket=self._config.bucket,
            Key=key.lstrip("/"),
            Body=body,
            ContentType="application/json",
        )
        self._object_count += 1


__all__ = [
    "R2Config",
    "R2ConfigError",
    "R2Uploader",
    "env_has_r2_config",
]
