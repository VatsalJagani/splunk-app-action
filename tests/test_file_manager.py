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

import os

import pytest

from helpers.file_manager import (
    FullRawFileHandler,
    PartConfFileHandler,
    PartRawFileHandler,
    get_file_hash,
    get_folder_hash,
    get_multi_files_hash,
)

from .helper import get_temp_directory  # pyright: ignore


# Use a fixture to create temporary files with known content for testing
@pytest.fixture
def sample_file(tmp_path):
    file_path = tmp_path / "test_file.txt"
    file_path.write_text("This is a test file")
    return file_path


def test_get_file_hash_nonexistent_file():
    file_path = "path/to/nonexistent_file"
    with pytest.raises(FileNotFoundError):
        get_file_hash(file_path)


def test_get_file_hash_with_tmp_file(sample_file):
    expected_hash = "0b26e313ed4a7ca6904b0e9369e5b957"  # MD5 hash of "This is a test file"
    assert get_file_hash(sample_file) == expected_hash


def test_get_folder_hash_empty_folder():
    folder_path = "empty_folder"
    os.makedirs(folder_path)
    expected_hash = "d41d8cd98f00b204e9800998ecf8427e"  # MD5 hash of an empty string
    assert get_folder_hash(folder_path) == expected_hash
    os.rmdir(folder_path)


def test_get_folder_hash_with_files(sample_file):
    folder_path = sample_file.parent
    expected_hash = "894c0cee919eb49f7a36060c7a607fb7"  # Hash of the single file in the folder
    assert get_folder_hash(folder_path) == expected_hash


def test_get_folder_hash_nonexistent_folder():
    folder_path = "path/to/nonexistent_folder"
    with pytest.raises(Exception, match="Incorrect folder_path provided."):
        abc = get_folder_hash(folder_path)
        print(f"abc={abc}")


def test_get_multi_files_hash_empty_list():
    file_paths = []
    expected_hash = "d41d8cd98f00b204e9800998ecf8427e"  # MD5 hash of an empty string
    assert get_multi_files_hash(file_paths) == expected_hash


def test_get_multi_files_hash_multiple_files(sample_file):
    file_paths = [sample_file, sample_file]  # Use the same file twice for simplicity
    expected_hash = "91405dbee0a9c47e7bc657bda7cb29a9"  # Hypothetical hash of the combined hashes
    assert get_multi_files_hash(file_paths) == expected_hash


def test_config_file_changed():
    with get_temp_directory() as temp_dir:
        input_content = "[section1]\nkey1 = value1\nkey2 = value2"
        input_file = os.path.join(temp_dir, "input_file.conf")
        with open(input_file, "w") as f:
            f.write(input_content)

        output_file = os.path.join(temp_dir, "output_file.conf")
        handler = PartConfFileHandler(input_file, output_file, {"value1": "new_value1"})
        result = handler.validate_config()

        assert result is True

        with open(output_file) as f:
            updated_content = f.read()

        expected_content = "[section1]\nkey1 = new_value1\nkey2 = value2\n"
        assert updated_content == expected_content


def test_config_file_output_dir_created():
    with get_temp_directory() as temp_dir:
        input_content = "[section1]\nkey1 = value1\nkey2 = value2"
        input_file = os.path.join(temp_dir, "input_file.conf")
        with open(input_file, "w") as f:
            f.write(input_content)

        output_file = os.path.join(temp_dir, "new_output_dir", "output_file.conf")
        handler = PartConfFileHandler(input_file, output_file, {"value1": "new_value1"})
        result = handler.validate_config()

        assert result is True

        with open(output_file) as f:
            updated_content = f.read()

        expected_content = "[section1]\nkey1 = new_value1\nkey2 = value2\n"
        assert updated_content == expected_content


def test_config_file_merge_in_existing_file_changed_1():
    with get_temp_directory() as temp_dir:
        input_content = "[section1]\nkey1 = value1\nkey2 = value2"
        input_file = os.path.join(temp_dir, "input_file.conf")
        with open(input_file, "w") as f:
            f.write(input_content)

        output_file = os.path.join(temp_dir, "output_file.conf")
        output_content = "[section3]\nkey3 = value3"
        with open(output_file, "w") as f:
            f.write(output_content)

        handler = PartConfFileHandler(input_file, output_file, {"value1": "new_value1"})
        result = handler.validate_config()

        assert result is True

        with open(output_file) as f:
            updated_content = f.read()

        expected_content = (
            "[section3]\nkey3 = value3\n[section1]\nkey1 = new_value1\nkey2 = value2\n"
        )
        assert updated_content == expected_content


