"""Tests for the user-contributed benchmark dataset artifact (sb-7je / Move 6).

The user-benchmark flow is the dataset twin of :mod:`synthbench.user_config`
(sb-vgb), so this suite intentionally mirrors ``tests/test_user_config.py``
case-for-case where the contract overlaps. New cases cover the parts that
have no analogue on the config side: question-list shape, distribution
mass + completeness, and the content hash.
"""

from __future__ import annotations

import json

import httpx
import pytest
from click.testing import CliRunner

from synthbench import __version__
from synthbench import user_benchmark as ub
from synthbench.cli import main


# --------------------------------------------------------------------------- #
# Helpers                                                                     #
# --------------------------------------------------------------------------- #


def _valid_dict() -> dict:
    return {
        "benchmark_id": "fintech-trust-2026q1",
        "title": "Fintech trust survey, Q1 2026",
        "contributor": "@wesley",
        "description": "Consumer trust in fintech products.",
        "domain": "fintech",
        "harness_version": __version__,
        "source": {
            "citation": "DataViking Internal Pilot, 2026-Q1",
            "license": "CC-BY-4.0",
            "url": "https://example.com/fintech-trust-2026q1",
        },
        "redistribution_policy": "aggregates_only",
        "questions": [
            {
                "key": f"q{i}",
                "text": f"Question {i}?",
                "options": ["A", "B"],
                "human_distribution": {"A": 0.6, "B": 0.4},
                "topic": "trust",
            }
            for i in range(5)
        ],
    }


def _write_json(tmp_path, payload, name="benchmark.json"):
    p = tmp_path / name
    p.write_text(json.dumps(payload))
    return p


# --------------------------------------------------------------------------- #
# JSON loading                                                                #
# --------------------------------------------------------------------------- #


def test_load_missing_file(tmp_path):
    err = ub.load_benchmark_file(tmp_path / "nope.json")
    assert isinstance(err, ub.BenchmarkError)
    assert "cannot read" in err.message


def test_load_malformed_json(tmp_path):
    p = tmp_path / "bad.json"
    p.write_text("{ this is not json")
    err = ub.load_benchmark_file(p)
    assert isinstance(err, ub.BenchmarkError)
    assert "invalid JSON" in err.message


def test_load_non_object_root(tmp_path):
    p = tmp_path / "list.json"
    p.write_text(json.dumps([1, 2, 3]))
    err = ub.load_benchmark_file(p)
    assert isinstance(err, ub.BenchmarkError)
    assert "must be an object" in err.message


def test_load_valid_returns_dict(tmp_path):
    p = _write_json(tmp_path, _valid_dict())
    result = ub.load_benchmark_file(p)
    assert isinstance(result, dict)
    assert result["benchmark_id"] == "fintech-trust-2026q1"


# --------------------------------------------------------------------------- #
# Top-level validation                                                        #
# --------------------------------------------------------------------------- #


def test_valid_dict_validates():
    result = ub.validate_benchmark(_valid_dict())
    assert isinstance(result, ub.UserBenchmark)
    assert result.benchmark_id == "fintech-trust-2026q1"
    assert result.domain == "fintech"
    assert result.n_questions == 5
    assert result.redistribution_policy == "aggregates_only"


def test_unknown_top_level_key_rejected():
    d = _valid_dict()
    d["surprise"] = "x"
    result = ub.validate_benchmark(d)
    assert isinstance(result, list)
    assert any("unknown top-level keys" in str(e) for e in result)


def test_missing_required_fields_all_collected():
    """The validator returns every error so contributors fix in one pass."""
    result = ub.validate_benchmark({"benchmark_id": "fine"})
    assert isinstance(result, list)
    # title, contributor, description, domain, harness_version,
    # source, redistribution_policy, questions — at minimum 8 misses.
    assert len(result) >= 8


