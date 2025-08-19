from pathlib import Path
import subprocess
import os

import logging
from typing import Optional

from .package import *

logger = logging.getLogger(__name__)


class Electron(Package):
    """ tested on 9/14/2024 """
    DEFAULT_VERSION = "32.1.0"
    def __init__(self, version=DEFAULT_VERSION) -> None:
        self.version = "v" + version.lower().strip("v")
        super().__init__(f'electron-{self.version}', "electron" + self.EXE)
        
    def install(self):
        platform_name = "linux" if self.IS_POSIX else "win32"
        archive_url = f"https://github.com/electron/electron/releases/download/{self.version}/electron-{self.version}-{platform_name}-x64.zip"
        self.download_extract(archive_url, "zip")
        

class Zig(Package):
    """ tested on 6/30/2025 """
    VERSION_2023_11_11 = "0.12.0-dev.1297+a9e66ed73"
    def __init__(self, version="0.14.1", add_path: Optional[Path | str] ="."):
        self.version = version
        super().__init__(f'zig-{self.version.split("+")[0]}', "zig" + self.EXE, add_path)
        self.drill_singleton_dirs = True
    
    def install(self):
        arch = "x86_64"
        os_name = "linux" if self.IS_POSIX else "windows"
        archive_type = "tar.xz" if self.IS_POSIX else "zip"
        archive_url = f"https://ziglang.org/download/{self.version}/zig-{arch}-{os_name}-{self.version}.{archive_type}"
        self.download_extract(archive_url, archive_type)


class GccArmNone(Package):
    """ tested on 11/11/2023 """
    def __init__(self):
        self.version = "13.2"
        self.prefix = "arm-none-eabi-"
        super().__init__(f"gcc-arm-none-eabi_{self.version}", Path("bin", self.prefix+"gcc"), add_path="bin")
        self.drill_singleton_dirs = True
        
    def install(self):
        archive_type = "tar.xz"
        archive_url = f"https://developer.arm.com/-/media/Files/downloads/gnu/13.2.rel1/binrel/arm-gnu-toolchain-13.2.rel1-x86_64-arm-none-eabi.tar.xz?rev=e434b9ea4afc4ed7998329566b764309&hash=688C370BF08399033CA9DE3C1CC8CF8E31D8C441"
        self.download_extract(archive_url, archive_type)
        sh("sudo add-apt-repository -y ppa:deadsnakes/ppa && sudo apt -y install python3.8")


class GccArmLinux(Package):
    """ tested on 11/11/2023 """
    def __init__(self):
        self.version = "13.2"
        self.prefix = "arm-none-linux-"
        super().__init__(f"gcc-arm-linux-gnueabihf_{self.version}", Path("bin", self.prefix+"gcc"), add_path="bin")
        self.drill_singleton_dirs = True
        
    def install(self):
        archive_type = "tar.xz"
        archive_url = f"https://developer.arm.com/-/media/Files/downloads/gnu/13.2.rel1/binrel/arm-gnu-toolchain-13.2.rel1-x86_64-arm-none-linux-gnueabihf.tar.xz?rev=adb0c0238c934aeeaa12c09609c5e6fc&hash=68DA67DE12CBAD82A0FA4B75247E866155C93053"
        self.download_extract(archive_url, archive_type)
        sh("sudo add-apt-repository -y ppa:deadsnakes/ppa && sudo apt -y install python3.8")


class TiPruNone(Package):
    """ tested on 11/11/2023 """
    def __init__(self):
        self.version = "2.3.3"
        super().__init__(f"ti-pru-none_{self.version}", Path("bin", "clpru"))
        self.drill_singleton_dirs = True
        
    def install(self):
        archive_type = "tar.bz2"
        archive_url = f"https://subinitial.com/public/art/ti-cgt-pru_2.3.3.tar.bz2"
        self.download_extract(archive_url, archive_type)


