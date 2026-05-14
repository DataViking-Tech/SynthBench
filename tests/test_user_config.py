"""Tests for the user-configuration artifact (sb-vgb / GH#257).

Covers:
  - YAML loading: missing file, malformed YAML, empty file, non-mapping root
  - Schema validation: required fields, slug regex, contributor format,
    target_subgroup shape, packs/ensemble_weights coherence, decoding bounds,
    unknown-key rejection
  - Submission stamping: attach_to_submission_body emits compact JSON with
    user_config at the top level and leaves the existing keys untouched
  - Harness-version cross-check
  - CLI surface: `synthbench validate-config` and `synthbench submit --config`
"""

from __future__ import annotations

import json

import httpx
import pytest
from click.testing import CliRunner

from synthbench import __version__
from synthbench import user_config as uc
from synthbench.cli import main


# --------------------------------------------------------------------------- #
# YAML loading                                                                #
# --------------------------------------------------------------------------- #


def _valid_dict() -> dict:
    return {
        "vendor": "synthpanel",
        "vendor_version": "1.4.0",
        "config_name": "wesley-healthcare-nc",
        "contributor": "@wesley",
        "harness_version": __version__,
        "target_subgroup": {
            "description": "Healthcare workers in NC/MN/WI/IA",
            "selector": {
                "geography": ["NC", "MN", "WI", "IA"],
                "occupation": ["healthcare"],
            },
        },
        "packs": ["healthcare-patient", "general-consumer"],
        "ensemble_weights": [0.7, 0.3],
        "extra_prompts": {"system": "You are a healthcare worker."},
        "decoding": {"temperature": 0.6, "top_p": 0.9, "model": "claude-haiku-4-5"},
    }


def _write_yaml(tmp_path, payload):
    import yaml

    p = tmp_path / "config.yaml"
    p.write_text(yaml.safe_dump(payload, sort_keys=False))
    return p


def test_load_missing_file(tmp_path):
    res = uc.load_config_file(tmp_path / "nope.yaml")
    assert isinstance(res, uc.ConfigError)
    assert "cannot read" in res.message


def test_load_empty_file(tmp_path):
    p = tmp_path / "empty.yaml"
    p.write_text("")
    res = uc.load_config_file(p)
    assert isinstance(res, uc.ConfigError)
    assert "empty" in res.message


def test_load_non_mapping(tmp_path):
    p = tmp_path / "list.yaml"
    p.write_text("- a\n- b\n")
    res = uc.load_config_file(p)
    assert isinstance(res, uc.ConfigError)
    assert "mapping" in res.message


def test_load_invalid_yaml(tmp_path):
    p = tmp_path / "bad.yaml"
    p.write_text("vendor: synthpanel\n  bad: indent\n")
    res = uc.load_config_file(p)
    assert isinstance(res, uc.ConfigError)
    assert "invalid YAML" in res.message


# --------------------------------------------------------------------------- #
# Schema validation                                                           #
# --------------------------------------------------------------------------- #


def test_valid_config_returns_user_config():
    result = uc.validate_config(_valid_dict())
    assert isinstance(result, uc.UserConfig)
    assert result.leaderboard_row_key == "synthpanel/wesley-healthcare-nc"
    assert result.contributor == "@wesley"


def test_load_and_validate_roundtrip(tmp_path):
    p = _write_yaml(tmp_path, _valid_dict())
    result = uc.load_and_validate(p)
    assert isinstance(result, uc.UserConfig)
    assert result.config_name == "wesley-healthcare-nc"


def test_required_fields_missing():
    result = uc.validate_config({})
    assert isinstance(result, list)
    fields = {e.field for e in result}
    for required in (
        "vendor",
        "vendor_version",
        "config_name",
        "contributor",
        "harness_version",
        "target_subgroup",
    ):
        assert required in fields


def test_vendor_slug_enforced():
    d = _valid_dict()
    d["vendor"] = "Bad Vendor!"
    result = uc.validate_config(d)
    assert isinstance(result, list)
    assert any(e.field == "vendor" and "kebab" in e.message for e in result)


def test_config_name_slug_enforced():
    d = _valid_dict()
    d["config_name"] = "UPPER_CASE"
    result = uc.validate_config(d)
    assert isinstance(result, list)
    assert any(e.field == "config_name" for e in result)


