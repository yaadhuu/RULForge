"""Load raw NASA C-MAPSS files and validate their structure.

Each subset (FD001..FD004) ships three whitespace-separated text files with no header:
  train_FDxxx.txt  engines run until failure
  test_FDxxx.txt   engines cut off BEFORE failure
  RUL_FDxxx.txt    one number per test engine: how many cycles it still had left after its last
                   recorded cycle (row i belongs to engine i, i = 1..N)
"""
from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

OP_COLS = ["op_setting_1", "op_setting_2", "op_setting_3"]
SENSOR_COLS = [f"s{i}" for i in range(1, 22)]
COLUMNS = ["unit_id", "cycle"] + OP_COLS + SENSOR_COLS  # 26 columns


def _read_table(path: Path) -> pd.DataFrame:
    df = pd.read_csv(path, sep=r"\s+", header=None)
    df = df.dropna(axis=1, how="all")  # raw files may carry trailing whitespace -> empty column
    if df.shape[1] != len(COLUMNS):
        raise ValueError(f"{path.name}: expected {len(COLUMNS)} columns, found {df.shape[1]}")
    df.columns = COLUMNS
    df["unit_id"] = df["unit_id"].astype(int)
    df["cycle"] = df["cycle"].astype(int)
    return df


def check_cycles(df: pd.DataFrame, name: str = "table") -> None:
    """Every engine must have cycles exactly 1..n (no gaps, no duplicates).

    Sequence building and rolling features rely on this, so we fail loudly if it is violated."""
    g = df.groupby("unit_id")["cycle"]
    ok = (g.min() == 1) & (g.max() == g.count()) & (g.nunique() == g.count())
    if not ok.all():
        bad = ok[~ok].index.tolist()[:5]
        raise ValueError(f"{name}: cycles are not exactly 1..n for engines {bad}")


def load_subset(raw_dir: str | Path, subset: str = "FD001"):
    """Return (train, test, rul_after_last).

    rul_after_last is a Series of ints indexed by ENGINE ID (1..N), not by row position.
    Keeping the engine id as the index is what lets us join it to the right engine later."""
    raw_dir = Path(raw_dir)
    train = _read_table(raw_dir / f"train_{subset}.txt")
    test = _read_table(raw_dir / f"test_{subset}.txt")
    values = pd.read_csv(raw_dir / f"RUL_{subset}.txt", header=None)[0].astype(int).to_numpy()
    rul = pd.Series(values, index=pd.Index(np.arange(1, len(values) + 1), name="unit_id"), name="rul_after_last")

    check_cycles(train, "train")
    check_cycles(test, "test")
    if set(rul.index) != set(test["unit_id"].unique()):
        raise ValueError(
            f"RUL file has {len(rul)} rows but test has {test['unit_id'].nunique()} engines (ids differ)"
        )
    return train, test, rul
