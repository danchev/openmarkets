"""Verify distribution metadata and, when supplied, the release tag and wheel."""

import argparse
import json
from email.parser import BytesParser
from pathlib import Path
from zipfile import ZipFile

import tomllib


def check(root: Path, tag: str | None = None, wheel: Path | None = None) -> None:
    project = tomllib.loads((root / "pyproject.toml").read_text())["project"]
    version = project["version"]
    registry = json.loads((root / "server.json").read_text())
    if registry["version"] != version:
        raise ValueError("Registry version differs from project version")
    packages = registry["packages"]
    if not packages or any(p["identifier"] != project["name"] or p["version"] != version for p in packages):
        raise ValueError("Registry package differs from project name/version")
    marker = f"<!-- mcp-name: {registry['name']} -->"
    if marker not in (root / "README.md").read_text():
        raise ValueError("README is missing the MCP Registry ownership marker")
    marketplace = json.loads((root / ".claude-plugin/marketplace.json").read_text())
    for entry in marketplace["plugins"]:
        plugin_root = (root / entry["source"]).resolve()
        if not plugin_root.is_relative_to(root.resolve()):
            raise ValueError("Plugin source must stay inside the repository")
        plugin = json.loads((plugin_root / ".claude-plugin/plugin.json").read_text())
        if (entry["name"], entry["version"]) != (plugin["name"], plugin["version"]):
            raise ValueError("Marketplace and plugin name/version differ")
        config = json.loads((plugin_root / ".mcp.json").read_text())["mcpServers"]["openmarkets"]
        if config["command"] != "uvx" or config["args"] != ["openmarkets@latest"]:
            raise ValueError("Plugin launcher differs from the supported installation command")
    if tag is not None and tag not in (version, f"v{version}"):
        raise ValueError(f"Release tag {tag!r} does not match package version {version!r}")
    if wheel is not None:
        with ZipFile(wheel) as archive:
            metadata_paths = [name for name in archive.namelist() if name.endswith(".dist-info/METADATA")]
            if len(metadata_paths) != 1:
                raise ValueError("Expected exactly one wheel metadata file")
            metadata = BytesParser().parsebytes(archive.read(metadata_paths[0]))
        if metadata["Name"] != project["name"] or metadata["Version"] != version:
            raise ValueError("Built wheel name/version differs from the project")
        if marker not in metadata.get_payload():
            raise ValueError("Built wheel is missing the MCP Registry ownership marker")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--tag")
    parser.add_argument("--wheel", type=Path)
    args = parser.parse_args()
    check(args.root, args.tag, args.wheel)
    print("Release metadata checks passed")
