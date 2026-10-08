"""Download NASA C-MAPSS (FD001-FD004) into data/raw and sanity-check row counts.

Source: a public GitHub mirror of the original NASA files. Row counts below match the official
dataset; if you have NASA's original download, you can copy those files into data/raw instead.

Usage:  python scripts/download_data.py [FD001 FD002 ...]
"""
from __future__ import annotations

import sys
import urllib.request
from pathlib import Path

BASE = "https://raw.githubusercontent.com/schwxd/LSTM-Keras-CMAPSS/master/C-MAPSS-Data"
# expected number of lines per file: (train, test, RUL)
EXPECTED = {
    "FD001": (20631, 13096, 100),
    "FD002": (53759, 33991, 259),
    "FD003": (24720, 16596, 100),
    "FD004": (61249, 41214, 248),
}
OUT = Path(__file__).resolve().parents[1] / "data" / "raw"


def fetch(subset: str) -> None:
    for kind, expected in zip(("train", "test", "RUL"), EXPECTED[subset]):
        dest = OUT / f"{kind}_{subset}.txt"
        if not dest.exists():
            print(f"downloading {dest.name} ...")
            urllib.request.urlretrieve(f"{BASE}/{dest.name}", dest)
        n = sum(1 for _ in dest.open())
        status = "OK" if n == expected else f"MISMATCH (expected {expected})"
        print(f"  {dest.name}: {n} lines {status}")
        if n != expected:
            raise SystemExit(f"{dest.name} failed its row-count check")


def main(argv: list[str]) -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    for subset in argv or ["FD001"]:
        if subset not in EXPECTED:
            raise SystemExit(f"unknown subset {subset}; choose from {list(EXPECTED)}")
        fetch(subset)


if __name__ == "__main__":
    main(sys.argv[1:])
