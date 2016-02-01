import json
import ckanapi
from massage_product import do_product

__author__ = 'marc'

set_archived = 0
rc = ckanapi.RemoteCKAN('http://ndmckanq1.stcpaz.statcan.gc.ca/zj/')
i = 0
n = 1
while i < n:
    query_results = rc.action.package_search(
        q='producttypecode_bi_strs:11',
        rows=1000,
        sort='productidnew_bi_strs ASC',
        start=i*1000
    )
    i += 1
    n = query_results['count'] / 1000.0
    for line in query_results['results']:
        for e in line['extras']:
            line[e['key']] = e['value']

        product_dict = do_product(line)
        product_dict['type'] = u'view'
        product_dict['name'] = u'{type}-{product_id}'.format(
                type=product_dict['type'],
                product_id=product_dict['product_id_new']
            ).lower()
        url_dict = {
            'en': line.get('url_en_strs', ''),
            'fr': line.get('url_fr_strs', '')
        }
        if url_dict['en'] or url_dict['fr']:
            product_dict['url'] = url_dict
        if not product_dict.get('archive_status_code') and \
                'archive' in \
                product_dict.get('admin_notes', {}).get('en', '').lower():
            product_dict['archive_status_code'] = '1'  # archived
            set_archived += 1

        if product_dict:
            print json.dumps(product_dict)

print 'set archive status for {set_archived} views'.format(
    set_archived=set_archived
)
