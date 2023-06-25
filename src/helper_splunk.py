

class SplunkConfigParser:
    def __init__(self, *args, **kwargs):
        self._multiline_option_chars = set(['\\'])
        self.content = {}

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
                if current_section not in self.content:
                    self.content[current_section] = {}

            elif current_option is None and '=' in line:
                if current_section is None:
                    # raise configparser.MissingSectionHeaderError(line)
                    # For splunk, no section, means default section
                    current_section = 'default'
                    self.content[current_section] = {}

                option, value = line.split('=', 1)
                option = option.strip()
                value = value.strip()

                if len(value) > 0 and value[-1] in self._multiline_option_chars:
                    current_option = option
                    current_value.append(value[:-1])
                # elif current_option is not None and value:
                #     current_value.append(value)
                #     self.content[current_section][current_option] = '\n'.join(current_value)
                #     current_option = None
                #     current_value = []
                else:
                    self.content[current_section][option] = value

            elif current_option:   # in-complete line (for multi-line values)
                if len(line) > 0 and line[-1] in self._multiline_option_chars:
                    current_value.append(line[:-1])
                else:
                    current_value.append(line)
                    self.content[current_section][current_option] = '\n'.join(current_value)
                    current_option = None
                    current_value = []
            
            else:
                print("SplunkConfigParser: something is wrong here.")


    def write(self, file, space_around_delimiters=True):
        with open(file, 'w') as fp:
            for section in self.sections():
                fp.write(f'[{section}]\n')
                for option, value in self.content[section].items():
                    if '\n' in value:
                        value = '\n' + '\n'.join(value.splitlines())
                    fp.write(f'{option} = {value}\n')
                fp.write('\n')
    
    def sections(self):
        return self.content.keys()