def test_bad_slug_rejected():
    d = _valid_dict()
    d["benchmark_id"] = "Bad Benchmark!"
    result = ub.validate_benchmark(d)
    assert isinstance(result, list)
    assert any(e.field == "benchmark_id" for e in result)


def test_bad_domain_slug_rejected():
    d = _valid_dict()
    d["domain"] = "Health Care"
    result = ub.validate_benchmark(d)
    assert isinstance(result, list)
    assert any(e.field == "domain" for e in result)


def test_bad_contributor_rejected():
    d = _valid_dict()
    d["contributor"] = "not an @handle or email"
    result = ub.validate_benchmark(d)
    assert isinstance(result, list)
    assert any(e.field == "contributor" for e in result)


def test_email_contributor_accepted():
    d = _valid_dict()
    d["contributor"] = "wesley@dataviking.tech"
    result = ub.validate_benchmark(d)
    assert isinstance(result, ub.UserBenchmark)


# --------------------------------------------------------------------------- #
# source block                                                                #
# --------------------------------------------------------------------------- #


def test_source_must_be_mapping():
    d = _valid_dict()
    d["source"] = "DataViking pilot"
    result = ub.validate_benchmark(d)
    assert isinstance(result, list)
    assert any(e.field == "source" for e in result)


def test_source_requires_citation_and_license():
    d = _valid_dict()
    d["source"] = {"url": "https://example.com"}
    result = ub.validate_benchmark(d)
    assert isinstance(result, list)
    assert any(e.field == "source.citation" for e in result)
    assert any(e.field == "source.license" for e in result)


def test_source_rejects_unknown_keys():
    d = _valid_dict()
    d["source"] = {**d["source"], "secret_token": "x"}
    result = ub.validate_benchmark(d)
    assert isinstance(result, list)
    assert any(e.field == "source" and "secret_token" in e.message for e in result)


# --------------------------------------------------------------------------- #
# redistribution_policy                                                       #
# --------------------------------------------------------------------------- #


@pytest.mark.parametrize(
    "policy", ["full", "gated", "aggregates_only", "citation_only"]
)
def test_redistribution_policy_accepts_known(policy):
    d = _valid_dict()
    d["redistribution_policy"] = policy
    result = ub.validate_benchmark(d)
    assert isinstance(result, ub.UserBenchmark)


def test_redistribution_policy_rejects_unknown():
    d = _valid_dict()
    d["redistribution_policy"] = "public"
    result = ub.validate_benchmark(d)
    assert isinstance(result, list)
    assert any(e.field == "redistribution_policy" for e in result)


def test_redistribution_policy_required():
    d = _valid_dict()
    del d["redistribution_policy"]
    result = ub.validate_benchmark(d)
    assert isinstance(result, list)
    assert any(e.field == "redistribution_policy" for e in result)


# --------------------------------------------------------------------------- #
# questions list                                                              #
# --------------------------------------------------------------------------- #


def test_questions_must_be_list():
    d = _valid_dict()
    d["questions"] = {"q1": "..."}
    result = ub.validate_benchmark(d)
    assert isinstance(result, list)
    assert any(e.field == "questions" for e in result)


def test_too_few_questions_rejected():
    d = _valid_dict()
    d["questions"] = d["questions"][:2]
    result = ub.validate_benchmark(d)
    assert isinstance(result, list)
    assert any(e.field == "questions" and "at least" in e.message for e in result)


def test_duplicate_question_keys_rejected():
    d = _valid_dict()
    d["questions"][1]["key"] = d["questions"][0]["key"]
    result = ub.validate_benchmark(d)
    assert isinstance(result, list)
    assert any("duplicate key" in str(e) for e in result)


def test_question_options_min_two():
    d = _valid_dict()
    d["questions"][0]["options"] = ["only"]
    d["questions"][0]["human_distribution"] = {"only": 1.0}
    result = ub.validate_benchmark(d)
    assert isinstance(result, list)
    assert any(e.field == "questions[0].options" for e in result)


