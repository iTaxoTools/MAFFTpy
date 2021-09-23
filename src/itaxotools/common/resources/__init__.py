# -----------------------------------------------------------------------------
# Commons - Utility classes for iTaxoTools modules
# Copyright (C) 2021  Patmanidis Stefanos
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
# -----------------------------------------------------------------------------

"""Get resource paths for Python3.8+"""


import pathlib
import sys
import os


def _package_path_pyinstaller(package):
    if isinstance(package, str):
        parts = package.split('.')
    elif isinstance(package, type(sys)):
        parts = package.__name__.split('.')
    else:
        return None
    path = pathlib.Path(sys._MEIPASS)
    for part in parts:
        path /= part
    return path


def _package_path_file(package):
    if isinstance(package, str):
        file = sys.modules[package].__file__
    elif isinstance(package, type(sys)):
        file = package.__file__
    else:
        return None
    path = pathlib.Path(os.path.dirname(file))
    return path


def _package_path_importlib(package):
    return importlib.resources.files(package)


try:
    import importlib.resources.files
    package_path = _package_path_importlib
except ModuleNotFoundError:
    if hasattr(sys, '_MEIPASS'):
        package_path = _package_path_pyinstaller
    else:
        package_path = _package_path_file

_resource_path = package_path(__package__)


def get_common(path):
    return str(_resource_path / path)


def get_local(package, path):
    return str(package_path(package) / path)


def get(*args):
    if len(args) == 1:
        return get_common(*args)
    return get_local(*args)
