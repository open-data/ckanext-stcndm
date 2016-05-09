import sys
import subprocess
from httplib import HTTPConnection as hc
from urlparse import urlparse, parse_qs
from urllib import urlencode

url = urlparse(sys.argv[1] if len(sys.argv) > 1 else 'http://localhost:8983/solr/stcndm/select?q:*.*')
query = parse_qs(url.query)
if not query.get('q'):
    query['q'] = ['*.*']
query['fl'] = ['name']
query['rows'] = ['1000']
query['wt'] = ['csv']
conn = hc(url.netloc)
conn.request('GET', url.path + '?' + urlencode(query, doseq=True))
response = conn.getresponse()
for x in response.read().split()[1:]:
    if x:
        subprocess.call([
            'paster',
            '--plugin=ckan',
            'search-index',
            'rebuild',
            x
        ])