def test_question_options_duplicates_rejected():
    d = _valid_dict()
    d["questions"][0]["options"] = ["A", "A"]
    result = ub.validate_benchmark(d)
    assert isinstance(result, list)
    assert any(e.field == "questions[0].options" for e in result)


def test_human_distribution_must_sum_to_one():
    d = _valid_dict()
    d["questions"][0]["human_distribution"] = {"A": 0.7, "B": 0.7}
    result = ub.validate_benchmark(d)
    assert isinstance(result, list)
    assert any(
        e.field == "questions[0].human_distribution" and "sum to 1.0" in e.message
        for e in result
    )


def test_human_distribution_tolerates_rounding():
    """Within 0.01 we accept — same slack as the in-tree Question class."""
    d = _valid_dict()
    d["questions"][0]["human_distribution"] = {"A": 0.601, "B": 0.399}
    result = ub.validate_benchmark(d)
    assert isinstance(result, ub.UserBenchmark)


def test_human_distribution_rejects_out_of_range():
    d = _valid_dict()
    d["questions"][0]["human_distribution"] = {"A": 1.2, "B": -0.2}
    result = ub.validate_benchmark(d)
    assert isinstance(result, list)
    assert any("must be in [0, 1]" in str(e) for e in result)


def test_human_distribution_missing_option():
    """Every declared option must have mass — silent omission would mean a
    submitter is hiding a response from the leaderboard score."""
    d = _valid_dict()
    d["questions"][0]["human_distribution"] = {"A": 1.0}
    result = ub.validate_benchmark(d)
    assert isinstance(result, list)
    assert any("missing mass" in str(e) for e in result)


def test_human_distribution_extra_option():
    """Mass for an option that isn't declared is a typo, not a feature."""
    d = _valid_dict()
    d["questions"][0]["human_distribution"] = {"A": 0.5, "B": 0.4, "C": 0.1}
    result = ub.validate_benchmark(d)
    assert isinstance(result, list)
    assert any("not declared in options" in str(e) for e in result)


def test_question_unknown_keys_rejected():
    d = _valid_dict()
    d["questions"][0]["sneaky"] = "x"
    result = ub.validate_benchmark(d)
    assert isinstance(result, list)
    assert any(e.field == "questions[0]" and "sneaky" in e.message for e in result)


# --------------------------------------------------------------------------- #
# Hashing                                                                     #
# --------------------------------------------------------------------------- #


def test_hash_is_stable_across_authoring_order():
    """The hash is the leaderboard slice's content identity — two
    contributors who author the same questions in different orders must
    collide deliberately."""
    d1 = _valid_dict()
    d2 = _valid_dict()
    # Reorder the questions list and keys within a question.
    d2["questions"] = list(reversed(d2["questions"]))
    b1 = ub.validate_benchmark(d1)
    b2 = ub.validate_benchmark(d2)
    assert isinstance(b1, ub.UserBenchmark) and isinstance(b2, ub.UserBenchmark)
    # Different question order => different hash (order is semantically
    # meaningful for some surveys). But the same dict twice must hash same.
    assert ub.compute_benchmark_hash(b1) == ub.compute_benchmark_hash(
        ub.validate_benchmark(_valid_dict())
    )


def test_hash_ignores_prose_metadata():
    """Fixing a typo in the description must not mint a new slice
    identity; only the questions block keys the hash."""
    d1 = _valid_dict()
    d2 = _valid_dict()
    d2["description"] = "Totally different prose."
    d2["title"] = "Different title."
    d2["notes"] = "extra notes added"
    b1 = ub.validate_benchmark(d1)
    b2 = ub.validate_benchmark(d2)
    assert isinstance(b1, ub.UserBenchmark) and isinstance(b2, ub.UserBenchmark)
    assert ub.compute_benchmark_hash(b1) == ub.compute_benchmark_hash(b2)


