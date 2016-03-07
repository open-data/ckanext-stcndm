#!/usr/bin/env python
# encoding: utf-8
import sys
import csv
from collections import namedtuple

import ckanapi
from docopt import docopt


USAGE = """insert_authors.py

Usage:
    insert_authors.py <remote> <source> [options]

Options:
    --api-key=<key>         API Key to use for insertion.
"""

record = namedtuple('record', ['full_name', 'first_name', 'last_name'])
OWNER_ORG = 'statcan'
PACKAGE_NAME = 'internal_authors'
PACKAGE_TITLE = 'Internal Authors'
ENCODING = 'utf-8'


def main():
    args = docopt(USAGE)

    rc = ckanapi.RemoteCKAN(
        args['<remote>'],
        apikey=args['--api-key']
    )

    with open(args['<source>'], 'rU') as fin:
        reader = csv.DictReader(fin)

        results = set(
            record(
                u'{0}, {1}'.format(
                    r['Last Name'].title().decode(ENCODING),
                    r['First Name'].title().decode(ENCODING)
                ),
                r['First Name'].title().decode(ENCODING),
                r['Last Name'].title().decode(ENCODING)
            ) for r in reader
        )

        # Create the host dataset and resource if missing
        search = rc.action.package_search(
            q='name:{name}'.format(name=PACKAGE_NAME)
        )
        if search['count'] == 0:
            rc.action.package_create(
                owner_org=OWNER_ORG,
                name=PACKAGE_NAME,
                title=PACKAGE_TITLE
            )

            rc.action.datastore_create(
                resource={
                    'package_id': PACKAGE_NAME,
                    'name': 'List',
                },
                fields=[{
                    'id': 'first_name',
                    'type': 'text'
                }, {
                    'id': 'last_name',
                    'type': 'text'
                }, {
                    'id': 'full_name',
                    'type': 'text'
                }],
                aliases=[
                    'internal_authors'
                ],
                primary_key=[
                    'first_name',
                    'last_name'
                ],
                records=list(r._asdict() for r in results)
            )
        else:
            pkg = rc.action.package_show(id=PACKAGE_NAME)

            rc.action.datastore_upsert(
                resource_id=pkg['resources'][0]['id'],
                force=True,
                records=list(r._asdict() for r in results)
            )


if __name__ == '__main__':
    sys.exit(main())
