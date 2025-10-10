import os
from .helper import get_temp_directory

from utilities.common_splunk_js_utilities import CommonJSUtilitiesFile


UTILITIES_FOLDER_PATH = os.path.join(os.path.dirname(__file__), os.path.pardir, 'src', 'utilities', 'common_splunk_js_utilities')


def test_implement_utility_create_folder():
    with get_temp_directory() as temp_dir:
        common_js_utilities_file = CommonJSUtilitiesFile('/app_read', temp_dir)
        result = common_js_utilities_file.implement_utility()

        folder_path = os.path.join(temp_dir, 'appserver', 'static')
        expected_file_path = os.path.join(folder_path, 'splunk_common_js_v_utilities.js')

        assert os.path.exists(folder_path)
        assert os.path.exists(expected_file_path)
        assert result == expected_file_path


def test_implement_utility_folder_exists():
    with get_temp_directory() as temp_dir:
        # Create the folder before running the test
        folder_path = os.path.join(temp_dir, 'appserver', 'static')
        os.makedirs(folder_path)

        common_js_utilities_file = CommonJSUtilitiesFile('/app_read', temp_dir)
        result = common_js_utilities_file.implement_utility()

        expected_file_path = os.path.join(folder_path, 'splunk_common_js_v_utilities.js')

        assert os.path.exists(expected_file_path)
        assert result == expected_file_path


def test_implement_utility_file_updated():
    with get_temp_directory() as temp_dir:

        folder_path = os.path.join(temp_dir, 'appserver', 'static')
        os.makedirs(folder_path)
        input_file_path = os.path.join(folder_path, 'splunk_common_js_v_utilities.js')

        with open(input_file_path, 'w') as input_file:
            input_file.write('Old content')

        common_js_utilities_file = CommonJSUtilitiesFile(input_file_path, temp_dir)
        result = common_js_utilities_file.implement_utility()

        folder_path = os.path.join(temp_dir, 'appserver', 'static')
        expected_file_path = os.path.join(folder_path, 'splunk_common_js_v_utilities.js')

        # Validate that the content of the file is updated
        with open(expected_file_path, 'r') as output_file:
            updated_content = output_file.read()

        assert "This file is generated and maintained by splunk-app-action" in updated_content
        assert "VSearchManagerUtility" in updated_content
        assert result == expected_file_path



def test_implement_utility_file_created_new():
    with get_temp_directory() as temp_dir:

        common_js_utilities_file = CommonJSUtilitiesFile("sample", temp_dir)
        result = common_js_utilities_file.implement_utility()

        folder_path = os.path.join(temp_dir, 'appserver', 'static')
        expected_file_path = os.path.join(folder_path, 'splunk_common_js_v_utilities.js')

        # Validate that the content of the file is updated
        with open(expected_file_path, 'r') as output_file:
            updated_content = output_file.read()

        assert "This file is generated and maintained by splunk-app-action" in updated_content
        assert "VSearchManagerUtility" in updated_content
        assert result == expected_file_path


def test_implement_utility_file_not_updated():
    with get_temp_directory() as temp_dir:

        folder_path = os.path.join(temp_dir, 'appserver', 'static')
        os.makedirs(folder_path)
        input_file_path = os.path.join(folder_path, 'splunk_common_js_v_utilities.js')

        with open(input_file_path, 'w') as input_file:
            with open(os.path.join(UTILITIES_FOLDER_PATH, 'splunk_common_js_v_utilities.js'), 'r') as actual_f:
                input_file.write(actual_f.read())

        common_js_utilities_file = CommonJSUtilitiesFile(input_file_path, temp_dir)
        result = common_js_utilities_file.implement_utility()

        assert result is None
