import hashlib
import os
import pathlib
from collections.abc import Sequence

import github_action_toolkit as gat

from helpers.splunk_config_parser import SplunkConfigParser


def get_file_hash(file_path: str) -> str:
    """Generate MD5 hash for a single file."""
    hash_md5 = hashlib.md5()
    try:
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
        return hash_md5.hexdigest()
    except OSError as e:
        raise OSError(f"Unable to read file '{file_path}': {e}") from e


def get_folder_hash(folder_path: str) -> str:
    """Generate MD5 hash for all files in a folder."""
    hash_md5 = hashlib.md5()
    if not os.path.isdir(folder_path):
        raise ValueError(f"Path '{folder_path}' is not a directory or does not exist.")
    for root, _dirs, files in os.walk(folder_path):
        for file in files:
            file_path = os.path.join(root, file)
            try:
                file_hash = get_file_hash(file_path)
                hash_md5.update(file_hash.encode("utf-8"))
            except OSError as e:
                gat.warning(f"Skipping file {file_path}: {e}")
                continue
    return hash_md5.hexdigest()


def get_multi_files_hash(file_paths: Sequence[str]) -> str:
    hash_md5 = hashlib.md5()
    for file_path in file_paths:
        file_hash = get_file_hash(file_path)
        hash_md5.update(file_hash.encode("utf-8"))
    return hash_md5.hexdigest()


class BaseFileHandler:
    def __init__(
        self,
        input_file_path: str,
        output_file_path: str,
        words_for_replacement: dict[str, str] | None = None,
    ) -> None:
        self.input_file_path: str = input_file_path
        self.output_file_path: str = output_file_path
        self.words_for_replacement: dict[str, str] = words_for_replacement or {}

    def text_words_replacement(self, content: str) -> str:
        # do words replacement for file content
        for word, replacement in self.words_for_replacement.items():
            content = content.replace(word, replacement)

        return content

    def get_input_file_content(self) -> str:
        input_content = None
        with open(self.input_file_path) as fr:
            input_content = fr.read()

        return self.text_words_replacement(input_content)

    def create_output_directory_path_if_not_exist(self) -> None:
        output_dir_path = os.path.dirname(self.output_file_path)
        pathlib.Path(output_dir_path).mkdir(parents=True, exist_ok=True)


class PartConfFileHandler(BaseFileHandler):
    def _util_write_config_option(
        self, writer_parser: SplunkConfigParser, sect: str, key: str, value: str
    ) -> None:
        if not writer_parser.has_section(sect):
            writer_parser.add_section(sect)
        writer_parser.set(sect, key, value)

    def validate_config(self) -> bool:
        input_content = self.get_input_file_content()
        temp_file = f"{self.input_file_path}_temp"
        with open(temp_file, "w") as f:
            f.write(input_content)

        input_parser = SplunkConfigParser(temp_file)

        self.create_output_directory_path_if_not_exist()
        if not os.path.exists(self.output_file_path):
            with open(self.output_file_path, "w") as f:
                pass  # writing empty file

        output_parser = SplunkConfigParser(self.output_file_path)
        is_file_changed = output_parser.merge(input_parser)

        if is_file_changed:
            output_parser.write(self.output_file_path)

        return is_file_changed


class FullRawFileHandler(BaseFileHandler):
    def validate_file_content(self) -> bool:
        input_content = self.get_input_file_content()

        already_present_file_content = None
        if os.path.isfile(self.output_file_path):
            with open(self.output_file_path) as fr:
                already_present_file_content = fr.read()

        if already_present_file_content != input_content:
            gat.debug(f"File changed - file={self.output_file_path}")
            self.create_output_directory_path_if_not_exist()
            with open(self.output_file_path, "w") as fw:
                fw.write(input_content)
            return True
        return False


class PartRawFileHandler(BaseFileHandler):
    def validate_file_content(
        self,
        new_content: str,
        start_markers: Sequence[str],
        end_markers: Sequence[str],
        start_marker_to_add: str = "",
        end_marker_to_add: str = "",
    ) -> bool:
        new_content = self.text_words_replacement(new_content)

        content = ""
        lower_content = ""
        start_index = -1
        end_index = -1

        with open(self.output_file_path) as file:
            content = file.read()
            lower_content = content.lower()

        for sm in start_markers:
            start_index = lower_content.find(sm.lower())
            if start_index >= 0:
                start_index += len(sm)
                break

        if start_index > 0:
            for em in end_markers:
                end_index = lower_content.find(em.lower(), start_index)
                if end_index >= 0:
                    break

        if start_index >= 0:
            # Content found
            if end_index < 0:
                end_index = len(lower_content) - 1

            gat.debug(f"Found start_index={start_index}, end_index={end_index}")

            updated_content = content[:start_index] + new_content + content[end_index:]

        else:
            # Content not found in the file
            updated_content = content + start_marker_to_add + new_content + end_marker_to_add

        if updated_content != content:
            with open(self.output_file_path, "w") as fw:
                fw.write(updated_content)
            return True

        return False
