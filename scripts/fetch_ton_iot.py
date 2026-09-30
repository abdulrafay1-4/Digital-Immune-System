"""Check the TON_IoT train/test files you downloaded and put them where the code reads them.

TON_IoT's terms allow academic use but not redistribution, so the files are not in this
repository. Download them from https://research.unsw.edu.au/projects/toniot-datasets
(folder "Train_Test_datasets"), put the three CSV files below in data/ton_iot/, and run

    python scripts/fetch_ton_iot.py

Each file is checked against the SHA-256 the calibration recorded, then gzip-compressed.
"""

from __future__ import annotations

import gzip
import hashlib
import shutil
import sys
from pathlib import Path

TARGET = Path(__file__).resolve().parents[1] / "data" / "ton_iot"
#: SHA-256 of each decompressed CSV, as recorded in configs/ton_iot*_calibration.json.
SHA256 = {
    "Train_Test_Network.csv": "65d5465df1809b984fd10e4703bc9c012d1aefd11803773856364216f0a3520d",
    "Train_Test_Windows_7.csv": "5ed0c685148449bb493dd4196a35fcf0d1dc82d0a50b66da84a34114be36ef1d",
    "Train_Test_Windows_10.csv": "85f0827697ef5b0faf76a8b41371e95fd5e6ea3950d19ea35a9d7f35042703a8",
}


def digest(path: Path) -> str:
    opener = gzip.open if path.suffix == ".gz" else open
    h = hashlib.sha256()
    with opener(path, "rb") as fh:
        for block in iter(lambda: fh.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def main() -> int:
    failed = 0
    for name, expected in SHA256.items():
        csv, packed = TARGET / name, TARGET / f"{name}.gz"
        if packed.exists() and digest(packed) == expected:
            print(f"{packed.name}: ok")
            continue
        if not csv.exists():
            print(f"{name}: missing; download it into {TARGET}", file=sys.stderr)
            failed += 1
            continue
        if digest(csv) != expected:
            print(f"{name}: SHA-256 does not match the recorded calibration", file=sys.stderr)
            failed += 1
            continue
        with csv.open("rb") as src, gzip.open(packed, "wb") as dst:
            shutil.copyfileobj(src, dst)
        print(f"{packed.name}: ok")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
