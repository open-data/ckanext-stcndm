__author__ = 'marc'

import sys
import json
import yaml
import datetime
import ckanapi


def listify(value):
    if isinstance(value, unicode):
        return filter(None, map(unicode.strip, value.split(';')))  # filter removes empty strings
    elif isinstance(value, list):
        return filter(None, map(unicode.strip, value[0].split(';')))
    else:
        return []


def code_lookup(old_field_name, data_set, choice_list):
    _temp = data_set[old_field_name]
    field_values = listify(_temp)
    codes = []
    for field_value in field_values:
        code = None
        for choice in choice_list:
            if choice['label']['en'].lower() == field_value.lower():
                if choice['value']:
                    code = choice['value']
        if not code:
            sys.stderr.write('imdb-{0}: weird {1} .{2}.{3}.\n'.format(line['productidnew_bi_strs'], old_field_name, _temp, field_value))
        else:
            codes.append(code)
    return codes

content_type_list = []
rc = ckanapi.RemoteCKAN('http://127.0.0.1:5000')
results = rc.action.package_search(
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
    if preset['preset_name'] == 'ndm_survey_participation':
        survey_participation_list = preset['values']['choices']
        if not survey_participation_list:
            raise ValueError('could not find survey participation preset')
    if preset['preset_name'] == 'ndm_survey_owner':
        survey_owner_list = preset['values']['choices']
        if not survey_owner_list:
            raise ValueError('could not find survey owner preset')
    if preset['preset_name'] == 'ndm_formats':
        format_list = preset['values']['choices']
        if not format_list:
            raise ValueError('could not find format preset')

rc = ckanapi.RemoteCKAN('http://ndmckanq1.stcpaz.statcan.gc.ca/zj/')
i = 0
n = 1
while i < n:
    query_results = rc.action.package_search(
        q='organization:maimdb',
        rows=1000,
        start=i*1000)
    i += 1
    n = query_results['count'] / 1000

    for line in query_results['results']:
        for e in line['extras']:
            line[e['key']] = e['value']

        line_out = {'owner_org': u'statcan',
                    'private': False,
                    'type': u'imdb'}

        if 'archived_bi_strs' in line:
            result = code_lookup('archived_bi_strs', line, archive_status_list)
            if result:
                line_out['archive_status_code'] = result[0]

        if 'collenddate_bi_strs' in line and line['collenddate_bi_strs']:
            line_out['collection_end_date'] = line['collenddate_bi_strs']

        if 'collmethod_en_txtm' in line:
            result = code_lookup('collmethod_en_txtm', line, collection_method_list)
            if result:
                line_out['collection_method_codes'] = result

        if 'collstartdate_bi_strs' in line and line['collstartdate_bi_strs']:
            line_out['collection_start_date'] = line['collstartdate_bi_strs']

        if 'conttype_en_txtm' in line:
            line_out['content_type_codes'] = ['2003']

        temp = {}
        if 'description_en_txts' in line and line['description_en_txts']:
            temp[u'en'] = line['description_en_txts']
        if 'description_fr_txts' in line and line['description_fr_txts']:
            temp[u'fr'] = line['description_fr_txts']
        if temp:
            line_out['notes'] = temp

        if 'featureweight_bi_ints' in line:
            line_out['feature_weight'] = line['featureweight_bi_ints']

        if 'extras_frccode_bi_strs' in line and line['extras_frccode_bi_strs']:
            line_out['frc'] = line['extras_frccode_bi_strs']

        if 'freqcode_bi_txtm' in line:
            # line_out['frequency_codes'] = [u'00{0}'.format(i)[-2:] for i in listify(line['freqcode_bi_txtm'])]
            result = listify(line['freqcode_bi_txtm'])
            if result:
                line_out['frequency_codes'] = result

        if 'imdbinstanceitem_bi_ints' in line:
            line_out['imdb_instance_item'] = line['imdbinstanceitem_bi_ints']

        if 'extras_imdbsurveyitem_bi_ints' in line:
            line_out['imdb_survey_item'] = line['extras_imdbsurveyitem_bi_ints']

        temp = {}
        if 'isplink_en_strs' in line and line['isplink_en_strs']:
            temp[u'en'] = line['isplink_en_strs']
        if 'isplink_fr_strs' in line and line['isplink_en_strs']:
            temp[u'fr'] = line['isplink_fr_strs']
        if temp:
            line_out['isp_url'] = temp

        temp = {}
        if 'keywordsuncon_en_txtm' in line:
            result = listify(line['keywordsuncon_en_txtm'])
            if result:
                temp[u'en'] = []
                for i in result:
                    while len(i) > 100:
                        temp[u'en'].append(i[:100])
                        i = i[100:]
        if 'keywordsuncon_fr_txtm' in line:
            result = listify(line['keywordsuncon_fr_txtm'])
            if result:
                temp[u'fr'] = []
                for i in result:
                    while len(i) > 100:
                        temp[u'fr'].append(i[:100])
                        i = i[100:]
        if temp:
            line_out['keywords'] = temp

        if 'levelsubjcode_bi_txtm' in line:
            result = listify(line['levelsubjcode_bi_txtm'])
            if result:
                line_out['level_subject_codes'] = result

        if 'productidnew_bi_strs' in line and line['productidnew_bi_strs']:
            line_out['product_id_new'] = line['productidnew_bi_strs']
            line_out['name'] = u'imdb-{0}'.format(line['productidnew_bi_strs'])

        temp = {}
        if 'questlink_en_strs' in line and line['questlink_en_strs']:
            temp[u'en'] = line['questlink_en_strs']
        if 'questlink_fr_strs' in line and line['questlink_fr_strs']:
            temp[u'fr'] = line['questlink_fr_strs']
        if temp:
            line_out['question_url'] = temp

        temp = {}
        if 'refperiod_en_txtm' in line:
            result = listify(line['refperiod_en_txtm'])
            if result:
                temp[u'en'] = []
                for i in result:
                    while len(i) > 100:
                        temp[u'en'].append(i[:100])
                        i = i[100:]
        if 'refperiod_fr_txtm' in line:
            result = listify(line['refperiod_fr_txtm'])
            if result:
                temp[u'fr'] = []
                for i in result:
                    while len(i) > 100:
                        temp[u'fr'].append(i[:100])
                        i = i[100:]
        if temp:
            line_out['reference_periods'] = temp

        if 'releasedate_bi_strs' in line:
            _temp = line['releasedate_bi_strs']
            try:
                datetime.datetime.strptime(_temp, '%Y-%m-%dT%H:%M')
            except ValueError:
                sys.stderr.write('imdb-{0}: Invalid release date .{1}.\n'.format(line['productidnew_bi_strs'], _temp))
                _temp = u'0001-01-01T08:30'
            line_out['release_date'] = _temp

        temp = {}
        if 'stcthesaurus_en_txtm' in line:
            result = listify(line['stcthesaurus_en_txtm'])
            if result:
                temp[u'en'] = result
        if 'stcthesaurus_fr_txtm' in line:
            result = listify(line['stcthesaurus_fr_txtm'])
            if result:
                temp[u'fr'] = result
        if temp:
            line_out['thesaurus'] = temp

        if 'statusf_en_strs' in line:
            result = code_lookup('statusf_en_strs', line, imdb_status_list)
            if result:
                line_out['imdb_status_code'] = result[0]

        if 'subjnewcode_bi_txtm' in line:
            result = listify(line['subjnewcode_bi_txtm'])
            if result:
                line_out['subject_codes'] = result

        temp = {}
        if 'surveylink_en_strs' in line and line['surveylink_en_strs']:
            temp[u'en'] = line['surveylink_en_strs']
        if 'surveylink_fr_strs' in line and line['surveylink_fr_strs']:
            temp[u'fr'] = line['surveylink_fr_strs']
        if temp:
            line_out['survey_url'] = temp

        if 'surveyparticipation_en_strs' in line:
            result = code_lookup('surveyparticipation_en_strs', line, survey_participation_list)
            if result:
                line_out['survey_participation_code'] = result[0]

        if 'survowner_en_strs' in line:
            result = code_lookup('survowner_en_strs', line, survey_owner_list)
            if result:
                line_out['survey_owner_code'] = result[0]

        temp = {}
        if 'title_en_txts' in line and line['title_en_txts']:
            temp[u'en'] = line['title_en_txts']
        if 'title_fr_txts' in line and line['title_fr_txts']:
            temp[u'fr'] = line['title_fr_txts']
        if temp:
            line_out['title'] = temp

        temp = {}
        if 'url_en_strs' in line and line['url_en_strs']:
            temp[u'en'] = line['url_en_strs']
        if 'url_fr_strs' in line and line['url_fr_strs']:
            temp[u'fr'] = line['url_fr_strs']
        if temp:
            line_out['url'] = temp

        if 'navsubjcodesemi' in line:
            result = listify(line['navsubjcodesemi'])
            if result:
                line_out['navigation_subject_codes'] = result

        if 'res_format' in line:
            result = code_lookup('res_format', line, format_list)
            if isinstance(result, list):
                line_out['format_codes'] = result
            else:
                raise ValueError('result .{0}. is not a list')

        if 'res_url' in line and line['res_url'][0]:
            line_out['resource_url'] = line['res_url'][0]

        print json.dumps(line_out)
