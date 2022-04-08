"""
(test) fprime.fbuild.settings:

Tests the F prime settings module.
@author joshuaa
"""

import pytest
import os
from pathlib import Path

from fprime.fbuild.settings import IniSettings

LOCAL_PATH = Path(__file__).parent


def full_path(path):
    path = LOCAL_PATH / Path(path)
    return path.resolve()


# The following tests use a fake framework path due to the separation of fprime and fprime-tools


def test_settings():
    test_cases = [
        {
            "file": "settings-empty.ini",
            "expected": {
                "settings_file": full_path("settings-data/settings-empty.ini"),
                "default_toolchain": "native",
                "default_ut_toolchain": "native",
                "framework_path": full_path(".."),
                "install_dest": full_path("settings-data/build-artifacts"),
                "library_locations": [],
                "environment_file": full_path("settings-data/settings-empty.ini"),
                "environment": {},
                "component_cookiecutter": "default",
            },
        },
        {
            "file": "settings-custom-install.ini",
            "expected": {
                "settings_file": full_path("settings-data/settings-custom-install.ini"),
                "default_toolchain": "native",
                "default_ut_toolchain": "native",
                "framework_path": full_path(".."),
                "install_dest": full_path("test"),
                "library_locations": [],
                "environment_file": full_path(
                    "settings-data/settings-custom-install.ini"
                ),
                "environment": {},
                "component_cookiecutter": "default",
            },
        },
        {
            "file": "settings-custom-toolchain.ini",
            "expected": {
                "settings_file": full_path(
                    "settings-data/settings-custom-toolchain.ini"
                ),
                "default_toolchain": "custom1",
                "default_ut_toolchain": "custom2",
                "framework_path": full_path(".."),
                "install_dest": full_path("settings-data/build-artifacts"),
                "library_locations": [],
                "environment_file": full_path(
                    "settings-data/settings-custom-toolchain.ini"
                ),
                "environment": {},
                "component_cookiecutter": "default",
            },
        },
        {
            "file": "settings-outside-cookiecutter.ini",
            "expected": {
                "settings_file": full_path(
                    "settings-data/settings-outside-cookiecutter.ini"
                ),
                "default_toolchain": "native",
                "default_ut_toolchain": "native",
                "framework_path": full_path(".."),
                "install_dest": full_path("settings-data/build-artifacts"),
                "library_locations": [],
                "environment_file": full_path(
                    "settings-data/settings-outside-cookiecutter.ini"
                ),
                "environment": {},
                "component_cookiecutter": "gh:SterlingPeet/cookiecutter-fprime-deployment",
            },
        },
    ]

    for case in test_cases:
        fp = full_path("settings-data/" + case["file"])
        results = IniSettings.load(fp)
        assert (
            case["expected"] == results
        ), f'{fp}: Expected {case["expected"]}, got {results}'
