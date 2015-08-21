__author__ = 'marc'

import json
import ckanapi
from optparse import OptionParser


def listify(value):
    if isinstance(value, unicode):
        return filter(None, map(unicode.strip, value.split(';')))  # filter removes empty strings
    elif isinstance(value, list):
        return filter(None, map(unicode.strip, value[0].split(';')))
    else:
        return []


parser = OptionParser()
parser.add_option("-u", "--url", dest="ckan_url", default="http://ndmckanq1.stcpaz.statcan.gc.ca/zj/",
                  help="url of CKAN instance to query")
parser.add_option("-o", "--organization", dest="ckan_org", default="maprimary",
                  help="organization in which to search")
parser.add_option("-f", "--field", dest="ckan_fields",
                  help="field(s) to search for unique values.  If omitted return field names in organization. "
                       "If multiple fields separated by semicolon, append their values before finding unique values.")

(options, args) = parser.parse_args()

if options.ckan_fields:
    ckan_fields = listify(unicode(options.ckan_fields))
else:
    ckan_fields = []

result = []

rc = ckanapi.RemoteCKAN(options.ckan_url)
i = 0
n = 1
while i < n:
    query_results = rc.action.package_search(
        q='organization:'+options.ckan_org,
        rows=1000,
        start=i*1000)
    i += 1
    n = query_results['count'] / 1000.0
    for line in query_results['results']:
        for e in line['extras']:
            line[e['key']] = e['value']
        if ckan_fields:
            temp = u''
            for field in ckan_fields:
                if field in line:
                    temp += line[field].lower().strip() + u' | '
                elif len(ckan_fields) > 1:
                    temp += u'N/A | '
            if temp:
                result = list(set(result+[temp.strip(' | ')]))
        else:
            result = list(set(result+line.keys()))

print json.dumps(sorted(result), indent=2)
