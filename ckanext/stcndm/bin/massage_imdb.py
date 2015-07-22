__author__ = 'marc'

import sys
import json
import yaml
import ckanapi


def listify(value):
    if isinstance(value, unicode):
        return map(unicode.strip, value.split(';'))
    elif isinstance(value, list):
        return map(unicode.strip, value[0].split(';'))
    else:
        return []


def code_lookup(old_field_name, data_set, choice_list):
    _temp = data_set[old_field_name]
    field_values = listify(_temp)
    codes = []
    for field_value in field_values:
        code = None
        for choice in choice_list:
            if choice['label']['en'] == field_value:
                if choice['value']:
                    code = choice['value']
        if not code:
            print 'weird {0} .{1}.{2}'.format(old_field_name, data_set[old_field_name], field_value)
        else:
            codes.append(code)
    return codes

content_type_list = []
lc = ckanapi.RemoteCKAN('http://127.0.0.1:5000')
results = lc.action.package_search(
    q='type:codeset',
    rows=1000)

raw_codesets = results['results']
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
        if not archive_status_list:
            raise ValueError('could not find archive status preset')
    if preset['preset_name'] == 'ndm_collection_methods':
        collection_method_list = preset['values']['choices']
        if not collection_method_list:
            raise ValueError('could not find collection method preset')
    if preset['preset_name'] == 'ndm_imdb_status':
        imdb_status_list = preset['values']['choices']
        if not imdb_status_list:
            raise ValueError('could not find imdb status preset')

lines = json.load(sys.stdin)
out = []
for line in lines:
    line_out = {'owner_org': 'statcan', 'private': False}

    if 'archived_bi_strs' in line:
        result = code_lookup('archived_bi_strs', line, archive_status_list)
        if result:
            line_out['archive_status_code'] = result[0]

    if 'collenddate_bi_strs' in line:
        line_out['collection_end_date'] = line['collenddate_bi_strs']

    if 'collmethod_en_txtm' in line:
        result = code_lookup('collmethod_en_txtm', line, collection_method_list)
        if result:
            line_out['collection_method_codes'] = result

    if 'collstartdate_bi_strs' in line:
        line_out['collection_start_date'] = line['collstartdate_bi_strs']

    if 'conttype_en_txtm' in line:
        line_out['content_type_codes'] = ['03']

    temp = {}
    if 'description_en_txts' in line:
        temp['en'] = line['description_en_txts']
    if 'description_fr_txts' in line:
        temp['fr'] = line['description_fr_txts']
    if temp:
        line_out['description'] = temp

    if 'featureweight_bi_ints' in line:
        line_out['feature_weight'] = line['featureweight_bi_ints']

    if 'extras_frccode_bi_strs' in line:
        line_out['frc'] = line['extras_frccode_bi_strs'][0]

    if 'freqcode_bi_txtm' in line:
        line_out['frequency_codes'] = [u'00{0}'.format(i)[-2:] for i in listify(line['freqcode_bi_txtm'])]

    if 'imdbinstanceitem_bi_ints' in line:
        line_out['imdb_instance_item'] = line['imdbinstanceitem_bi_ints']

    if 'extras_imdbsurveyitem_bi_ints' in line:
        line_out['imdb_survey_item'] = line['extras_imdbsurveyitem_bi_ints']

    temp = {}
    if 'keywordsuncon_en_txtm' in line:
        temp['en'] = listify(line['keywordsuncon_en_txtm'])
    if 'keywordsuncon_fr_txtm' in line:
        temp['fr'] = listify(line['keywordsuncon_fr_txtm'])
    if temp:
        line_out['keywords'] = temp

    if 'levelsubjcode_bi_txtm' in line:
        line_out['level_subject_code'] = line['levelsubjcode_bi_txtm']

    if 'productidnew_bi_strs' in line:
        line_out['product_id_new'] = line['productidnew_bi_strs']

    temp = {}
    if 'questlink_en_strs' in line:
        temp['en'] = line['questlink_en_strs']
    if 'questlink_fr_strs' in line:
        temp['fr'] = line['questlink_fr_strs']
    if temp:
        line_out['question_url'] = temp

    temp = {}
    if 'refperiod_en_txtm' in line:
        temp['en'] = line['refperiod_en_txtm']
    if 'refperiod_fr_txtm' in line:
        temp['fr'] = line['refperiod_fr_txtm']
    if temp:
        line_out['reference_period'] = temp

    if 'releasedate_bi_strs' in line:
        line_out['release_date'] = line['releasedate_bi_strs']

    if 'statusf_en_strs' in line:
        result = code_lookup('statusf_en_strs', line, imdb_status_list)
        if result:
            line_out['imdb_status_code'] = result[0]



    print json.dumps(line_out)

#print json.dumps(out)

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
