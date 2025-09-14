#!/usr/bin/env python3
from __future__ import annotations

import argparse
import os
import re
import shutil
import subprocess
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
PKG = SRC / "openai_types"
TYPES_DST = PKG / "types"


@dataclass
class UpstreamInfo:
    repo_url: str
    ref: str  # tag or branch
    version: str


def run(cmd: list[str], cwd: Path | None = None) -> str:
    print("$", " ".join(cmd))
    out = subprocess.check_output(cmd, cwd=str(cwd) if cwd else None)
    return out.decode().strip()


def detect_latest_tag(repo_url: str) -> str:
    # List remote tags and pick the highest semver-like tag
    data = run(["git", "ls-remote", "--tags", "--refs", repo_url])
    tags = []
    for line in data.splitlines():
        _, ref = line.split("\t", 1)
        tag = ref.rsplit("/", 1)[-1]
        if re.match(r"^v?\d+\.\d+\.\d+$", tag):
            tags.append(tag)
    if not tags:
        raise RuntimeError("No version tags found in upstream repo")

    def key(t: str):
        t = t[1:] if t.startswith("v") else t
        return tuple(map(int, t.split(".")))

    return sorted(tags, key=key)[-1]


def read_upstream_version(src_root: Path) -> str:
    # Read src/openai/__init__.py __version__
    init_py = src_root / "src" / "openai" / "__init__.py"
    if init_py.exists():
        m = re.search(r"__version__\s*=\s*['\"]([^'\"]+)['\"]", init_py.read_text())
        if m:
            return m.group(1)
    raise RuntimeError("Could not determine upstream version")


def clone_upstream(repo_url: str, ref: str | None) -> tuple[Path, str]:
    tmp = Path(tempfile.mkdtemp(prefix="openai-python-"))
    run(["git", "init"], cwd=tmp)
    run(["git", "remote", "add", "origin", repo_url], cwd=tmp)
    run(["git", "fetch", "--depth", "1", "origin", ref or "HEAD"], cwd=tmp)
    run(["git", "checkout", "FETCH_HEAD"], cwd=tmp)
    version = None
    if ref and re.match(r"^v?\d+\.\d+\.\d+$", ref):
        version = ref[1:] if ref.startswith("v") else ref
    if not version:
        try:
            version = read_upstream_version(tmp)
        except Exception:
            pass
    if not version:
        # Fallback to git describe
        try:
            desc = run(["git", "describe", "--tags", "--abbrev=0"], cwd=tmp)
            if re.match(r"^v?\d+\.\d+\.\d+$", desc):
                version = desc[1:] if desc.startswith("v") else desc
        except Exception:
            pass
    if not version:
        raise RuntimeError("Could not determine upstream version")
    return tmp, version


def clean_dst() -> None:
    # Remove previous synced content, keep our shims
    if TYPES_DST.exists():
        shutil.rmtree(TYPES_DST)

    # Remove generated top-level proxies (packages and modules), keep __init__ and _models
    for p in PKG.iterdir():
        if p.name in {"__init__.py", "_models.py", "types", "__pycache__"}:
            continue
        if p.is_dir():
            shutil.rmtree(p)
        else:
            p.unlink()


def copy_types(upstream_root: Path) -> Path:
    src = upstream_root / "src" / "openai" / "types"
    if not src.exists():
        raise RuntimeError(f"Upstream types dir not found at {src}")
    shutil.copytree(src, TYPES_DST)
    return src


def generate_proxies() -> None:
    # Create top-level import proxies so `openai_types.x` maps to `openai_types.types.x`
    for entry in sorted(TYPES_DST.iterdir()):
        if entry.name == "__pycache__":
            continue
        if entry.is_dir():
            pkg_dir = PKG / entry.name
            pkg_dir.mkdir(parents=True, exist_ok=True)
            init = pkg_dir / "__init__.py"
            # Make this a package whose __path__ points at the upstream types subdir
            init.write_text(
                """
from __future__ import annotations
from pathlib import Path

_here = Path(__file__)
__path__ = [str(_here.parent.parent.joinpath('types', _here.parent.name))]
""".lstrip()
            )
        elif entry.suffix == ".py" and entry.name != "__init__.py":
            # Create a forwarding module openai_types/<stem>.py -> openai_types.types.<stem>
            stem = entry.stem
            mod = PKG / f"{stem}.py"
            mod.write_text(
                f"from .types.{stem} import *  # noqa\n"
            )


def update_pyproject_version(new_version: str) -> None:
    pj = ROOT / "pyproject.toml"
    # Use a simple string replace of the version assignment
    txt = pj.read_text()
    new_txt = re.sub(
        r"(?m)^version\s*=\s*['\"]([^'\"]+)['\"]",
        f"version = \"{new_version}\"",
        txt,
    )
    pj.write_text(new_txt)


def get_repo_url(default: str) -> str:
    return os.environ.get("OPENAI_PYTHON_REPO", default)


def main() -> None:
    ap = argparse.ArgumentParser(description="Sync OpenAI types into this package")
    ap.add_argument("--ref", help="Upstream git ref (tag/branch). Defaults to latest tag.")
    ap.add_argument("--repo", help="Upstream repo URL", default=get_repo_url("https://github.com/openai/openai-python.git"))
    args = ap.parse_args()

    ref = args.ref or detect_latest_tag(args.repo)
    upstream_root, upstream_version = clone_upstream(args.repo, ref)
    print(f"Using upstream version {upstream_version} from {ref}")

    clean_dst()
    copy_types(upstream_root)
    generate_proxies()
    update_pyproject_version(upstream_version)

    print("Sync complete.")


if __name__ == "__main__":
    main()
