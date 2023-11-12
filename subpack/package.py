import logging
import platform
import subprocess
import os
import shutil
from pathlib import Path
from typing import Optional

import urllib.request

logger = logging.getLogger(__name__)


def sh(cmd, shell=True, **kwargs):
    logger.info("sh: %s", cmd)
    return subprocess.run(cmd, shell=shell, **kwargs)


class Package:
    IS_POSIX = "linux" in platform.system().lower()

    EXE = "" if IS_POSIX else ".exe"
    
    SUBPACK_DIR = Path.home().joinpath(".config/subpack" if IS_POSIX else "AppData\\Roaming\\subpack")
    """ Path to the common assets managed by subpack """

    def _init_env(self) -> Path:
        if not self.IS_POSIX:
            raise NotImplementedError()

        envfile = self.SUBPACK_DIR.joinpath("env")
        if not envfile.exists():
            envfile.touch()

            profile_path = Path.home().joinpath(".profile")
            line = f'. "{self.SUBPACK_DIR}/env"'
            
            if profile_path.exists():
                with open(profile_path) as f:
                    profile = f.read()
                    if line in profile:
                        return envfile
                
            with open(profile_path, mode="a") as f:
                f.write(f"\n{line}\n")

            self.print(f"added '{line}' to {profile_path}")
        return envfile

    def _add_path(self):
        if not self.add_path:
            return
        
        envfile = self._init_env()

        with open(envfile) as f:
            env = f.readlines()

        tag = f"# {self.__class__.__name__}"

        for line in env:
            if tag in line:
               env.remove(line)
               break

        symbo = self.SUBPACK_DIR.joinpath(self.__class__.__name__.lower())
        symbo.unlink(missing_ok=True)
        sh("ln -sf {0} {1}".format(self.path.absolute(), symbo.absolute()))
        
        env.append(f'export PATH=$PATH:"{symbo.joinpath(self.add_path).absolute()}"  {tag}')

        with open(envfile, mode="w") as f:
            f.writelines(env)

    @property
    def path(self) -> Path:
        return self.SUBPACK_DIR.joinpath(self.name)
    
    def __init__(self, name: str, artifact: str | Path, add_path: Optional[Path | str] = None) -> None:
        self.name = name
        """ Package contents will be located in subpack/{name}/* """
        self.artifact: Path = self.SUBPACK_DIR.joinpath(name, artifact)
        """ The primary file of interest, usually an executable, that by default determines if the package is installed """
        self.add_path = add_path
        """ optional path, relative to self.path, that should be added to the system env PATH """
        self.drill_singleton_dirs = False
        """ upon extraction, drill through until path's contents are a single directory """

    def print(self, *args):
        print("      ", *args, flush=True)

    def mktmp(self) -> Path:
        tmp = self.SUBPACK_DIR.joinpath("tmp")
        tmp.mkdir(exist_ok=True, parents=True)
        return tmp

    def install(self):
        raise NotImplementedError()

    def is_installed(self) -> bool:
        return self.artifact.exists()

    def ensure_installed(self) -> Path:
        if not self.is_installed():
            self.install()
        return self.artifact

    def _extraction_method_linux(self, archive: str) -> str:
        larchive = archive.lower()
        if larchive.endswith(".zip"):
            return "unzip {0} -d {1}"
        elif larchive.endswith(".tar.xz"):
            return "tar -xf {0} -C {1}"
        elif larchive.endswith(".tar.gz"):
            return "tar -xf {0} -C {1}"

        raise Exception(f"unsupported archive type: {archive}")

    def _extraction_method_windows(self, archive: str) -> str:
        raise NotImplementedError()

    def extract(self, src: str | Path, dst_dir: Path, delete_src=False):
        if self.IS_POSIX:
            extraction_method = self._extraction_method_linux(str(src))
        else:
            extraction_method = self._extraction_method_windows(str(src))

        extraction_cmd = extraction_method.format(src, dst_dir)
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

    def download(self, url: str, dst: str | Path):
        logger.info("download(%s) ->\n\t%s", url, dst)
        urllib.request.urlretrieve(url, dst)        

    def download_extract(self, archive_url: str, archive_type: str, extract_dir: Optional[Path]=None, delete_src=True):
        ark_file = str(self.mktmp().joinpath(f"{self.name}.{archive_type}"))
        self.print(f"downloading {self.name}...")
        self.download(archive_url, ark_file)
        
        self.print("extracting archive...")
        self.extract(ark_file, extract_dir or self.path, delete_src=delete_src)

    def _drill_singleton_dirs(self, p: Path):
        listing = os.listdir(p)
        while len(listing) == 1:
            singleton = listing[0]
            self.print(f"drilling: {singleton}")
            for f in os.listdir(p.joinpath(singleton)):
                print(f"\tmv {f} ..")
                shutil.move(p.joinpath(singleton, f), p)
            os.rmdir(p.joinpath(singleton))
            listing = os.listdir(p)

    def remove(self):
        sh(f"rm -rf {self.path.absolute()}")
