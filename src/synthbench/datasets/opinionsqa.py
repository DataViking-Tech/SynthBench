"""OpinionsQA dataset loader.

Loads the 684 canonical survey questions of the OpinionsQA dataset
(Santurkar et al., ICML 2023) based on Pew American Trends Panel data.

Data source: https://worksheets.codalab.org/worksheets/0x6fb693719477478aac73fc07db333f69
Paper: https://arxiv.org/abs/2303.17548

Raw data is fetched, in order, from:

1. SynthBench's private R2 mirror (``datasets/opinionsqa/...`` in the gated
   bucket, when the ``R2_*`` env vars are set): the canonical per-wave files
   (``info.csv`` + ``NONE_data.json``) for the 684 questions the leaderboard
   uses, built by ``scripts/build-opinionsqa-mirror.py``.
2. CodaLab's ``human_resp`` bundle, aggregated locally with
   :func:`build_canonical_wave_files`. This needs a repo checkout, because the
   canonical key list lives in ``data/question-text-registries/opinionsqa.json``.

Both downloads are pinned to a sha256, so a tampered or changed upstream file
is rejected rather than silently scored.
"""

from __future__ import annotations

import csv
import hashlib
import io
import json
import tarfile
from collections import defaultdict
from ast import literal_eval
from pathlib import Path

import httpx

from synthbench.datasets.base import Dataset, DatasetDownloadError, Question

_CODALAB_WORKSHEET = "0x6fb693719477478aac73fc07db333f69"
_CODALAB_API = "https://worksheets.codalab.org/rest"

# The worksheet's `human_resp` bundle (raw per-respondent answers). Its other
# bundles are not needed (`runs` alone is 4.1 GB).
CODALAB_HUMAN_RESP_BUNDLE = "0x050b7e72abb04d1f9b493c1743e580cf"
CODALAB_HUMAN_RESP_SHA256 = (
    "e58f634fc5b24a8cac9b8cfc068871b0ae70027ae5c47089bc7c08d88e762103"
)

# Canonical per-wave files in the gated R2 bucket (see module docstring).
MIRROR_KEY = "datasets/opinionsqa/human_resp-canonical-v1.tar.gz"
MIRROR_SHA256 = "e0193599bebbbb1c2498df82f0d8ce5784d5b4ca6abdf5f42298a117d7ab8666"
# The raw CodaLab bundle, mirrored unchanged for provenance.
MIRROR_RAW_KEY = (
    f"datasets/opinionsqa/codalab-{CODALAB_HUMAN_RESP_BUNDLE}-human_resp.tar.gz"
)

_REGISTRY_PATH = (
    Path(__file__).resolve().parents[3]
    / "data"
    / "question-text-registries"
    / "opinionsqa.json"
)

# Surveys included in OpinionsQA
PEW_WAVES = [26, 27, 29, 32, 34, 36, 41, 42, 43, 45, 49, 50, 54, 82, 92]

# ATP wave number → survey fielding year (Pew American Trends Panel)
WAVE_YEAR_MAP: dict[int, int] = {
    26: 2017,
    27: 2017,
    29: 2017,
    32: 2018,
    34: 2018,
    36: 2019,
    41: 2019,
    42: 2019,
    43: 2019,
    45: 2019,
    49: 2020,
    50: 2020,
    54: 2020,
    82: 2022,
    92: 2022,
}


def wave_year(survey: str) -> int:
    """Extract survey year from an ATP survey label like 'ATP W82'.

    Falls back to 0 if the wave number is unrecognised.
    """
    if survey.startswith("ATP W"):
        try:
            wave_num = int(survey.removeprefix("ATP W"))
            return WAVE_YEAR_MAP.get(wave_num, 0)
        except ValueError:
            pass
    return 0


def _default_cache_dir() -> Path:
    return Path.home() / ".synthbench" / "data" / "opinionsqa"


