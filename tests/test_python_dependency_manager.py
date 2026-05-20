# pyright: reportPrivateUsage=false
# pyright: reportUnusedVariable=false
# pyright: reportUnusedParameter=false
# pyright: reportMissingParameterType=false
# pyright: reportUnknownVariableType=false
# pyright: reportUnknownParameterType=false
# pyright: reportUnknownMemberType=false
# pyright: reportUnknownArgumentType=false
# pyright: reportFunctionMemberAccess=false
# pyright: reportUnannotatedClassAttribute=false
# pyright: reportUninitializedInstanceVariable=false

import os
import subprocess
import tarfile
import tempfile
import unittest
from pathlib import Path
from typing import override
from unittest.mock import MagicMock, patch

import python_dependency_manager  # pyright: ignore[reportMissingImports]
from helpers.saved_values import AppInfo, SavedPaths  # pyright: ignore[reportMissingImports]
from main import main  # pyright: ignore[reportMissingImports]

from .helper_test import setup_action_yml


def extract_app_build(tgz_file):
    """Extract app build and return files and folders."""
    extract_dir = "temp_extraction"
    os.makedirs(extract_dir, exist_ok=True)

    try:
        with tarfile.open(tgz_file, "r:gz") as tar:
            tar.extractall(extract_dir)

        all_files = []
        all_folders = []
        is_root = True

        for root, dirs, files in os.walk(extract_dir):
            if is_root:
                is_root = False
                continue

            for file in files:
                if file.startswith("._") or file == ".DS_Store":
                    continue
                relative_path = os.path.relpath(os.path.join(root, file), extract_dir)
                all_files.append(relative_path)

            for dir in dirs:
                relative_path = os.path.relpath(os.path.join(root, dir), extract_dir)
                all_folders.append(relative_path)

        return len(all_files), len(all_folders), all_files, all_folders

    finally:
        if os.path.exists(extract_dir):
            for root, dirs, files in os.walk(extract_dir, topdown=False):
                for file in files:
                    os.remove(os.path.join(root, file))
                for dir in dirs:
                    os.rmdir(os.path.join(root, dir))
            os.rmdir(extract_dir)


class TestPythonDependencyManager(unittest.TestCase):
    def test_python_deps_basic(self):
        """Test basic Python dependency installation. Requires network access for pip install."""
        with setup_action_yml(
            "repo_python_deps",
            app_dir="my_app_3",
            python_requirements_file="lib/requirements.txt",
            is_app_inspect_check="false",
        ):
            try:
                main()
            except RuntimeError as e:
                # Network issues can cause this test to fail
                if "Read timed out" in str(e) or "Failed to install dependencies" in str(e):
                    self.skipTest("Network connectivity required for this test")
                raise

            app_build_name = "my_app_3_1_2_3_1.tgz"
            assert os.path.isfile(app_build_name), f"App build {app_build_name} not found"

            file_count, folder_count, all_files, all_folders = extract_app_build(app_build_name)

            # Verify basic app structure
            assert "my_app_3/default/app.conf" in all_files
            assert "my_app_3/README.md" in all_files
            # requirements.txt should be removed from build
            assert "my_app_3/lib/requirements.txt" not in all_files

            # Verify lib folder was created
            assert "my_app_3/lib" in all_folders

            # Verify dependencies were installed
            # Check for requests library
            requests_files = [f for f in all_files if "my_app_3/lib/requests" in f]
            assert len(requests_files) > 0, "requests library not found in lib folder"

            # Check for certifi library
            certifi_files = [f for f in all_files if "my_app_3/lib/certifi" in f]
            assert len(certifi_files) > 0, "certifi library not found in lib folder"

            # Verify no .pyc or __pycache__ files
            pyc_files = [f for f in all_files if f.endswith(".pyc")]
            assert len(pyc_files) == 0, "Found .pyc files in build"

            pycache_folders = [f for f in all_folders if "__pycache__" in f]
            assert len(pycache_folders) == 0, "Found __pycache__ folders in build"

    def test_mutually_exclusive_ucc_and_python_deps(self):
        """Test that UCC and Python dependency manager cannot be used together."""
        with setup_action_yml(
            "repo_python_deps",
            app_dir="my_app_3",
            use_ucc_gen="true",
            python_requirements_file="lib/requirements.txt",
            is_app_inspect_check="false",
        ):
            # Should exit with error code 1
            with self.assertRaises(SystemExit) as cm:
                main()
            assert cm.exception.code == 1

    def test_requirements_file_not_found(self):
        """Test error when requirements.txt file doesn't exist."""
        with setup_action_yml(
            "repo_python_deps",
            app_dir="my_app_3",
            python_requirements_file="lib/nonexistent_requirements.txt",
            is_app_inspect_check="false",
        ):
            # Should raise FileNotFoundError
            with self.assertRaises(FileNotFoundError):
                main()


