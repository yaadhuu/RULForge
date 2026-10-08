# Audit of the old Colab notebooks (2026-10-08)

Source: PDF prints of the old notebooks (now in `legacy/`). `train_final.csv`, `test_final.csv` and all
checkpoints were NOT available.

## Critical: test RUL labels were misaligned (reproduced on the real FD001 files)
`add_test_rul` did `last_cycle.to_frame().join(rul_df.reset_index(drop=True))`. `last_cycle` is indexed by
unit_id 1..100 and the RUL frame by 0..99, so every engine received the NEXT engine's RUL and engine 100
got NaN.
- Engine 1 last-cycle RUL: old 98, correct 112. Engine 2: old 69, correct 98.
- 12,898 of 12,898 labelled test rows were wrong; 198 rows (engine 100) were NaN.
- Visible symptom in the EDA: test `start_rul` count = 99, not 100.
- NaNs were hidden by `fillna(median)` (LSTM notebook) and `dropna` (XGBoost notebook).
- Wrong vs correct clipped labels differ by ~31.5 cycles RMSE, so every old TEST metric was scored against
  wrong labels: XGBoost 43.82 / 43.16 / 44.09 RMSE, Attention-LSTM 43.35 RMSE / 81.05% accuracy. Do not quote them.

## Other problems
- No validation split; early stopping and "best model" chosen on the TEST set.
- Scored all test rows instead of the official last-cycle-per-engine protocol; single run, no seeds.
- Stage thresholds (RUL>40 healthy, >15 warning, else critical) never justified. Train classes 16531/2500/1600:
  always predicting "healthy" gives ~80.1% accuracy, so ~81% says little without macro-F1 / confusion matrix.
- Attention analysis: a "v2" 4-class checkpoint with a different 18-feature set (incl. cycle, lag1) than the
  training notebook (whose training notebook is missing); weights nearly uniform (0.024-0.039 vs 1/30=0.033) on ONE
  training sample; "critical timesteps 23-27" is just the tail of a smooth ramp. Window loop dropped the last window.
- SHAP notebook: refit 300-tree model; `cycle` is a top-4 feature; `sensor_map` labels look invented
  (NASA docs: s11 = static pressure at HPC outlet, s4 = LPT outlet temperature, s7 = HPC outlet total pressure,
  s12 = fuel flow / Ps30). Verify from NASA documentation before use. SHAP shows model behaviour, not root cause.

## Worth keeping
- EDA is sound: 100 train engines, lifetimes ~128-362, constant columns s1, s5, s10, s16, s18, s19 (+ op_setting_3),
  top RUL correlates s11, s4, s12, s7, s15, s21, s20, s2, s17, s3; degradation accelerates near failure.
- Per-engine rolling-5 mean / lag1 / delta features were grouped correctly by engine.
- Attention-LSTM design is a reasonable starting config: window 30, 2-layer LSTM hidden 128, linear attention
  pooling, RUL head (Huber) + stage head (class-weighted CE, weight 0.5), Adam 3e-4, grad clip 0.5, RUL/125.

## Still unknown
Contents of train_final/test_final and how they were made (27 -> 21 columns); whether LSTM inputs were scaled;
the 4-class training notebook; the origin of the earlier XGBoost 70.69 / 57.13 figure.
