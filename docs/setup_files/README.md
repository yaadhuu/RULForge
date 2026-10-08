# Setup files to move into place

These two were written here because the tooling that created this project may not write protected
config paths. Move/rename them yourself:

- `ci.yml.txt`                 -> `.github/workflows/ci.yml`
- `pre-commit-config.yaml.txt` -> `.pre-commit-config.yaml`  (then run `pre-commit install`)

Delete this folder afterwards.
