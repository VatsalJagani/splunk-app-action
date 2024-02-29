
import os
import xml.etree.ElementTree as ET

import helper_github_action as utils
from helpers.file_manager import PartRawFileHandler
from helpers.splunk_config_parser import SplunkConfigParser
from utilities.base_utility import BaseUtility


class WhatsInsideTheAppUtility(BaseUtility):
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


    def _get_readme_file_location(self):
        for file in os.listdir(self.app_write_dir):
            if file.lower() in ['readme.md', 'readme.txt']:
                return os.path.join(self.app_write_dir, file)


    def implement_utility(self):
        '''
        It returns the file_path of README file when the file has been changed, otherwise None
        '''
        utils.info("Adding WhatsInsideTheAppUtility.")

        start_markers = ["# What's in the App", "What's in the Add-on",
                         "# What's inside the App", "# What's inside the Add-on"]
        end_markers = ['\n\n\n']
        start_marker_to_add = "# What's inside the App"
        end_marker_to_add = "\n\n\n"
        # TODO - marker: maybe take as user input as well

        content = []
        content.extend(self._get_xml_dashboards())
        content.extend(self._get_imp_conf_files_details())
        content.extend(self._get_csv_lookup_files())

        file_path = self._get_readme_file_location()
        if not file_path:
            utils.info("No Readme.md file found in the App.")
            return

        is_changed = PartRawFileHandler(None, file_path).validate_file_content(
            '\n\n* ' + '\n* '.join(content),
            start_markers, end_markers,
            start_marker_to_add, end_marker_to_add)

        if is_changed:
            utils.info("Readme file updated for WhatsInsideTheAppUtility.")
            return file_path
        utils.info("No change in Readme file for WhatsInsideTheAppUtility.")


    def _get_conf_stanzas(self, file_path):
        config = SplunkConfigParser(file_path)
        stanzas = config.sections()
        return stanzas


    def _do_conf_specific_processing(self, file_key, label, stanzas):
        if len(stanzas) > 0:
            return 'No of {}: **{}**'.format(label, len(stanzas))


    def _get_stanzas(self, conf_file_name):
        stanzas = set()
        local_conf_file = os.path.join(
            self.app_read_dir, 'local', "{}.conf".format(conf_file_name))
        default_conf_file = os.path.join(
            self.app_read_dir, 'default', "{}.conf".format(conf_file_name))

        if os.path.isfile(local_conf_file):
            stanzas.update(self._get_conf_stanzas(local_conf_file))

        if os.path.isfile(default_conf_file):
            stanzas.update(self._get_conf_stanzas(default_conf_file))

        stanzas = list(stanzas)
        if 'default' in stanzas:
            stanzas.remove('default')
        return stanzas


    def _get_imp_conf_files_details(self):
        details = []
        for file_key, label in self.IMP_CONF_FILES.items():
            _stanzas = self._get_stanzas(file_key)
            _detail = self._do_conf_specific_processing(
                file_key, label, _stanzas)
            if _detail:
                details.append(_detail)

        return details


    def _get_csv_lookup_files(self):
        csv_lookup_files = []
        lookups_path = os.path.join(
            self.app_read_dir, 'lookups')
        if os.path.isdir(lookups_path):
            csv_lookup_files = [file for file in os.listdir(
                lookups_path) if file.endswith(".csv") or file.endswith(".CSV")]

        if len(csv_lookup_files) > 0:
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
            dashboard_label = labels[0] if len(labels) > 0 else ""

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


    def _get_xml_dashboards(self):
        dashboards = {}

        local_dashboards_path = os.path.join(
            self.app_read_dir, 'local', 'data', 'ui', 'views')
        if os.path.isdir(local_dashboards_path):
            local_xml_files = [file for file in os.listdir(
                local_dashboards_path) if file.endswith(".xml") or file.endswith(".XML")]

            for df in local_xml_files:
                dashboard_details = self._get_xml_dashboard_details(
                    os.path.join(local_dashboards_path, df))
                dashboards[df] = dashboard_details

        default_dashboards_path = os.path.join(
            self.app_read_dir, 'default', 'data', 'ui', 'views')
        if os.path.isdir(default_dashboards_path):
            default_xml_files = [file for file in os.listdir(
                default_dashboards_path) if file.endswith(".xml") or file.endswith(".XML")]

            for df in default_xml_files:
                if df not in dashboards:
                    # local folders' view takes precedence
                    dashboard_details = self._get_xml_dashboard_details(
                        os.path.join(default_dashboards_path, df))
                    dashboards[df] = dashboard_details

        # utils.info("dashboards: {}".format(dashboards))

        approx_total_viz = 0
        for key, val in dashboards.items():
            approx_total_viz += val['total_viz_count']

        things_to_return = []

        if len(dashboards) > 0:
            things_to_return.append("No of XML Dashboards: **{}**".format(len(dashboards)))

        if approx_total_viz > 0:
            things_to_return.append("Approx Total Viz(Charts/Tables/Map) in XML dashboards: **{}**".format(approx_total_viz))

        return things_to_return
