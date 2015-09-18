import json
import ckanapi
from massage_product import do_product, do_release  # , do_format

__author__ = 'marc'


rc = ckanapi.RemoteCKAN('http://ndmckanq1.stcpaz.statcan.gc.ca/zj/')
i = 0
n = 1
while i < n:
    query_results = rc.action.package_search(
        q='producttypecode_bi_strs:10',
        rows=1000,
        start=i*1000)
    i += 1
    n = query_results['count'] / 1000.0
    for line in query_results['results']:
        for e in line['extras']:
            line[e['key']] = e['value']

        product_out = do_product(line)
        product_out['type'] = u'cube'
        product_out['name'] = u'cube-{product_id}'.format(
                product_id=product_out['product_id_new']
            ).lower()
        print json.dumps(product_out)

        release_out = do_release(line)
        print json.dumps(release_out)
