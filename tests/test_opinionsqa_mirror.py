"""OpinionsQA raw-data fetch: R2 mirror, CodaLab fallback, and aggregation."""

from __future__ import annotations

import gzip
import hashlib
import io
import json
import tarfile
from pathlib import Path

import pytest

from synthbench.datasets import opinionsqa as oqa
from synthbench.datasets.base import DatasetDownloadError
from synthbench.r2_upload import R2Config, R2Uploader

INFO = (
    ",key,question,references,option_ordinal\n"
    "0,SAFE_W26,\"How safe?\",\"['Very safe', 'Not safe', 'Refused']\",\"[1.0, 2.0]\"\n"
    '1,EXTRA_W26,"Not canonical?","[\'Yes\', \'No\']","[1.0, 2.0]"\n'
)
RESPONSES = (
    ",QKEY,SAFE_W26,EXTRA_W26,WEIGHT_W26\n"
    "0,1,Very safe,Yes,3.0\n"
    "1,2,Very safe,No,0.5\n"
    "2,3,Not safe,Yes,1.0\n"
    "3,4,Refused,,1.0\n"
    "4,5,,Yes,1.0\n"
)


def _wave(root: Path) -> Path:
    wave = root / "human_resp" / "American_Trends_Panel_W26"
    wave.mkdir(parents=True)
    (wave / "info.csv").write_text(INFO, encoding="utf-8")
    (wave / "responses.csv").write_text(RESPONSES, encoding="utf-8")
    return wave


def _tar_gz(files: dict[str, bytes]) -> bytes:
    buf = io.BytesIO()
    with gzip.GzipFile(fileobj=buf, mode="wb", mtime=0) as gz:
        with tarfile.open(fileobj=gz, mode="w") as tf:
            for name, data in files.items():
                info = tarfile.TarInfo(name)
                info.size = len(data)
                tf.addfile(info, io.BytesIO(data))
    return buf.getvalue()


def test_build_canonical_wave_files_counts_unweighted_and_filters(tmp_path):
    wave = _wave(tmp_path)
    n = oqa.build_canonical_wave_files(tmp_path / "human_resp", ["SAFE_W26"])
    assert n == 1
    data = json.loads((wave / "NONE_data.json").read_text(encoding="utf-8"))
    # Unweighted counts (weights ignored), Refused kept, blanks skipped,
    # non-canonical keys left out.
    assert data == {
        "SAFE_W26": {"NONE": {"Very safe": 2.0, "Not safe": 1.0, "Refused": 1.0}}
    }


def test_adapter_loads_aggregated_files(tmp_path):
    _wave(tmp_path)
    oqa.build_canonical_wave_files(tmp_path / "human_resp", ["SAFE_W26"])
    ds = oqa.OpinionsQADataset(data_dir=tmp_path)
    (q,) = ds._process_raw_data(tmp_path)
    assert q.key == "SAFE_W26"
    assert q.human_distribution == pytest.approx(
        {"Very safe": 0.5, "Not safe": 0.25, "Refused": 0.25}
    )


def test_download_prefers_mirror_with_matching_sha(tmp_path, monkeypatch):
    blob = _tar_gz({"human_resp/American_Trends_Panel_W26/info.csv": INFO.encode()})
    monkeypatch.setattr(oqa, "MIRROR_SHA256", hashlib.sha256(blob).hexdigest())
    monkeypatch.setattr(oqa, "_fetch_mirror", lambda key, errors: blob)

    def no_codalab():
        raise AssertionError("CodaLab must not be used when the mirror is valid")

    monkeypatch.setattr(oqa, "fetch_codalab_human_resp", no_codalab)
    raw = tmp_path / "raw"
    oqa.OpinionsQADataset(data_dir=tmp_path)._download_from_codalab(raw)
    assert (raw / "human_resp" / "American_Trends_Panel_W26" / "info.csv").exists()


def test_mirror_sha_mismatch_falls_back_to_codalab(tmp_path, monkeypatch):
    monkeypatch.setattr(oqa, "_fetch_mirror", lambda key, errors: b"tampered")
    raw_bundle = _tar_gz(
        {
            "human_resp/American_Trends_Panel_W26/info.csv": INFO.encode(),
            "human_resp/American_Trends_Panel_W26/responses.csv": RESPONSES.encode(),
        }
    )
    monkeypatch.setattr(oqa, "fetch_codalab_human_resp", lambda: raw_bundle)
    monkeypatch.setattr(oqa, "load_canonical_keys", lambda: ["SAFE_W26"])
    raw = tmp_path / "raw"
    oqa.OpinionsQADataset(data_dir=tmp_path)._download_from_codalab(raw)
    assert (
        raw / "human_resp" / "American_Trends_Panel_W26" / "NONE_data.json"
    ).exists()


