import os
import re
import configparser


def get_all_stanzas(config_file_path):
    """
    Retrieves all stanzas (sections) from a configuration file.

    Args:
        config_file_path (str): Path to the configuration file.

    Returns:
        list: A list of stanza (section) names.

    Raises:
        configparser.Error: If there's an error parsing the configuration file.
    """
    try:
        config = configparser.ConfigParser()
        config.read(config_file_path)

        return config.sections()

    except configparser.Error as e:
        raise ValueError(f"Error parsing configuration file '{config_file_path}': {e}")


def get_all_input_names(addon_name):
    """
    Get all Input names from Add-on
    """
    return get_all_stanzas(os.path.join('output', addon_name, 'default', 'inputs.conf'))


def generate_input_handler_file(addon_name, input_name):
    _file_path = os.path.join('output', addon_name, 'bin', f'{input_name}_handler.py')

    if os.path.exists(_file_path):
        print(f"Input handler python file for {input_name} already created by user ignoring.")
        return
    else:
        print(f"Creating input handler python file for {input_name}.")

    _content = """
from splunklib import modularinput as smi


def validate_input(input_script: smi.Script, definition: smi.ValidationDefinition):
    return


def stream_events(input_script: smi.Script, inputs: smi.InputDefinition, event_writer: smi.EventWriter):
    return

"""

    with open(_file_path, 'w') as f:
        f.write(_content)


def modify_original_input_py_file(addon_name, input_name):
    file_path = os.path.join('output', addon_name, 'bin', f'{input_name}.py')
    with open(file_path, "r") as f:
        file_content = f.read()
    
    # print(f"file_content1 = {file_content}")

    # Insert import statement for your modular input
    file_content = re.sub(
        r"(?m)^(import[^\n]*)$(?!.*^import[^\n]*)",
        r"\1\nimport " + input_name + "_handler",
        file_content,
        flags=re.DOTALL
    )

    # print(f"file_content2 = {file_content}")

    # Update validate_input method
    pattern_validate_input_fun = r"def validate_input[\w\W]*return\n"
    replacement_content_validate_input_fun = f"def validate_input(self, definition: smi.ValidationDefinition):\n        {input_name}_handler.validate_input(self, definition)\n\n"

    file_content = re.sub(pattern_validate_input_fun, replacement_content_validate_input_fun, file_content)

    # print(f"file_content3 = {file_content}")

    # Update stream_events method
    pattern_stream_events_fun = r"def stream_events[\w\W]*(?:\n\n)"
    replacement_content_stream_events_fun = f"def stream_events(self, inputs: smi.InputDefinition, event_writer: smi.EventWriter):\n        {input_name}_handler.stream_events(self, inputs, event_writer)\n\n\n"

    file_content = re.sub(pattern_stream_events_fun, replacement_content_stream_events_fun, file_content)

    # print(f"file_content4 = {file_content}")

    with open(file_path, "w") as f:
        f.write(file_content)


def additional_packaging(addon_name):
    print("Running additional_packaging.py for better inputs python handler file generation.")

    # Iterate over all inputs available
    for i in get_all_input_names(addon_name):
        print(f"Processing Input={i}")
        generate_input_handler_file(addon_name, i)
        modify_original_input_py_file(addon_name, i)
