"""
fprime.fbuild.settings:

An implementation used to pull settings into the fprime build.  This version uses INI files in order to load the
settings from the settings.default file that is part of the F prime deployment directory.

@author mstarch
"""
import os
import configparser
from typing import Dict, List
from pathlib import Path


class IniSettings:
    """Class to load settings from INI files"""

    DEF_FILE = "settings.ini"
    SET_ENV = "FPRIME_SETTINGS_FILE"

    @staticmethod
    def find_fprime(cwd: Path) -> Path:
        """
        Finds F prime by recursing parent to parent until a matching directory is found.
        """
        needle = Path("cmake/FPrime.cmake")
        path = cwd.resolve()
        while path != path.parent:
            if Path(path, needle).is_file():
                return path
            path = path.parent
        raise FprimeLocationUnknownException(
            "Please set 'framework_path' in [fprime] section in 'settings.ini"
        )

    @staticmethod
    def read_safe_path(
        parser: configparser.ConfigParser,
        section: str,
        key: str,
        ini_file: Path,
        exists: bool = True,
    ) -> List[str]:
        """
        Reads path(s), safely, from the config parser.  Validates the path(s) exists or raises an exception. Paths are
        separated by ':'.  This will also expand relative paths relative to the settings file.

        :param parser: parser to read from
        :param key: key to read from
        :param ini_file: ini_file path for clean errors
        :return: path, validated
        """
        base_dir = os.path.dirname(ini_file)
        all_paths = parser.get(section, key, fallback="").split(":")
        expanded = []
        for path in all_paths:
            if path == "" or path is None:
                continue
            full_path = os.path.abspath(os.path.normpath(os.path.join(base_dir, path)))
            if exists and not os.path.exists(full_path):
                raise FprimeSettingsException(
                    f"Nonexistent path '{path}' found in section '{section}' option '{key}' of file '{ini_file}'"
                )

            expanded.append(full_path)
        return expanded

    @staticmethod
    def load(settings_file: Path):
        """
        Load settings from specified file or from specified build directory. Either a specific file or the build
        directory must be not None.

        :param settings_file: file to load settings from (in INI format). Must be specified if build_dir is not.
        :return: a dictionary of needed settings
        """
        settings_file = (
            Path.cwd() / IniSettings.DEF_FILE
            if settings_file is None
            else settings_file
        ).resolve()
        dfl_install_dest = Path(settings_file.parent, "build-artifacts")

        # Check file existence if specified
        if not os.path.exists(settings_file):
            print(f"[WARNING] Failed to find settings file: {settings_file}")
            fprime_location = IniSettings.find_fprime(settings_file.parent)
            return {"framework_path": fprime_location, "install_dest": dfl_install_dest}
        confparse = configparser.ConfigParser()
        confparse.read(settings_file)
        # Search through F prime locations
        fprime_location = IniSettings.read_safe_path(
            confparse, "fprime", "framework_path", settings_file
        )
        fprime_location = (
            Path(fprime_location[0])
            if fprime_location
            else IniSettings.find_fprime(settings_file.parent)
        )

        # Read project root if it is available
        proj_root = IniSettings.read_safe_path(
            confparse, "fprime", "project_root", settings_file
        )
        proj_root = proj_root[0] if proj_root else None
        # Read ac constants if it is available
        ac_consts = IniSettings.read_safe_path(
            confparse, "fprime", "ac_constants", settings_file
        )
        ac_consts = ac_consts[0] if ac_consts else None
        # Read include constants if it is available
        config_dir = IniSettings.read_safe_path(
            confparse, "fprime", "config_directory", settings_file
        )
        config_dir = config_dir[0] if config_dir else None

        install_dest = IniSettings.read_safe_path(
            confparse, "fprime", "install_dest", settings_file, False
        )

        install_dest = Path(install_dest[0]) if install_dest else dfl_install_dest
        # Read separate environment file if necessary
        env_file = IniSettings.read_safe_path(
            confparse, "fprime", "environment_file", settings_file
        )
        env_file = env_file[0] if env_file else settings_file
        libraries = IniSettings.read_safe_path(
            confparse, "fprime", "library_locations", settings_file
        )
        environment = IniSettings.load_environment(env_file)

        settings = {
            "settings_file": settings_file,
            "framework_path": fprime_location,
            "library_locations": libraries,
            "default_toolchain": confparse.get(
                "fprime", "default_toolchain", fallback="native"
            ),
            "default_ut_toolchain": confparse.get(
                "fprime", "default_ut_toolchain", fallback="native"
            ),
            "install_dest": install_dest,
            "environment_file": env_file,
            "environment": environment,
            "component_cookiecutter": confparse.get(
                "fprime", "component_cookiecutter", fallback="default"
            ),
        }
        # Set the project root
        if proj_root is not None:
            settings["project_root"] = proj_root
        # Set AC constants if available
        if ac_consts is not None:
            settings["ac_constants"] = ac_consts
        # Set the config dir
        if config_dir is not None:
            settings["config_dir"] = config_dir
        return settings

    @staticmethod
    def load_environment(env_file):
        """
        Load the environment from the given parser.

        :param env_file: load environment from this file
        :return: environment dictionary
        """
        parser = configparser.ConfigParser()
        parser.optionxform = str
        parser.read(env_file)
        env_dict = {}
        try:
            for key, value in parser.items("environment"):
                env_dict[key] = value
        except configparser.NoSectionError:
            pass  # Ignore missing environment
        return env_dict


class FprimeLocationUnknownException(Exception):
    """Fprime location could not be determined"""


class FprimeSettingsException(Exception):
    """An exception for handling F prime settings misconfiguration"""
