#!/usr/bin/env python3
import argparse
import logging
from subpack.package import *
import subpack.packages


def main():
    parser = argparse.ArgumentParser(description="SubPack - Package Manager")
    parser.set_defaults(func=None)
    parser.add_argument("-v", "--verbose", action="store_true")
    
    subparsers = parser.add_subparsers(title="commands")
    sparser = subparsers.add_parser('install', help='install package')
    sparser.set_defaults(func=install)
    sparser.add_argument("packages", nargs="*")
    
    sparser = subparsers.add_parser('remove', help='remove package')
    sparser.set_defaults(func=remove)
    sparser.add_argument("packages", nargs="*")
    
    sparser = subparsers.add_parser('update', help='pull latest subpack git repo')
    sparser.set_defaults(func=update)
    
    sparser = subparsers.add_parser('run', help='execute an installed binary')
    sparser.set_defaults(func=run)
    sparser.add_argument('package', help='package name whose binary to execute')
    sparser.add_argument('args', help='arguments passed to the binary', nargs=argparse.REMAINDER)
    
    sparser = subparsers.add_parser('pwd', help='print working directory [store|lib]')
    sparser.add_argument('dir', help='destination to print: store=default|lib', nargs='?', default="store")
    sparser.set_defaults(func=cd)

    args = parser.parse_args()

    if args.verbose:
        logging.basicConfig(level=logging.INFO)

    if args.func:
        args.func(args)

def run(args):
    packages = get_packages()
    pack = packages.get(args.package)
    if not pack:
        print("unknown package: ", args.package)
        return
    
    pack.ensure_installed()
    cmd = [str(pack.artifact), *args.args]
    subprocess.run([pack.artifact, *args.args]).check_returncode()


def cd(args):
    if args.dir == "store":
        d = subpack.Package.SUBPACK_DIR    
    elif args.dir == "lib":
        d = Path(__file__).parent.parent
    else:
        print("unknown directory: ", args.dir)
        return
    print(d)

def update(args):
    libdir = Path(__file__).parent.parent
    sh("git pull", cwd=libdir)

def install(args):
    packages = get_packages()
    if not args.packages:
        print("select package(s) to install:\n\t" + "\n\t".join(packages))
        
    for package in args.packages:
        p = packages[package]
        if p.is_installed():
            p._add_path()
            print(f"{package}: is already installed @ {p.path}")
        else:
            packages[package].install()


def remove(args):
    packages = get_packages()
    if not args.packages:
        print("select package(s) to remove:\n\t" + "\n\t".join(packages))
        
    for package in args.packages:
        print(f"removing {package}")
        packages[package].remove()
    


def get_packages() -> dict[str, Package]:
    ret = {}

    for k, v in subpack.packages.__dict__.items():
        try:
            if issubclass(v, Package):
                ret[k.lower()] = v()  # type: ignore
        except TypeError:
            pass

    return ret



if __name__ == "__main__":
    main()
