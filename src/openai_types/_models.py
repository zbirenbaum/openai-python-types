from __future__ import annotations

# Minimal shim so upstream type models that depend on
# `openai._models.BaseModel` continue to work.

try:
    from pydantic import BaseModel as _BaseModel
    try:
        from pydantic import ConfigDict  # pydantic v2
    except Exception:  # pragma: no cover
        ConfigDict = dict  # type: ignore
    try:
        # pydantic v2 location
        from pydantic.generics import GenericModel as _GenericModel  # type: ignore
    except Exception:  # pragma: no cover
        _GenericModel = _BaseModel  # type: ignore[misc,assignment]
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


class GenericModel(_GenericModel):
    pass


__all__ = ["BaseModel", "GenericModel"]
