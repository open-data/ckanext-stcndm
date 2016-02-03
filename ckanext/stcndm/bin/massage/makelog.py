import re
import json

__author__ = 'marc'

log_entry = re.compile('^\d+ \[')
jsonl_file_lines = []
dataset_type = ''
error_file = open('jsonl_dumps/load_errs.txt')
for line in error_file:
    if line.startswith('-'):
        dataset_type = line.strip()[1:]
        jsonl_file = open(
            'jsonl_dumps/{dataset_type}.jsonl'.format(
                dataset_type=dataset_type
            )
        )
        jsonl_file_lines = jsonl_file.readlines()
        jsonl_file.close()
    elif log_entry.match(line):
        lookup_line = int(line[:line.find(' [')])
        jsonl_dict = json.loads(jsonl_file_lines[lookup_line-1])
        name = jsonl_dict['name']
        print '{name}: {line}'.format(
            name=name,
            line=line
        )