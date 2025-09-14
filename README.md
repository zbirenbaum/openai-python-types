OpenAI Python Types
===================

Tiny package that exposes only the `openai` SDK's `types` as `openai_types`,
keeping install size as small as possible while staying in sync with upstream.

Install
- `pip install openai-python-types`

Usage
- Instead of `from openai.types.realtime.realtime_audio_formats import RealtimeAudioFormats`
  use `from openai_types.realtime.realtime_audio_formats import RealtimeAudioFormats`.

What’s Included
- Only the upstream `src/openai/types` tree, vendored under `openai_types/types`.
- A tiny `_models.BaseModel` shim (pydantic v2) needed by the generated types.
- Auto-generated import proxies so `openai_types.<module>` maps to `openai_types.types.<module>`.

What’s Not Included
- No client logic, transport, or other `openai` SDK files — keeping the wheel minimal.

Syncing with Upstream
- A GitHub Action (`.github/workflows/sync.yml`) runs hourly and on demand to:
  - Fetch the latest OpenAI Python release tag
  - Copy `src/openai/types` into this repo
  - Generate import proxies
  - Bump this package version to match upstream
  - Open a PR with changes

Releasing
- Optional workflow (`.github/workflows/release.yml`) publishes to PyPI on tags `v*.*.*`.
- Configure repository secret `PYPI_API_TOKEN` for automated publishing.

Local Development
- Run `python scripts/sync_types.py` to sync locally.
- Build locally with `python -m build`.

Notes
- Requires Python 3.8+ and `pydantic>=2` at runtime.
