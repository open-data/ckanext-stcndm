__author__ = 'marc'

import sys
import json
import yaml
import commands
import subprocess


def run_command(command):
    p = subprocess.Popen(command,
                         stdout=subprocess.PIPE)
    return iter(p.stdout.readline, b'')


def do_it(old_field_name, data_set, choice_list):
    temp = data_set[old_field_name]
    if isinstance(temp,str):
        field_values = [].append(temp)
    else:
        field_values = map(unicode.strip, data_set[old_field_name][0].split(';'))
    codes = []
    for field_value in field_values:
        code = None
        for choice in choice_list:
            if choice['label']['en'] == field_value:
                if choice['value']:
                    code = choice['value']
        if not code:
            print 'weird '+old_field_name+' .'+data_set[old_field_name]+'.'+field_value+'.'
        else:
            codes.append(code)
    return codes

for line in run_command('curl http://127.0.0.1:5000/api/3/action/package_search?q=type:codeset&rows=100'.split()):
    raw_codesets = json.loads(line)['result']['results']

content_type_list = []
for codeset in raw_codesets:
    if codeset['codeset_type'] == 'content_type':
        content_type_list.append({
            'label': codeset['title'],
            'value': codeset['codeset_value']
        })

f = open('../schemas/presets.yaml')
presetMap = yaml.safe_load(f)
f.close()
for preset in presetMap['presets']:
    if preset['preset_name'] == 'ndm_archive_status':
        archive_status_list = preset['values']['choices']


f = open('../schemas/imdb.yaml')
imdbMap = yaml.safe_load(f)
f.close()
for field in imdbMap['dataset_fields']:
    if field['field_name'] == 'collection_method_code':
        collection_method_list = field['choices']

lines = json.load(sys.stdin)
out = []
for line in lines:
    line_out = {'owner_org': 'statcan'}

    if 'archived_bi_strs' in line and archive_status_list:
        print line
        print archive_status_list
        result = do_it('archived_bi_strs', line, archive_status_list)
        if result:
            line_out['archive_status_code'] = result[0]
#        for choice in archive_status_list:
#            if choice['label']['en'] == line['archived_bi_strs']:
#                if choice['value']:
#                    line_out['archive_status_code'] = choice['value']
#        if 'archive_status_code' not in line_out:
#            print 'weird archived_bi_strs ' + line['archived_bi_strs'] + '\n'

    if 'collenddate_bi_strs' in line:
        line_out['collection_end_date'] = line['collenddate_bi_strs']

    if 'collmethod_en_txtm' in line and collection_method_list:
        result = do_it('collmethod_en_txtm', line, collection_method_list)
        if result:
            line_out['collection_method_codes'] = result

    if 'collstartdate_bi_strs' in line:
        line_out['collection_start_date'] = line['collstartdate_bi_strs']

    if 'conttype_en_txtm' in line:
        result = do_it('conttype_en_txtm', line, content_type_list)
        if result:
            line_out['content_type_codes'] = result

    out.append(line_out)

"""
    if 'tmtaxdisp_en_tmtxtm' in line:
        if line['tmtaxdisp_en_tmtxtm'][0] == 'a_to_z':
            line_out['subject_display_code'] = '1'
        elif line['tmtaxdisp_en_tmtxtm'][0] == 'taxonomy':
            line_out['subject_display_code'] = '2'
        elif line['tmtaxdisp_en_tmtxtm'][0] == 'both':
            line_out['subject_display_code'] = '3'
        elif line['tmtaxdisp_en_tmtxtm'][0] == 'hide':
            line_out['subject_display_code'] = '4'

    temp = {}
    if 'tmtaxsubj_en_tmtxtm' in line:
        temp['en'] = line['tmtaxsubj_en_tmtxtm'][0]
    if 'tmtaxsubj_fr_tmtxtm' in line:
        temp['fr'] = line['tmtaxsubj_fr_tmtxtm'][0]
    if temp:
        line_out['title'] = temp

    if 'tmtaxsubjcode_bi_tmtxtm' in line:
        line_out['subject_code'] = line['tmtaxsubjcode_bi_tmtxtm'][0]
        line_out['name'] = 'subject-{0}'.format(('000000'+line['tmtaxsubjcode_bi_tmtxtm'][0])[-6:])

    if 'tmtaxadminnotes_bi_tmtxts' in line:
        line_out['notes'] = {
            'en': line['tmtaxadminnotes_bi_tmtxts'][0],
            'fr': line['tmtaxadminnotes_bi_tmtxts'][0]
        }

    if 'tmtaxsubjoldcode_bi_tmtxtm' in line:
        line_out['subjectold_code'] = map(str.strip, line['tmtaxsubjoldcode_bi_tmtxtm'][0].split(';'))

    temp = {}
    if 'tmtaxatozalias_en_tmtxtm' in line:
        temp['en'] = line['tmtaxatozalias_en_tmtxtm'][0]
    if 'tmtaxatozalias_fr_tmtxtm' in line:
        temp['fr'] = line['tmtaxatozalias_fr_tmtxtm'][0]
    if temp:
        line_out['a_to_z_alias'] = temp
"""


print json.dumps(out)

