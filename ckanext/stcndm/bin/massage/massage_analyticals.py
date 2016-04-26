import sys
import inspect
import os
import json
import ckanapi
from massage_product import do_format, do_product
import re
import csv

__author__ = 'marc'


def clean_dict(dict_in):
    dict_out = {}
    for dict_key in dict_in:
        if isinstance(dict_in[dict_key], dict):
            if (
                    u'en' in dict_in[dict_key] and
                    u'fr' in dict_in[dict_key] and
                    (dict_in[dict_key][u'en'] or dict_in[dict_key][u'fr'])
               ):
                dict_out[dict_key] = dict_in[dict_key]
        elif dict_in[dict_key]:
            dict_out[dict_key] = dict_in[dict_key]
    return dict_out


dropped_products = [  # Jackie says these shouldn't go into refactored
    '93-317-X',
    '93-320-X',
    '93-325-X',
    '93-326-X',
    '93-328-X',
    '93-329-X',
    '93-330-X',
    '93-332-X',
    '93F0032X',
    '98-107-X',
    '98-108-X',
    '98-109-X',
    '11999999001',
    '13-605-X1997001',
    '13-605-X1998001',
    '13-605-X2000001',
    '13-605-X2001001',
    '13-605-X2001002',
    '13-605-X2002001',
    '13-605-X2002002',
    '13-605-X2002003',
    '13-605-X2002004',
    '13-605-X2003001',
    '13-605-X2003002',
    '13-605-X2003003',
    '13-605-X2003004',
    '13-605-X2003005',
    '13-605-X2004001',
    '13-605-X2004002',
    '13-605-X2004003',
    '13-605-X2004004',
    '13-605-X2005001',
    '21-004-X1993010',
    '21-004-X1994003',
    '21-004-X1994009',
    '21-004-X1995003',
    '21-004-X1996003',
    '21-004-X1996009',
    '21-004-X2002009',
    '85-002-X1981001',
    '85-002-X1981002',
    '85-002-X1982001',
    '85-002-X1982002',
    '85-002-X1982003',
    '85-002-X1982004',
    '85-002-X1982005',
    '85-002-X1983001',
    '85-002-X1983002',
    '85-002-X1984001',
    '85-002-X1984002',
    '85-002-X1984003',
    '85-002-X1984004',
    '85-002-X1984005',
    '85-002-X1984006',
    '85-002-X1984007',
    '85-002-X1985001',
    '85-002-X1985002',
    '85-002-X1985003',
    '85-002-X1985004',
    '85-002-X1986001',
    '85-002-X1986002',
    '85-002-X1986003',
    '85-002-X1987001',
    '85-002-X1987002',
    '85-002-X1987003',
    '85-002-X1987004',
    '85-002-X1987005',
    '85-002-X1988001',
    '85-002-X1988002',
    '85-002-X1988003',
    '85-002-X1988004',
    '85-002-X1988005',
    '85-002-X1989001',
    '85-002-X1989002',
    '85-002-X1989003',
    '85-002-X1989004',
    '85-002-X1990001',
    '85-002-X1990002',
    '85-002-X2002012',
    '14-31-00001-000-00',
    '19-13-00001-000-17',
    '19-13-00002-000-17',
    '19-13-00003-000-17',
    '19-13-00004-000-17',
    '19-13-00004-001-17',
    '19-13-00004-002-17',
    '19-13-00005-000-17',
    '19-13-00005-001-17',
    '19-13-00005-002-17',
    '19-13-00005-003-17',
    '19-19-00001-000-00',
    '19-19-00003-000-00',
    '19-19-00004-000-00',
    '19-19-00005-000-00',
    '19-19-00006-000-00',
    '19-19-00007-000-00',
    '19-19-00010-000-00',
    '19-19-00010-001-00',
    '19-19-00010-002-00',
    '19-19-00010-003-00',
    '19-19-00010-004-00',
    '19-19-00010-005-00',
    '19-19-00013-000-00',
    '19-19-00016-000-00',
    '19-19-00017-000-17',
    '19-19-00018-000-17',
    '19-19-00019-000-17',
    '19-19-00020-000-17',
    '19-19-00021-000-17',
    '19-19-00022-000-17',
    '19-36-00001-000-00',
    '19-36-00001-001-00',
    '19-36-00001-002-00',
    '19-36-00002-000-00',
    '19-36-00003-001-00',
    '19-36-00003-002-00',
    '19-36-00004-000-00',
    '19-36-00004-001-00',
    '19-36-00004-002-00',
    '19-36-00004-003-00',
    '19-36-00004-004-00',
    '19-36-00004-005-00',
    '19-36-00005-000-00',
    '19-36-00006-000-00',
    '19-36-00008-000-00',
    '19-36-00009-000-00',
    '19-36-00009-001-00',
    '19-36-00009-002-00',
    '19-36-00009-003-00',
    '19-36-00010-001-00',
    '19-36-00010-002-00',
    '19-36-00011-001-00',
    '19-36-00011-002-00',
    '19-36-00012-000-00',
    '19-36-00012-001-00',
    '19-36-00012-002-00',
    '19-36-0013-605-00',
]
product_id_list = []
current_pid = u''
product_dict_out = {}
format_dict_dict = {}
path = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))