def test_hash_changes_with_question_content():
    d1 = _valid_dict()
    d2 = _valid_dict()
    d2["questions"][0]["human_distribution"] = {"A": 0.5, "B": 0.5}
    b1 = ub.validate_benchmark(d1)
    b2 = ub.validate_benchmark(d2)
    assert isinstance(b1, ub.UserBenchmark) and isinstance(b2, ub.UserBenchmark)
    assert ub.compute_benchmark_hash(b1) != ub.compute_benchmark_hash(b2)


def test_hash_is_sha256_hex():
    b = ub.validate_benchmark(_valid_dict())
    assert isinstance(b, ub.UserBenchmark)
    h = ub.compute_benchmark_hash(b)
    assert len(h) == 64 and all(c in "0123456789abcdef" for c in h)


# --------------------------------------------------------------------------- #
# Submission attachment                                                       #
# --------------------------------------------------------------------------- #


def test_attach_to_submission_body_adds_user_benchmark():
    bm = ub.validate_benchmark(_valid_dict())
    assert isinstance(bm, ub.UserBenchmark)
    body = json.dumps({"benchmark": "synthbench", "config": {"provider": "openrouter"}})
    stamped = ub.attach_to_submission_body(body, bm)
    parsed = json.loads(stamped)
    assert parsed["benchmark"] == "synthbench"
    assert parsed["config"] == {"provider": "openrouter"}
    assert parsed["user_benchmark"]["benchmark_id"] == "fintech-trust-2026q1"
    assert parsed["user_benchmark"]["domain"] == "fintech"


def test_attach_to_submission_body_stamps_hash():
    bm = ub.validate_benchmark(_valid_dict())
    assert isinstance(bm, ub.UserBenchmark)
    body = json.dumps({"benchmark": "synthbench"})
    stamped = ub.attach_to_submission_body(body, bm)
    parsed = json.loads(stamped)
    assert parsed["user_benchmark"]["benchmark_hash"] == ub.compute_benchmark_hash(bm)


def test_attach_to_submission_body_emits_compact_json():
    """Compact serialisation matters because the Worker hashes the canonical
    body — the stamped output must not introduce whitespace that changes the
    hash across machines. We look for the JSON-level separators (``", "``
    between values, ``": "`` between keys and values) rather than any
    comma-space substring, because legitimate prose inside string values
    can contain commas-and-spaces."""
    bm = ub.validate_benchmark(_valid_dict())
    assert isinstance(bm, ub.UserBenchmark)
    body = json.dumps({"benchmark": "synthbench"})
    stamped = ub.attach_to_submission_body(body, bm)
    # Round-trip through compact dumps; the stamped output must already be
    # in canonical compact form, so re-dumping with the same settings
    # produces byte-identical output.
    parsed = json.loads(stamped)
    recompact = json.dumps(parsed, sort_keys=False, separators=(",", ":"))
    assert stamped == recompact


def test_attach_to_submission_body_rejects_non_object():
    bm = ub.validate_benchmark(_valid_dict())
    assert isinstance(bm, ub.UserBenchmark)
    with pytest.raises(ValueError):
        ub.attach_to_submission_body(json.dumps([1, 2, 3]), bm)


def test_attach_to_submission_body_canonicalises_key_order():
    """``user_benchmark`` keys must come out in the schema's declared order
    regardless of how the JSON was authored — keeps byte-stability across
    contributors who reorder fields."""
    d = _valid_dict()
    shuffled = {
        "notes": "x",
        "questions": d["questions"],
        "redistribution_policy": d["redistribution_policy"],
        "source": d["source"],
        "harness_version": d["harness_version"],
        "domain": d["domain"],
        "description": d["description"],
        "contributor": d["contributor"],
        "title": d["title"],
        "benchmark_id": d["benchmark_id"],
    }
    bm = ub.validate_benchmark(shuffled)
    assert isinstance(bm, ub.UserBenchmark)
    stamped = ub.attach_to_submission_body(json.dumps({"benchmark": "synthbench"}), bm)
    parsed = json.loads(stamped)
    keys = list(parsed["user_benchmark"].keys())
    assert keys[0] == "benchmark_id"
    assert keys[1] == "title"
    assert keys[2] == "contributor"


