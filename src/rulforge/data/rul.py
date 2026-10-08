"""RUL (Remaining Useful Life) targets.

  train engine:  RUL(t) = last_cycle - t                       (it runs to failure)
  test engine:   RUL(t) = rul_after_last + (last_cycle - t)    (it was cut off early)

Two columns are produced:
  rul_raw  the true value
  rul      the training target = rul_raw capped at `cap` (piece-wise linear degradation idea:
           a healthy engine is not "more healthy" at 300 cycles left than at 125).
           cap=None means no capping. The cap is a SETTING to be validated, not a constant.

Why test RUL is joined by engine id: the old pipeline joined it by row position, so each engine got
its neighbour's RUL. `Series.map` looks values up by label, which cannot shift.
"""
from __future__ import annotations

import pandas as pd


def _check_cap(cap):
    if cap is not None and (not isinstance(cap, (int, float)) or cap <= 0):
        raise ValueError(f"cap must be a positive number or None, got {cap!r}")


def add_train_rul(train: pd.DataFrame, cap: float | None = None) -> pd.DataFrame:
    _check_cap(cap)
    out = train.copy()
    out["rul_raw"] = out.groupby("unit_id")["cycle"].transform("max") - out["cycle"]
    out["rul"] = out["rul_raw"] if cap is None else out["rul_raw"].clip(upper=cap)
    return out


def add_test_rul(test: pd.DataFrame, rul_after_last: pd.Series, cap: float | None = None) -> pd.DataFrame:
    _check_cap(cap)
    missing = set(test["unit_id"].unique()) - set(rul_after_last.index)
    if missing:
        raise ValueError(f"no RUL value for engines {sorted(missing)[:5]}")
    out = test.copy()
    last_cycle = out.groupby("unit_id")["cycle"].transform("max")
    out["rul_raw"] = out["unit_id"].map(rul_after_last) + (last_cycle - out["cycle"])
    out["rul"] = out["rul_raw"] if cap is None else out["rul_raw"].clip(upper=cap)
    return out