dnl_list = []
file_path = '{path}/oldprintdonotload.csv'.format(path=path)
with open(file_path, 'rb') as csv_file:
    spam_reader = csv.DictReader(csv_file, delimiter=',')
    for row in spam_reader:
        dnl_list.append(row['extras_productidnew_bi_strs'])

issn_dict = {}
file_path = '{path}/ISSNbatchwithformat.csv'.format(path=path)
with open(file_path, 'rb') as csv_file:
    spam_reader = csv.DictReader(csv_file, delimiter=',')
    for row in spam_reader:
        product_id_new = row['productidnew_bi_strs']
        if product_id_new not in issn_dict:
            issn_dict[product_id_new] = {}
        format_code = row['formatcode_bi_txtm']
        issn_dict[product_id_new][format_code] = {
            u'en': row['issnnum_en_strs'],
            u'fr': row['issnnum_fr_strs']
        }

generic_ids = []
file_path = '{path}/generic_ids.txt'.format(path=path)
with open(file_path, 'r') as text_file:
    lines = text_file.readlines()
for line in lines:
    generic_ids.append(line.strip())

rc = ckanapi.RemoteCKAN('http://ndmckanq1.stcpaz.statcan.gc.ca/zj')
i = 0
n = 1
while i < n:
    query_results = rc.action.package_search(
        q='producttypecode_bi_strs:20',
        sort='productidnew_bi_strs ASC, '
             'title_en_txts DESC, '
             'zckownerorg_bi_strs DESC',
        rows=1000,
        start=i*1000
    )
    n = query_results['count'] / 1000.0
    i += 1

    for line in query_results['results']:
        for e in line['extras']:
            line[e['key'].strip()] = e['value'].strip()

        product_id_new = line.get(u'productidnew_bi_strs').upper()
        if product_id_new[:8] in generic_ids:
            continue
        if (product_id_new in dropped_products or
                product_id_new[:8] in dropped_products or
                product_id_new[:15] in dropped_products):
            continue
        product_dict = do_product(line)
        format_dict = do_format(line)
        format_code = format_dict.get(u'format_code')
        if format_code == u'12' and (
            product_id_new[:8] in dnl_list or
            product_id_new in dnl_list
        ):
            format_dict[u'load_to_olc_code'] = u'0'
        if len(product_id_new) == 8:
            product_dict[u'type'] = u'publication'
            product_dict[u'name'] = u'{type}-{product_id}'.format(
                    type=product_dict[u'type'],
                    product_id=product_id_new
                ).lower()
            if product_id_new not in product_id_list:
                product_id_list.append(product_id_new)
        elif len(product_id_new) == 15:
            product_dict[u'type'] = u'article'
            product_dict[u'name'] = u'{type}-{product_id}'.format(
                    type=product_dict[u'type'],
                    product_id=product_id_new
                ).lower()
            if product_id_new not in product_id_list:
                product_id_list.append(product_id_new)
                if product_id_new[:8] not in product_id_list:
                    sys.stderr.write(
                        '{product_id}: missing parent {parent_id}\n'
                        .format(
                            product_id=product_id_new,
                            parent_id=product_id_new[:8]
                        )
                    )
        elif len(product_id_new) > 15 and not \
                re.match('\d\d-\d\d-\d\d*', product_id_new):
            product_dict[u'type'] = u'article'
            product_dict[u'name'] = u'{type}-{product_id}'.format(
                    type=product_dict[u'type'],
                    product_id=product_id_new
                ).lower()
            if product_id_new not in product_id_list:
                product_id_list.append(product_id_new)
                if product_id_new[:8] not in product_id_list:
                    sys.stderr.write(
                        '{product_id}: missing parent {parent_id}\n'
                        .format(
                            product_id=product_id_new,
                            parent_id=product_id_new[:8]
                        )
                    )
                if product_id_new[:15] not in product_id_list:
                    sys.stderr.write(
                        '{product_id}: missing parent {parent_id}\n'
                        .format(
                            product_id=product_id_new,
                            parent_id=product_id_new[:15]
                        )
                    )
        else:
            sys.stderr.write(
                'ignoring analytical with unexpected product_id: '
                '{product_id} - name: {name}\n'
                .format(
                    product_id=line.get(u'productidnew_bi_strs', u'product_id'),
                    name=line.get(u'name', u'name')
                )
            )
            continue

        if current_pid == product_id_new:
            for key in clean_dict(product_dict):
                if key not in product_dict_out:
                    product_dict_out[key] = product_dict[key]

            if format_code:
                if format_code not in format_dict_dict:
                    format_dict_dict[format_code] = {}
                for key in format_dict:
                    if key not in format_dict_dict[format_code]:
                        format_dict_dict[format_code][key] = format_dict[key]
            else:
                sys.stderr.write(
                    '{product_id}: missing a format_code for {name}\n'
                    .format(
                        product_id=current_pid,
                        name=line.get(u'name', u'name')
                    )
                )

        else:
            if product_dict_out:
                # if current_pid[:8] in dnl_list:
                #     product_dict_out[u'load_to_olc_code'] = u'0'
                print json.dumps(clean_dict(product_dict_out))
                product_dict_out = {}

                for format_dict_key in format_dict_dict:
                    format_dict_out = format_dict_dict[format_dict_key]
                    if format_dict_out:
                        if not format_dict_out[u'issn_number'][u'en']:
                            format_dict_out[u'issn_number'] = \
                                issn_dict.get(
                                    current_pid,
                                    {}
                                ).get(format_dict_out[u'format_code'],
                                      {u'en': u'', u'fr': u''})
                        print json.dumps(clean_dict(format_dict_out))

            current_pid = product_id_new
            product_dict_out = product_dict
            format_dict_dict = {}
            if format_dict:
                if format_code:
                    format_dict_dict = {format_code: format_dict}

print json.dumps(clean_dict(product_dict_out))
for format_dict_key in format_dict_dict:
    format_dict_out = format_dict_dict[format_dict_key]
    if format_dict_out:
        if not format_dict_out[u'issn_number'][u'en']:
            format_dict_out[u'issn_number'] = \
                issn_dict.get(
                    current_pid,
                    {}
                ).get(format_dict_out[u'format_code'],
                      {u'en': u'', u'fr': u''})
        print json.dumps(clean_dict(format_dict_out))