def test_config_file_merge_in_existing_file_changed_2():
    with get_temp_directory() as temp_dir:
        input_content = "[section1]\nkey1 = value1\nkey2 = value2"
        input_file = os.path.join(temp_dir, "input_file.conf")
        with open(input_file, "w") as f:
            f.write(input_content)

        output_file = os.path.join(temp_dir, "output_file.conf")
        output_content = "[section3]\nkey3 = value3"
        with open(output_file, "w") as f:
            f.write(output_content)

        handler = PartConfFileHandler(input_file, output_file)
        result = handler.validate_config()

        assert result is True

        with open(output_file) as f:
            updated_content = f.read()

        expected_content = "[section3]\nkey3 = value3\n[section1]\nkey1 = value1\nkey2 = value2\n"
        assert updated_content == expected_content


def test_config_file_unchanged():
    with get_temp_directory() as temp_dir:
        input_content = "[section1]\nkey1 = value1\nkey2 = value2"
        input_file_path = os.path.join(temp_dir, "input_file.conf")
        with open(input_file_path, "w") as f:
            f.write(input_content)

        output_file_path = os.path.join(temp_dir, "output_file.conf")
        with open(output_file_path, "w") as f:
            f.write(input_content)

        handler = PartConfFileHandler(input_file_path, output_file_path)
        result = handler.validate_config()

        assert result is False


def test_config_input_file_not_found():
    with get_temp_directory() as temp_dir:
        input_file = os.path.join(temp_dir, "nonexistent_input_file.conf")
        output_file = os.path.join(temp_dir, "output_file.conf")

        handler = PartConfFileHandler(input_file, output_file)
        with pytest.raises(FileNotFoundError, match="No such file or directory"):
            handler.validate_config()


def test_full_file_content_file_changed():
    with get_temp_directory() as temp_dir:
        input_content = "New content"
        input_file = os.path.join(temp_dir, "input_file.txt")
        with open(input_file, "w") as f:
            f.write(input_content)

        output_file = os.path.join(temp_dir, "output_file.txt")
        with open(output_file, "w") as f:
            f.write("Old content")

        handler = FullRawFileHandler(input_file, output_file)
        result = handler.validate_file_content()

        assert result is True

        with open(output_file) as f:
            updated_content = f.read()

        assert updated_content == input_content


def test_full_file_content_file_with_word_dict_changed():
    with get_temp_directory() as temp_dir:
        input_content = "New content"
        input_file = os.path.join(temp_dir, "input_file.txt")
        with open(input_file, "w") as f:
            f.write(input_content)

        output_file = os.path.join(temp_dir, "output_file.txt")
        with open(output_file, "w") as f:
            f.write("Old content")

        handler = FullRawFileHandler(input_file, output_file, {"New": "NEW"})
        result = handler.validate_file_content()

        assert result is True

        with open(output_file) as f:
            updated_content = f.read()

        assert updated_content == "NEW content"


def test_full_file_content_file_unchanged():
    with get_temp_directory() as temp_dir:
        input_content = "Same content"
        input_file = os.path.join(temp_dir, "input_file.txt")
        with open(input_file, "w") as f:
            f.write(input_content)

        output_file = os.path.join(temp_dir, "output_file.txt")
        with open(output_file, "w") as f:
            f.write(input_content)

        handler = FullRawFileHandler(input_file, output_file, {})
        result = handler.validate_file_content()

        assert result is False

        with open(output_file) as f:
            unchanged_content = f.read()

        assert unchanged_content == input_content


def test_full_file_content_output_file_not_exists():
    with get_temp_directory() as temp_dir:
        input_content = "New file content"
        input_file = os.path.join(temp_dir, "input_file.txt")
        with open(input_file, "w") as f:
            f.write(input_content)

        output_file = os.path.join(temp_dir, "output_file.txt")

        handler = FullRawFileHandler(input_file, output_file, {})
        result = handler.validate_file_content()

        assert result is True

        with open(output_file) as f:
            created_content = f.read()

        assert created_content == input_content


def test_part_file_content_marker_found():
    with get_temp_directory() as temp_dir:
        # Initial content in the file
        initial_content = "Existing content\nStartMarker1\nExisting middle content\nEndMarker1\n"

        # Create the input file with initial content
        input_file = os.path.join(temp_dir, "input_file.txt")
        with open(input_file, "w") as f:
            f.write(initial_content)

        # Specify the new content and markers
        new_content = "\nUpdated middle content\n"
        start_markers = ["StartMarker1"]
        end_markers = ["EndMarker1"]

        # Create the output file handler
        output_file = os.path.join(temp_dir, "output_file.txt")
        with open(output_file, "w") as f:
            f.write(initial_content)

        handler = PartRawFileHandler(input_file, output_file, {})

        # Call the validate_file_content method
        result = handler.validate_file_content(new_content, start_markers, end_markers)

        # Verify the result and content in the output file
        assert result is True

        with open(output_file) as f:
            updated_content = f.read()

        expected_content = "Existing content\nStartMarker1\nUpdated middle content\nEndMarker1\n"
        assert updated_content == expected_content


