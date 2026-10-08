"""Feature selection, per-engine rolling/lag features, scaling, sliding-window sequences.

Rules: everything per engine and backward-looking; scalers fit on training engines only;
windows never cross engine boundaries."""
