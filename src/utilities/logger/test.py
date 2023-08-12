
import os, sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from helper_file_handler import FullRawFileHandler, PartConfFileHandler


words_for_replacement = {
    '<<<log_files_prefix>>>': "cyences",
    '<<<logger_sourcetype>>>': "cyences:logs:test"
}

PartConfFileHandler(
    os.path.join(os.path.dirname(__file__), 'props.conf'),
    os.path.join(os.path.dirname(__file__), 'default', 'props.conf'),
    words_for_replacement
).validate_config()

