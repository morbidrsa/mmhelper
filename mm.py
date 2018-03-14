#!/usr/bin/env python3
# -*- mode: python -*-
# Copyright © 2018 Johannes Thumshirn
# Licensed under the GPLv2

import sys
import argparse

def auto_int(x):
    return int(x, 0)


def main():
    parser = argparse.ArgumentParser(
        description='Memory Management helper utilities',)
    parser.add_argument('--arch', action='store', default='x86_64',
                        help='architecture')
    parser.add_argument('--address', action='store', help='', type=auto_int)
    parser.add_argument('--cr3', action='store', type=auto_int,
                        help='Value of CR3 register, only valid on x86_64')

    args = parser.parse_args()

    if not args.arch:
        print("Need address of fault")
        sys.exit(1)

    if args.cr3 and not args.arch == 'x86_64':
        print("--cr3 only valid with --arch x86_64")
        sys.exit(1)
    elif args.arch == 'x86_64' and not args.cr3:
        print("--arch x86_64 needs --cr3 as well")
        sys.exit(1)

    if args.arch == 'x86_64':
        from mmhelper.x86_64 import x86_64
        helper = x86_64()
        fault_address = args.address
        pgd_base = args.cr3
    else:
        print("Not a valid architecture " + args.arch)
        sys.exit(1)

    helper.dump_pagetable(fault_address, pgd_base)


if __name__ == '__main__':
    sys.exit(main())