def test_all_sources_failing_reports_each(tmp_path, monkeypatch):
    monkeypatch.delenv("SYNTHBENCH_API_KEY", raising=False)

    def mirror(key, errors):
        errors.append("R2 mirror: R2_* env vars not set")

    def codalab():
        raise DatasetDownloadError("sha256 does not match pinned")

    monkeypatch.setattr(oqa, "_fetch_mirror", mirror)
    monkeypatch.setattr(oqa, "fetch_codalab_human_resp", codalab)
    with pytest.raises(DatasetDownloadError) as exc:
        oqa.OpinionsQADataset(data_dir=tmp_path)._download_from_codalab(
            tmp_path / "raw"
        )
    assert "R2 mirror" in str(exc.value)
    assert "CodaLab" in str(exc.value)


def test_codalab_bundle_sha_is_enforced(monkeypatch):
    class Resp:
        content = b"not the pinned bundle"

        def raise_for_status(self):
            pass

    monkeypatch.setattr(oqa.httpx, "get", lambda *a, **k: Resp())
    with pytest.raises(DatasetDownloadError, match="does not match pinned"):
        oqa.fetch_codalab_human_resp()


def test_extract_rejects_path_traversal(tmp_path):
    blob = _tar_gz({"../escape.txt": b"x"})
    with pytest.raises((DatasetDownloadError, tarfile.TarError)):
        oqa._extract_tar_gz(blob, tmp_path / "dest")
    assert not (tmp_path / "escape.txt").exists()


def test_canonical_keys_come_from_registry():
    keys = oqa.load_canonical_keys()
    assert len(keys) == 684


class _FakeS3:
    def __init__(self):
        self.objects: dict[str, bytes] = {}

    def put_object(self, *, Bucket, Key, Body, ContentType):
        self.objects[Key] = Body

    def get_object(self, *, Bucket, Key):
        if Key not in self.objects:
            err = Exception("missing")
            err.response = {"Error": {"Code": "NoSuchKey"}}
            raise err
        return {"Body": io.BytesIO(self.objects[Key])}


def test_r2_bytes_round_trip():
    cfg = R2Config(account_id="a", access_key_id="k", secret_access_key="s", bucket="b")
    r2 = R2Uploader(cfg, client=_FakeS3())
    assert r2.get_bytes("datasets/x.tar.gz") is None
    r2.put_bytes("/datasets/x.tar.gz", b"\x1f\x8b data", "application/gzip")
    assert r2.get_bytes("datasets/x.tar.gz") == b"\x1f\x8b data"


class _Resp:
    def __init__(
        self, status_code: int, content: bytes = b"", error: str | None = None
    ):
        self.status_code = status_code
        self.content = content
        self._error = error
        self.text = content.decode("utf-8", "replace")

    def json(self):
        return {"error": self._error}


def test_api_fetch_needs_a_key(monkeypatch):
    monkeypatch.delenv("SYNTHBENCH_API_KEY", raising=False)
    errors: list[str] = []
    assert oqa._fetch_via_api(oqa.MIRROR_KEY, errors) is None
    assert errors == ["synthbench.org: SYNTHBENCH_API_KEY not set"]


def test_api_fetch_sends_bearer_key(monkeypatch):
    monkeypatch.setenv("SYNTHBENCH_API_KEY", "sb_" + "r" * 32)
    monkeypatch.setenv("SYNTHBENCH_API_URL", "https://api.example.test/")
    seen = {}

    def fake_get(url, headers, **kwargs):
        seen["url"], seen["auth"] = url, headers["Authorization"]
        return _Resp(200, b"archive")

    monkeypatch.setattr(oqa.httpx, "get", fake_get)
    errors: list[str] = []
    assert oqa._fetch_via_api(oqa.MIRROR_KEY, errors) == b"archive"
    assert seen["url"] == f"https://api.example.test/data/{oqa.MIRROR_KEY}"
    assert seen["auth"] == "Bearer sb_" + "r" * 32
    assert errors == []


def test_api_fetch_reports_scope_errors(monkeypatch):
    monkeypatch.setenv("SYNTHBENCH_API_KEY", "sb_" + "s" * 32)
    monkeypatch.setattr(
        oqa.httpx, "get", lambda *a, **k: _Resp(403, b"{}", "api key lacks read scope")
    )
    errors: list[str] = []
    assert oqa._fetch_via_api(oqa.MIRROR_KEY, errors) is None
    assert errors == ["synthbench.org: HTTP 403 api key lacks read scope"]


def test_download_uses_api_when_no_r2(tmp_path, monkeypatch):
    blob = _tar_gz({"human_resp/American_Trends_Panel_W26/info.csv": INFO.encode()})
    monkeypatch.setattr(oqa, "MIRROR_SHA256", hashlib.sha256(blob).hexdigest())
    monkeypatch.setattr(oqa, "_fetch_mirror", lambda key, errors: None)
    monkeypatch.setattr(oqa, "_fetch_via_api", lambda key, errors: blob)
    raw = tmp_path / "raw"
    oqa.OpinionsQADataset(data_dir=tmp_path)._download_from_codalab(raw)
    assert (raw / "human_resp" / "American_Trends_Panel_W26" / "info.csv").exists()
