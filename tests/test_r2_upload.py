"""Unit tests for ``synthbench.r2_upload`` (sb-sjs).

Covers config resolution from env vars, the env-detection helper, and
JSON-serialization parity between local writes and R2 uploads via an
injected fake S3 client (no boto3 round-trip).
"""

from __future__ import annotations

import json

import pytest

from synthbench.r2_upload import (
    R2Config,
    R2ConfigError,
    R2Uploader,
    env_has_r2_config,
)


# -- R2Config.from_env ------------------------------------------------------


def _full_env() -> dict[str, str]:
    return {
        "R2_ACCOUNT_ID": "abc123",
        "R2_ACCESS_KEY_ID": "AKIAEXAMPLE",
        "R2_SECRET_ACCESS_KEY": "secret",
        "R2_BUCKET": "synthbench-data-test",
    }


def test_from_env_returns_resolved_config():
    cfg = R2Config.from_env(_full_env())
    assert cfg.account_id == "abc123"
    assert cfg.access_key_id == "AKIAEXAMPLE"
    assert cfg.secret_access_key == "secret"
    assert cfg.bucket == "synthbench-data-test"


def test_from_env_endpoint_url_uses_account_subdomain():
    cfg = R2Config.from_env(_full_env())
    assert cfg.endpoint_url == "https://abc123.r2.cloudflarestorage.com"


def test_from_env_raises_when_any_var_missing():
    env = _full_env()
    del env["R2_BUCKET"]
    with pytest.raises(R2ConfigError) as exc:
        R2Config.from_env(env)
    assert "R2_BUCKET" in str(exc.value)


def test_from_env_treats_empty_string_as_missing():
    # GH Actions surfaces unset secrets as empty strings; that must not
    # silently produce a half-initialized client that fails on first PUT.
    env = _full_env()
    env["R2_ACCESS_KEY_ID"] = ""
    with pytest.raises(R2ConfigError) as exc:
        R2Config.from_env(env)
    assert "R2_ACCESS_KEY_ID" in str(exc.value)


def test_from_env_lists_all_missing_vars_in_one_message():
    with pytest.raises(R2ConfigError) as exc:
        R2Config.from_env({})
    msg = str(exc.value)
    assert "R2_ACCOUNT_ID" in msg
    assert "R2_ACCESS_KEY_ID" in msg
    assert "R2_SECRET_ACCESS_KEY" in msg
    assert "R2_BUCKET" in msg


# -- env_has_r2_config ------------------------------------------------------


def test_env_has_r2_config_true_when_complete():
    assert env_has_r2_config(_full_env()) is True


def test_env_has_r2_config_false_when_any_missing():
    env = _full_env()
    del env["R2_ACCOUNT_ID"]
    assert env_has_r2_config(env) is False


def test_env_has_r2_config_false_for_empty_env():
    assert env_has_r2_config({}) is False


def test_env_has_r2_config_false_when_value_blank():
    env = _full_env()
    env["R2_SECRET_ACCESS_KEY"] = ""
    assert env_has_r2_config(env) is False


# -- R2Uploader.put_json (with injected fake client) ------------------------


class _FakeS3Client:
    """Captures put_object calls so tests can assert payloads without boto3."""

    def __init__(self):
        self.calls: list[dict] = []

    def put_object(self, *, Bucket: str, Key: str, Body: bytes, ContentType: str):
        self.calls.append(
            {
                "Bucket": Bucket,
                "Key": Key,
                "Body": Body,
                "ContentType": ContentType,
            }
        )
        return {"ETag": "fake-etag"}


def _uploader_with_fake() -> tuple[R2Uploader, _FakeS3Client]:
    client = _FakeS3Client()
    cfg = R2Config.from_env(_full_env())
    return R2Uploader(cfg, client=client), client


def test_put_json_sends_minified_utf8_json():
    uploader, client = _uploader_with_fake()
    uploader.put_json("run/abc.json", {"sps": 0.42, "extra": [1, 2]})
    assert len(client.calls) == 1
    call = client.calls[0]
    assert call["Bucket"] == "synthbench-data-test"
    assert call["Key"] == "run/abc.json"
    assert call["ContentType"] == "application/json"
    # Minified: no whitespace between separators (matches _write_minified).
    assert call["Body"] == b'{"sps":0.42,"extra":[1,2]}'


def test_put_json_round_trips_payload():
    uploader, client = _uploader_with_fake()
    payload = {"nested": {"a": 1, "b": [True, None, "x"]}}
    uploader.put_json("question/ds/Q1.json", payload)
    body = client.calls[0]["Body"]
    assert json.loads(body) == payload


def test_put_json_strips_leading_slash_from_key():
    uploader, client = _uploader_with_fake()
    uploader.put_json("/config/cfg-1.json", {})
    assert client.calls[0]["Key"] == "config/cfg-1.json"


def test_put_json_idempotent_repeat_overwrites_same_key():
    uploader, client = _uploader_with_fake()
    uploader.put_json("run/abc.json", {"v": 1})
    uploader.put_json("run/abc.json", {"v": 2})
    assert [c["Key"] for c in client.calls] == ["run/abc.json", "run/abc.json"]
    assert json.loads(client.calls[1]["Body"]) == {"v": 2}


def test_object_count_tracks_uploads():
    uploader, _ = _uploader_with_fake()
    assert uploader.object_count == 0
    uploader.put_json("a.json", {})
    uploader.put_json("b.json", {})
    assert uploader.object_count == 2


def test_uploader_bucket_property_exposes_config_bucket():
    uploader, _ = _uploader_with_fake()
    assert uploader.bucket == "synthbench-data-test"


def test_uploader_default_client_requires_boto3(monkeypatch):
    # Hide boto3 to simulate a minimal install (no [r2] extra). The error
    # must point operators at the install fix rather than spelunking import
    # tracebacks.
    import builtins

    real_import = builtins.__import__

    def fake_import(name, *args, **kwargs):
        if name == "boto3":
            raise ImportError("no boto3 installed in this venv")
        return real_import(name, *args, **kwargs)

    monkeypatch.setattr(builtins, "__import__", fake_import)
    cfg = R2Config.from_env(_full_env())
    with pytest.raises(R2ConfigError) as exc:
        R2Uploader(cfg)
    assert "boto3" in str(exc.value)
