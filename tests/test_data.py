from pathlib import Path

import pytest

from rulforge.data.load import COLUMNS, load_subset
from rulforge.data.rul import add_test_rul, add_train_rul

REAL_RAW = Path(__file__).resolve().parents[1] / "data" / "raw"


# ---------- loading ----------
def test_load_shapes_and_columns(raw_dir):
    train, test, rul = load_subset(raw_dir)
    assert list(train.columns) == COLUMNS and list(test.columns) == COLUMNS
    assert len(train) == 5 + 7 + 4 and len(test) == 3 + 4 + 2
    assert list(rul.index) == [1, 2, 3] and list(rul.values) == [10, 5, 20]


def test_gap_in_cycles_is_rejected(raw_dir):
    path = raw_dir / "train_FD001.txt"
    lines = path.read_text().splitlines(keepends=True)
    del lines[2]  # drop cycle 3 of engine 1 -> gap
    path.write_text("".join(lines))
    with pytest.raises(ValueError, match="cycles"):
        load_subset(raw_dir)


def test_rul_file_with_wrong_length_is_rejected(raw_dir):
    (raw_dir / "RUL_FD001.txt").write_text("10\n5\n")
    with pytest.raises(ValueError, match="RUL file"):
        load_subset(raw_dir)


# ---------- train RUL ----------
def test_train_rul_counts_down_per_engine(raw_dir):
    train, _, _ = load_subset(raw_dir)
    out = add_train_rul(train)
    for _, g in out.sort_values(["unit_id", "cycle"]).groupby("unit_id"):
        assert g["rul_raw"].iloc[-1] == 0                    # fails at its last cycle
        assert g["rul_raw"].iloc[0] == len(g) - 1            # starts at lifetime - 1
        assert (g["rul_raw"].diff().dropna() == -1).all()    # drops by exactly 1 per cycle


def test_cap_limits_target_but_not_raw(raw_dir):
    train, _, _ = load_subset(raw_dir)
    out = add_train_rul(train, cap=3)
    assert out["rul"].max() == 3 and out["rul_raw"].max() == 6
    assert add_train_rul(train, cap=None)["rul"].equals(out["rul_raw"])


def test_bad_cap_is_rejected(raw_dir):
    train, _, _ = load_subset(raw_dir)
    with pytest.raises(ValueError):
        add_train_rul(train, cap=0)


# ---------- test RUL: the bug that invalidated the old results ----------
def test_test_rul_is_joined_by_engine_id_not_position(raw_dir):
    """Test rows are shuffled on disk; each engine's LAST cycle must equal its own RUL-file value."""
    _, test, rul = load_subset(raw_dir)
    out = add_test_rul(test, rul)
    last = out.sort_values("cycle").groupby("unit_id").tail(1).set_index("unit_id")["rul_raw"]
    assert last.to_dict() == {1: 10, 2: 5, 3: 20}


def test_test_rul_counts_down_and_has_no_nan(raw_dir):
    _, test, rul = load_subset(raw_dir)
    out = add_test_rul(test, rul)
    assert not out["rul_raw"].isna().any()
    for _, g in out.sort_values(["unit_id", "cycle"]).groupby("unit_id"):
        assert (g["rul_raw"].diff().dropna() == -1).all()


def test_old_positional_join_would_be_caught(raw_dir):
    """Re-create the old bug and prove the assertion above detects it."""
    _, test, rul = load_subset(raw_dir)
    last_cycle = test.groupby("unit_id")["cycle"].max().to_frame("last_cycle")
    buggy = last_cycle.join(rul.reset_index(drop=True).to_frame("r"))  # index 1..3 vs 0..2
    assert buggy["r"].isna().any()                   # one engine gets nothing
    assert buggy["r"].iloc[0] != rul.loc[1]          # and the others are shifted by one


# ---------- real FD001 data (skipped if not downloaded) ----------
real = pytest.mark.skipif(not (REAL_RAW / "train_FD001.txt").exists(), reason="run scripts/download_data.py")


@real
def test_fd001_structure():
    train, test, rul = load_subset(REAL_RAW, "FD001")
    assert (len(train), len(test), len(rul)) == (20631, 13096, 100)
    assert train["unit_id"].nunique() == 100
    lifetimes = train.groupby("unit_id")["cycle"].max()
    assert (lifetimes.min(), lifetimes.max()) == (128, 362)


@real
def test_fd001_known_test_ruls():
    """RUL_FD001.txt starts 112, 98, 69; engines 1..3 must END at exactly those values."""
    _, test, rul = load_subset(REAL_RAW, "FD001")
    out = add_test_rul(test, rul)
    last = out.sort_values("cycle").groupby("unit_id").tail(1).set_index("unit_id")["rul_raw"]
    assert [last[1], last[2], last[3]] == [112, 98, 69]
    assert not out["rul_raw"].isna().any()