def test_contributor_accepts_email():
    d = _valid_dict()
    d["contributor"] = "wesley@dataviking.tech"
    result = uc.validate_config(d)
    assert isinstance(result, uc.UserConfig)


def test_contributor_rejects_garbage():
    d = _valid_dict()
    d["contributor"] = "not a handle"
    result = uc.validate_config(d)
    assert isinstance(result, list)
    assert any(e.field == "contributor" for e in result)


def test_target_subgroup_requires_description():
    d = _valid_dict()
    d["target_subgroup"] = {"selector": {"geography": ["NC"]}}
    result = uc.validate_config(d)
    assert isinstance(result, list)
    assert any(e.field == "target_subgroup.description" for e in result)


def test_target_subgroup_selector_must_be_list_of_strings():
    d = _valid_dict()
    d["target_subgroup"]["selector"]["geography"] = "NC"
    result = uc.validate_config(d)
    assert isinstance(result, list)
    assert any(e.field == "target_subgroup.selector.geography" for e in result)


def test_target_subgroup_selector_optional():
    d = _valid_dict()
    d["target_subgroup"] = {"description": "anyone, anywhere"}
    result = uc.validate_config(d)
    assert isinstance(result, uc.UserConfig)


def test_ensemble_weights_must_sum_to_one():
    d = _valid_dict()
    d["ensemble_weights"] = [0.5, 0.3]
    result = uc.validate_config(d)
    assert isinstance(result, list)
    assert any("sum to 1.0" in e.message for e in result)


def test_ensemble_weights_length_matches_packs():
    d = _valid_dict()
    d["ensemble_weights"] = [0.5, 0.3, 0.2]
    d["packs"] = ["a", "b"]
    result = uc.validate_config(d)
    assert isinstance(result, list)
    assert any("packs length" in e.message for e in result)


def test_ensemble_weights_rejects_negative():
    d = _valid_dict()
    d["ensemble_weights"] = [1.1, -0.1]
    result = uc.validate_config(d)
    assert isinstance(result, list)
    assert any("non-negative" in e.message for e in result)


def test_decoding_temperature_bounds():
    d = _valid_dict()
    d["decoding"]["temperature"] = -0.1
    result = uc.validate_config(d)
    assert isinstance(result, list)
    assert any(e.field == "decoding.temperature" for e in result)


def test_decoding_top_p_bounds():
    d = _valid_dict()
    d["decoding"]["top_p"] = 1.5
    result = uc.validate_config(d)
    assert isinstance(result, list)
    assert any(e.field == "decoding.top_p" for e in result)


def test_unknown_top_level_keys_rejected():
    d = _valid_dict()
    d["mystery_field"] = "smuggled"
    result = uc.validate_config(d)
    assert isinstance(result, list)
    assert any("unknown top-level keys" in e.message for e in result)


def test_validation_collects_all_errors():
    """Validator should NOT short-circuit on the first failure; users get
    one pass of error output rather than a fix-and-rerun loop."""
    d = {
        "vendor": "Bad Vendor!",
        "config_name": "UPPERCASE",
        "contributor": "garbage",
        "target_subgroup": {"description": ""},
    }
    result = uc.validate_config(d)
    assert isinstance(result, list)
    # at least: vendor slug, config_name slug, contributor, target_subgroup.description,
    # vendor_version missing, harness_version missing
    assert len(result) >= 4


# --------------------------------------------------------------------------- #
# Submission attachment                                                       #
# --------------------------------------------------------------------------- #


def test_attach_to_submission_body_adds_user_config():
    cfg = uc.validate_config(_valid_dict())
    assert isinstance(cfg, uc.UserConfig)
    body = json.dumps({"benchmark": "synthbench", "config": {"provider": "synthpanel"}})
    stamped = uc.attach_to_submission_body(body, cfg)
    parsed = json.loads(stamped)
    assert parsed["benchmark"] == "synthbench"
    assert parsed["config"] == {"provider": "synthpanel"}
    assert parsed["user_config"]["vendor"] == "synthpanel"
    assert parsed["user_config"]["config_name"] == "wesley-healthcare-nc"


