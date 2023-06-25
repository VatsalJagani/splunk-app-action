
import os
import xml.etree.ElementTree as ET


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


class SplunkAppDetails:
    IMP_CONF_FILES = {
        'savedsearches': 'Reports and Alerts',
        'commands': 'Custom Commands',
        'visualizations': 'Custom Visualization',
        'inputs': 'Custom Inputs',
        'indexes': 'Custom Indexes',
        'alert_actions': 'Custom Alert Actions',
        'datamodels': 'Data Models',
        'workflow_actions': 'Custom Workflow Actions',
        'collections': 'Lookups - KVStore Collections',
    }

    def __init__(self, app_root_path, markers=["# What's in the App", "What's in the Add-on", "# What's inside the App", "What's inside the Add-on"]) -> None:
        self.app_root_path = app_root_path
        self.markers = markers

        self.content = []
        self.content.extend(self.get_xml_dashboards())
        self.content.extend(self.get_imp_conf_files_details())
        self.content.extend(self.get_csv_lookup_files())


    def _get_readme_file_location(self):
        for file in os.listdir(self.app_root_path):
            if file.lower() in ['readme.md', 'readme.txt']:
                return os.path.join(self.app_root_path, file)


    def update_readme(self):
        # Read the file
        file_path = self._get_readme_file_location()
        if not file_path:
            print("No Readme.md file found.")
            return

        lines = []
        with open(file_path, 'r') as file:
            lines = file.readlines()
        
        # Find the marker line
        start_line_no = -1
        end_line_no = -1
        for i, line in enumerate(lines):
            _l = line.lower()
            for m in self.markers:
                if m.lower() in _l:
                    start_line_no = i
                    break
            else:
                continue
            break

        for i in range(start_line_no+1, len(lines)):
            if lines[i].strip() == '':
                if i+1 < len(lines):
                    if lines[i+1].strip() == '':
                        end_line_no = i+1
                        break
                else:
                    end_line_no = i
                    break

        if start_line_no>=0 and end_line_no>0:
            new_lines = ["* {}\n".format(element) for element in self.content]
            new_lines.extend(['\n', '\n'])
            lines[start_line_no+1:end_line_no+1] = new_lines
            print("Writing the What's in the App Content")

        with open(file_path, 'w') as file:
            file.writelines(lines)


    def _get_conf_stanzas(self, file_path):
        config = SplunkConfigParser()
        config.read(file_path)
        stanzas = config.sections()
        return stanzas


    def do_conf_specific_processing(self, file_key, label, stanzas):
        if len(stanzas)>0:
            return 'No of {}: **{}**'.format(label, len(stanzas))


    def get_stanzas(self, conf_file_name):
        stanzas = set()
        local_conf_file = os.path.join(self.app_root_path, 'local', "{}.conf".format(conf_file_name))
        default_conf_file = os.path.join(self.app_root_path, 'default', "{}.conf".format(conf_file_name))

        if os.path.isfile(local_conf_file):
            stanzas.update(self._get_conf_stanzas(local_conf_file))
        
        if os.path.isfile(default_conf_file):
            stanzas.update(self._get_conf_stanzas(default_conf_file))

        stanzas = list(stanzas)
        if 'default' in stanzas:
            stanzas.remove('default')
        return stanzas


    def get_imp_conf_files_details(self):
        details = []
        for file_key, label in self.IMP_CONF_FILES.items():
            _stanzas = self.get_stanzas(file_key)
            _detail = self.do_conf_specific_processing(file_key, label, _stanzas)
            if _detail:
                details.append(_detail)

        return details


    def get_csv_lookup_files(self):
        lookups_path = os.path.join(self.app_root_path, 'lookups')
        csv_lookup_files = [file for file in os.listdir(lookups_path) if file.endswith(".csv") or file.endswith(".CSV")]

        if len(csv_lookup_files)>0:
            return ["No of Static CSV Lookup Files: **{}**".format(len(csv_lookup_files))]
        else:
            return []


    def _get_xml_dashboard_details(self, xml_file_path):
        with open(xml_file_path, 'r') as f:
            xml_content = f.read()

            # Parse the XML content
            root = ET.fromstring(xml_content)

            labels = []
            for child in root:
                if child.tag == "label":
                    labels.append(child.text)
                    break
            dashboard_label = labels[0] if len(labels)>0 else ""

            # Fetch the count of table, chart, map, viz, event, and single elements
            counts = {
                "table": len(root.findall(".//table")),
                "chart": len(root.findall(".//chart")),
                "map": len(root.findall(".//map")),
                "viz": len(root.findall(".//viz")),
                "event": len(root.findall(".//event")),
                "single": len(root.findall(".//single")),
            }

            total_viz = 0
            for key, value in counts.items():
                total_viz += value

            return {
                "dashboard_label": dashboard_label,
                "viz_details": counts,
                "total_viz_count": total_viz
            }


    def get_xml_dashboards(self):
        dashboards = {}
        
        local_dashboards_path = os.path.join(self.app_root_path, 'local', 'data', 'ui', 'views')
        if os.path.isdir(local_dashboards_path):
            local_xml_files = [file for file in os.listdir(local_dashboards_path) if file.endswith(".xml") or file.endswith(".XML")]

            for df in local_xml_files:
                dashboard_details = self._get_xml_dashboard_details(os.path.join(local_dashboards_path, df))
                dashboards[df] = dashboard_details

        default_dashboards_path = os.path.join(self.app_root_path, 'default', 'data', 'ui', 'views')
        if os.path.isdir(default_dashboards_path):
            default_xml_files = [file for file in os.listdir(default_dashboards_path) if file.endswith(".xml") or file.endswith(".XML")]

            for df in default_xml_files:
                if df not in dashboards:
                    # local folders' view takes precedence
                    dashboard_details = self._get_xml_dashboard_details(os.path.join(default_dashboards_path, df))
                    dashboards[df] = dashboard_details
        
        # print("dashboards: {}".format(dashboards))

        approx_total_viz = 0
        for key, val in dashboards.items():
            approx_total_viz += val['total_viz_count']

        if(len(dashboards)>0):
            return ["No of XML Dashboards: **{}**".format(len(dashboards)),
                   "Approx Total Viz(Charts/Tables/Map) in XML dashboards: **{}**".format(approx_total_viz)]
        else:
            return []


def main(app_dir):
    sp = SplunkAppDetails(app_dir)
    sp.update_readme()