class OpinionsQADataset(Dataset):
    """OpinionsQA: 1,498 questions from Pew American Trends Panel."""

    # The CodaLab worksheet does not publish an explicit license and the
    # underlying Pew ATP data carries its own redistribution restrictions.
    # Per founder direction (sb-dek, 2026-04-15): treated as ``gated``
    # alongside other research-use datasets (SubPOP, WVS, Pew Tech, etc.)
    # — per-question artifacts ship via Cloudflare R2 behind the Supabase
    # JWT gate, never anonymously.
    redistribution_policy = "gated"
    license_url = (
        "https://worksheets.codalab.org/worksheets/0x6fb693719477478aac73fc07db333f69"
    )
    citation = (
        "Santurkar et al., ICML 2023 — Whose Opinions Do LLMs Reflect? "
        "(derived from Pew American Trends Panel)"
    )

    def __init__(self, data_dir: Path | str | None = None):
        self._data_dir = Path(data_dir) if data_dir else _default_cache_dir()

    @property
    def name(self) -> str:
        return "opinionsqa"

    def info(self) -> dict:
        return {
            "name": "OpinionsQA",
            "source": "Santurkar et al., ICML 2023",
            "paper": "https://arxiv.org/abs/2303.17548",
            "n_questions": 1498,
            "n_waves": len(PEW_WAVES),
            "demographics": 13,
        }

    def load(self, n: int | None = None) -> list[Question]:
        cache_path = self._data_dir / "questions.json"

        if cache_path.exists():
            questions = self._load_cached(cache_path)
        else:
            questions = self._download_and_process()

        if n is not None:
            questions = questions[:n]
        return questions

    def _load_cached(self, path: Path) -> list[Question]:
        with open(path) as f:
            data = json.load(f)
        return [
            Question(
                key=q["key"],
                text=q["text"],
                options=q["options"],
                human_distribution=q["human_distribution"],
                survey=q.get("survey", ""),
                topic=q.get("topic", ""),
            )
            for q in data["questions"]
        ]

    def _save_cache(self, questions: list[Question]) -> None:
        self._data_dir.mkdir(parents=True, exist_ok=True)
        data = {
            "dataset": "opinionsqa",
            "version": "1.0",
            "n_questions": len(questions),
            "questions": [
                {
                    "key": q.key,
                    "text": q.text,
                    "options": q.options,
                    "human_distribution": q.human_distribution,
                    "survey": q.survey,
                    "topic": q.topic,
                }
                for q in questions
            ],
        }
        cache_path = self._data_dir / "questions.json"
        with open(cache_path, "w") as f:
            json.dump(data, f, indent=2)

    def _download_and_process(self) -> list[Question]:
        """Try to download from CodaLab, then process raw data."""
        raw_dir = self._data_dir / "raw"

        if not raw_dir.exists():
            self._download_from_codalab(raw_dir)

        questions = self._process_raw_data(raw_dir)
        self._save_cache(questions)
        return questions

    def _download_from_codalab(self, raw_dir: Path) -> None:
        """Fetch raw data into *raw_dir*: R2 mirror first, then CodaLab."""
        raw_dir.mkdir(parents=True, exist_ok=True)
        errors: list[str] = []

        blob = _fetch_mirror(MIRROR_KEY, errors)
        if blob is not None:
            if _sha256(blob) == MIRROR_SHA256:
                _extract_tar_gz(blob, raw_dir)
                return
            errors.append("R2 mirror: sha256 mismatch, ignoring the mirrored copy")

        try:
            blob = fetch_codalab_human_resp()
            _extract_tar_gz(blob, raw_dir)
            human_resp = self._find_subdir(raw_dir, "human_resp") or raw_dir
            build_canonical_wave_files(human_resp, load_canonical_keys())
        except Exception as e:  # noqa: BLE001 - surface every source's failure
            errors.append(f"CodaLab: {e}")
            raise DatasetDownloadError(
                "Could not fetch OpinionsQA data:\n  - "
                + "\n  - ".join(errors)
                + "\n\nSet the R2_* env vars to use SynthBench's mirror, or run from a "
                "repo checkout so the CodaLab bundle can be aggregated."
            ) from e

    def _process_raw_data(self, raw_dir: Path) -> list[Question]:
        """Process raw OpinionsQA data into Question objects.

        Expected directory structure under raw_dir:
          human_resp/American_Trends_Panel_W{N}/
            info.csv          — question metadata (key, question, references, ...)
            NONE_data.json    — overall response counts (preferred)
            *_data.json       — demographic response counts (fallback)
        """
        human_resp_dir = self._find_subdir(raw_dir, "human_resp")

        if human_resp_dir is None:
            raise DatasetDownloadError(
                f"Expected human_resp/ directory in {raw_dir}.\n"
                "Download the OpinionsQA dataset and extract it there."
            )

        questions: list[Question] = []

        for wave in PEW_WAVES:
            wave_dir = human_resp_dir / f"American_Trends_Panel_W{wave}"
            if not wave_dir.is_dir():
                continue

            info_path = wave_dir / "info.csv"
            if not info_path.exists():
                continue

            # Load response distributions from JSON
            dist_by_key = self._load_wave_distributions(wave_dir)

            for row in self._read_csv(info_path):
                qkey = row.get("key", "")
                if not qkey:
                    continue

                refs_raw = row.get("references", "")
                try:
                    refs = literal_eval(refs_raw) if refs_raw else []
                except (ValueError, SyntaxError):
                    refs = [r.strip() for r in refs_raw.split(",")]

                if not refs:
                    continue

                question_text = row.get("question", qkey)
                human_dist = dist_by_key.get(qkey, {})

                if not human_dist:
                    continue

                questions.append(
                    Question(
                        key=qkey,
                        text=question_text,
                        options=refs,
                        human_distribution=human_dist,
                        survey=f"ATP W{wave}",
                    )
                )

        return questions

    @staticmethod
    def _load_wave_distributions(wave_dir: Path) -> dict[str, dict[str, float]]:
        """Load aggregated human response distributions for one survey wave.

        Prefers NONE_data.json (overall population). Falls back to summing
        sub-groups from the first available demographic *_data.json.
        Returns {question_key: {option: count}} (unnormalized — Question
        __post_init__ handles normalization).
        """
        # Prefer NONE_data.json; fall back to any *_data.json
        none_path = wave_dir / "NONE_data.json"
        json_path = None
        if none_path.exists():
            json_path = none_path
        else:
            for p in sorted(wave_dir.glob("*_data.json")):
                json_path = p
                break

        if json_path is None:
            return {}

        with open(json_path) as f:
            data = json.load(f)

        result: dict[str, dict[str, float]] = {}
        for qkey, entry in data.items():
            if not isinstance(entry, dict):
                continue
            totals: dict[str, float] = {}
            for sub_key, counts in entry.items():
                if sub_key in ("MC_options", "question_text"):
                    continue
                if not isinstance(counts, dict):
                    continue
                for option, val in counts.items():
                    totals[option] = totals.get(option, 0.0) + float(val)
            if totals:
                result[qkey] = totals
        return result

    @staticmethod
    def _find_subdir(root: Path, name: str) -> Path | None:
        if (root / name).is_dir():
            return root / name
        for p in root.rglob(name):
            if p.is_dir():
                return p
        return None

    @staticmethod
    def _read_csv(path: Path) -> list[dict[str, str]]:
        with open(path, newline="", encoding="utf-8-sig") as f:
            reader = csv.DictReader(f)
            return list(reader)

    # The 8 universal demographic attributes in OpinionsQA
    DEMOGRAPHIC_ATTRIBUTES = [
        "AGE",
        "CREGION",
        "EDUCATION",
        "INCOME",
        "POLIDEOLOGY",
        "POLPARTY",
        "RACE",
        "SEX",
    ]

    def load_demographic_distributions(
        self,
        attribute: str,
    ) -> dict[str, dict[str, dict[str, float]]]:
        """Load per-group human distributions for a demographic attribute.

        Reads {attribute}_data.json from each survey wave directory and
        aggregates them into a single mapping.

        Args:
            attribute: Demographic attribute name (e.g., "AGE", "POLIDEOLOGY").
                Must be one of the 8 universal OpinionsQA attributes.

        Returns:
            {question_key: {group_name: {option: probability}}}
            Counts are normalized to probabilities per group.
        """
        raw_dir = self._data_dir / "raw"
        human_resp_dir = self._find_subdir(raw_dir, "human_resp")
        if human_resp_dir is None:
            return {}

        result: dict[str, dict[str, dict[str, float]]] = {}

        for wave in PEW_WAVES:
            wave_dir = human_resp_dir / f"American_Trends_Panel_W{wave}"
            attr_path = wave_dir / f"{attribute}_data.json"
            if not attr_path.exists():
                continue

            with open(attr_path) as f:
                data = json.load(f)

            for qkey, entry in data.items():
                if not isinstance(entry, dict):
                    continue

                groups: dict[str, dict[str, float]] = {}
                for sub_key, counts in entry.items():
                    if sub_key in ("MC_options", "question_text"):
                        continue
                    if sub_key == "nan":
                        continue
                    if not isinstance(counts, dict):
                        continue

                    # Normalize counts to probabilities
                    total = sum(float(v) for v in counts.values())
                    if total <= 0:
                        continue
                    groups[sub_key] = {
                        opt: float(val) / total for opt, val in counts.items()
                    }

                if groups:
                    result[qkey] = groups

        return result


