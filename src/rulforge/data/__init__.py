"""Loading raw C-MAPSS files, RUL generation (+ configurable cap), stage labels, engine-level splits.

Rules: RUL is computed per engine; test RUL = RUL_FDxxx.txt value for that engine + (last_cycle - cycle).
Join RUL values by ENGINE ID, never by positional index (the old pipeline broke here)."""
