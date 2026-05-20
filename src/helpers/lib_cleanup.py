import os

import github_action_toolkit as gat
import magic


def remove_not_allowed_executables(lib_dir: str) -> None:
    """Remove files with mimetype application/x-executable or application/x-sharedlib from lib_dir.

    Walks lib_dir recursively and deletes any file whose mimetype is
    application/x-executable or application/x-sharedlib. Files that cannot
    be identified (magic failure) are left untouched and a warning is logged.

    Args:
        lib_dir: Path to the lib directory to clean. No-op if the directory does not exist.
    """
    if not os.path.isdir(lib_dir):
        gat.info(f"lib directory not found, skipping executable cleanup: {lib_dir}")
        return

    removed_files_count = 0
    for root, _, files in os.walk(lib_dir):
        for file_name in files:
            file_path = os.path.join(root, file_name)
            try:
                magic_mime = magic.Magic(mime=True)
                mimetype_val = magic_mime.from_file(file_path)  # pyright: ignore[reportUnknownMemberType, reportUnknownVariableType]
            except Exception as e:
                gat.warning(f"magic failed for {file_path}: {e}")
                continue
            if mimetype_val in ("application/x-executable", "application/x-sharedlib"):
                os.remove(file_path)
                removed_files_count += 1
                gat.info(f"Removed not allowed executable type: {file_path} ({mimetype_val})")

    gat.debug(f"Removed not allowed executables count: {removed_files_count}")
