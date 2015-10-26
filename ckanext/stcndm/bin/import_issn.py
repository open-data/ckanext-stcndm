import ckanapi
import ckan
import ConfigParser
import csv
import json

__author__ = 'marc'

parser = ConfigParser.SafeConfigParser()
parser.read("./ckanparameters.config")

API_KEY = parser.get("ckanlocal", "api_key")
BASE_URL = parser.get("ckanlocal", "base_url")

rc = ckanapi.RemoteCKAN(
    BASE_URL,
    apikey=API_KEY
)

with open('ISSNbatch.csv', 'rb') as csv_file:
    spam_reader = csv.reader(csv_file, delimiter=',')
    for row in spam_reader:
        results = rc.action.package_search(
            q='product_id_new:{product_id} and'
              'name:publication*'.format(
                product_id=row[0]
            )
        )
        if results['count'] == 0:
            print 'product_id_new {product_id}: no data sets found'.format(
                product_id=row[0]
            )
        elif results['count'] > 1:
            print 'product_id_new {product_id}: more than one data set found'.format(
                product_id=row[0]
            )
        else:
            result = results['results'][0]
            result[u'issn_number'] = {
                u'en': row[1],
                u'fr': row[2]
            }
            rc.action.package_update(**result)
            print 'product_id_new {product_id}: updated ISSN for data set'.format(
                product_id=row[0]
            )
