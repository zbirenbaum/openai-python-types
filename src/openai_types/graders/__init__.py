from __future__ import annotations
from pathlib import Path

_here = Path(__file__)
__path__ = [str(_here.parent.parent.joinpath('types', _here.parent.name))]
