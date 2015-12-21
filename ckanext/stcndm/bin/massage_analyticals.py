import sys
import json
import ckanapi
from massage_product import do_format, do_product
import re
import csv

__author__ = 'marc'

product_id_list = []
current_pid = u''
product_dict = {}
format_dict = {}
dnl_list = []
with open('jsonl_dumps/oldprintdonotload.csv', 'rb') as csv_file:
    spam_reader = csv.DictReader(csv_file, delimiter=',')
    for row in spam_reader:
        dnl_list.append(row['extras_productidnew_bi_strs'])
issn_dict = {}
with open('jsonl_dumps/ISSNbatch.csv', 'rb') as csv_file:
    spam_reader = csv.DictReader(csv_file, delimiter=',')
    for row in spam_reader:
        issn_dict[row['extras_productidnew_bi_strs']] = {
            u'en': row['issnnum_en_bi_strs'],
            u'fr': row['issnnum_fr_bi_strs']
        }

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

        product_id_new = line.get(u'productidnew_bi_strs')
        if product_id_new not in product_id_list:
            product_id_list.append(product_id_new)
        product_out = do_product(line)
        format_out = do_format(line)
        if len(product_id_new) == 8:
            product_out[u'type'] = u'publication'
            product_out[u'name'] = u'{type}-{product_id}'.format(
                    type=product_out[u'type'],
                    product_id=product_id_new
                ).lower()
        elif len(product_id_new) == 15:
            product_out[u'type'] = u'article'
            product_out[u'name'] = u'{type}-{product_id}'.format(
                    type=product_out[u'type'],
                    product_id=product_id_new
                ).lower()
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
            product_out[u'type'] = u'article'
            product_out[u'name'] = u'{type}-{product_id}'.format(
                    type=product_out[u'type'],
                    product_id=product_id_new
                ).lower()
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
                'ignoring analytical with unexpected product_id: {product_id}\n'
                .format(
                    product_id=line.get(u'productidnew_bi_strs', u'product_id')
                )
            )
            continue

        if current_pid == product_id_new:
            for key in product_out:
                if key not in product_dict:
                    product_dict[key] = product_out[key]
            format_code = format_out.get(u'format_code', u'format_code')
            for key in format_out:
                if format_code not in format_dict:
                    format_dict[format_code] = {}
                if key not in format_dict[format_code]:
                    format_dict[format_code][key] = format_out[key]
        else:
            if current_pid in dnl_list:
                product_dict[u'load_to_olc_code'] = u'0'
            if current_pid in issn_dict:
                product_dict[u'issn_number'] = issn_dict[current_pid]
            if product_dict:
                print json.dumps(product_dict)
                for a_format in format_dict:
                    print json.dumps(format_dict[a_format])
            current_pid = product_id_new
            product_dict = product_out
            format_dict = {
                format_out.get(u'format_code', u'format_code'): format_out
            }
