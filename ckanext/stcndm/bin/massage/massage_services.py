import json
import ckanapi
import csv
from massage_product import do_product
import inspect, os

__author__ = 'marc'

path = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
issn_dict = {}
with open('{path}/ISSNbatch.csv'.format(path=path), 'rb') as csv_file:
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
        q='producttypecode_bi_strs:23',
        rows=1000,
        start=i*1000,
        sort='productidnew_bi_strs ASC')
    n = query_results['count'] / 1000.0
    i += 1
    for line in query_results['results']:
        for e in line['extras']:
            line[e['key']] = e['value']

        product_dict = do_product(line)
        current_pid = product_dict['product_id_new']
        product_dict['type'] = u'service'
        product_dict['name'] = u'{type}-{product_id}'.format(
                type=product_dict['type'],
                product_id=current_pid
            ).lower()
        if current_pid in issn_dict:
            product_dict[u'issn_number'] = issn_dict[current_pid]
        if product_dict:
            print json.dumps(product_dict)