def test_part_file_content_marker_found_with_markers_to_add():
    with get_temp_directory() as temp_dir:
        # Initial content in the file
        initial_content = "Existing content\nStartMarker1\nExisting middle content\nEndMarker1\n"

        # Create the input file with initial content
        input_file = os.path.join(temp_dir, "input_file.txt")
        with open(input_file, "w") as f:
            f.write(initial_content)

        # Specify the new content and markers
        new_content = "\nUpdated middle content\n"
        start_markers = ["StartMarker1"]
        end_markers = ["EndMarker1"]

        # Create the output file handler
        output_file = os.path.join(temp_dir, "output_file.txt")
        with open(output_file, "w") as f:
            f.write(initial_content)

        handler = PartRawFileHandler(input_file, output_file, {})

        # Call the validate_file_content method
        result = handler.validate_file_content(new_content, start_markers, end_markers)

        # Verify the result and content in the output file
        assert result is True

        with open(output_file) as f:
            updated_content = f.read()

        expected_content = "Existing content\nStartMarker1\nUpdated middle content\nEndMarker1\n"
        assert updated_content == expected_content


def test_part_file_content_marker_not_found():
    with get_temp_directory() as temp_dir:
        # Initial content in the file
        initial_content = (
            "Existing content\nDifferentStartMarker\nExisting middle content\nDifferentEndMarker\n"
        )

        # Create the input file with initial content
        input_file = os.path.join(temp_dir, "input_file.txt")
        with open(input_file, "w") as f:
            f.write(initial_content)

        # Specify the new content and markers
        new_content = "\nUpdated middle content\n"
        start_markers = ["StartMarker1"]
        end_markers = ["EndMarker1"]

        # Create the output file handler
        output_file = os.path.join(temp_dir, "output_file.txt")
        with open(output_file, "w") as f:
            f.write(initial_content)

        handler = PartRawFileHandler(input_file, output_file, {})

        # Call the validate_file_content method
        result = handler.validate_file_content(new_content, start_markers, end_markers)

        # Verify the result and content in the output file
        assert result is True

        with open(output_file) as f:
            updated_content = f.read()

        expected_content = (
            "Existing content\nDifferentStartMarker\nExisting middle content\nDifferentEndMarker\n"
            + "\nUpdated middle content\n"
        )
        assert updated_content == expected_content


def test_part_file_content_marker_not_found_with_marker_to_add():
    with get_temp_directory() as temp_dir:
        # Initial content in the file
        initial_content = (
            "Existing content\nDifferentStartMarker\nExisting middle content\nDifferentEndMarker\n"
        )

        # Create the input file with initial content
        input_file = os.path.join(temp_dir, "input_file.txt")
        with open(input_file, "w") as f:
            f.write(initial_content)

        # Specify the new content and markers
        new_content = "\nUpdated middle content\n"
        start_markers = ["StartMarker1"]
        end_markers = ["EndMarker1"]
        start_marker_to_add = "ABCD EFGH"
        end_marker_to_add = "\n\n\n"

        # Create the output file handler
        output_file = os.path.join(temp_dir, "output_file.txt")
        with open(output_file, "w") as f:
            f.write(initial_content)

        handler = PartRawFileHandler(input_file, output_file, {})

        # Call the validate_file_content method
        result = handler.validate_file_content(
            new_content, start_markers, end_markers, start_marker_to_add, end_marker_to_add
        )

        # Verify the result and content in the output file
        assert result is True

        with open(output_file) as f:
            updated_content = f.read()

        expected_content = (
            "Existing content\nDifferentStartMarker\nExisting middle content\nDifferentEndMarker\n"
            + "ABCD EFGH\nUpdated middle content\n\n\n\n"
        )
        assert updated_content == expected_content


def test_part_file_content_exception_on_output_file_not_found():
    with get_temp_directory() as temp_dir:
        # Initial content in the file
        initial_content = "Existing content\nStartMarker1\nExisting middle content\nEndMarker1\n"

        # Create the input file with initial content
        input_file = os.path.join(temp_dir, "input_file.txt")
        with open(input_file, "w") as f:
            f.write(initial_content)

        # Specify the new content and markers
        new_content = "Updated middle content"
        start_markers = ["StartMarker1"]
        end_markers = ["EndMarker1"]

        output_file = os.path.join(temp_dir, "output_file.txt")
        # Note we aren't creating output file, so file don't exist
        handler = PartRawFileHandler(input_file, output_file, {})

        with pytest.raises(FileNotFoundError, match="No such file or directory"):
            handler.validate_file_content(new_content, start_markers, end_markers)


