from __future__ import annotations

# Minimal shim so upstream type models that depend on
# `openai._models.BaseModel` continue to work.

try:
    from pydantic import BaseModel as _BaseModel
    try:
        from pydantic import ConfigDict  # pydantic v2
    except Exception:  # pragma: no cover
        ConfigDict = dict  # type: ignore
except Exception as e:  # pragma: no cover
    raise RuntimeError(
        "openai-python-types requires pydantic>=2 at runtime"
    ) from e


class BaseModel(_BaseModel):
    """Base model used by generated types.

    The configuration here aims to be permissive to match upstream
    expectations while keeping package surface minimal.
    """

    model_config = ConfigDict(
        extra="allow",
        arbitrary_types_allowed=True,
        populate_by_name=True,
        frozen=False,
    )


__all__ = ["BaseModel"]
