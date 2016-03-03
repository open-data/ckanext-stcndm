#!/usr/bin/env python
# encoding: utf-8
import sys
import csv
from collections import namedtuple

import ckanapi
from docopt import docopt


USAGE = """insert_thesaurus.py

Usage:
    insert_insert_thesaurus.py <remote> <source> [options]

Options:
    --api-key=<key>         API Key to use for insertion.
"""

record = namedtuple('record', ['id', 'term_en', 'term_fr'])
OWNER_ORG = 'statcan'
PACKAGE_NAME = 'thesaurus'
PACKAGE_TITLE = 'Thesaurus'


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
                index,
                r['STC thesaurus ENG'].title(),
                r['STC thesaurus FRE'].title()
            ) for index, r in enumerate(reader)
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
                    'id': 'term_id',
                    'type': 'integer'
                }, {
                    'id': 'term_en',
                    'type': 'text'
                }, {
                    'id': 'term_fr',
                    'type': 'text'
                }],
                aliases=[
                    'thesaurus'
                ],
                primary_key=[
                    'term_id'
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
