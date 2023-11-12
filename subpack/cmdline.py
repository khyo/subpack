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

    args = parser.parse_args()

    if args.verbose:
        logging.basicConfig(level=logging.INFO)

    if args.func:
        args.func(args)


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
