import os
import xml.etree.ElementTree as ET
from typing import override

import github_action_toolkit as gat

from helpers.file_manager import PartRawFileHandler
from helpers.splunk_config_parser import SplunkConfigParser
from utilities.base_utility import BaseUtility


class WhatsInsideTheAppUtility(BaseUtility):
    """
    Utility to generate and maintain a "What's inside the App" section in README.

    Automatically scans the Splunk app for dashboards, reports, alerts, custom commands,
    and other configuration elements, then generates or updates a summary section in the
    README file documenting what features are included in the app.
    """

    IMP_CONF_FILES: dict[str, str] = {
        "savedsearches": "Reports and Alerts",
        "commands": "Custom Commands",
        "visualizations": "Custom Visualization",
        "inputs": "Custom Inputs",
        "indexes": "Custom Indexes",
        "alert_actions": "Custom Alert Actions",
        "datamodels": "Data Models",
        "workflow_actions": "Custom Workflow Actions",
        "collections": "Lookups - KVStore Collections",
    }

    def _get_readme_file_location(self) -> str | None:
        """
        Locate the README file in the app directory.

        Returns:
            Path to README.md or README.txt if found, None otherwise.
        """
        for file in os.listdir(self.app_write_dir):
            if file.lower() in ["readme.md", "readme.txt"]:
                return os.path.join(self.app_write_dir, file)
        return None

    @override
    def implement_utility(self) -> str | bool | None:
        """
        Generate or update the "What's inside the App" section in README.

        Scans the app for various components (dashboards, alerts, commands, etc.)
        and updates the README file with a formatted summary of what's included.

        Returns:
            Path to the updated README file if changes were made, None otherwise.
        """
        gat.info("📋 Adding WhatsInsideTheAppUtility")
        start_markers = [
            "# What's in the App",
            "What's in the Add-on",
            "# What's inside the App",
            "# What's inside the Add-on",
        ]
        end_markers = ["\n\n\n"]
        start_marker_to_add = "# What's inside the App"
        end_marker_to_add = "\n\n\n"
        # TODO - marker: maybe take as user input as well

        content: list[str] = []
        content.extend(self._get_xml_dashboards())
        content.extend(self._get_imp_conf_files_details())
        content.extend(self._get_csv_lookup_files())

        file_path = self._get_readme_file_location()
        if not file_path:
            gat.info("No Readme.md file found in the App.")
            return

        is_changed = PartRawFileHandler(file_path, file_path).validate_file_content(
            "\n\n* " + "\n* ".join(content),
            start_markers,
            end_markers,
            start_marker_to_add,
            end_marker_to_add,
        )

        if is_changed:
            gat.info("Readme file updated for WhatsInsideTheAppUtility.")
            return file_path
        gat.info("No change in Readme file for WhatsInsideTheAppUtility.")

    def _get_conf_stanzas(self, file_path: str) -> list[str]:
        config = SplunkConfigParser(file_path)
        stanzas = config.sections()
        return stanzas

    def _do_conf_specific_processing(
        self, _file_key: str, label: str, stanzas: list[str]
    ) -> str | None:
        if len(stanzas) > 0:
            return f"No of {label}: **{len(stanzas)}**"

    def _get_stanzas(self, conf_file_name: str) -> list[str]:
        stanzas: set[str] = set()
        local_conf_file = os.path.join(self.app_read_dir, "local", f"{conf_file_name}.conf")
        default_conf_file = os.path.join(self.app_read_dir, "default", f"{conf_file_name}.conf")

        if os.path.isfile(local_conf_file):
            stanzas.update(self._get_conf_stanzas(local_conf_file))

        if os.path.isfile(default_conf_file):
            stanzas.update(self._get_conf_stanzas(default_conf_file))

        stanzas_list: list[str] = list(stanzas)
        if "default" in stanzas_list:
            stanzas_list.remove("default")
        return stanzas_list

    def _get_imp_conf_files_details(self) -> list[str]:
        details: list[str] = []
        for file_key, label in self.IMP_CONF_FILES.items():
            _stanzas = self._get_stanzas(file_key)
            _detail = self._do_conf_specific_processing(file_key, label, _stanzas)
            if _detail:
                details.append(_detail)

        return details

    def _get_csv_lookup_files(self) -> list[str]:
        csv_lookup_files: list[str] = []
        lookups_path = os.path.join(self.app_read_dir, "lookups")
        if os.path.isdir(lookups_path):
            csv_lookup_files = [
                file
                for file in os.listdir(lookups_path)
                if file.endswith(".csv") or file.endswith(".CSV")
            ]

        if len(csv_lookup_files) > 0:
            return [f"No of Static CSV Lookup Files: **{len(csv_lookup_files)}**"]
        else:
            return []

    def _get_xml_dashboard_details(
        self, xml_file_path: str
    ) -> dict[str, str | dict[str, int] | int]:
        with open(xml_file_path) as f:
            xml_content = f.read()

            # Parse the XML content
            root = ET.fromstring(xml_content)

            labels: list[str] = []
            for child in root:
                if child.tag == "label" and child.text is not None:
                    labels.append(child.text)
                    break
            dashboard_label: str = labels[0] if len(labels) > 0 else ""

            # Fetch the count of table, chart, map, viz, event, and single elements
            counts = {
                "table": len(root.findall(".//table")),
                "chart": len(root.findall(".//chart")),
                "map": len(root.findall(".//map")),
                "viz": len(root.findall(".//viz")),
                "event": len(root.findall(".//event")),
                "single": len(root.findall(".//single")),
            }

            total_viz: int = 0
            for _key, value in counts.items():
                total_viz += value

            return {
                "dashboard_label": dashboard_label,
                "viz_details": counts,
                "total_viz_count": total_viz,
            }

    def _get_xml_dashboards(self) -> list[str]:
        dashboards: dict[str, dict[str, str | dict[str, int] | int]] = {}

        local_dashboards_path = os.path.join(self.app_read_dir, "local", "data", "ui", "views")
        if os.path.isdir(local_dashboards_path):
            local_xml_files = [
                file
                for file in os.listdir(local_dashboards_path)
                if file.endswith(".xml") or file.endswith(".XML")
            ]

            for df in local_xml_files:
                dashboard_details = self._get_xml_dashboard_details(
                    os.path.join(local_dashboards_path, df)
                )
                dashboards[df] = dashboard_details

        default_dashboards_path = os.path.join(self.app_read_dir, "default", "data", "ui", "views")
        if os.path.isdir(default_dashboards_path):
            default_xml_files = [
                file
                for file in os.listdir(default_dashboards_path)
                if file.endswith(".xml") or file.endswith(".XML")
            ]

            for df in default_xml_files:
                if df not in dashboards:
                    # local folders' view takes precedence
                    dashboard_details = self._get_xml_dashboard_details(
                        os.path.join(default_dashboards_path, df)
                    )
                    dashboards[df] = dashboard_details

        # gat.info("dashboards: {}".format(dashboards))

        approx_total_viz: int = 0
        for _key, val in dashboards.items():
            total_viz_count = val["total_viz_count"]
            if isinstance(total_viz_count, int):
                approx_total_viz += total_viz_count

        things_to_return: list[str] = []

        if len(dashboards) > 0:
            things_to_return.append(f"No of XML Dashboards: **{len(dashboards)}**")

        if approx_total_viz > 0:
            things_to_return.append(
                f"Approx Total Viz(Charts/Tables/Map) in XML dashboards: **{approx_total_viz}**"
            )

        return things_to_return
