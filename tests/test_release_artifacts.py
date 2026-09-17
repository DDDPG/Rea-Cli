"""Release archive contracts, using small fixtures instead of package builds."""
import hashlib
import importlib.util
import io
from pathlib import Path
import shutil
import stat
import tarfile
from types import SimpleNamespace
import zipfile

import pytest


CHECKER_PATH = Path(__file__).resolve().parents[1] / "scripts/check_dist.py"
SPEC = importlib.util.spec_from_file_location("reacli_check_dist", CHECKER_PATH)
assert SPEC is not None and SPEC.loader is not None
checker = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(checker)

BUILD_RELEASE_PATH = Path(__file__).resolve().parents[1] / "tools/build_release.py"
BUILD_SPEC = importlib.util.spec_from_file_location("reacli_build_release", BUILD_RELEASE_PATH)
assert BUILD_SPEC is not None and BUILD_SPEC.loader is not None
build_release = importlib.util.module_from_spec(BUILD_SPEC)
BUILD_SPEC.loader.exec_module(build_release)


def _write_sdist(release, extra_member=None):
    with tarfile.open(release.sdist_path, "w:gz") as archive:
        for name, content in release.sdist_members.items():
            member = tarfile.TarInfo(name)
            member.size = len(content)
            archive.addfile(member, io.BytesIO(content))
        if extra_member is not None:
            archive.addfile(extra_member)


def _write_archives(release):
    with zipfile.ZipFile(release.wheel_path, "w") as archive:
        for name, content in release.wheel_members.items():
            archive.writestr(name, content)
    _write_sdist(release)


@pytest.fixture
def release(tmp_path):
    root = tmp_path / "source"
    directory = tmp_path / "dist"
    directory.mkdir()
    source = {
        "src/rac/__init__.py": b'__version__ = "0.1.0"\n',
        "src/rac/py.typed": b"",
        "src/rac/data/lua/entry.lua": b"local fixture = true\n",
        "src/rac/data/knowledge/api_index.json": b'{"functions": {}}\n',
        "pyproject.toml": b'[project]\nname = "reacli"\ndynamic = ["version"]\n',
        "LICENSE": b"Fixture project license\n",
        "THIRD_PARTY_NOTICES.md": b"Fixture third-party notices\n",
        "README.md": b"# Fixture project\n",
        "README.zh-CN.md": b"# Fixture translated readme\n",
        "CONTRIBUTING.md": b"Fixture contributor guide\n",
        "SECURITY.md": b"Fixture reporting guidance\n",
        "scripts/check_dist.py": b"# Fixture checker source\n",
        "tests/test_distribution.py": b"# Fixture distribution tests\n",
    }
    for name, content in source.items():
        file = root / name
        file.parent.mkdir(parents=True, exist_ok=True)
        file.write_bytes(content)
    metadata = b"Metadata-Version: 2.4\nName: reacli\nVersion: 0.1.0\n\n"
    wheel_members = {name.removeprefix("src/"): content
                     for name, content in source.items() if name.startswith("src/")}
    wheel_members.update({
        "reacli-0.1.0.dist-info/METADATA": metadata,
        "reacli-0.1.0.dist-info/WHEEL": b"Wheel-Version: 1.0\nTag: py3-none-any\n",
        "reacli-0.1.0.dist-info/licenses/LICENSE": source["LICENSE"],
        "reacli-0.1.0.dist-info/licenses/THIRD_PARTY_NOTICES.md": source["THIRD_PARTY_NOTICES.md"],
    })
    sdist_members = {"reacli-0.1.0/" + name: content for name, content in source.items()}
    sdist_members["reacli-0.1.0/PKG-INFO"] = metadata
    result = SimpleNamespace(
        root=root, directory=directory,
        wheel_path=directory / "reacli-0.1.0-py3-none-any.whl",
        sdist_path=directory / "reacli-0.1.0.tar.gz",
        wheel_members=wheel_members, sdist_members=sdist_members,
    )
    _write_archives(result)
    return result


def test_matching_release_reports_verifiable_artifacts(release):
    report = checker.check_dist(release.directory, release.root)

    assert report["ok"] is True
    assert report["version"] == "0.1.0"
    assert report["runtime_files_verified"] == 4
    assert report["supplemental_reference_included"] is False
    assert {artifact["file"] for artifact in report["artifacts"]} == {
        release.wheel_path.name, release.sdist_path.name}
    for artifact in report["artifacts"]:
        content = (release.directory / artifact["file"]).read_bytes()
        assert artifact["bytes"] == len(content)
        assert artifact["sha256"] == hashlib.sha256(content).hexdigest()


@pytest.mark.parametrize("archive_kind,member", [
    ("wheel", "reference/knowledge/private-notes.md"),
    ("sdist", "reacli-0.1.0/reference/knowledge/private-notes.md"),
    ("wheel", "rac/data/knowledge/actions_index.json"),
    ("sdist", "reacli-0.1.0/src/rac/data/knowledge/actions_index.json"),
])
def test_repository_reference_payload_is_rejected(release, archive_kind, member):
    getattr(release, archive_kind + "_members")[member] = b"supplemental reference"
    _write_archives(release)

    with pytest.raises(ValueError, match="Excluded payload"):
        checker.check_dist(release.directory, release.root)


