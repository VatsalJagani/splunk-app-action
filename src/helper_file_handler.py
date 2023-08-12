
import os, pathlib
from helper_splunk_config_parser import SplunkConfigParser


class BaseFileHandler:
    def __init__(self, input_file_path, output_file_path, words_for_replacement=dict()) -> None:
        self.input_file_path = input_file_path
        self.output_file_path = output_file_path
        self.words_for_replacement: dict = words_for_replacement


    def get_input_file_content(self):
        input_content = None
        with open(self.input_file_path, 'r') as fr:
            input_content = fr.read()
        
        for word, replacement in self.words_for_replacement.items():
            input_content = input_content.replace(word, replacement)

        return input_content


    def create_output_directory_path_if_not_exist(self):
        output_dir_path = os.path.dirname(self.output_file_path)
        pathlib.Path(output_dir_path).mkdir(parents=True, exist_ok=True)



class PartConfFileHandler(BaseFileHandler):
    def _util_write_config_option(self, writer_parser: SplunkConfigParser, sect, key, value):
        if not writer_parser.has_section(sect):
            writer_parser.add_section(sect)
        writer_parser.set(sect, key, value)


    def validate_config(self):
        input_content = self.get_input_file_content()
        temp_file = '{}_temp'.format(self.input_file_path)
        with open(temp_file, 'w') as f:
            f.write(input_content)

        input_parser = SplunkConfigParser(temp_file)

        self.create_output_directory_path_if_not_exist()
        output_parser = SplunkConfigParser(self.output_file_path)

        is_file_changed = output_parser.merge(input_parser)

        if is_file_changed:
            output_parser.write(self.output_file_path)

        return is_file_changed



class FullRawFileHandler(BaseFileHandler):

    def validate_file_content(self):
        input_content = self.get_input_file_content()

        already_present_file_content = None
        if os.path.isfile(self.output_file_path):
            with open(self.output_file_path, 'r') as fr:
                already_present_file_content = fr.read()

        if already_present_file_content != input_content:
            print("File changed - file={}".format(self.output_file_path))
            self.create_output_directory_path_if_not_exist()
            with open(self.output_file_path, 'w') as fw:
                fw.write(input_content)
            return True
        return False



class PartRawFileHandler(BaseFileHandler):

    def validate_file_content(self, new_content, start_markers, end_markers, start_marker_to_add='', end_marker_to_add=''):
        content = ''
        lower_content = ''
        start_index = -1
        end_index = -1

        with open(self.output_file_path, 'r') as file:
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

            # print(f"start_index={start_index}, end_index={end_index}")

            updated_content = content[:start_index] + new_content + content[end_index:]

        else:
            # Content not found in the file
            updated_content = content + start_marker_to_add + new_content + end_marker_to_add

        if updated_content != content:
            with open(self.output_file_path, 'w') as fw:
                fw.write(updated_content)
            return True

        return False
