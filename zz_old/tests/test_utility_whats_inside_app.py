import unittest
from unittest.mock import patch

from utilities.whats_inside_app import WhatsInsideTheAppUtility



class TestWhatsInsideTheAppUtility(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.utility = WhatsInsideTheAppUtility("abc", "abc")


    @patch('os.listdir')
    def test_get_readme_file_location_found(self, mock_listdir):
        mock_listdir.return_value = ['README.md']
        result = self.utility._get_readme_file_location()
        self.assertIsNotNone(result)


    @patch('os.listdir')
    def test_get_readme_file_location_not_found(self, mock_listdir):
        mock_listdir.return_value = []
        result = self.utility._get_readme_file_location()
        self.assertIsNone(result)


    def test_implement_utility_readme_updated(self):
        with patch.object(self.utility, '_get_xml_dashboards', return_value=['Dashboard 1', 'Dashboard 2']):
            with patch.object(self.utility, '_get_imp_conf_files_details', return_value=['Details']):
                with patch.object(self.utility, '_get_csv_lookup_files', return_value=['Lookup Files']):
                    with patch.object(self.utility, '_get_readme_file_location', return_value='/path/to/README.md'):
                        with patch('helpers.file_manager.PartRawFileHandler.validate_file_content', return_value=True):
                            result = self.utility.implement_utility()
                            self.assertEqual(result, '/path/to/README.md')


    def test_implement_utility_no_readme(self):
        with patch.object(self.utility, '_get_readme_file_location', return_value=None):
            result = self.utility.implement_utility()
            self.assertIsNone(result)


    def test_implement_utility_no_change(self):
        with patch.object(self.utility, '_get_xml_dashboards', return_value=['Dashboard 1', 'Dashboard 2']):
            with patch.object(self.utility, '_get_imp_conf_files_details', return_value=['Details']):
                with patch.object(self.utility, '_get_csv_lookup_files', return_value=['Lookup Files']):
                    with patch.object(self.utility, '_get_readme_file_location', return_value='/path/to/README.md'):
                        with patch('helpers.file_manager.PartRawFileHandler.validate_file_content', return_value=False):
                            result = self.utility.implement_utility()
                            self.assertIsNone(result)


    def test_do_conf_specific_processing(self):
        file_key = 'savedsearches'
        label = 'Reports and Alerts'
        stanzas = ['stanza1', 'stanza2']
        result = self.utility._do_conf_specific_processing(file_key, label, stanzas)
        self.assertEqual(result, 'No of Reports and Alerts: **2**')


    def test_get_stanzas(self):
        conf_file_name = 'indexes'
        with patch('os.path.isfile', return_value=True):
            with patch('utilities.whats_inside_app.WhatsInsideTheAppUtility._get_conf_stanzas', return_value=['stanza1', 'stanza2']):
                result = self.utility._get_stanzas(conf_file_name)
                self.assertSetEqual(set(result), set(['stanza1', 'stanza2']))


    def test_get_imp_conf_files_details(self):
        with patch('utilities.whats_inside_app.WhatsInsideTheAppUtility._get_stanzas', return_value=['stanza1', 'stanza2']):
            result = self.utility._get_imp_conf_files_details()
            self.assertSetEqual(set(result), set(['No of Reports and Alerts: **2**',
                            'No of Lookups - KVStore Collections: **2**',
                            'No of Custom Alert Actions: **2**',
                            'No of Custom Workflow Actions: **2**',
                            'No of Custom Indexes: **2**',
                            'No of Custom Visualization: **2**',
                            'No of Custom Inputs: **2**',
                            'No of Data Models: **2**',
                            'No of Custom Commands: **2**']))


    def test_get_csv_lookup_files_found(self):
        with patch('os.path.isdir', return_value=True):
            with patch('os.listdir', return_value=['file1.csv', 'file2.csv']):
                result = self.utility._get_csv_lookup_files()
                self.assertEqual(result, ["No of Static CSV Lookup Files: **2**"])


    def test_get_csv_lookup_files_not_found(self):
        with patch('os.path.isdir', return_value=True):
            with patch('os.listdir', return_value=[]):
                result = self.utility._get_csv_lookup_files()
                self.assertEqual(result, [])


    def test_get_xml_dashboard_details(self):
        xml_file_path = 'path/to/your/dashboard.xml'
        with patch('builtins.open') as mock_open:
            mock_open.return_value.__enter__.return_value.read.return_value = '<dashboard><label>My Dashboard</label><table/><chart/><map/></dashboard>'
            result = self.utility._get_xml_dashboard_details(xml_file_path)
            self.assertEqual(result['dashboard_label'], 'My Dashboard')
            self.assertEqual(result['viz_details'], {'table': 1, 'chart': 1, 'map': 1, 'viz': 0, 'event': 0, 'single': 0})
            self.assertEqual(result['total_viz_count'], 3)


    def test_get_xml_dashboards(self):
        with patch('os.path.isdir', return_value=True):
            with patch('os.listdir', return_value=['dashboard1.xml', 'dashboard2.xml']):
                with patch('utilities.whats_inside_app.WhatsInsideTheAppUtility._get_xml_dashboard_details', return_value={'dashboard_label': 'My Dashboard', 'viz_details': {'table': 1, 'chart': 1, 'map': 1, 'viz': 0, 'event': 0, 'single': 0}, 'total_viz_count': 3}):
                    result = self.utility._get_xml_dashboards()
                    self.assertSetEqual(set(result), set(["No of XML Dashboards: **2**", "Approx Total Viz(Charts/Tables/Map) in XML dashboards: **6**"]))


    def test_get_xml_dashboards_no_dashboards_found(self):
        with patch('os.path.isdir', return_value=True):
            with patch('os.listdir', return_value=[]):
                result = self.utility._get_xml_dashboards()
                self.assertEqual(result, [])


    def test_get_xml_dashboards_no_viz_found(self):
        with patch('os.path.isdir', return_value=True):
            with patch('os.listdir', return_value=['dashboard1.xml']):
                with patch('utilities.whats_inside_app.WhatsInsideTheAppUtility._get_xml_dashboard_details', return_value={'dashboard_label': 'My Dashboard', 'viz_details': {'table': 1, 'chart': 1, 'map': 0, 'viz': 3, 'event': 0, 'single': 0}, 'total_viz_count': 5}):
                    result = self.utility._get_xml_dashboards()
                    self.assertSetEqual(set(result), set(["No of XML Dashboards: **1**", "Approx Total Viz(Charts/Tables/Map) in XML dashboards: **5**"]))
