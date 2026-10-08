"""Single predict() path shared by the API and agent tools (same preprocessing + saved scaler
as training) so training and serving cannot drift apart. Built in Phase 2."""
