2026-01-22

- Branch: code-cleanup
- High-level summary of differences compared to `main`:
  - Project restructured / files moved: many files were renamed/moved from `gradio_pages/...` into the repository root under `app/...` (e.g., interface, llms, prompt_profiles, repositories, documentation).
  - Added new/updated application files under `app/` including `app/config.py`, `app/common/*`, `app/interface/*`, `app/llms/*`, and `app/repositories/*`.
  - API fixes and improvements:
    - Dryad URL normalization fixes (see commit: "fixing normalization for dryad urls").
    - Zenodo API fixes including setting a `User-Agent` header and related tests. (Now required by Zenodo)
    - Added retry logic for token retrieval and fixed OAuth token handling. Dryad now requires OAuth for downloading any files.
  - Tests: added `tests/test_dryad_api.py` and `tests/test_repo_interface.py`.
  - Removed legacy/extra directories: `dryad_meta_dl/`, `zenodo_meta_dl/`, and the old `gradio_pages/` subtree was largely removed or moved.
  - Build/dependency changes: updated `requirements.in` / `requirements.txt` and upgraded dependencies for security.
  - Misc: updates to `main.py`, `gradio_control.sh`, `.gitignore`, README and other repo housekeeping.