# --------------------------------------------------------------------------- #
# Harness version cross-check                                                 #
# --------------------------------------------------------------------------- #


def test_harness_version_match():
    bm = ub.validate_benchmark(_valid_dict())
    assert isinstance(bm, ub.UserBenchmark)
    assert ub.check_harness_version(bm) is None


def test_harness_version_mismatch():
    d = _valid_dict()
    d["harness_version"] = "99.99.99"
    bm = ub.validate_benchmark(d)
    assert isinstance(bm, ub.UserBenchmark)
    err = ub.check_harness_version(bm)
    assert isinstance(err, ub.BenchmarkError)
    assert err.field == "harness_version"


# --------------------------------------------------------------------------- #
# Shipped template                                                            #
# --------------------------------------------------------------------------- #


def test_shipped_template_validates():
    """The example file in templates/user-benchmarks/ must pass validation,
    or we ship a broken contributor starting point."""
    from pathlib import Path

    template = (
        Path(__file__).resolve().parent.parent
        / "templates"
        / "user-benchmarks"
        / "example-fintech-trust.json"
    )
    assert template.exists(), f"missing template: {template}"
    result = ub.load_and_validate(template)
    assert isinstance(result, ub.UserBenchmark), result


# --------------------------------------------------------------------------- #
# CLI: validate-benchmark                                                     #
# --------------------------------------------------------------------------- #


def test_cli_validate_benchmark_success(tmp_path):
    p = _write_json(tmp_path, _valid_dict())
    res = CliRunner().invoke(main, ["validate-benchmark", str(p)])
    assert res.exit_code == 0, res.output
    assert "valid" in res.output
    assert "fintech-trust-2026q1" in res.output
    assert "fintech" in res.output
    assert "hash:" in res.output


def test_cli_validate_benchmark_failure(tmp_path):
    bad = _valid_dict()
    bad["benchmark_id"] = "Bad Benchmark!"
    p = _write_json(tmp_path, bad)
    res = CliRunner().invoke(main, ["validate-benchmark", str(p)])
    assert res.exit_code == 2, res.output
    assert "invalid" in res.output
    assert "benchmark_id" in res.output


def test_cli_validate_benchmark_missing_file(tmp_path):
    res = CliRunner().invoke(main, ["validate-benchmark", str(tmp_path / "nope.json")])
    assert res.exit_code != 0


# --------------------------------------------------------------------------- #
# CLI: submit --benchmark                                                     #
# --------------------------------------------------------------------------- #


VALID_KEY = "sb_" + "a" * 32


