#!/usr/bin/env python3
"""Build (and optionally upload) SynthBench's OpinionsQA mirror.

Downloads CodaLab's human_resp bundle (sha256-pinned), aggregates it into the
canonical per-wave files the OpinionsQA adapter reads (info.csv +
NONE_data.json for the 684 questions in
data/question-text-registries/opinionsqa.json), and packs them into a
deterministic tarball. Prints the tarball's sha256, which must match
``MIRROR_SHA256`` in ``synthbench/datasets/opinionsqa.py``.

It also builds the public variant, with private-holdout answers replaced by
``{"withheld": true}`` (sha256 must match ``PUBLIC_MIRROR_SHA256``).

With ``--upload`` (needs the four R2_* env vars) it puts three objects in the
gated bucket:

- ``MIRROR_KEY`` (canonical/): the full tarball, read directly from R2 by
  maintainers and CI; never served by the data-proxy Worker;
- ``PUBLIC_MIRROR_KEY`` (datasets/): the public tarball, served to
  read-scope API keys;
- ``MIRROR_RAW_KEY`` (provenance/): the raw CodaLab bundle, unchanged.

Usage:
    python scripts/build-opinionsqa-mirror.py [--out DIR] [--upload]
"""

from __future__ import annotations

import argparse
import gzip
import hashlib
import io
import shutil
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
        public_dir = tmp_path / "public" / "human_resp"
        shutil.copytree(tmp_path / "human_resp", public_dir)
        withheld = oqa.withhold_private_answers(public_dir)
        public = pack_canonical(public_dir)

    for label, blob, name, pinned in (
        (
            "canonical",
            canonical,
            "opinionsqa-human_resp-canonical-v1.tar.gz",
            oqa.MIRROR_SHA256,
        ),
        (
            "public",
            public,
            "opinionsqa-human_resp-public-v1.tar.gz",
            oqa.PUBLIC_MIRROR_SHA256,
        ),
    ):
        digest = hashlib.sha256(blob).hexdigest()
        out = args.out / name
        out.write_bytes(blob)
        print(f"{label}: {out} ({len(blob):,} bytes) sha256 {digest}")
        if digest != pinned:
            print(f"  note: differs from the sha256 pinned in the adapter ({pinned})")
    print(
        f"{n} canonical questions; {withheld} private-holdout answers withheld in the public file"
    )

    if args.upload:
        from synthbench.r2_upload import R2Uploader

        r2 = R2Uploader.from_env()
        r2.put_bytes(oqa.MIRROR_KEY, canonical, "application/gzip")
        r2.put_bytes(oqa.PUBLIC_MIRROR_KEY, public, "application/gzip")
        r2.put_bytes(oqa.MIRROR_RAW_KEY, raw, "application/gzip")
        print(
            f"uploaded to r2://{r2.bucket}/ {oqa.MIRROR_KEY}, {oqa.PUBLIC_MIRROR_KEY}, "
            f"{oqa.MIRROR_RAW_KEY}"
        )
    return 0


if __name__ == "__main__":
    sys.exit(main())
