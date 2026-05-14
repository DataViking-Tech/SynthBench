"""User-configuration artifact loading and validation (sb-vgb / GH#257).

A *user configuration* describes how a contributor tuned a vendor adapter to
target a specific subgroup of respondents — system prompts, persona packs,
decoding parameters, ensemble weights. The leaderboard treats each
``{vendor}/{config_name}`` pair as its own row so a community-contributed
"healthcare workers in NC/MN/WI/IA" configuration shows up alongside (and
can outperform, on its target slice) the vendor's default settings.

This module is the schema/validator. The CLI calls :func:`load_config_file`
to read a YAML artifact, :func:`validate_config` to enforce the schema, and
:func:`attach_to_submission_body` to stamp the config block onto a run JSON
before it goes to ``POST /submit``.

The submission body grows one new top-level key, ``user_config``, carrying
the parsed-and-canonicalised dict. We keep it at the top level (not inside
``config``) so the existing canonical config_id hash, which only reads a
fixed set of keys under ``config``, is unaffected — the leaderboard row
identity is ``{vendor}/{config_name}``, not the underlying provider config.
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Optional, Union

import yaml

from synthbench import __version__

# Top-level keys we serialise into the submission body in a stable order.
# Anything not in this set is rejected at validation time so contributors
# can't smuggle opaque fields past the leaderboard.
_ALLOWED_KEYS: tuple[str, ...] = (
    "vendor",
    "vendor_version",
    "config_name",
    "contributor",
    "harness_version",
    "target_subgroup",
    "packs",
    "ensemble_weights",
    "extra_prompts",
    "decoding",
    "notes",
)

# Identifier regex for vendor and config_name — kebab-case ASCII so the
# composite ``{vendor}/{config_name}`` lands cleanly in a URL path segment
# and in filesystem paths under ``leaderboard-results/<vendor>/<config>/``.
_SLUG_RE = re.compile(r"^[a-z0-9][a-z0-9-]{0,62}[a-z0-9]$")

# Contributor handle: GitHub-style ``@username`` or a bare email. Kept
# permissive (no GitHub API call) so offline validation works.
_HANDLE_RE = re.compile(r"^@[A-Za-z0-9](?:[A-Za-z0-9-]{0,38})$")
_EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


@dataclass
class ConfigError:
    """Structured validation failure. ``field`` points at the offending key
    (dotted path for nested dicts) so the CLI can print actionable lines.
    """

    field: str
    message: str

    def __str__(self) -> str:
        return f"{self.field}: {self.message}" if self.field else self.message


@dataclass
class UserConfig:
    """Parsed-and-validated config artifact, ready to embed in a submission.

    ``raw`` keeps the original (already-canonicalised) dict so the caller
    can attach it verbatim to the submission body without re-serialising
    through the dataclass layer.
    """

    vendor: str
    vendor_version: str
    config_name: str
    contributor: str
    harness_version: str
    raw: dict[str, Any]

    @property
    def leaderboard_row_key(self) -> str:
        """The string the leaderboard uses to identify the row this config
        produces. ``{vendor}/{config_name}`` — pinned so renaming either
        field deliberately creates a new row."""
        return f"{self.vendor}/{self.config_name}"


# --- Loading -----------------------------------------------------------------


def load_config_file(path: Union[str, Path]) -> Union[dict[str, Any], ConfigError]:
    """Read a YAML config file from disk and return its parsed dict.

    Returns a :class:`ConfigError` for IO failures, non-YAML content, or a
    document that doesn't parse to a mapping. The caller is expected to
    pipe the dict through :func:`validate_config` before trusting any field.
    """
    p = Path(path)
    try:
        text = p.read_text()
    except OSError as exc:
        return ConfigError(field="", message=f"cannot read {p}: {exc}")
    try:
        data = yaml.safe_load(text)
    except yaml.YAMLError as exc:
        return ConfigError(field="", message=f"{p}: invalid YAML: {exc}")
    if data is None:
        return ConfigError(field="", message=f"{p}: empty config file")
    if not isinstance(data, dict):
        return ConfigError(
            field="",
            message=f"{p}: top-level YAML must be a mapping, got {type(data).__name__}",
        )
    return data


# --- Validation --------------------------------------------------------------


def _check_str(data: dict, key: str, errors: list[ConfigError]) -> Optional[str]:
    val = data.get(key)
    if not isinstance(val, str) or not val.strip():
        errors.append(ConfigError(key, "required non-empty string"))
        return None
    return val.strip()


def _check_slug(value: Optional[str], field: str, errors: list[ConfigError]) -> None:
    if value is None:
        return
    if not _SLUG_RE.match(value):
        errors.append(
            ConfigError(
                field,
                "must be kebab-case ASCII slug: lowercase letters, digits, "
                "and internal hyphens, 2-64 chars",
            )
        )


def _check_contributor(value: Optional[str], errors: list[ConfigError]) -> None:
    if value is None:
        return
    if _HANDLE_RE.match(value) or _EMAIL_RE.match(value):
        return
    errors.append(
        ConfigError(
            "contributor",
            "must be a GitHub-style @handle or a bare email address",
        )
    )


def _check_target_subgroup(data: dict, errors: list[ConfigError]) -> None:
    sub = data.get("target_subgroup")
    if sub is None:
        errors.append(ConfigError("target_subgroup", "required"))
        return
    if not isinstance(sub, dict):
        errors.append(ConfigError("target_subgroup", "must be a mapping"))
        return
    desc = sub.get("description")
    if not isinstance(desc, str) or not desc.strip():
        errors.append(
            ConfigError("target_subgroup.description", "required non-empty string")
        )
    selector = sub.get("selector")
    if selector is None:
        # Selector is optional — a contributor can describe a subgroup
        # qualitatively without machine-checkable criteria. Win-region
        # computation falls back to whole-bench scoring in that case.
        return
    if not isinstance(selector, dict):
        errors.append(ConfigError("target_subgroup.selector", "must be a mapping"))
        return
    for k, v in selector.items():
        if not isinstance(k, str):
            errors.append(
                ConfigError("target_subgroup.selector", f"non-string key: {k!r}")
            )
            continue
        if not isinstance(v, list) or not all(isinstance(x, str) for x in v):
            errors.append(
                ConfigError(
                    f"target_subgroup.selector.{k}",
                    "must be a list of strings",
                )
            )


def _check_ensemble_weights(data: dict, errors: list[ConfigError]) -> None:
    weights = data.get("ensemble_weights")
    if weights is None:
        return
    if not isinstance(weights, list) or not weights:
        errors.append(
            ConfigError("ensemble_weights", "must be a non-empty list of floats")
        )
        return
    for i, w in enumerate(weights):
        if not isinstance(w, (int, float)) or isinstance(w, bool):
            errors.append(ConfigError(f"ensemble_weights[{i}]", "must be a number"))
            return
        if w < 0:
            errors.append(ConfigError(f"ensemble_weights[{i}]", "must be non-negative"))
            return
    total = sum(weights)
    if total <= 0 or abs(total - 1.0) > 1e-3:
        errors.append(
            ConfigError(
                "ensemble_weights",
                f"must sum to 1.0 (got {total:.4f}); rescale or drop the field",
            )
        )
    packs = data.get("packs")
    if isinstance(packs, list) and len(packs) != len(weights):
        errors.append(
            ConfigError(
                "ensemble_weights",
                f"length ({len(weights)}) must match packs length ({len(packs)})",
            )
        )


def _check_packs(data: dict, errors: list[ConfigError]) -> None:
    packs = data.get("packs")
    if packs is None:
        return
    if not isinstance(packs, list) or not packs:
        errors.append(ConfigError("packs", "must be a non-empty list of strings"))
        return
    for i, p in enumerate(packs):
        if not isinstance(p, str) or not p.strip():
            errors.append(ConfigError(f"packs[{i}]", "must be a non-empty string"))


def _check_extra_prompts(data: dict, errors: list[ConfigError]) -> None:
    prompts = data.get("extra_prompts")
    if prompts is None:
        return
    if not isinstance(prompts, dict):
        errors.append(ConfigError("extra_prompts", "must be a mapping"))
        return
    for k, v in prompts.items():
        if not isinstance(k, str):
            errors.append(ConfigError("extra_prompts", f"non-string key: {k!r}"))
            continue
        if not isinstance(v, str):
            errors.append(ConfigError(f"extra_prompts.{k}", "must be a string"))


def _check_decoding(data: dict, errors: list[ConfigError]) -> None:
    dec = data.get("decoding")
    if dec is None:
        return
    if not isinstance(dec, dict):
        errors.append(ConfigError("decoding", "must be a mapping"))
        return
    # Bounded numeric checks for the two knobs every provider uses. Other
    # keys (model, top_k, ...) pass through unvalidated — providers vary.
    temp = dec.get("temperature")
    if temp is not None:
        if not isinstance(temp, (int, float)) or isinstance(temp, bool) or temp < 0:
            errors.append(
                ConfigError("decoding.temperature", "must be a non-negative number")
            )
    top_p = dec.get("top_p")
    if top_p is not None:
        if (
            not isinstance(top_p, (int, float))
            or isinstance(top_p, bool)
            or not (0 <= top_p <= 1)
        ):
            errors.append(ConfigError("decoding.top_p", "must be a number in [0, 1]"))


def validate_config(
    data: dict[str, Any],
) -> Union[UserConfig, list[ConfigError]]:
    """Validate a parsed config dict against the schema.

    Returns a :class:`UserConfig` on success, or a list of :class:`ConfigError`
    on failure. We collect *all* errors instead of failing on the first so a
    contributor can fix everything in one pass rather than re-running after
    each fix.
    """
    errors: list[ConfigError] = []

    if not isinstance(data, dict):
        return [ConfigError("", "top-level config must be a mapping")]

    unknown = sorted(set(data) - set(_ALLOWED_KEYS))
    if unknown:
        errors.append(
            ConfigError(
                "",
                f"unknown top-level keys: {', '.join(unknown)}. "
                f"Allowed: {', '.join(_ALLOWED_KEYS)}",
            )
        )

    vendor = _check_str(data, "vendor", errors)
    vendor_version = _check_str(data, "vendor_version", errors)
    config_name = _check_str(data, "config_name", errors)
    contributor = _check_str(data, "contributor", errors)
    harness_version = _check_str(data, "harness_version", errors)

    _check_slug(vendor, "vendor", errors)
    _check_slug(config_name, "config_name", errors)
    _check_contributor(contributor, errors)

    _check_target_subgroup(data, errors)
    _check_packs(data, errors)
    _check_ensemble_weights(data, errors)
    _check_extra_prompts(data, errors)
    _check_decoding(data, errors)

    notes = data.get("notes")
    if notes is not None and not isinstance(notes, str):
        errors.append(ConfigError("notes", "must be a string"))

    if errors:
        return errors

    assert vendor and vendor_version and config_name and contributor
    assert harness_version
    return UserConfig(
        vendor=vendor,
        vendor_version=vendor_version,
        config_name=config_name,
        contributor=contributor,
        harness_version=harness_version,
        raw=_canonicalise(data),
    )


def _canonicalise(data: dict[str, Any]) -> dict[str, Any]:
    """Reorder keys to match :data:`_ALLOWED_KEYS` so the embedded config
    block is byte-stable across machines. Nested dicts keep their insertion
    order — only the top-level layout is normalised.
    """
    return {k: data[k] for k in _ALLOWED_KEYS if k in data}


# --- Loading + validation (convenience) --------------------------------------


def load_and_validate(
    path: Union[str, Path],
) -> Union[UserConfig, list[ConfigError]]:
    """One-shot: read YAML from disk and validate. Returns either the parsed
    :class:`UserConfig` or a list of :class:`ConfigError`."""
    parsed = load_config_file(path)
    if isinstance(parsed, ConfigError):
        return [parsed]
    return validate_config(parsed)


# --- Attaching to a submission body ------------------------------------------


def attach_to_submission_body(body: str, config: UserConfig) -> str:
    """Return a new submission body string with ``user_config`` stamped on.

    The input ``body`` MUST be valid JSON serialising a top-level object.
    We re-serialise compactly (no spaces, no trailing whitespace) so the
    server-side hash that anchors the leaderboard row identity stays
    deterministic across CLI invocations.

    The ``harness_version`` declared in the config is cross-checked against
    the installed :mod:`synthbench` version. A mismatch surfaces as a
    :class:`ConfigError` because the leaderboard pins each row to a harness
    version — silently submitting under a different harness would break the
    "reproducible artifact" contract the contributor signed up for.
    """
    data = json.loads(body)
    if not isinstance(data, dict):
        raise ValueError("submission body must be a JSON object at the top level")
    data["user_config"] = config.raw
    return json.dumps(data, sort_keys=False, separators=(",", ":"))


def check_harness_version(config: UserConfig) -> Optional[ConfigError]:
    """Compare ``config.harness_version`` against the installed harness.

    Returns ``None`` on a match and a :class:`ConfigError` otherwise. Kept
    as a standalone helper so the CLI can downgrade the mismatch to a
    warning if a future ``--allow-harness-mismatch`` flag is added; the
    library never decides exit codes itself.
    """
    if config.harness_version != __version__:
        return ConfigError(
            "harness_version",
            f"config pins harness {config.harness_version!r} but installed "
            f"synthbench is {__version__!r}. Re-run the benchmark against the "
            f"pinned harness or bump the field deliberately.",
        )
    return None
