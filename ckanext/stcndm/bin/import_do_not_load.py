import ckanapi
import ConfigParser
import csv
import sys
import yaml
from time import sleep
from ckan.logic import ValidationError, _

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

API_KEY = parser.get("ckandev", "api_key")
BASE_URL = parser.get("ckandev", "base_url")

PID_list = []

rc = ckanapi.RemoteCKAN(
    BASE_URL,
    apikey=API_KEY
)

with open('jsonl_dumps/oldprintdonotload.csv', 'rb') as csv_file:
    spam_reader = csv.DictReader(csv_file, delimiter=',')
    for row in spam_reader:
        sleep(.1)
        product_id = row.get('extras_productidnew_bi_strs', 'product_id')
        query_results = rc.action.package_search(
            q='product_id_new:{product_id}'.format(product_id=product_id)
        )
        if query_results.get('count', 0) < 1:
            sys.stderr.write('{product_id}: not found\n'.format(
                product_id=product_id
            ))
        elif query_results.get('count') > 1:
            sys.stderr.write(
                '{product_id}: more than one product with this '
                'product_id_new\n'.format(
                    product_id=row['extras_productidnew_bi_strs']
                ))
        else:
            update = False
            result = query_results['results'][0]
            if result.get(u'load_to_olc_code') is not None:
                sys.stderr.write(
                    '{product_id}: load_to_olc already set\n'.format(
                        product_id=product_id
                    )
                )
            else:
                print '{product_id}: set load_to_olc_code'\
                    .format(product_id=product_id)
                result[u'load_to_olc_code'] = u'0'
                update = True

            old_status_code = result.get(u'status_code')
            if old_status_code in [u'33', u'36']:
                sys.stderr.write('{product_id}: remove deprecated status_code\n'
                                 .format(product_id=product_id))
                result[u'status_code'] = None
                update = True
            new_status = row.get('extras_statusf_en_strs')
            new_status_code = reverse_lookup_dict.get(new_status)

            if new_status_code and new_status_code != old_status_code:
                print '{product_id}: set status_code {status_code} ' \
                      '{status}'.format(
                        product_id=product_id,
                        status_code=new_status_code,
                        status=new_status
                    )
                result[u'status_code'] = new_status_code
                update = True

            if update:
                print '{product_id}: update'.format(product_id=product_id)
                try:
                    rc.action.package_update(**result)
                except ValidationError:
                    sys.stderr.write('{product_id}: Validation Error'.format(
                        product_id=product_id
                    ))