# ---------------------------------------------------------------------------
# Raw-data helpers (mirror + CodaLab)
# ---------------------------------------------------------------------------


def _sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _extract_tar_gz(blob: bytes, dest: Path) -> None:
    """Extract a gzip tarball, refusing members that escape *dest*."""
    with tarfile.open(fileobj=io.BytesIO(blob), mode="r:gz") as tf:
        if hasattr(tarfile, "data_filter"):
            tf.extractall(dest, filter="data")
            return
        root = dest.resolve()
        for member in tf.getmembers():
            target = (dest / member.name).resolve()
            if root not in target.parents and target != root:
                raise DatasetDownloadError(f"Unsafe path in archive: {member.name}")
            if not (member.isfile() or member.isdir()):
                raise DatasetDownloadError(f"Unsupported archive member: {member.name}")
        tf.extractall(dest)


def _fetch_mirror(key: str, errors: list[str]) -> bytes | None:
    """Read *key* from the gated R2 bucket, or ``None`` if unavailable."""
    from synthbench.r2_upload import R2Uploader, env_has_r2_config

    if not env_has_r2_config():
        errors.append("R2 mirror: R2_* env vars not set")
        return None
    try:
        blob = R2Uploader.from_env().get_bytes(key)
    except Exception as e:  # noqa: BLE001
        errors.append(f"R2 mirror: {e}")
        return None
    if blob is None:
        errors.append(f"R2 mirror: {key} not found")
    return blob


