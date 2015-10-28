import ckanapi
import ConfigParser
import csv
import sys
import yaml

__author__ = 'marc'

reverse_lookup_dict = {}
stream = file('../schemas/presets.yaml', 'r')
presets = yaml.load(stream)
for preset in presets['presets']:
    if preset['preset_name'] == 'ndm_status':
        choices = preset['values']['choices']
        for choice in choices:
            reverse_lookup_dict[choice['label']['en']] = choice['value']

parser = ConfigParser.SafeConfigParser()
parser.read("./ckanparameters.config")

API_KEY = parser.get("ckanlocal", "api_key")
BASE_URL = parser.get("ckanlocal", "base_url")

PID_list = []

rc = ckanapi.RemoteCKAN(
    BASE_URL,
    apikey=API_KEY
)
i = 0
n = 1
while i < n:
    query_results = rc.action.package_search(
        q='product_id_new:?*',
        rows=1000,
        start=i*1000
    )
    n = query_results['count'] / 1000.0
    i += 1

    for line in query_results['results']:

        PID_list.append(line.get(u'product_id_new'))

missing = 0
with open('jsonl_dumps/oldprintdonotload.csv', 'rb') as csv_file:
    spam_reader = csv.DictReader(csv_file, delimiter=',')
    for row in spam_reader:
        if row['extras_productidnew_bi_strs'] not in PID_list:
            sys.stderr.write('{product_id}: missing from {base_url}\n'.format(
                product_id=row['extras_productidnew_bi_strs'],
                base_url=BASE_URL
            ))
            missing += 1

if not missing:
    print 'no products missing - proceeding with update'
    with open('jsonl_dumps/oldprintdonotload.csv', 'rb') as csv_file:
        spam_reader = csv.DictReader(csv_file, delimiter=',')
        for row in spam_reader:
            query_results = rc.action.package_search(
                q='product_id_new:{product_id}'.format(
                    product_id=row['extras_productidnew_bi_strs']
                )
            )
            if not query_results['count']:
                sys.stderr.write('{product_id}: not found\n'.format(
                    product_id=row['extras_productidnew_bi_strs']
                ))
                continue
            elif query_results['count'] > 1:
                sys.stderr.write('{product_id}: more than one product with this product_id_new\n'.format(
                    product_id=row['extras_productidnew_bi_strs']
                ))
            else:
                result = query_results['results'][0]
                old_status_code = result.get(u'status_code')
                if row['extras_statusf_en_strs'] in ['',
                                                     'Discontinued/Not available',
                                                     'Do not load to OLC']:
                    new_status_code = None
                else:
                    new_status_code = reverse_lookup_dict.get(row['extras_statusf_en_strs'], u'unknown new status')

                if old_status_code != new_status_code:
                    sys.stderr.write(
                        '{product_id}: status_code is {old_status_code}, should be {new_status_code}\n'.format(
                            product_id=row['extras_productidnew_bi_strs'],
                            old_status_code=old_status_code,
                            new_status_code=new_status_code
                        )
                    )
                else:
                    print '{product_id}: status code {status_code} OK'.format(
                        product_id=row['extras_productidnew_bi_strs'],
                        status_code=old_status_code
                    )
