import sys
import inspect
import os
import json
import ckanapi
from massage_product import do_format, do_product
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


product_id_list = []
current_pid = u''
product_dict_out = {}
format_dict_dict = {}
path = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))

generic_ids = []
file_path = '{path}/generic_ids.txt'.format(path=path)
with open(file_path, 'r') as text_file:
    lines = text_file.readlines()
for line in lines:
    generic_ids.append(line.strip())

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
with open(file_path, 'r') as generics:
    generic_list = generics.readlines()
for generic in generic_list:
    generic_ids.append(generic.strip())

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
            line[e['key']] = e['value']

        product_id_new = line.get(u'productidnew_bi_strs').upper()
        if product_id_new[:8] not in generic_ids:
            continue
        product_dict = do_product(line)
        format_dict = do_format(line)
        format_code = format_dict.get(u'format_code')
        product_dict[u'type'] = u'generic'
        product_dict[u'name'] = u'{type}-{product_id}'.format(
                type=product_dict[u'type'],
                product_id=product_id_new
            ).lower()
        product_dict[u'product_type_code'] = u'26'
        if product_id_new not in product_id_list:
            product_id_list.append(product_id_new)
        if len(product_id_new) > 8 and \
                product_id_new[:8] not in product_id_list:
            sys.stderr.write(
                '{product_id}: missing parent {parent_id}\n'
                .format(
                    product_id=product_id_new,
                    parent_id=product_id_new[:8]
                )
            )
        if len(product_id_new) > 15 and \
                product_id_new[:15] not in product_id_list:
            sys.stderr.write(
                '{product_id}: missing parent {parent_id}\n'
                .format(
                    product_id=product_id_new,
                    parent_id=product_id_new[:15]
                )
            )

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
                if current_pid in dnl_list:
                    product_dict_out[u'load_to_olc_code'] = u'0'
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
