import os
from .helper import get_temp_directory

from utilities.ucc_additional_packaging import UCCAdditionalPackagingUtility


UTILITIES_FOLDER_PATH = os.path.join(os.path.dirname(__file__), os.path.pardir, 'src', 'utilities', 'ucc_additional_packaging')



def test_implement_utility_file_updated():
    with get_temp_directory() as temp_dir:
        input_file_path = os.path.join(temp_dir, 'additional_packaging.py')

        with open(input_file_path, 'w') as input_file:
            input_file.write('Old content')

        utilities_file = UCCAdditionalPackagingUtility(input_file_path, os.path.join(temp_dir, "my_app"))
        result = utilities_file.implement_utility()

        expected_file_path = os.path.join(temp_dir, 'additional_packaging.py')

        # Validate that the content of the file is updated
        with open(expected_file_path, 'r') as output_file:
            updated_content = output_file.read()

        assert "This file is generated and maintained by splunk-app-action" in updated_content
        assert "additional_packaging(addon_name)" in updated_content
        assert result == expected_file_path



def test_implement_utility_file_created_new():
    with get_temp_directory() as temp_dir:

        utilities_file = UCCAdditionalPackagingUtility("sample", os.path.join(temp_dir, "my_app"))
        result = utilities_file.implement_utility()

        expected_file_path = os.path.join(temp_dir, 'additional_packaging.py')

        # Validate that the content of the file is updated
        with open(expected_file_path, 'r') as output_file:
            updated_content = output_file.read()

        assert "This file is generated and maintained by splunk-app-action" in updated_content
        assert "additional_packaging(addon_name)" in updated_content
        assert result == expected_file_path


def test_implement_utility_file_not_updated():
    with get_temp_directory() as temp_dir:

        input_file_path = os.path.join(temp_dir, 'additional_packaging.py')

        with open(input_file_path, 'w') as input_file:
            with open(os.path.join(UTILITIES_FOLDER_PATH, 'additional_packaging.py'), 'r') as actual_f:
                input_file.write(actual_f.read())

        utilities_file = UCCAdditionalPackagingUtility(input_file_path, os.path.join(temp_dir, "my_app"))
        result = utilities_file.implement_utility()

        assert result == None
