import os, sys

# path to be added -> /<this-repo>/tests/src
sys.path.insert(0, os.path.join(
    os.path.dirname(os.path.dirname(__file__)),
    'src'
    )
)

import unittest


from helpers.splunk_config_parser import SplunkConfigParser, FILE_SECTION, DEFAULT_SETTING, GLOBAL_SETTING

class TestSplunkConfigParser(unittest.TestCase):

    def _util_conf_path(self, file_name):
        return os.path.join(os.path.dirname(__file__), 'splunk_config_files', file_name)

    def test_file_not_found(self):
        with self.assertRaises(Exception):
            conf = SplunkConfigParser(self._util_conf_path('no_file.conf'))

    def test_read_config_file(self):
        conf = SplunkConfigParser(self._util_conf_path('read_config_file.conf'))
        assert conf != None

    def test_get_config_sections(self):
        conf = SplunkConfigParser(self._util_conf_path('read_config_file.conf'))
        self.assertListEqual(["abc"], conf.sections())

    def test_get_config_as_string(self):
        conf = SplunkConfigParser(self._util_conf_path('read_config_file.conf'))
        assert conf.as_string() == "[abc]\nxyz = pqrst1\n"

    def assert_conf_content(self, conf_obj, expected_sections, expected_content_as_string):
        self.assertListEqual(conf_obj.sections(), expected_sections)
        print(f"content={conf_obj.as_string()}")
        assert conf_obj.as_string() == expected_content_as_string

    def test_parse_1(self):
        conf = SplunkConfigParser(self._util_conf_path('parse_1.conf'))
        self.assert_conf_content(conf, ["STANZA1", "STANZA2"], 
                "[STANZA1]\nOPTION1 = VALUE1\nOPTION2 = VALUE2\n\n[STANZA2]\n# comment in stanza2\nOPTION3 = VALUE3\n\n# Comment after stanza\n# This is a comment\n")
        assert conf["STANZA1"]["OPTION1"] == "VALUE1"
        assert conf["STANZA2"]["OPTION3"] == "VALUE3"

    def test_parse_2_multiline_value(self):
        conf = SplunkConfigParser(self._util_conf_path('parse_2_multiline_value.conf'))
        self.assert_conf_content(conf, ["STANZA1", "STANZA2"], 
                "[STANZA1]\nOPTION1 = VALUE1\n\nVALUE2\n\nWITH\n\nNEWLINES\n# above option1 is multi-valued\nOPTION2 = VALUE2\n\n[STANZA2]\nOPTION3 = VALUE3\n")
        assert conf["STANZA1"]["OPTION1"] == "VALUE1\nVALUE2\nWITH\nNEWLINES"
        assert conf["STANZA1"]["OPTION2"] == "VALUE2"
        assert conf["STANZA2"]["OPTION3"] == "VALUE3"

    def test_invalid_config(self):
        with self.assertRaisesRegex(Exception, "SplunkConfigParser: Unable to parse the Splunk config file properly."):
            conf = SplunkConfigParser(self._util_conf_path('invalid_config.conf'))

    def test_empty_config(self):
        conf = SplunkConfigParser(self._util_conf_path('empty_config.conf'))
        self.assert_conf_content(conf, [], "")

    def test_empty_config_2(self):
        conf = SplunkConfigParser(self._util_conf_path('empty_config_2.conf'))
        self.assert_conf_content(conf, [], "# just a comment in the file\n")

    def test_global_settings_present(self):
        conf = SplunkConfigParser(self._util_conf_path('global_settings_present.conf'))
        self.assert_conf_content(conf, ["STANZA1"], "\n# global comment-1\n\nGLOBAL_OPTION1 = GLOBAL_VALUE1\nGLOBAL_OPTION2 = GLOBAL_VALUE2\n\n# global comment-2\n\n[STANZA1]\n# comment in stanza1\nOPTION1 = VALUE1\n")
        assert conf["STANZA1"]["OPTION1"] == "VALUE1"
        assert conf[FILE_SECTION]["GLOBAL_OPTION1"] == "GLOBAL_VALUE1"
        assert conf[FILE_SECTION]["GLOBAL_OPTION2"] == "GLOBAL_VALUE2"
        assert conf[DEFAULT_SETTING]["GLOBAL_OPTION1"] == "GLOBAL_VALUE1"
        assert conf[DEFAULT_SETTING]["GLOBAL_OPTION2"] == "GLOBAL_VALUE2"
        assert conf[GLOBAL_SETTING]["GLOBAL_OPTION1"] == "GLOBAL_VALUE1"
        assert conf[GLOBAL_SETTING]["GLOBAL_OPTION2"] == "GLOBAL_VALUE2"