def test_attach_to_submission_body_emits_compact_json():
    """Compact serialisation matters because the Worker hashes the canonical
    body — the stamped output must not introduce whitespace that changes the
    hash across machines."""
    cfg = uc.validate_config(_valid_dict())
    assert isinstance(cfg, uc.UserConfig)
    body = json.dumps({"benchmark": "synthbench"})
    stamped = uc.attach_to_submission_body(body, cfg)
    assert ", " not in stamped
    assert ": " not in stamped


def test_attach_to_submission_body_rejects_non_object():
    cfg = uc.validate_config(_valid_dict())
    assert isinstance(cfg, uc.UserConfig)
    with pytest.raises(ValueError):
        uc.attach_to_submission_body(json.dumps([1, 2, 3]), cfg)


def test_attach_to_submission_body_canonicalises_key_order():
    """The user_config dict must come out in the schema's declared key order
    regardless of how the YAML was authored — keeps byte-stability across
    contributors who reorder fields."""
    d = _valid_dict()
    # Construct in shuffled order:
    shuffled = {
        "notes": "x",
        "decoding": d["decoding"],
        "vendor": d["vendor"],
        "vendor_version": d["vendor_version"],
        "config_name": d["config_name"],
        "contributor": d["contributor"],
        "harness_version": d["harness_version"],
        "target_subgroup": d["target_subgroup"],
    }
    cfg = uc.validate_config(shuffled)
    assert isinstance(cfg, uc.UserConfig)
    stamped = uc.attach_to_submission_body(json.dumps({"benchmark": "synthbench"}), cfg)
    parsed = json.loads(stamped)
    keys = list(parsed["user_config"].keys())
    assert keys[0] == "vendor"
    assert keys[1] == "vendor_version"
    assert keys[2] == "config_name"


# --------------------------------------------------------------------------- #
# Harness version cross-check                                                 #
# --------------------------------------------------------------------------- #


def test_harness_version_match():
    cfg = uc.validate_config(_valid_dict())
    assert isinstance(cfg, uc.UserConfig)
    assert uc.check_harness_version(cfg) is None


def test_harness_version_mismatch():
    d = _valid_dict()
    d["harness_version"] = "99.99.99"
    cfg = uc.validate_config(d)
    assert isinstance(cfg, uc.UserConfig)
    err = uc.check_harness_version(cfg)
    assert isinstance(err, uc.ConfigError)
    assert err.field == "harness_version"


# --------------------------------------------------------------------------- #
# Sample template                                                             #
# --------------------------------------------------------------------------- #


def test_shipped_template_validates():
    """The example file in templates/user-configs/ must pass validation, or
    we ship a broken contributor starting point."""
    from pathlib import Path

    template = (
        Path(__file__).resolve().parent.parent
        / "templates"
        / "user-configs"
        / "example-healthcare-northcentral.yaml"
    )
    assert template.exists(), f"missing template: {template}"
    result = uc.load_and_validate(template)
    assert isinstance(result, uc.UserConfig), result


# --------------------------------------------------------------------------- #
# CLI: validate-config                                                        #
# --------------------------------------------------------------------------- #


def test_cli_validate_config_success(tmp_path):
    p = _write_yaml(tmp_path, _valid_dict())
    res = CliRunner().invoke(main, ["validate-config", str(p)])
    assert res.exit_code == 0, res.output
    assert "valid" in res.output
    assert "synthpanel/wesley-healthcare-nc" in res.output


def test_cli_validate_config_failure(tmp_path):
    bad = _valid_dict()
    bad["vendor"] = "Bad Vendor!"
    p = _write_yaml(tmp_path, bad)
    res = CliRunner().invoke(main, ["validate-config", str(p)])
    assert res.exit_code == 2, res.output
    assert "invalid" in res.output
    assert "vendor" in res.output


def test_cli_validate_config_missing_file(tmp_path):
    res = CliRunner().invoke(main, ["validate-config", str(tmp_path / "nope.yaml")])
    # Click's path-exists check trips first.
    assert res.exit_code != 0


# --------------------------------------------------------------------------- #
# CLI: submit --config                                                        #
# --------------------------------------------------------------------------- #


VALID_KEY = "sb_" + "a" * 32


