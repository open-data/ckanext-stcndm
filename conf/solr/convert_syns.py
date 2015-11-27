#!/usr/bin/env python
# encoding: utf-8
import sys


def main():
    with open(sys.argv[1], 'rU') as source:
        for line in source:
            if not line.strip():
                return

            l, r = line.split(':')
            l = l.strip()
            r = r.strip().strip('"')

            print('{l} => {r}'.format(l=l, r=r))


if __name__ == '__main__':
    sys.exit(main())
