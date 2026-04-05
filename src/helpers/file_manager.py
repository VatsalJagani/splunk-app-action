import hashlib
import os
import pathlib
from collections.abc import Sequence

import github_action_toolkit as gat

from helpers.splunk_config_parser import SplunkConfigParser


def get_file_hash(file_path: str) -> str:
    """Generate MD5 hash for a single file."""
    hash_md5 = hashlib.md5(usedforsecurity=False)
    try:
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
        return hash_md5.hexdigest()
    except OSError as e:
        raise OSError(f"Unable to read file '{file_path}': {e}") from e


def get_folder_hash(folder_path: str) -> str:
    """Generate MD5 hash for all files in a folder."""
    hash_md5 = hashlib.md5(usedforsecurity=False)
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
    """
    Generate a combined MD5 hash for multiple files.

    Args:
        file_paths: Sequence of file paths to hash.

    Returns:
        Combined MD5 hash as a hexadecimal string.
    """
    hash_md5 = hashlib.md5(usedforsecurity=False)
    for file_path in file_paths:
        file_hash = get_file_hash(file_path)
        hash_md5.update(file_hash.encode("utf-8"))
    return hash_md5.hexdigest()


class BaseFileHandler:
    """
    Base class for handling file operations with template word replacement.

    Provides common functionality for reading input files, performing word
    replacements, and writing to output files. Used by specialized handlers
    for different file types.
    """

    def __init__(
        self,
        input_file_path: str,
        output_file_path: str,
        words_for_replacement: dict[str, str] | None = None,
    ) -> None:
        """
        Initialize the file handler.

        Args:
            input_file_path: Path to the input/template file.
            output_file_path: Path where the processed file will be written.
            words_for_replacement: Dictionary mapping placeholder strings to their
                replacement values. Defaults to empty dict if not provided.
        """
        self.input_file_path: str = input_file_path
        self.output_file_path: str = output_file_path
        self.words_for_replacement: dict[str, str] = words_for_replacement or {}

    def text_words_replacement(self, content: str) -> str:
        """
        Perform word/phrase replacements in file content.

        Args:
            content: Original file content.

        Returns:
            Content with all replacements applied.
        """
        # do words replacement for file content
        for word, replacement in self.words_for_replacement.items():
            content = content.replace(word, replacement)

        return content

    def get_input_file_content(self) -> str:
        """
        Read input file content and apply word replacements.

        Returns:
            File content with replacements applied.
        """
        input_content = None
        with open(self.input_file_path) as fr:
            input_content = fr.read()

        return self.text_words_replacement(input_content)

    def create_output_directory_path_if_not_exist(self) -> None:
        """Create the output directory if it doesn't exist."""
        output_dir_path = os.path.dirname(self.output_file_path)
        pathlib.Path(output_dir_path).mkdir(parents=True, exist_ok=True)


class PartConfFileHandler(BaseFileHandler):
    """
    Handler for merging partial Splunk .conf file content.

    Reads configuration from an input file and merges it with an existing output
    .conf file, preserving existing settings while adding or updating values from
    the input file.
    """

    def _util_write_config_option(
        self, writer_parser: SplunkConfigParser, sect: str, key: str, value: str
    ) -> None:
        """
        Write a configuration option to the parser, creating the section if needed.

        Args:
            writer_parser: Configuration parser to write to.
            sect: Section name.
            key: Configuration key.
            value: Configuration value.
        """
        if not writer_parser.has_section(sect):
            writer_parser.add_section(sect)
        writer_parser.set(sect, key, value)

    def validate_config(self) -> bool:
        """
        Merge input configuration with output file and write if changed.

        Reads the input .conf file, merges it with the existing output .conf file,
        and writes the merged result if any changes were detected.

        Returns:
            True if the output file was modified, False otherwise.
        """
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
    """
    Handler for completely replacing file content.

    Reads input file content, applies word replacements, and writes it to the output
    file, completely replacing any existing content. Only writes if content has changed.
    """

    def validate_file_content(self) -> bool:
        """
        Compare and update file content if changed.

        Reads the input file, applies word replacements, compares with existing
        output file content, and writes the new content if different.

        Returns:
            True if the output file was modified, False otherwise.
        """
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
    """
    Handler for updating specific sections of a file based on markers.

    Searches for start and end markers in an existing file and replaces the content
    between them, or appends new content with markers if not found. Useful for
    maintaining auto-generated sections within larger files.
    """

    def validate_file_content(
        self,
        new_content: str,
        start_markers: Sequence[str],
        end_markers: Sequence[str],
        start_marker_to_add: str = "",
        end_marker_to_add: str = "",
    ) -> bool:
        """
        Update or insert content between markers in a file.

        Searches for any of the start markers and end markers in the file. If found,
        replaces the content between them. If not found, appends the content with
        the specified markers.

        Args:
            new_content: Content to insert or replace.
            start_markers: List of possible start marker strings to search for.
            end_markers: List of possible end marker strings to search for.
            start_marker_to_add: Marker to add before content if section not found.
            end_marker_to_add: Marker to add after content if section not found.

        Returns:
            True if the file was modified, False otherwise.
        """
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
