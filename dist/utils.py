import os
import datetime


def get_input(name):
    return os.getenv(f"SPLUNK_{name}")


def set_output(name, value):
    print(f"::set-output name={name}::{_escape_data(value)}")


def format_message(message):
    timestamp = datetime.now().strftime("%H:%M:%S.%f")
    return "{} | {}".format(timestamp, message)


def debug(message):
    message = format_message(message)
    print(f"::debug::{_escape_data(message)}")


def info(message):
    message = format_message(message)
    print(f"{_escape_data(message)}")


def warning(message):
    message = format_message(message)
    print(f"::warning::{_escape_data(message)}")


def error(message):
    message = format_message(message)
    print(f"::error::{_escape_data(message)}")


def group(title):
    print(f"::group::{title}")


def end_group():
    print(f"::endgroup::")


def add_mask(value):
    print(f"::add-mask::{_escape_data(value)}")


def stop_commands():
    print(f"::stop-commands::pause-commands")


def resume_commands():
    print(f"::pause-commands::")


def save_state(name, value):
    print(f"::save-state name={name}::{_escape_data(value)}")


def _escape_data(value: str):
    return value.replace("%", "%25").replace("\r", "%0D").replace("\n", "%0A")
