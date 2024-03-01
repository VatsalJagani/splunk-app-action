
import os

MULTI_LINE_CHAR = '\\'
COMMENT_CHAR = '#'
FILE_SECTION = '___FILE___'
NEW_LINE_CHAR = '\n'


class _SplunkStanzaOptions:
    def __init__(self) -> None:
        self._stanza_content = []
        self._stanza_pre_comments = []


    def add(self, key, value=None):
        if value is not None:
            self._stanza_content.append((key, value))
        else:
            self._stanza_content.append(key)


    def extend(self, list_of_attributes):
        self._stanza_content.extend(list_of_attributes)


    def add_stanza_pre_comments(self, comments):
        self._stanza_pre_comments = comments.copy()


    def __getitem__(self, key):
        for key_value in self._stanza_content:
            if type(key_value) == tuple:
                if key_value[0] == key:
                    return key_value[1]
        raise KeyError(key)


    def __setitem__(self, key, value):
        self.add(key, value)


    def __delitem__(self, key):
        for i in range(len(self._stanza_content)):
            key_value = self._stanza_content[i]
            if type(key_value) == tuple:
                if key_value[0] == key:
                    self._stanza_content.pop(i)
                    return
        raise KeyError(key)


    def __contains__(self, key):
        for key_value in self._stanza_content:
            if type(key_value) == tuple:
                if key_value[0] == key:
                    return True
        return False


    def __len__(self):
        length = 0
        for key_value in self._stanza_content:
            if type(key_value) == tuple:
                length += 1
        return length


    def __iter__(self):
        return iter(self._stanza_content)


    def merge(self, second_options_obj, to_merge_pre_stanza_comments=True):
        is_changed = False

        if to_merge_pre_stanza_comments:
            original_stanza_pre_comments = self._stanza_pre_comments.copy()

            for _pre_comment_line in second_options_obj._stanza_pre_comments:
                if _pre_comment_line not in original_stanza_pre_comments:
                    self._stanza_pre_comments.append(_pre_comment_line)

        for key_value in second_options_obj:
            if type(key_value) == str:
                if key_value not in self._stanza_content:
                    self._stanza_content.append(key_value)
                    is_changed = True

            elif type(key_value) == tuple:
                option = key_value[0]
                value = key_value[1]

                for i in range(len(self._stanza_content)):
                    ex_key_val = self._stanza_content[i]
                    if type(ex_key_val) != tuple:
                        continue

                    ex_op = ex_key_val[0]
                    ex_val = ex_key_val[1]

                    if ex_op == option:
                        if value != ex_val:
                            self._stanza_content[i] = (option, value)
                            is_changed = True
                        break
                    else:
                        continue

                else:
                    # no match found, add new
                    self._stanza_content.append((option, value))
                    is_changed = True

            else:
                raise Exception(
                    "SplunkConfigParser: Unexpected parsing error while writing the conf file.")

        return is_changed


    def __str__(self) -> str:
        content_str = ''
        for key_value in self._stanza_content:
            if type(key_value) == str:
                content_str += f'{key_value}\n'

            elif type(key_value) == tuple:
                option = key_value[0]
                value = key_value[1]

                if NEW_LINE_CHAR in value:
                    new_line_ch = NEW_LINE_CHAR + '\n'
                    value = new_line_ch.join(value.splitlines())

                content_str += f'{option} = {value}\n'

        return content_str


    def __repr__(self) -> str:
        return self.__str__()


    def as_string(self, section) -> str:
        content_str = "\n".join(self._stanza_pre_comments)
        if content_str:
            content_str += "\n"
        if section != FILE_SECTION:
            content_str += f"[{section}]"
        if content_str:
            content_str += "\n"
        content_str += str(self)
        return content_str



