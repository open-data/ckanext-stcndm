#!/usr/bin/env python
# encoding: utf-8
import sys
import json
from functools import partial

import requests
from lxml import etree
from docopt import docopt

USAGE = """parse_surveys.py

Generates ckanapi import files from the legacy IMDB surveys database.

Usage:
    parse_surveys.py file <file>
    parse_surveys.py url <url>
"""


frequencies = {
    'ONCE': 23,
    'ON DEMAND': 23,
    'ANNUAL': 12,
    'MONTHLY': 6,
    'QUARTERLY': 9,
    'OCCASIONAL': 18,
    'IRREGULAR': 19,
    'QUINQUENNIAL': 16,
    'EVERY 5 YEARS': 16,
    'EVERY 10 YEARS': 17,
    'DAILY': 1,
    'WEEKLY': 2,
    'SEMI-ANNUAL': 11,
    'BIANNUAL': 11,
    'EVERY 4 YEARS': 15,
    'EVERY 2 YEARS': 13,
    'BIENNIAL': 13,
    'EVERY_THREE_YEARS': 14,
    'EVERY 3 YEARS': 14,
    'UNKNOWN': 0,
    'EVERY 10 DAYS': 3,
    'EVERY 2 MONTHS': 7,
    'EVERY 2 WEEKS': 4,
    'THREE_TIMES_A_YEAR': 10,
    '3 TIMES PER YEAR': 10,
    'SIX_TIMES_A_YEAR': 5,
    'TWICE PER MONTH': 5
}

SURVEY_STATUS = {
    'ACTIVE': 1,
    'INACTIVE': 2,
    'DISCONTINUED': 2
}

SURVEY_PARTICIPATION = {
    'MANDATORY': 1,
    'VOLUNTARY': 2,
    'NOT APPLICAPBLE': 3,
    'NOT SPECIFIED': 4
}

DETAILS_BASE_URL_EN = ('http://www23.statcan.gc.ca/imdb/'
                       'p2SV.pl?Function=getSurvey&SDDS={0}')
DETAILS_BASE_URL_FR = ('http://www23.statcan.gc.ca/imdb/'
                       'p2SV_f.pl?Function=getSurvey&SDDS={0}')


def parse_file(file_path):
    with open(file_path, 'rb') as file_in:
        tree = etree.parse(file_in)

        for raw_record in tree.xpath('//SurveySummary'):
            product_id = raw_record.attrib['id']

            record = {
                u'product_id_new': raw_record.attrib['id'],
                u'name': 'survey-{0}'.format(product_id),
                u'private': False,
                u'type': 'survey',
                u'frc': raw_record.attrib.get('frc'),
                u'title': {
                    u'en': raw_record.xpath('string(./name/english)'),
                    u'fr': raw_record.xpath('string(./name/french)')
                },
                u'frequency_codes': [
                    frequencies.get(
                        raw_record.xpath('string(./frequency)').upper(),
                        0
                    )
                ],
                u'archive_status': raw_record.xpath('string(./status)'),
                u'url': {
                    u'en': DETAILS_BASE_URL_EN.format(product_id),
                    u'fr': DETAILS_BASE_URL_FR.format(product_id)
                },
                u'survey_url': {
                    u'en': DETAILS_BASE_URL_EN.format(product_id),
                    u'fr': DETAILS_BASE_URL_FR.format(product_id)
                },
                u'survey_status_code': SURVEY_STATUS[
                    raw_record.xpath('string(./status)')
                ],
                u'survey_participation_code': SURVEY_PARTICIPATION.get(
                    raw_record.xpath('string(./particiation)'),
                    4
                )
            }

            yield record


def parse_url(url):
    tree = etree.fromstring(requests.get(url).content)

    for raw_record in tree.xpath('//SurveySummary'):
        product_id = raw_record.attrib['id']

        detailed_record = etree.fromstring(
            requests.get(
                DETAILS_BASE_URL_EN.format(product_id)
            ).content
        )

        record = {
            u'product_id_new': raw_record.attrib['id'],
            u'name': 'survey-{0}'.format(product_id),
            u'private': False,
            u'type': 'survey',
            u'frc': raw_record.attrib.get('frc'),
            u'title': {
                u'en': raw_record.xpath('string(./name/english)'),
                u'fr': raw_record.xpath('string(./name/french)')
            },
            u'frequency_codes': [
                frequencies.get(
                    raw_record.xpath('string(./frequency)').upper(),
                    0
                )
            ],
            u'archive_status': raw_record.xpath('string(./status)'),
            u'url': {
                u'en': DETAILS_BASE_URL_EN.format(product_id),
                u'fr': DETAILS_BASE_URL_FR.format(product_id)
            },
            u'survey_url': {
                u'en': DETAILS_BASE_URL_EN.format(product_id),
                u'fr': DETAILS_BASE_URL_FR.format(product_id)
            },
            u'survey_status_code': SURVEY_STATUS[
                raw_record.xpath('string(./status)')
            ],
            u'survey_participation_code': SURVEY_PARTICIPATION.get(
                raw_record.xpath('string(./particiation)'),
                4
            )
        }

        # Update with fields only available from the detailed view.
        record.update({
            u'note': {
                u'en': detailed_record.xpath(
                    'string(//purpose/text/english)'
                ),
                u'fr': detailed_record.xpath(
                    'string(//purpose/text/french)'
                ),
            }
        })

        yield record


def main():
    args = docopt(USAGE)

    if args['file']:
        parser = partial(parse_file, args['<file>'])
    elif args['url']:
        parser = partial(parse_url, args['<url>'])

    for record in parser():
        sys.stdout.write(json.dumps(record))
        sys.stdout.write('\n')

    sys.stdout.write('\n')
    sys.stdout.flush()

if __name__ == '__main__':
    sys.exit(main())