class TestPathJoinBug(unittest.TestCase):
    def test_absolute_app_dir_path_discards_prefix(self):
        """Verify os.path.join with absolute path discards the prefix (the bug)."""
        absolute_path = "/workspace/repodir/my_app"
        # This is the buggy behavior: absolute path discards "python_deps_build_dir"
        result = os.path.join("python_deps_build_dir", absolute_path)
        assert result == absolute_path

    def test_app_dir_name_produces_correct_path(self):
        """Verify os.path.join with relative name produces the correct path."""
        app_dir_name = "my_app"
        result = os.path.join("python_deps_build_dir", app_dir_name)
        assert result == "python_deps_build_dir/my_app"

    def test_app_dir_name_dot_produces_correct_path(self):
        """When app_dir_name is '.', the path should still be under the build dir."""
        result = os.path.join("python_deps_build_dir", ".")
        assert result == "python_deps_build_dir/."


class TestPythonVersionInput(unittest.TestCase):
    def _capture_subprocess(self, pip_install_calls):
        def side_effect(cmd, **kwargs):
            if "install" in cmd:
                pip_install_calls.append(list(cmd))
            return MagicMock(returncode=0, stdout="", stderr="")

        return side_effect

    def test_pip_install_uses_python_39_by_default(self):
        """uv pip install should target Python 3.9 when splunk_python_version is not specified."""
        pip_install_calls: list[list[str]] = []
        with setup_action_yml(
            "repo_python_deps",
            app_dir="my_app_3",
            python_requirements_file="lib/requirements.txt",
            is_app_inspect_check="false",
        ):
            with patch(
                "python_dependency_manager.subprocess.run",
                side_effect=self._capture_subprocess(pip_install_calls),
            ):
                main()

        assert len(pip_install_calls) == 1
        cmd = pip_install_calls[0]
        assert cmd[0] == "uv"
        assert "--python" in cmd
        assert cmd[cmd.index("--python") + 1] == "3.9"

    def test_pip_install_uses_custom_splunk_python_version(self):
        """uv pip install should use the splunk_python_version input when explicitly specified."""
        pip_install_calls: list[list[str]] = []
        with setup_action_yml(
            "repo_python_deps",
            app_dir="my_app_3",
            python_requirements_file="lib/requirements.txt",
            is_app_inspect_check="false",
            splunk_python_version="3.11",
        ):
            with patch(
                "python_dependency_manager.subprocess.run",
                side_effect=self._capture_subprocess(pip_install_calls),
            ):
                main()

        assert len(pip_install_calls) == 1
        cmd = pip_install_calls[0]
        assert cmd[0] == "uv"
        assert "--python" in cmd
        assert cmd[cmd.index("--python") + 1] == "3.11"


class TestPythonVersionFileExclusion(unittest.TestCase):
    def test_python_version_file_excluded_from_build(self):
        """The .python-version file must not appear in the final app build."""
        real_run = subprocess.run

        def mock_only_pip_install(cmd, **kwargs):
            if "pip" in cmd and "install" in cmd:
                return MagicMock(returncode=0, stdout="", stderr="")
            return real_run(cmd, **kwargs)

        with setup_action_yml(
            "repo_python_deps",
            app_dir="my_app_3",
            python_requirements_file="lib/requirements.txt",
            is_app_inspect_check="false",
        ):
            with patch(
                "python_dependency_manager.subprocess.run", side_effect=mock_only_pip_install
            ):
                main()

            app_build_name = "my_app_3_1_2_3_1.tgz"
            assert os.path.isfile(app_build_name), f"App build {app_build_name} not found"
            _fc, _dc, all_files, _fd = extract_app_build(app_build_name)
            python_version_files = [f for f in all_files if ".python-version" in f]
            assert len(python_version_files) == 0, (
                f".python-version found in build: {python_version_files}"
            )