@pytest.mark.parametrize("archive_kind,member", [
    ("wheel", "rac/data/lua/entry.lua"),
    ("sdist", "reacli-0.1.0/src/rac/data/lua/entry.lua"),
])
def test_stale_runtime_bytes_are_rejected(release, archive_kind, member):
    getattr(release, archive_kind + "_members")[member] = b"local stale = true\n"
    _write_archives(release)

    with pytest.raises(ValueError, match="differs from source"):
        checker.check_dist(release.directory, release.root)


@pytest.mark.parametrize("archive_kind,member", [
    ("wheel", "rac/deleted_module.py"),
    ("sdist", "reacli-0.1.0/src/rac/deleted_module.py"),
])
def test_removed_module_cannot_survive_in_release(release, archive_kind, member):
    getattr(release, archive_kind + "_members")[member] = b"# Deleted from source\n"
    _write_archives(release)

    with pytest.raises(ValueError, match="runtime file set differs from source"):
        checker.check_dist(release.directory, release.root)


@pytest.mark.parametrize("archive_kind,member", [
    ("wheel", "rac/data/knowledge/api_index.json"),
    ("sdist", "reacli-0.1.0/src/rac/data/knowledge/api_index.json"),
])
def test_missing_runtime_asset_is_rejected(release, archive_kind, member):
    del getattr(release, archive_kind + "_members")[member]
    _write_archives(release)

    with pytest.raises(ValueError, match="runtime file set differs from source"):
        checker.check_dist(release.directory, release.root)


@pytest.mark.parametrize("archive_kind,member", [
    ("wheel", "reacli-0.1.0.dist-info/METADATA"),
    ("sdist", "reacli-0.1.0/PKG-INFO"),
])
def test_metadata_version_must_match_checkout(release, archive_kind, member):
    members = getattr(release, archive_kind + "_members")
    members[member] = members[member].replace(b"Version: 0.1.0", b"Version: 0.2.0")
    _write_archives(release)

    with pytest.raises(ValueError, match="Metadata mismatch"):
        checker.check_dist(release.directory, release.root)


def test_version_change_requires_rebuilding_release(release):
    (release.root / "src/rac/__init__.py").write_text('__version__ = "0.2.0"\n')

    with pytest.raises(ValueError, match="filenames do not match"):
        checker.check_dist(release.directory, release.root)


def test_changed_readme_requires_rebuilding_sdist(release):
    (release.root / "README.md").write_text("# Updated after building\n")

    with pytest.raises(ValueError, match="sdist differs from source: README.md"):
        checker.check_dist(release.directory, release.root)


@pytest.mark.parametrize("archive_kind,member", [
    ("wheel", "../outside.txt"),
    ("sdist", "reacli-0.1.0/../../outside.txt"),
    ("wheel", "C:/outside.txt"),
    ("sdist", "C:/outside.txt"),
])
def test_archive_path_traversal_is_rejected(release, archive_kind, member):
    getattr(release, archive_kind + "_members")[member] = b"outside payload"
    _write_archives(release)

    with pytest.raises(ValueError, match="Unsafe archive path"):
        checker.check_dist(release.directory, release.root)


@pytest.mark.parametrize("archive_kind", ["wheel", "sdist"])
def test_archive_symlinks_are_rejected(release, archive_kind):
    if archive_kind == "wheel":
        member = zipfile.ZipInfo("rac/external-link")
        member.create_system = 3
        member.external_attr = (stat.S_IFLNK | 0o777) << 16
        with zipfile.ZipFile(release.wheel_path, "a") as archive:
            archive.writestr(member, b"../../outside")
    else:
        member = tarfile.TarInfo("reacli-0.1.0/external-link")
        member.type = tarfile.SYMTYPE
        member.linkname = "../../outside"
        _write_sdist(release, extra_member=member)

    with pytest.raises(ValueError):
        checker.check_dist(release.directory, release.root)


def test_old_artifacts_in_output_directory_are_rejected(release):
    shutil.copyfile(release.wheel_path, release.directory / "reacli-0.0.9-py3-none-any.whl")

    with pytest.raises(ValueError, match="exactly one wheel and one sdist"):
        checker.check_dist(release.directory, release.root)


def test_release_zip_rejects_symlink_and_unsafe_member(tmp_path):
    root = tmp_path / "root"
    root.mkdir()
    source = root / "source.txt"
    source.write_text("safe")
    outside = tmp_path / "outside.txt"
    outside.write_text("outside")
    link = root / "link.txt"
    link.symlink_to(outside)

    with pytest.raises(ValueError, match="non-symlink"):
        build_release.zip_files(
            tmp_path / "symlink.zip", [("link.txt", link)], [root]
        )
    for name in ("../outside.txt", r"..\outside.txt", r"C:\outside.txt"):
        with pytest.raises(ValueError, match="Unsafe ZIP member"):
            build_release.zip_files(tmp_path / "unsafe.zip", [(name, source)], [root])
    alias = tmp_path / "root-alias"
    alias.symlink_to(root, target_is_directory=True)
    with pytest.raises(ValueError, match="source root must not be a symlink"):
        build_release.zip_files(tmp_path / "root-alias.zip", [("source.txt", source)], [alias])


def test_release_source_root_rejects_symlink(tmp_path):
    root = tmp_path / "root"
    root.mkdir()
    alias = tmp_path / "alias"
    alias.symlink_to(root, target_is_directory=True)

    with pytest.raises(ValueError, match="source root must not be a symlink"):
        list(build_release._source_files(alias))