class SplunkConfigParser:

    def __init__(self, file_path):
        self.file_path = file_path
        self._content = {}
        self.read()


    def read(self, encoding=None):
        if os.path.isfile(self.file_path):
            with open(self.file_path, 'r', encoding=encoding) as file:
                content = file.read()
            self._parse(content)
        else:
            raise Exception("Splunk Conf File Not Found.")


    def _parse(self, content):
        lines = content.splitlines()
        current_section = FILE_SECTION
        self._content[current_section] = _SplunkStanzaOptions()
        current_option = None
        current_value = []

        self.comments_before_stanza = []

        def _handle_stanza_pre_comments(next_line_type, line):
            if next_line_type == "COMMENT":
                self.comments_before_stanza.append(line)
            elif (next_line_type == "EMPTY_LINE" or next_line_type == "OPTION"):
                if self.comments_before_stanza:
                    self._content[current_section].extend(
                        self.comments_before_stanza)
                    self.comments_before_stanza = []
            elif next_line_type == "STANZA" and self.comments_before_stanza:
                self._content[current_section].add_stanza_pre_comments(
                    self.comments_before_stanza)
                self.comments_before_stanza = []

        for original_line in lines:
            line = original_line.strip()

            # Empty Line
            if not line:
                _handle_stanza_pre_comments('EMPTY_LINE', line)
                self._content[current_section].add(original_line)

            # Comment Line
            # comment character, preserve the comments in the conf file
            elif line.startswith(COMMENT_CHAR):
                _handle_stanza_pre_comments('COMMENT', original_line)

            # Stanza line - []
            elif current_option is None and line.startswith('[') and line.endswith(']'):
                current_section = line[1:-1]
                if current_section not in self._content:
                    self._content[current_section] = _SplunkStanzaOptions()
                else:
                    # TODO - Handle the same stanza in the file again
                    pass
                _handle_stanza_pre_comments('STANZA', line)

            # New option line
            elif current_option is None and '=' in line:
                _handle_stanza_pre_comments('OPTION', line)

                option, value = line.split('=', 1)
                option = option.strip()
                value = value.strip()

                if len(value) > 0 and value[-1] == MULTI_LINE_CHAR:
                    current_option = option
                    current_value.append(value[:-1])
                else:
                    self._content[current_section].add(option, value)

            # Second line of multi-line option value
            elif current_option:
                if len(line) > 0 and line[-1] == MULTI_LINE_CHAR:
                    current_value.append(line[:-1])
                else:
                    current_value.append(line)
                    self._content[current_section].add(
                        current_option, NEW_LINE_CHAR.join(current_value))
                    current_option = None
                    current_value = []

            else:
                raise Exception(
                    "SplunkConfigParser: Unable to parse the Splunk config file properly.")

        if self.comments_before_stanza:
            self._content[current_section].extend(self.comments_before_stanza)
            self.comments_before_stanza = []


    def write(self, file):
        with open(file, 'w') as fp:
            fp.write(str(self))


    def sections(self):
        return [element for element in self._content.keys() if not element == FILE_SECTION]


    def __getitem__(self, key):
        if key not in self._content:
            raise KeyError(key)
        return self._content[key]


    def __setitem__(self, key, value):
        self._content[key] = value


    def __delitem__(self, key):
        if key not in self._content:
            raise KeyError(key)
        del self._content[key]


    def __contains__(self, key):
        return key in self._content


    def __len__(self):
        if FILE_SECTION in self:
            return len(self._content) - 1
        return len(self._content)


    def __iter__(self):
        return iter(self._content)

    # def items(self):
    #     return self._content.items()


    def merge(self, second_conf_parser, to_merge_pre_stanza_comments=True, to_merge_file_level_parameters=False):
        is_changed = False

        for stanza, options in second_conf_parser.items():
            if stanza not in self._content:
                self._content[stanza] = _SplunkStanzaOptions()
                is_changed = True

            if stanza != FILE_SECTION or to_merge_file_level_parameters:
                is_changed1 = self._content[stanza].merge(
                    options, to_merge_pre_stanza_comments)
                if is_changed1:
                    is_changed = True

        return is_changed


    def __str__(self) -> str:
        # NOTE - Do not change the code of this function as this might fail the working or even fail some test-cases
        content_str = ''
        for section, options in self._content.items():
            content_str += options.as_string(section)
        return content_str


    def __repr__(self) -> str:
        return self.__str__()


    def as_string(self) -> str:
        return str(self)
