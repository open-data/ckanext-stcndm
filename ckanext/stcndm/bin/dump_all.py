import ckanapi
import ConfigParser
import json

__author__ = 'marc'

parser = ConfigParser.SafeConfigParser()
parser.read("./ckanparameters.config")

BASE_URL = parser.get("ckanedctest", "base_url")

rc = ckanapi.RemoteCKAN(
    BASE_URL,
    requests_kwargs={'verify': False}
)
i = 0
n = 1
while i < n:
    query_results = rc.action.package_search(
        q='*:*',
        rows=1000,
        start=i*1000
    )
    n = query_results['count'] / 1000.0
    i += 1

    for line in query_results['results']:
        print json.dumps(line)
