"""
openai_types
-------------

This package exposes the data models ("types") from the upstream
`openai` Python SDK under the top-level module `openai_types`.

Example:
    from openai_types.realtime.realtime_audio_formats import RealtimeAudioFormats

The actual upstream sources live under `openai_types/types`. Thin proxy
packages and modules are generated to make imports work without the
intermediate `types` segment.
"""

from importlib.metadata import version, PackageNotFoundError

try:
    __version__ = version("openai-python-types")
except PackageNotFoundError:  # pragma: no cover
    # When running from a source tree without an installed dist
    __version__ = "0"

__all__ = ["__version__"]