class TestUvArtifactCleanup(unittest.TestCase):
    def _mock_pip(self, real_run, extra_files: dict[str, str] | None = None):
        """Side effect simulating uv pip install creating artifacts in the target dir.

        extra_files: mapping of relative path → file content to create inside target_dir.
        """

        def side_effect(cmd, **kwargs):
            if "pip" in cmd and "install" in cmd:
                target_dir = cmd[cmd.index("--target") + 1]
                os.makedirs(target_dir, exist_ok=True)
                with open(os.path.join(target_dir, ".lock"), "w"):
                    pass
                if extra_files:
                    for rel_path, content in extra_files.items():
                        full_path = os.path.join(target_dir, rel_path)
                        os.makedirs(os.path.dirname(full_path), exist_ok=True)
                        with open(full_path, "w") as f:
                            f.write(content)
                return MagicMock(returncode=0, stdout="", stderr="")
            return real_run(cmd, **kwargs)

        return side_effect

    def _run_and_extract(self, extra_files: dict[str, str] | None = None):
        real_run = subprocess.run
        with setup_action_yml(
            "repo_python_deps",
            app_dir="my_app_3",
            python_requirements_file="lib/requirements.txt",
            is_app_inspect_check="false",
        ):
            with patch(
                "python_dependency_manager.subprocess.run",
                side_effect=self._mock_pip(real_run, extra_files),
            ):
                main()

            app_build_name = "my_app_3_1_2_3_1.tgz"
            assert os.path.isfile(app_build_name), f"App build {app_build_name} not found"
            _fc, _dc, all_files, all_folders = extract_app_build(app_build_name)
            return all_files, all_folders

    def test_uv_lock_file_excluded_from_build(self):
        """The .lock file created by uv pip install must not appear in the final build."""
        all_files, _ = self._run_and_extract()
        lock_files = [f for f in all_files if ".lock" in f]
        assert len(lock_files) == 0, f".lock file found in build: {lock_files}"

    def test_bin_with_only_console_scripts_excluded_from_build(self):
        """bin/ containing only shebang scripts (uv console entry points) is removed from build."""
        all_files, all_folders = self._run_and_extract(
            extra_files={
                "bin/normalizer": "#!/usr/bin/env python3\nprint('normalizer')\n",
                "bin/another_tool": "#!/usr/bin/env python\nprint('tool')\n",
            }
        )
        lib_bin = [f for f in all_folders if f.endswith("lib/bin")]
        assert len(lib_bin) == 0, f"lib/bin/ found in build: {lib_bin}"

    def test_bin_with_non_script_files_kept_in_build(self):
        """bin/ containing non-shebang files (real Python module) is NOT removed from build."""
        all_files, all_folders = self._run_and_extract(
            extra_files={
                "bin/normalizer": "#!/usr/bin/env python3\nprint('normalizer')\n",
                "bin/__init__.py": "# real Python module\n",
            }
        )
        lib_bin = [f for f in all_folders if f.endswith("lib/bin")]
        assert len(lib_bin) > 0, "lib/bin/ should be kept when it contains non-script files"

    def test_bin_with_subdirectory_kept_in_build(self):
        """bin/ containing a subdirectory is NOT removed (subdirs can't be validated as scripts)."""
        all_files, all_folders = self._run_and_extract(
            extra_files={
                "bin/normalizer": "#!/usr/bin/env python3\nprint('normalizer')\n",
                "bin/subpackage/__init__.py": "# subpackage\n",
            }
        )
        lib_bin = [f for f in all_folders if f.endswith("lib/bin")]
        assert len(lib_bin) > 0, "lib/bin/ should be kept when it contains subdirectories"
        assert any("bin/subpackage/__init__.py" in f for f in all_files), (
            "bin/subpackage/__init__.py should be preserved in the build"
        )

    def test_bin_with_dangling_symlink_kept_in_build(self):
        """bin/ containing a dangling symlink is NOT removed (uncertain content — preserve)."""
        real_run = subprocess.run

        def mock_pip_with_dangling_symlink(cmd, **kwargs):
            if "pip" in cmd and "install" in cmd:
                target_dir = cmd[cmd.index("--target") + 1]
                os.makedirs(os.path.join(target_dir, "bin"), exist_ok=True)
                with open(os.path.join(target_dir, ".lock"), "w"):
                    pass
                with open(os.path.join(target_dir, "bin", "normalizer"), "w") as f:
                    f.write("#!/usr/bin/env python3\n")
                os.symlink(
                    "/nonexistent/target",
                    os.path.join(target_dir, "bin", "dangling_link"),
                )
                return MagicMock(returncode=0, stdout="", stderr="")
            return real_run(cmd, **kwargs)

        with setup_action_yml(
            "repo_python_deps",
            app_dir="my_app_3",
            python_requirements_file="lib/requirements.txt",
            is_app_inspect_check="false",
        ):
            with patch(
                "python_dependency_manager.subprocess.run",
                side_effect=mock_pip_with_dangling_symlink,
            ):
                main()

            app_build_name = "my_app_3_1_2_3_1.tgz"
            assert os.path.isfile(app_build_name), f"App build {app_build_name} not found"
            _fc, _dc, all_files, all_folders = extract_app_build(app_build_name)
            lib_bin = [f for f in all_folders if f.endswith("lib/bin")]
            assert len(lib_bin) > 0, "lib/bin/ should be kept when it contains a dangling symlink"

    def test_dangling_symlink_outside_bin_preserved_in_build(self):
        """A dangling symlink outside bin/ (e.g., installed into lib/) must survive into the tarball."""
        real_run = subprocess.run

        def mock_pip_with_lib_symlink(cmd, **kwargs):
            if "pip" in cmd and "install" in cmd:
                target_dir = cmd[cmd.index("--target") + 1]
                os.makedirs(target_dir, exist_ok=True)
                os.symlink("/nonexistent/target", os.path.join(target_dir, "dangling_lib_link"))
                return MagicMock(returncode=0, stdout="", stderr="")
            return real_run(cmd, **kwargs)

        with setup_action_yml(
            "repo_python_deps",
            app_dir="my_app_3",
            python_requirements_file="lib/requirements.txt",
            is_app_inspect_check="false",
        ):
            with patch(
                "python_dependency_manager.subprocess.run",
                side_effect=mock_pip_with_lib_symlink,
            ):
                main()

            app_build_name = "my_app_3_1_2_3_1.tgz"
            assert os.path.isfile(app_build_name), f"App build {app_build_name} not found"
            with tarfile.open(app_build_name, "r:gz") as tar:
                symlink_names = [m.name for m in tar.getmembers() if m.issym()]
            assert any("dangling_lib_link" in n for n in symlink_names), (
                f"dangling symlink in lib/ should be preserved in the tarball; symlinks found: {symlink_names}"
            )


