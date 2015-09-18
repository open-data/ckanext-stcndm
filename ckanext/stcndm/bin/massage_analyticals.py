import sys
import json
import ckanapi
from massage_product import do_format, do_release, do_product
__author__ = 'marc'


rc = ckanapi.RemoteCKAN('http://ndmckanq1.stcpaz.statcan.gc.ca/zj')
i = 0
n = 1
while i < n:
    query_results = rc.action.package_search(
        q='producttypecode_bi_strs:20',
        sort='productidnew_bi_strs asc',
        rows=1000,
        start=i*1000)
    n = query_results['count'] / 1000.0
    i += 1

    for line in query_results['results']:
        for e in line['extras']:
            line[e['key']] = e['value']

        if len(line['productidnew_bi_strs']) == 8:
            product_out = do_product(line)
            product_out['type'] = u'publication'
            product_out['name'] = u'{type}-{product_id}'.format(
                    type=product_out['type'],
                    product_id=product_out['product_id_new']
                ).lower()

            release_out = do_release(line)
            print json.dumps(release_out)

            format_out = do_format(line)
            format_out['release_slug'] = release_out['name']
            print json.dumps(format_out)

        elif len(line['productidnew_bi_strs']) == 15:
            release_out = do_release(line)
            print json.dumps(release_out)

            format_out = do_format(line)
            format_out['release_slug'] = release_out['name']
            print json.dumps(format_out)
        elif len(line['productidnew_bi_strs']) > 15:
            product_out = do_product(line)
            product_out['type'] = u'article'
            product_out['name'] = u'{type}-{product_id}'.format(
                    type=product_out['type'],
                    product_id=product_out['product_id_new']
                ).lower()

            release_out = do_release(line)
            print json.dumps(release_out)

            format_out = do_format(line)
            format_out['release_slug'] = release_out['name']
            print json.dumps(format_out)
        else:
            sys.stderr.write(
                'weird analytical {product_id}\n'
                .format(product_id=line['productidnew_bi_strs'])
            )