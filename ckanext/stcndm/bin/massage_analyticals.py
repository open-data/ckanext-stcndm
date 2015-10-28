import sys
import json
import ckanapi
from massage_product import do_format, do_release, do_product
import re

__author__ = 'marc'

release_dict = {}
rc = ckanapi.RemoteCKAN('http://ndmckanq1.stcpaz.statcan.gc.ca/zj')
i = 0
n = 1
while i < n:
    query_results = rc.action.package_search(
        q='producttypecode_bi_strs:20',
        sort='productidnew_bi_strs ASC, zckownerorg_bi_strs DESC, title_string DESC',
        rows=1000,
        start=i*1000
    )
    n = query_results['count'] / 1000.0
    i += 1

    for line in query_results['results']:
        for e in line['extras']:
            line[e['key']] = e['value']

        product_id_new = line.get(u'productidnew_bi_strs')
        if not product_id_new:
            sys.stderr.write('product missing product_id_new')
            continue
        if product_id_new in release_dict:
            release_dict[product_id_new] += 1
        else:
            release_dict[product_id_new] = 1

        line[u'release_id'] = unicode(release_dict[product_id_new])

        if len(product_id_new) == 8:
            if release_dict[product_id_new] == 1:
                product_out = do_product(line)
                product_out[u'type'] = u'publication'
                product_out[u'name'] = u'{type}-{product_id}'.format(
                        type=product_out[u'type'],
                        product_id=product_out[u'product_id_new']
                    ).lower()
                print json.dumps(product_out)

            release_out = do_release(line)
            print json.dumps(release_out)

            format_out = do_format(line)
            format_out[u'release_slug'] = release_out[u'name']
            print json.dumps(format_out)

        elif len(product_id_new) == 15:
            if not product_id_new[:8] in release_dict:
                sys.stderr.write('{product_id}: parent publication {parent_id} is missing\n'.format(
                    product_id=product_id_new,
                    parent_id=product_id_new[:8]
                ))
            if not line.get(u'issueno_bi_strs'):
                line[u'issueno_bi_strs'] = line.get(u'productidnew_bi_strs')[8:15]
            if not line.get(u'hierarchyid_bi_strm'):
                line[u'hierarchyid_bi_strm'] = line.get(u'productidnew_bi_strs')[:8]
            if release_dict[product_id_new] == 1:
                product_out = do_product(line)
                product_out[u'type'] = u'publication'
                product_out[u'name'] = u'{type}-{product_id}'.format(
                        type=product_out[u'type'],
                        product_id=product_out[u'product_id_new']
                    ).lower()
                print json.dumps(product_out)

            release_out = do_release(line)
            print json.dumps(release_out)

            format_out = do_format(line)
            format_out[u'release_slug'] = release_out[u'name']
            print json.dumps(format_out)
        elif len(product_id_new) > 15 and not re.match('\d\d-\d\d-\d\d*', product_id_new):
            if not product_id_new[:8] in release_dict:
                sys.stderr.write('{product_id}: parent publication {parent_id} is missing\n'.format(
                    product_id=product_id_new,
                    parent_id=product_id_new[:8]
                ))
            if not line.get(u'issueno_bi_strs'):
                line[u'issueno_bi_strs'] = line.get(u'productidnew_bi_strs')[8:15]
            if not line.get(u'hierarchyid_bi_strm'):
                line[u'hierarchyid_bi_strm'] = line.get(u'productidnew_bi_strs')[:8]
            if release_dict[product_id_new] == 1:
                product_out = do_product(line)
                product_out[u'type'] = u'article'
                product_out[u'name'] = u'{type}-{product_id}'.format(
                        type=product_out[u'type'],
                        product_id=product_out[u'product_id_new']
                    ).lower()
                print json.dumps(product_out)

            release_out = do_release(line)
            print json.dumps(release_out)

            format_out = do_format(line)
            format_out[u'release_slug'] = release_out[u'name']
            print json.dumps(format_out)
        else:
            sys.stderr.write(
                'ignoring analytical with unexpected product_id: {product_id}\n'
                .format(product_id=line.get(u'productidnew_bi_strs', u'product_id'))
            )