class TestRemoveNotAllowedExecutablesFromLib(unittest.TestCase):
    """Tests for is_remove_not_allowed_executables_from_lib in install_dependencies."""

    temp_dir: tempfile.TemporaryDirectory[str]
    original_cwd: str
    saved_paths: SavedPaths
    app_info: AppInfo

    @override
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.original_cwd = os.getcwd()
        os.chdir(self.temp_dir.name)

        # Create repo/app/lib structure with requirements.txt
        repo_dir = os.path.join(self.temp_dir.name, "repodir")
        app_dir_name = "my_app"
        lib_dir = os.path.join(repo_dir, app_dir_name, "lib")
        os.makedirs(lib_dir)
        Path(os.path.join(lib_dir, "requirements.txt")).write_text("requests\n")
        Path(os.path.join(repo_dir, app_dir_name, "default")).mkdir()
        Path(os.path.join(repo_dir, app_dir_name, "default", "app.conf")).write_text(
            "[launcher]\nversion = 1.0.0\n"
        )

        self.saved_paths = MagicMock(spec=SavedPaths)
        self.saved_paths.repo_dir_path = repo_dir
        self.saved_paths.app_dir_name = app_dir_name

        self.app_info = MagicMock(spec=AppInfo)
        self.app_info.package_id = "my_app"

    @override
    def tearDown(self) -> None:
        os.chdir(self.original_cwd)
        self.temp_dir.cleanup()

    def _mock_pip_install_with_so_files(self, cmd: list[str], **kwargs) -> MagicMock:
        """Simulate uv pip install creating platform-specific .so files and a pure Python file."""
        if "install" in cmd:
            target_dir = cmd[cmd.index("--target") + 1]
            os.makedirs(target_dir, exist_ok=True)
            Path(
                os.path.join(target_dir, "charset_normalizer.cpython-39-x86_64-linux-gnu.so")
            ).write_bytes(b"\x7fELF")
            Path(os.path.join(target_dir, "pure_python_module.py")).write_text("# pure python\n")
        return MagicMock(returncode=0, stdout="", stderr="")

    def _fake_mimetype(self, path: str) -> str:
        if path.endswith(".so"):
            return "application/x-sharedlib"
        return "text/plain"

    def test_so_files_removed_when_enabled(self) -> None:
        """x86_64 .so files are removed when is_remove_not_allowed_executables_from_lib=True."""
        with patch(
            "python_dependency_manager.subprocess.run",
            side_effect=self._mock_pip_install_with_so_files,
        ):
            with patch("helpers.lib_cleanup.magic.Magic") as mock_magic_cls:
                mock_magic_instance = MagicMock()
                mock_magic_instance.from_file.side_effect = self._fake_mimetype
                mock_magic_cls.return_value = mock_magic_instance

                with patch.dict(
                    os.environ,
                    {
                        "INPUT_PYTHON_REQUIREMENTS_FILE": "lib/requirements.txt",
                        "INPUT_SPLUNK_PYTHON_VERSION": "3.9",
                    },
                ):
                    python_dependency_manager.install_dependencies(
                        self.saved_paths,
                        self.app_info,
                        is_remove_not_allowed_executables_from_lib=True,
                    )

        lib_dir = Path("python_deps_generated_build") / "lib"
        so_files = list(lib_dir.glob("*.so"))
        assert len(so_files) == 0, f".so files should be removed but found: {so_files}"
        assert (lib_dir / "pure_python_module.py").exists(), "pure Python file should be kept"

    def test_so_files_kept_when_disabled(self) -> None:
        """x86_64 .so files are kept when is_remove_not_allowed_executables_from_lib=False."""
        with patch(
            "python_dependency_manager.subprocess.run",
            side_effect=self._mock_pip_install_with_so_files,
        ):
            with patch.dict(
                os.environ,
                {
                    "INPUT_PYTHON_REQUIREMENTS_FILE": "lib/requirements.txt",
                    "INPUT_SPLUNK_PYTHON_VERSION": "3.9",
                },
            ):
                python_dependency_manager.install_dependencies(
                    self.saved_paths,
                    self.app_info,
                    is_remove_not_allowed_executables_from_lib=False,
                )

        lib_dir = Path("python_deps_generated_build") / "lib"
        so_files = list(lib_dir.glob("*.so"))
        assert len(so_files) == 1, f".so file should be kept but found: {so_files}"

    def test_magic_failure_keeps_files(self) -> None:
        """When magic raises an exception for a file, that file is left untouched."""
        with patch(
            "python_dependency_manager.subprocess.run",
            side_effect=self._mock_pip_install_with_so_files,
        ):
            with patch("helpers.lib_cleanup.magic.Magic", side_effect=Exception("magic error")):
                with patch.dict(
                    os.environ,
                    {
                        "INPUT_PYTHON_REQUIREMENTS_FILE": "lib/requirements.txt",
                        "INPUT_SPLUNK_PYTHON_VERSION": "3.9",
                    },
                ):
                    python_dependency_manager.install_dependencies(
                        self.saved_paths,
                        self.app_info,
                        is_remove_not_allowed_executables_from_lib=True,
                    )

        lib_dir = Path("python_deps_generated_build") / "lib"
        so_files = list(lib_dir.glob("*.so"))
        assert len(so_files) == 1, ".so file should be kept when magic raises an error"
