#!/usr/bin/env python3
"""Build (and optionally upload) SynthBench's OpinionsQA mirror.

Downloads CodaLab's human_resp bundle (sha256-pinned), aggregates it into the
canonical per-wave files the OpinionsQA adapter reads (info.csv +
NONE_data.json for the 684 questions in
data/question-text-registries/opinionsqa.json), and packs them into a
deterministic tarball. Prints the tarball's sha256, which must match
``MIRROR_SHA256`` in ``synthbench/datasets/opinionsqa.py``.

With ``--upload`` (needs the four R2_* env vars) it puts two objects in the
gated bucket:

- ``MIRROR_KEY``: the canonical tarball the adapter fetches;
- ``MIRROR_RAW_KEY``: the raw CodaLab bundle, unchanged, for provenance.

Usage:
    python scripts/build-opinionsqa-mirror.py [--out DIR] [--upload]
"""

from __future__ import annotations

import argparse
import gzip
import hashlib
import io
import sys
import tarfile
import tempfile
from pathlib import Path

from synthbench.datasets import opinionsqa as oqa


def pack_canonical(human_resp_dir: Path) -> bytes:
    """Tar only info.csv + NONE_data.json per wave, byte-for-byte reproducible."""
    buf = io.BytesIO()
    with gzip.GzipFile(fileobj=buf, mode="wb", mtime=0) as gz:
        with tarfile.open(fileobj=gz, mode="w", format=tarfile.PAX_FORMAT) as tf:
            for wave_dir in sorted(human_resp_dir.glob("American_Trends_Panel_W*")):
                none = wave_dir / "NONE_data.json"
                if not none.exists() or none.read_text(encoding="utf-8") == "{}":
                    continue
                for name in ("info.csv", "NONE_data.json"):
                    data = (wave_dir / name).read_bytes()
                    info = tarfile.TarInfo(f"human_resp/{wave_dir.name}/{name}")
                    info.size = len(data)
                    info.mtime = 0
                    info.mode = 0o644
                    tf.addfile(info, io.BytesIO(data))
    return buf.getvalue()


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument(
        "--out", type=Path, default=Path("."), help="where to write the tarball"
    )
    ap.add_argument(
        "--upload",
        action="store_true",
        help="upload both objects to the gated R2 bucket",
    )
    args = ap.parse_args()

    raw = oqa.fetch_codalab_human_resp()
    print(f"CodaLab human_resp bundle: {len(raw):,} bytes, sha256 verified")

    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        oqa._extract_tar_gz(raw, tmp_path)
        n = oqa.build_canonical_wave_files(
            tmp_path / "human_resp", oqa.load_canonical_keys()
        )
        canonical = pack_canonical(tmp_path / "human_resp")

    digest = hashlib.sha256(canonical).hexdigest()
    out = args.out / "opinionsqa-human_resp-canonical-v1.tar.gz"
    out.write_bytes(canonical)
    print(f"{n} canonical questions -> {out} ({len(canonical):,} bytes)")
    print(f"sha256 {digest}")
    if digest != oqa.MIRROR_SHA256:
        print(f"note: differs from MIRROR_SHA256 in the adapter ({oqa.MIRROR_SHA256})")

    if args.upload:
        from synthbench.r2_upload import R2Uploader

        r2 = R2Uploader.from_env()
        r2.put_bytes(oqa.MIRROR_KEY, canonical, "application/gzip")
        r2.put_bytes(oqa.MIRROR_RAW_KEY, raw, "application/gzip")
        print(
            f"uploaded to r2://{r2.bucket}/{oqa.MIRROR_KEY} and /{oqa.MIRROR_RAW_KEY}"
        )
    return 0


if __name__ == "__main__":
    sys.exit(main())
