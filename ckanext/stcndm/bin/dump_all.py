import ckanapi
import ConfigParser
import json

__author__ = 'marc'

parser = ConfigParser.SafeConfigParser()
parser.read("./ckanparameters.config")

BASE_URL = parser.get("ckanedctest", "base_url")

rc = ckanapi.RemoteCKAN(
    BASE_URL,
)

order=['subject',
       'geolevel',
       'codeset',
       'survey',
       'geodescriptor',
       'province',
       'cube',
       'view',
       'indicator',
       'chart',
       'publication',
       'article',
       'pumf',
       'generic',
       'service',
       'conference',
       'daily',
       'format',
       'release'
       ]

for type in order:
    i = 0
    n = 1
    while i < n:
        query_results = rc.action.package_search(
            q='type:{type}'.format(type=type),
            rows=1000,
            start=i*1000,
        )
        n = query_results['count'] / 1000.0
        i += 1

        for line in query_results['results']:
            print json.dumps(line)
