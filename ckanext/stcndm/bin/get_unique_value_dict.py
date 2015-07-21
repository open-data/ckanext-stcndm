__author__ = 'marc'

import sys
import json
import subprocess


# import commands


def run_command(command):
    p = subprocess.Popen(command,
                         stdout=subprocess.PIPE)
    return iter(p.stdout.readline, b'')


def code_lookup(old_field_name, data_set, choice_list):
    temp = data_set[old_field_name]
    if isinstance(temp, unicode):
        field_values = map(unicode.strip, temp.split(';'))
    else:
        field_values = map(unicode.strip, temp[0].split(';'))
    codes = []
    for field_value in field_values:
        code = None
        for choice in choice_list:
            if choice['label']['en'] == field_value:
                if choice['value']:
                    code = choice['value']
        if not code:
            print 'weird ' + old_field_name + ' .' + data_set[old_field_name] + '.' + field_value + '.'
        else:
            codes.append(code)
    return codes


value_dict_set = set()
q = 'curl http://localhost:8983/solr/ndm/query?q=organization:{0}&rows=10&fl={1},{2}'.format(sys.argv[1],sys.argv[2],sys.argv[3])

for line in run_command(q.split()):
    print line
    print 'bogon\nbogon'
    if line:
        raw_codesets = json.loads(line)['response']['docs']
        value_dict = {}
        for codeset in raw_codesets:
            if codeset.has_key(sys.argv[2]):
                value_dict['en'] = codeset[sys.argv[2]]
            if codeset.has_key(sys.argv[3]):
                value_dict['fr'] = codeset[sys.argv[3]]
            if len(value_dict):
                value_dict_set.add(value_dict)

print json.dumps([c for c in value_dict_set])
