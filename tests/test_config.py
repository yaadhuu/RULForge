from rulforge.config import load_config


def test_data_config_has_required_keys():
    cfg = load_config("data")
    assert cfg["dataset"]["subset"] == "FD001"
    assert cfg["split"]["val_fraction"] == 0.2