def test_validate_file_content_no_change_needed():
    with get_temp_directory() as temp_dir:
        # Initial content in the file
        initial_content = "Existing content\nStartMarker1\nExisting middle content\nEndMarker1\n"

        # Create the input file with initial content
        input_file = os.path.join(temp_dir, "input_file.txt")
        with open(input_file, "w") as f:
            f.write(initial_content)

        # Specify the new content and markers
        new_content = "\nExisting middle content\n"
        start_markers = ["StartMarker1"]
        end_markers = ["EndMarker1"]

        # Create the output file handler
        output_file = os.path.join(temp_dir, "output_file.txt")
        with open(output_file, "w") as f:
            f.write(initial_content)

        handler = PartRawFileHandler(input_file, output_file, {})

        # Call the validate_file_content method
        result = handler.validate_file_content(new_content, start_markers, end_markers)

        # Verify the result and content in the output file
        assert result is False

        with open(output_file) as f:
            unchanged_content = f.read()

        assert unchanged_content == initial_content


def test_validate_file_content_no_change_needed_with_marker_to_add():
    with get_temp_directory() as temp_dir:
        # Initial content in the file
        initial_content = "Existing content\nStartMarker1\nExisting middle content\nEndMarker1\n"

        # Create the input file with initial content
        input_file = os.path.join(temp_dir, "input_file.txt")
        with open(input_file, "w") as f:
            f.write(initial_content)

        # Specify the new content and markers
        new_content = "\nExisting middle content\n"
        start_markers = ["StartMarker1"]
        end_markers = ["EndMarker1"]
        start_marker_to_add = "ABCD EFGH"
        end_marker_to_add = "\n\n\n"

        # Create the output file handler
        output_file = os.path.join(temp_dir, "output_file.txt")
        with open(output_file, "w") as f:
            f.write(initial_content)

        handler = PartRawFileHandler(input_file, output_file, {})

        # Call the validate_file_content method
        result = handler.validate_file_content(
            new_content, start_markers, end_markers, start_marker_to_add, end_marker_to_add
        )

        # Verify the result and content in the output file
        assert result is False

        with open(output_file) as f:
            unchanged_content = f.read()

        assert unchanged_content == initial_content


def test_part_file_with_replacement_dict_input():
    with get_temp_directory() as temp_dir:
        # Initial content in the file
        initial_content = (
            "Existing XYZ content\nStartMarker1\nExisting middle content\nEndMarker1\n"
        )

        # Create the input file with initial content
        input_file = os.path.join(temp_dir, "input_file.txt")
        with open(input_file, "w") as f:
            f.write(initial_content)

        # Specify the new content and markers
        new_content = "\nUpdated middle content\n"
        start_markers = ["StartMarker1"]
        end_markers = ["EndMarker1"]

        # Create the output file handler
        output_file = os.path.join(temp_dir, "output_file.txt")
        with open(output_file, "w") as f:
            f.write(initial_content)

        handler = PartRawFileHandler(input_file, output_file, {"XYZ": "ZZZZZ"})

        # Call the validate_file_content method
        result = handler.validate_file_content(new_content, start_markers, end_markers)

        # Verify the result and content in the output file
        assert result is True

        with open(output_file) as f:
            updated_content = f.read()

        expected_content = (
            "Existing XYZ content\nStartMarker1\nUpdated middle content\nEndMarker1\n"
        )
        assert updated_content == expected_content


def test_part_file_with_replacement_dict_output():
    with get_temp_directory() as temp_dir:
        # Initial content in the file
        initial_content = "Existing content\nStartMarker1\nExisting middle content\nEndMarker1\n"

        # Create the input file with initial content
        input_file = os.path.join(temp_dir, "input_file.txt")
        with open(input_file, "w") as f:
            f.write(initial_content)

        # Specify the new content and markers
        new_content = "\nUpdated middle XYZ content\n"
        start_markers = ["StartMarker1"]
        end_markers = ["EndMarker1"]

        # Create the output file handler
        output_file = os.path.join(temp_dir, "output_file.txt")
        with open(output_file, "w") as f:
            f.write(initial_content)

        handler = PartRawFileHandler(input_file, output_file, {"XYZ": "ZZZZZ"})

        # Call the validate_file_content method
        result = handler.validate_file_content(new_content, start_markers, end_markers)

        # Verify the result and content in the output file
        assert result is True

        with open(output_file) as f:
            updated_content = f.read()

        expected_content = (
            "Existing content\nStartMarker1\nUpdated middle ZZZZZ content\nEndMarker1\n"
        )
        assert updated_content == expected_content