class StLink(Package):
    """ tested on 02/02/2024 """
    def __init__(self):
        self.version = "v1.1.0"
        super().__init__(f"stlink_{self.version}", Path("STM32CubeProgrammer", "bin", "STM32_Programmer_CLI"))
        self.drill_singleton_dirs = True
        
    def install(self):
        archive_type = "tar.bz2"
        archive_url = f"https://subinitial.com/public/art/stlink_{self.version}.tar.bz2"
        self.download_extract(archive_url, archive_type)
        sh(f"/bin/bash {self.path.joinpath('install.sh')}", cwd=self.path)


class Bun(Package):
    """ tested on 11/14/2024 """
    def __init__(self, version="v1.2.2"):
        self.version = "v" + version.lower().strip("v")
        super().__init__(f"bun_{self.version}", Path("bun"), add_path=".")
        self.drill_singleton_dirs = True
        
    def install(self):
        archive_type = "zip"
        archive_url = f"https://github.com/oven-sh/bun/releases/download/bun-{self.version}/bun-linux-x64.zip"
        self.download_extract(archive_url, archive_type)
        self.path.joinpath("bunx").symlink_to(self.artifact.resolve())


class Node(Package):
    """ tested on 9/14/2024 """
    def __init__(self, version="22.12.0"):
        self.version = version.lower().strip("v")
        super().__init__(f"node_{self.version}", Path("bin", "node"), add_path="bin")
        self.drill_singleton_dirs = True
        
    def install(self):
        archive_type = "tar.xz"
        archive_url = f"https://nodejs.org/dist/v{self.version}/node-v{self.version}-linux-x64.tar.xz"
        self.download_extract(archive_url, archive_type)
        # self.path.joinpath("bunx").symlink_to(self.artifact)


class EsBuild(Package):
    """ tested on 9/14/2024 """
    def __init__(self, version="0.23.1"):
        self.version = version.lower().strip("v")
        super().__init__(f"esbuild_{self.version}", Path("package", "bin", "esbuild"))
        self.drill_singleton_dirs = True
        
    def install(self):
        archive_type = "tgz"
        platform_name = "linux" if self.IS_POSIX else "win32"
        # https://registry.npmjs.org/@esbuild/linux-x64/-/linux-x64-0.19.4.tgz
        # https://registry.npmjs.org/@esbuild/win32-x64/-/win32-x64-0.19.4.tgz
        archive_url = f"https://registry.npmjs.org/@esbuild/{platform_name}-x64/-/{platform_name}-x64-{self.version}.tgz"
        self.download_extract(archive_url, archive_type)

class Restic(Package):
    """ tested 2/12/2024 """
    def __init__(self, version="0.16.4"):
        self.version = version.lower().strip("v")
        super().__init__(f"restic_{self.version}", Path(f"restic"), add_path=".")
        self.drill_singleton_dirs = True
        
    def install(self):
        archive_type = "bz2"
        platform_name = "linux" if self.IS_POSIX else "windows"
        arch = "amd64"
        archive_url = f"https://github.com/restic/restic/releases/download/v{self.version}/restic_{self.version}_{platform_name}_{arch}.bz2"
        self.download_extract(archive_url, archive_type, delete_src=False)

    def extract(self, src: str | Path, dst_dir: Path, delete_src=False):
        dst = str(dst_dir.joinpath("restic"))

        extraction_cmd = f"mv {str(src)} {str(dst)}.bz2 && bzip2 -fd {dst}.bz2 && chmod +x {dst}"
        dst_dir.mkdir(exist_ok=True, parents=True)
        logger.info("extracting via: %s", extraction_cmd)
        try:
            sh(extraction_cmd, stdout=subprocess.PIPE).check_returncode()
            if self.drill_singleton_dirs:
                self._drill_singleton_dirs(self.path)
            self._add_path()
        finally:
            if delete_src:
                os.unlink(src)
