from __future__ import annotations

"""
Minimal utilities used by generated type modules.

Only what's required at runtime is included to keep this package light.
"""

from typing import Optional


class PropertyInfo:
    """Lightweight metadata container used with typing_extensions.Annotated.

    The generated models attach these as metadata to provide hints like
    field aliases and discriminators. Pydantic will ignore unknown objects in
    Annotated metadata, so this class only needs to exist for imports and
    type-checking. Keeping attributes allows advanced users to introspect.
    """

    def __init__(self, *, alias: Optional[str] = None, discriminator: Optional[str] = None):
        self.alias = alias
        self.discriminator = discriminator

    def __repr__(self) -> str:  # pragma: no cover
        parts = []
        if self.alias is not None:
            parts.append(f"alias={self.alias!r}")
        if self.discriminator is not None:
            parts.append(f"discriminator={self.discriminator!r}")
        return f"PropertyInfo({', '.join(parts)})"


__all__ = ["PropertyInfo"]