def _write_run(tmp_path):
    run = tmp_path / "result.json"
    run.write_text(
        json.dumps(
            {
                "benchmark": "synthbench",
                "config": {"provider": "openrouter"},
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


def test_cli_submit_benchmark_stamps_user_benchmark(tmp_path, monkeypatch):
    run = _write_run(tmp_path)
    bm = _write_json(tmp_path, _valid_dict(), name="bm.json")
    captured = {}

    def fake_post(url, content=None, headers=None, timeout=None):
        captured["content"] = content
        return _FakeResponse(202, {"submission_id": 1, "status": "validating"})

    monkeypatch.setattr(httpx, "post", fake_post)
    monkeypatch.setenv("SYNTHBENCH_API_KEY", VALID_KEY)

    res = CliRunner().invoke(main, ["submit", "--benchmark", str(bm), str(run)])
    assert res.exit_code == 0, res.output
    assert "attaching user_benchmark" in res.output
    sent = json.loads(captured["content"])
    assert sent["user_benchmark"]["benchmark_id"] == "fintech-trust-2026q1"
    assert sent["user_benchmark"]["domain"] == "fintech"
    assert "benchmark_hash" in sent["user_benchmark"]
    assert len(sent["user_benchmark"]["benchmark_hash"]) == 64
    # The existing body must be preserved.
    assert sent["benchmark"] == "synthbench"
    assert sent["config"] == {"provider": "openrouter"}


def test_cli_submit_benchmark_validation_failure_exits_2(tmp_path, monkeypatch):
    run = _write_run(tmp_path)
    bad = _valid_dict()
    bad["benchmark_id"] = "Bad Benchmark!"
    bm = _write_json(tmp_path, bad, name="bm.json")

    sent = {"called": False}

    def fake_post(*a, **kw):
        sent["called"] = True
        return _FakeResponse(200, {"submission_id": 1, "status": "validating"})

    monkeypatch.setattr(httpx, "post", fake_post)
    monkeypatch.setenv("SYNTHBENCH_API_KEY", VALID_KEY)

    res = CliRunner().invoke(main, ["submit", "--benchmark", str(bm), str(run)])
    assert res.exit_code == 2, res.output
    assert "Benchmark validation failed" in res.output
    assert sent["called"] is False, "POST must not run when validation fails"


def test_cli_submit_benchmark_harness_mismatch_blocks(tmp_path, monkeypatch):
    run = _write_run(tmp_path)
    d = _valid_dict()
    d["harness_version"] = "99.99.99"
    bm = _write_json(tmp_path, d, name="bm.json")

    def fake_post(*a, **kw):
        return _FakeResponse(200, {"submission_id": 1, "status": "validating"})

    monkeypatch.setattr(httpx, "post", fake_post)
    monkeypatch.setenv("SYNTHBENCH_API_KEY", VALID_KEY)

    res = CliRunner().invoke(main, ["submit", "--benchmark", str(bm), str(run)])
    assert res.exit_code == 2
    assert "harness" in res.output


def test_cli_submit_benchmark_harness_mismatch_allowed(tmp_path, monkeypatch):
    run = _write_run(tmp_path)
    d = _valid_dict()
    d["harness_version"] = "99.99.99"
    bm = _write_json(tmp_path, d, name="bm.json")
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
            "--benchmark",
            str(bm),
            "--allow-harness-mismatch",
            str(run),
        ],
    )
    assert res.exit_code == 0, res.output
    sent = json.loads(captured["content"])
    assert sent["user_benchmark"]["harness_version"] == "99.99.99"


def test_cli_submit_benchmark_composes_with_config(tmp_path, monkeypatch):
    """--benchmark and --config must coexist on a single submission: the
    contributor publishes both how the vendor was tuned and what questions
    it was scored against."""
    import yaml

    run = _write_run(tmp_path)
    bm = _write_json(tmp_path, _valid_dict(), name="bm.json")

    cfg_dict = {
        "vendor": "synthpanel",
        "vendor_version": "1.4.0",
        "config_name": "wesley-fintech",
        "contributor": "@wesley",
        "harness_version": __version__,
        "target_subgroup": {
            "description": "Fintech-savvy consumers",
            "selector": {"industry": ["fintech"]},
        },
    }
    cfg = tmp_path / "cfg.yaml"
    cfg.write_text(yaml.safe_dump(cfg_dict, sort_keys=False))

    captured = {}

    def fake_post(url, content=None, headers=None, timeout=None):
        captured["content"] = content
        return _FakeResponse(202, {"submission_id": 9, "status": "validating"})

    monkeypatch.setattr(httpx, "post", fake_post)
    monkeypatch.setenv("SYNTHBENCH_API_KEY", VALID_KEY)

    res = CliRunner().invoke(
        main,
        ["submit", "--config", str(cfg), "--benchmark", str(bm), str(run)],
    )
    assert res.exit_code == 0, res.output
    sent = json.loads(captured["content"])
    assert sent["user_config"]["vendor"] == "synthpanel"
    assert sent["user_benchmark"]["benchmark_id"] == "fintech-trust-2026q1"
    assert sent["benchmark"] == "synthbench"
