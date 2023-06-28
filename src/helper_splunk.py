

class SplunkConfigParser:
    def __init__(self, *args, **kwargs):
        self._multiline_option_chars = set(['\\'])
        self._content = {}


    def read(self, filenames, encoding=None):
        with open(filenames, 'r', encoding=encoding) as file:
            content = file.read()
        self._parse(content)


    def _parse(self, content):
        lines = content.splitlines()
        current_section = None
        current_option = None
        current_value = []
        for line in lines:
            line = line.strip()
            if not line:
                continue

            if line.startswith(';') or line.startswith('#'):   # comment characters
                continue

            if current_option is None and line.startswith('[') and line.endswith(']'):
                current_section = line[1:-1]
                if current_section not in self._content:
                    self._content[current_section] = {}

            elif current_option is None and '=' in line:
                if current_section is None:
                    # raise configparser.MissingSectionHeaderError(line)
                    # For splunk, no section, means default section
                    current_section = 'default'
                    self._content[current_section] = {}

                option, value = line.split('=', 1)
                option = option.strip()
                value = value.strip()

                if len(value) > 0 and value[-1] in self._multiline_option_chars:
                    current_option = option
                    current_value.append(value[:-1])
                else:
                    self._content[current_section][option] = value

            elif current_option:   # in-complete line (for multi-line values)
                if len(line) > 0 and line[-1] in self._multiline_option_chars:
                    current_value.append(line[:-1])
                else:
                    current_value.append(line)
                    self._content[current_section][current_option] = '\n'.join(current_value)
                    current_option = None
                    current_value = []
            
            else:
                raise Exception("SplunkConfigParser: Unable to parse the Splunk config file properly.")


    def write(self, file, space_around_delimiters=True):
        with open(file, 'w') as fp:
            for section in self.sections():
                fp.write(f'[{section}]\n')
                for option, value in self._content[section].items():
                    if '\n' in value:
                        value = '\n' + '\n'.join(value.splitlines())
                    fp.write(f'{option} = {value}\n')
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
        return iter(self.content.keys())