def fetch_codalab_human_resp() -> bytes:
    """Download CodaLab's human_resp bundle and check it against the pinned sha256.

    TLS verification is off for this request: worksheets.codalab.org served an
    expired certificate as of 2026-10-10. The pinned sha256 is what
    authenticates the content, so a changed or tampered bundle is rejected.
    """
    url = f"{_CODALAB_API}/bundles/{CODALAB_HUMAN_RESP_BUNDLE}/contents/blob/"
    resp = httpx.get(url, timeout=300, follow_redirects=True, verify=False)
    resp.raise_for_status()
    digest = _sha256(resp.content)
    if digest != CODALAB_HUMAN_RESP_SHA256:
        raise DatasetDownloadError(
            f"CodaLab human_resp bundle sha256 {digest} does not match pinned "
            f"{CODALAB_HUMAN_RESP_SHA256}; refusing to use it."
        )
    return resp.content


def load_canonical_keys(path: Path = _REGISTRY_PATH) -> list[str]:
    """The canonical OpinionsQA question keys (repo checkout only)."""
    if not path.exists():
        raise DatasetDownloadError(
            f"Canonical OpinionsQA key list not found at {path}; it ships with the "
            "repository, not the package."
        )
    return list(json.loads(path.read_text(encoding="utf-8"))["questions"])


def build_canonical_wave_files(human_resp_dir: Path, canonical_keys: list[str]) -> int:
    """Write NONE_data.json for each wave from the raw responses.csv.

    CodaLab's current human_resp bundle ships per-respondent answers rather
    than aggregated NONE_data.json files. Each canonical question becomes
    ``{key: {"NONE": {option: count}}}`` with **unweighted** response counts,
    "Refused" kept as an option: the recipe that reproduces the human
    distributions the leaderboard's existing OpinionsQA runs were scored
    against. Only canonical keys are written, so ``load(n=...)`` selects the
    same questions as published runs. Returns the number of questions written.
    """
    canonical = set(canonical_keys)
    csv.field_size_limit(10**9)
    written = 0
    for wave_dir in sorted(human_resp_dir.glob("American_Trends_Panel_W*")):
        with open(wave_dir / "info.csv", encoding="utf-8") as f:
            info = list(csv.DictReader(f))
        wanted = [q for q in info if q["key"] in canonical]
        if not wanted:
            continue
        with open(wave_dir / "responses.csv", encoding="utf-8") as f:
            rows = list(csv.DictReader(f))
        out: dict[str, dict] = {}
        for q in wanted:
            key = q["key"]
            options = literal_eval(q["references"])
            counts: dict[str, float] = defaultdict(float)
            for r in rows:
                answer = r.get(key)
                if answer in options:
                    counts[answer] += 1.0
            if counts:
                out[key] = {"NONE": {opt: counts.get(opt, 0.0) for opt in options}}
        (wave_dir / "NONE_data.json").write_text(json.dumps(out), encoding="utf-8")
        written += len(out)
    return written
