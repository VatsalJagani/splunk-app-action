"""
Prepares markdown release notes for GitHub releases.
"""

import os
import subprocess

import packaging.version

TAG = os.environ["TAG"]

ADDED_HEADER = "### Added 🎉"
CHANGED_HEADER = "### Changed ⚠️"
FIXED_HEADER = "### Fixed ✅"
REMOVED_HEADER = "### Removed 👋"


def get_change_log_notes() -> str:
    in_current_section = False
    current_section_notes: list[str] = []
    with open("CHANGELOG.md") as changelog:
        for line in changelog:
            if line.startswith("## "):
                if line.startswith("## Unreleased"):
                    continue
                if line.startswith(f"## [{TAG}]"):
                    in_current_section = True
                    continue
                if in_current_section:
                    break
                continue
            if in_current_section:
                if line.startswith("### Added"):
                    line = ADDED_HEADER + "\n"
                elif line.startswith("### Changed"):
                    line = CHANGED_HEADER + "\n"
                elif line.startswith("### Fixed"):
                    line = FIXED_HEADER + "\n"
                elif line.startswith("### Removed"):
                    line = REMOVED_HEADER + "\n"
                current_section_notes.append(line)
    assert current_section_notes
    return "## What's new\n\n" + "".join(current_section_notes).strip() + "\n"


def get_commit_history() -> str:
    new_version = packaging.version.parse(TAG)

    # Pull all tags.
    subprocess.run(["git", "fetch", "--tags"], check=False)

    # Get all tags sorted by version, latest first.
    all_tags = subprocess.run(
        ["git", "tag", "-l", "--sort=-version:refname", "v*"],
        capture_output=True,
        text=True,
        check=False,
    ).stdout.split("\n")

    # Out of `all_tags`, find the latest previous version so that we can collect all
    # commits between that version and the new version we're about to publish.
    # Note that we ignore pre-releases unless the new version is also a pre-release.
    last_tag: str | None = None
    for tag in all_tags:
        if not tag.strip():  # could be blank line
            continue
        version = packaging.version.parse(tag)
        if new_version.pre is None and version.pre is not None:
            continue
        if version < new_version:
            last_tag = tag
            break
    if last_tag is not None:
        commits = subprocess.run(
            ["git", "log", f"{last_tag}..{TAG}", "--oneline", "--first-parent"],
            capture_output=True,
            text=True,
            check=False,
        ).stdout
    else:
        commits = subprocess.run(
            ["git", "log", "--oneline", "--first-parent"],
            capture_output=True,
            text=True,
            check=False,
        ).stdout
    return "## Commits\n\n" + commits


def main():
    print(get_change_log_notes())
    print(get_commit_history())


if __name__ == "__main__":
    main()
