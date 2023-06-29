
import os


class SplunkConfigParser:
    MULTI_LINE_CHAR = '\\'
    COMMENT_CHAR = '#'
    FILE_SECTION = '___FILE___'
    NEW_LINE_CHAR = '\n'

    def __init__(self, file_path):
        self.file_path = file_path
        self._content = {}
        self.read()


    def read(self, encoding=None):
        if os.path.isfile(self.file_path):
            with open(self.file_path, 'r', encoding=encoding) as file:
                content = file.read()
            self._parse(content)


    def _parse(self, content):
        lines = content.splitlines()
        current_section = self.FILE_SECTION
        self._content[current_section] = []
        current_option = None
        current_value = []

        for original_line in lines:
            line = original_line.strip()

            # Empty Line
            if not line:
                self._content[current_section].append(original_line)

            # Comment Line
            elif line.startswith(self.COMMENT_CHAR):   # comment character, preserve the line
                self._add_option(current_option, original_line)

            # Stanza line - []
            elif current_option is None and line.startswith('[') and line.endswith(']'):
                current_section = line[1:-1]
                if current_section not in self._content:
                    self._content[current_section] = []

            # New option line
            elif current_option is None and '=' in line:
                option, value = line.split('=', 1)
                option = option.strip()
                value = value.strip()

                if len(value) > 0 and value[-1] == self.MULTI_LINE_CHAR:
                    current_option = option
                    current_value.append(value[:-1])
                else:
                    self._content[current_section].append((option, value))

            # Second line of multi-line option value
            elif current_option:
                if len(line) > 0 and line[-1] == self.MULTI_LINE_CHAR:
                    current_value.append(line[:-1])
                else:
                    current_value.append(line)
                    self._content[current_section].append((current_option, self.NEW_LINE_CHAR.join(current_value)))
                    current_option = None
                    current_value = []
            
            else:
                raise Exception("SplunkConfigParser: Unable to parse the Splunk config file properly.")


    def write(self, file):
        with open(file, 'w') as fp:
            for section, values in self._content.items():

                if section != self.FILE_SECTION:
                    fp.write(f'[{section}]\n')

                for key_value in self._content[section]:
                    if type(key_value) == str:
                        fp.write(f'{key_value}\n')

                    elif type(key_value) == tuple:
                        option = key_value[0]
                        value = key_value[1]

                        if self.NEW_LINE_CHAR in value:
                            new_line_ch = self.NEW_LINE_CHAR+'\n'
                            value = new_line_ch.join(value.splitlines())

                        fp.write(f'{option} = {value}\n')

                    else:
                        raise Exception("SplunkConfigParser: Unexpected parsing error while writing the conf file.")

                fp.write('\n')


    def sections(self):
        return self._content.keys()


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
        return len(self._content) + 1


    def __iter__(self):
        return iter(self._content)
    
    def items(self):
        return self._content.items()


    def merge(self, second_conf_parser):
        is_changed = False

        for stanza, options in second_conf_parser.items():
            if stanza not in self._content:
                # stanza not exist in the parser
                self._content[stanza] = []
                is_changed = True

            for key_value in options:
                if type(key_value) == str:
                    if key_value not in self._content[stanza]:
                        self._content[stanza].append(key_value)
                        is_changed = True

                elif type(key_value) == tuple:
                    option = key_value[0]
                    value = key_value[1]

                    for i in range(len(self._content[stanza])):
                        ex_key_val = self._content[stanza][i]
                        if type(ex_key_val) != tuple:
                            continue

                        ex_op = ex_key_val[0]
                        ex_val = ex_key_val[1]

                        if ex_op == option:
                            if value != ex_val:
                                self._content[stanza][i] = (option, value)
                                is_changed = True
                            break
                        else:
                            continue

                    else:
                        # no match found, add new
                        self._content[stanza].append((option, value))
                        is_changed = True

                else:
                    raise Exception("SplunkConfigParser: Unexpected parsing error while writing the conf file.")

        return is_changed