def _write_run(tmp_path):
    run = tmp_path / "result.json"
    run.write_text(
        json.dumps(
            {
                "benchmark": "synthbench",
                "config": {"provider": "synthpanel"},
                "aggregate": {"n_questions": 1, "composite_parity": 0.7},
                "per_question": [
                    {
                        "human_distribution": [0.5, 0.5],
                        "model_distribution": [0.5, 0.5],
                    }
                ],
                "scores": {"p_dist": 0.8},
            }
        )
    )
    return run


class _FakeResponse:
    def __init__(self, status_code, payload):
        self.status_code = status_code
        self.text = json.dumps(payload) if not isinstance(payload, str) else payload
        self._payload = payload

    def json(self):
        return self._payload


def test_cli_submit_config_stamps_user_config(tmp_path, monkeypatch):
    run = _write_run(tmp_path)
    cfg = _write_yaml(tmp_path, _valid_dict())
    captured = {}

    def fake_post(url, content=None, headers=None, timeout=None):
        captured["content"] = content
        return _FakeResponse(202, {"submission_id": 1, "status": "validating"})

    monkeypatch.setattr(httpx, "post", fake_post)
    monkeypatch.setenv("SYNTHBENCH_API_KEY", VALID_KEY)

    res = CliRunner().invoke(main, ["submit", "--config", str(cfg), str(run)])
    assert res.exit_code == 0, res.output
    assert "attaching user_config" in res.output
    sent = json.loads(captured["content"])
    assert sent["user_config"]["vendor"] == "synthpanel"
    assert sent["user_config"]["config_name"] == "wesley-healthcare-nc"
    # The existing body must be preserved.
    assert sent["benchmark"] == "synthbench"
    assert sent["config"] == {"provider": "synthpanel"}


def test_cli_submit_config_validation_failure_exits_2(tmp_path, monkeypatch):
    run = _write_run(tmp_path)
    bad = _valid_dict()
    bad["vendor"] = "Bad Vendor!"
    cfg = _write_yaml(tmp_path, bad)

    sent = {"called": False}

    def fake_post(*a, **kw):
        sent["called"] = True
        return _FakeResponse(200, {"submission_id": 1, "status": "validating"})

    monkeypatch.setattr(httpx, "post", fake_post)
    monkeypatch.setenv("SYNTHBENCH_API_KEY", VALID_KEY)

    res = CliRunner().invoke(main, ["submit", "--config", str(cfg), str(run)])
    assert res.exit_code == 2, res.output
    assert "Config validation failed" in res.output
    assert sent["called"] is False, "POST must not run when validation fails"


def test_cli_submit_config_harness_mismatch_blocks(tmp_path, monkeypatch):
    run = _write_run(tmp_path)
    d = _valid_dict()
    d["harness_version"] = "99.99.99"
    cfg = _write_yaml(tmp_path, d)

    def fake_post(*a, **kw):
        return _FakeResponse(200, {"submission_id": 1, "status": "validating"})

    monkeypatch.setattr(httpx, "post", fake_post)
    monkeypatch.setenv("SYNTHBENCH_API_KEY", VALID_KEY)

    res = CliRunner().invoke(main, ["submit", "--config", str(cfg), str(run)])
    assert res.exit_code == 2
    assert "harness" in res.output


def test_cli_submit_config_harness_mismatch_allowed(tmp_path, monkeypatch):
    run = _write_run(tmp_path)
    d = _valid_dict()
    d["harness_version"] = "99.99.99"
    cfg = _write_yaml(tmp_path, d)
    captured = {}

    def fake_post(url, content=None, headers=None, timeout=None):
        captured["content"] = content
        return _FakeResponse(202, {"submission_id": 7, "status": "validating"})

    monkeypatch.setattr(httpx, "post", fake_post)
    monkeypatch.setenv("SYNTHBENCH_API_KEY", VALID_KEY)

    res = CliRunner().invoke(
        main,
        [
            "submit",
            "--config",
            str(cfg),
            "--allow-harness-mismatch",
            str(run),
        ],
    )
    assert res.exit_code == 0, res.output
    sent = json.loads(captured["content"])
    assert sent["user_config"]["harness_version"] == "99.99.99"
