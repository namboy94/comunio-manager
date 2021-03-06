"""
LICENSE:
Copyright 2016 Hermann Krumrey

This file is part of comunio-manager.

    comunio-manager is a program that allows a user to track his/her comunio.de
    profile

    comunio-manager is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    comunio-manager is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with comunio-manager.  If not, see <http://www.gnu.org/licenses/>.
LICENSE
"""

import comunio.metadata as metadata
from gitlab_build_scripts.project_builders.python import build
from gitlab_build_scripts.buildmodules.python.PyInstallerLinux import PyInstallerLinux
from gitlab_build_scripts.buildmodules.python.PyInstallerWindows import PyInstallerWindows

if __name__ == "__main__":
    build(metadata, [PyInstallerLinux, PyInstallerWindows])
