"""Tiny synthetic C-MAPSS-like files so tests never need the real download."""
import numpy as np
import pytest

from rulforge.data.load import COLUMNS


def _write(path, engine_lengths, rng, shuffle=False):
    rows = []
    for unit, n in engine_lengths.items():
        for cycle in range(1, n + 1):
            rows.append([unit, cycle, *rng.normal(size=len(COLUMNS) - 2)])
    rows = np.array(rows)
    if shuffle:
        rows = rows[rng.permutation(len(rows))]
    with open(path, "w") as f:
        f.writelines(f"{int(r[0])} {int(r[1])} " + " ".join(f"{v:.4f}" for v in r[2:]) + " \n" for r in rows)


@pytest.fixture
def raw_dir(tmp_path):
    """3 train engines (5, 7, 4 cycles); 3 test engines (3, 4, 2 cycles) with true RUL 10, 5, 20."""
    rng = np.random.default_rng(0)
    _write(tmp_path / "train_FD001.txt", {1: 5, 2: 7, 3: 4}, rng)
    _write(tmp_path / "test_FD001.txt", {1: 3, 2: 4, 3: 2}, rng, shuffle=True)  # rows NOT in order
    (tmp_path / "RUL_FD001.txt").write_text("10\n5\n20\n")
    return tmp_path
