import subprocess
import os

import logging

from .package import *

logger = logging.getLogger(__name__)


class Electron(Package):
    """ tested on 11/11/2023 """
    def __init__(self, version="27.0.2") -> None:
        self.version = "v" + version.lower().strip("v")
        super().__init__(f'electron-{self.version}', "electron" + self.EXE)
        
    def install(self):
        platform_name = "linux" if self.IS_POSIX else "win32"
        archive_url = f"https://github.com/electron/electron/releases/download/{self.version}/electron-{self.version}-{platform_name}-x64.zip"
        self.download_extract(archive_url, "zip")
        

class Zig(Package):
    """ tested on 11/11/2023 """
    def __init__(self, version="0.12.0-dev.1297+a9e66ed73"):
        self.version = version
        super().__init__(f'zig-{self.version.split("+")[0]}', "zig" + self.EXE, add_path=".")
        self.drill_singleton_dirs = True
    
    def install(self):
        arch = "x86_64"
        os_name = "linux" if self.IS_POSIX else "windows"
        archive_type = "tar.xz" if self.IS_POSIX else "zip"
        archive_url = f"https://ziglang.org/builds/zig-{os_name}-{arch}-{self.version}.{archive_type}"
        self.download_extract(archive_url, archive_type)
