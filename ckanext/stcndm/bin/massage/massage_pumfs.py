# coding=utf-8
import json
import ckanapi
import csv
import inspect
import os
import sys
from massage_product import do_product, do_format

__author__ = 'marc'

pumf_history_note_en = u'These data are available at no additional charge to ' \
                       u'Canadian educational institutions participating in ' \
                       u'the Data Liberation Initiative. (hyperlink Data ' \
                       u'Liberation Initiative to: ' \
                       u'http://www.statcan.gc.ca/dli-ild/dli-idd-eng.htm)'
pumf_history_note_fr = u'Ces données sont offertes gratuitement aux ' \
                       u'établissements d’enseignement canadiens participant ' \
                       u'à l\'Initiative de démocratisation des données ' \
                       u'(hyperlink l\'initative de démocratisation des ' \
                       u'données : ' \
                       u'http://www.statcan.gc.ca/dli-ild/dli-idd-fra.htm)'


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
issn_dict = {}
with open('{path}/ISSNbatchwithformat.csv'.format(path=path), 'rb') as csv_file:
    spam_reader = csv.DictReader(csv_file, delimiter=',')
    for row in spam_reader:
        issn_dict[row['productidnew_bi_strs']] = {
            u'en': row['issnnum_en_strs'],
            u'fr': row['issnnum_fr_strs']
        }

rc = ckanapi.RemoteCKAN('http://ndmckanq1.stcpaz.statcan.gc.ca/zj')
i = 0
n = 1
while i < n:
    query_results = rc.action.package_search(
        q='producttypecode_bi_strs:25',
        rows=1000,
        start=i*1000,
        sort='productidnew_bi_strs ASC, '
             'title_en_txts DESC, '
             'zckownerorg_bi_strs DESC')
    n = query_results['count'] / 1000.0
    i += 1
    for line in query_results['results']:
        for e in line['extras']:
            line[e['key'].strip()] = e['value'].strip()

        product_dict = do_product(line)
        format_dict = do_format(line)
        format_code = format_dict.get(u'format_code')
        product_id_new = product_dict.get('product_id_new').upper()
        product_dict['type'] = u'pumf'
        product_dict['name'] = u'{type}-{product_id}'.format(
                type=product_dict['type'],
                product_id=product_id_new
            ).lower()
        if u'history_notes' in product_dict:
            if product_dict[u'history_notes'].get(u'en'):
                product_dict[u'history_notes'][u'en'] += u'; ' + \
                                                         pumf_history_note_en
            else:
                product_dict[u'history_notes'][u'en'] = pumf_history_note_en
            if product_dict[u'history_notes'].get(u'fr'):
                product_dict[u'history_notes'][u'fr'] += u'; ' + \
                                                         pumf_history_note_fr
            else:
                product_dict[u'history_notes'][u'fr'] = pumf_history_note_fr
        else:
            product_dict[u'history_notes'] = {
                u'en': pumf_history_note_en,
                u'fr': pumf_history_note_fr
            }
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
