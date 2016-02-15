import sys
import inspect
import os
import json
import ckanapi
import csv
from datetime import datetime
from dateutil.parser import parse
from dateutil.tz import gettz

__author__ = 'marc'

default_date = datetime(1, 1, 1, 0, 0, 0, 0, tzinfo=gettz('America/Toronto'))
default_release_date = datetime(1, 1, 1, 8, 30, 0, 0,
                                tzinfo=gettz('America/Toronto'))


def to_utc(date_str, def_date=default_date):
    result = parse(date_str, default=def_date)
    utc_result = result.astimezone(gettz('UTC'))
    return utc_result.replace(tzinfo=None).isoformat()


def massage(_line, _correction_dict):
    _correction_id = _line.get('correctionid_bi_strm')
    if not _correction_id:
        sys.stderr.write('Correction missing ID: {line}\n'.format(
            line=_line
        ))
        return
    if _correction_id not in _correction_dict:
        _correction_dict[_correction_id] = {}
    _correction_dict[_correction_id]['correction_date'] = to_utc(
        _line.get('correcdate_bi_strm'))
    _correction_dict[_correction_id]['correction_impact_level_code'] = \
        _line.get('correcimplevelcode_bi_strs')[:1]
    _correction_dict[_correction_id]['correction_type_code'] = \
        _line.get('correctypecode_bi_txtm')
    product_id_new = _line.get('productidnew_bi_strs')
    _correction_dict[_correction_id]['product_id_new'] = \
        product_id_new[7:].upper() \
        if product_id_new.startswith('article') else product_id_new.upper()
    _correction_dict[_correction_id]['notes'] = {
        u'en': _line.get('correcnote_en_txtm'),
        u'fr': _line.get('correcnote_fr_txtm')
    }
    if 'format_codes' not in _correction_dict[_correction_id]:
        _correction_dict[_correction_id]['format_codes'] = []
    _correction_dict[_correction_id]['format_codes'].append(
        _line.get('formatcode_bi_txtm')
    )

path = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
correction_dict = {}

rc = ckanapi.RemoteCKAN('http://ndmckanq1.stcpaz.statcan.gc.ca/zj')
i = 0
n = 1
while i < n:
    query_results = rc.action.package_search(
        q='organization:corrections',
        sort='productidnew_bi_strs ASC',
        rows=1000,
        start=i*1000)
    n = query_results['count'] / 1000.0
    i += 1

    for line in query_results['results']:
        for e in line['extras']:
            line[e['key']] = e['value']
        massage(line, correction_dict)

with open('{path}/CorrectionsJan2015toNov2015_2.csv'.format(path=path)) \
        as csv_file:
    spam_reader = csv.DictReader(csv_file, delimiter=',')
    for row in spam_reader:
        for key in row:
            row[key] = row[key].decode('windows-1256')
        massage(row, correction_dict)

for correction_id in correction_dict:
    dict_out = {
        u'owner_org': u'statcan',
        u'private': False,
        u'type': u'correction',
        u'correction_id': correction_id,
        u'name': u'correction-{id}'.format(id=correction_id)
    }
    dict_out.update(correction_dict[correction_id])
    if dict_out:
        print json.dumps(dict_out)
