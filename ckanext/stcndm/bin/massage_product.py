import sys
import yaml
import ckanapi

__author__ = 'marc'


def in_and_def(key, a_dict):
    if key in a_dict and a_dict[key]:
        return True
    else:
        return False


def listify(value):
    if isinstance(value, unicode):
        return filter(None, map(unicode.strip, value.split(';')))  # filter removes empty strings
    elif isinstance(value, list):
        return filter(None, map(unicode.strip, value[0].split(';')))
    else:
        return []


def code_lookup(old_field_name, data_set, choice_list):
    temp = data_set[old_field_name]
    field_values = listify(temp)
    codes = []
    for field_value in field_values:
        code = None
        if '|' in field_value:
            (field_value, bogon) = field_value.split('|', 1)
        elif '/' in field_value:
            (field_value, bogon) = field_value.split('/', 1)
        for choice in choice_list:
            if choice[u'label'][u'en'].lower().strip() == field_value.lower().strip():
                if choice[u'value']:
                    code = choice[u'value']
        if not code:
            sys.stderr.write('{product_id}: weird {old_name} .{temp}.{field_value}.\n'.format(
                product_id=data_set[u'productidnew_bi_strs'],
                old_name=old_field_name,
                temp=temp, 
                field_value=field_value))
        else:
            codes.append(code)
    return codes


def do_product(data_set):
    product_out = {
        u'owner_org': u'statcan',
        u'private': False
    }

    temp = {}
    if in_and_def('adminnotes_bi_txts', data_set):
        temp[u'en'] = data_set[u'adminnotes_bi_txts']
        temp[u'fr'] = data_set[u'adminnotes_bi_txts']
    if temp:
        product_out[u'admin_notes'] = temp

    if in_and_def('archived_bi_strs', data_set):
        result = code_lookup('archived_bi_strs', data_set, archive_status_list)
        if result:
            product_out[u'archive_status_code'] = result[0]

    if in_and_def('archivedate_bi_txts', data_set):
        product_out[u'archive_date'] = data_set[u'archivedate_bi_txts']

    if in_and_def('arrayterminatedcode_bi_strs', data_set):
        product_out[u'array_terminated_code'] = data_set[u'arrayterminatedcode_bi_strs']

    if in_and_def('conttypecode_bi_txtm', data_set):
        result = listify(data_set[u'conttypecode_bi_txtm'])
        if result:
            product_out[u'content_type_codes'] = result

    if in_and_def('correcimplevelcode_bi_strs', data_set):
        product_out[u'correction_impact_level_code'] = data_set[u'correcimplevelcode_bi_strs']

    if in_and_def('correctionid_bi_strs', data_set):
        product_out[u'correction_id'] = data_set[u'correctionid_bi_strs']

    if in_and_def('correctiontypecode_bi_strm', data_set):
        result = listify(data_set[u'correctiontypecode_bi_strm'])
        if result:
            product_out[u'correction_type_codes'] = result

    temp = {}
    if in_and_def('correctnote_en_txtm', data_set):
        temp[u'en'] = data_set[u'correctnote_en_txtm']
    if in_and_def('correctnote_fr_txtm', data_set):
        temp[u'fr'] = data_set[u'correctnote_fr_txtm']
    if temp:
        product_out[u'correction_notes'] = temp

    if in_and_def('defaultviewid_bi_strs', data_set):
        product_out[u'default_view_id'] = data_set[u'defaultviewid_bi_strs']

    temp = {}
    if in_and_def('description_en_txts', data_set):
        temp[u'en'] = data_set[u'description_en_txts']
    if in_and_def('description_fr_txts', data_set):
        temp[u'fr'] = data_set[u'description_fr_txts']
    if temp:
        product_out[u'notes'] = temp

    temp = {}
    if in_and_def('dimmembers_en_txtm', data_set):
        result = listify(data_set[u'dimmembers_en_txtm'])
        if result:
            temp[u'en'] = result
    if in_and_def('dimmembers_fr_txtm', data_set):
        result = listify(data_set[u'dimmembers_fr_txtm'])
        if result:
            temp[u'fr'] = result
    if temp:
        product_out[u'dimension_members'] = temp

    if in_and_def('dispandtrack_bi_txtm', data_set):
        result = code_lookup('dispandtrack_bi_txtm', data_set, tracking_list)
        if result:
            product_out[u'tracking_codes'] = result

    temp = {}
    if in_and_def('doinum_en_strs', data_set):
        temp[u'en'] = data_set[u'doinum_en_strs']
    if in_and_def('doinum_fr_strs', data_set):
        temp[u'fr'] = data_set[u'doinum_fr_strs']
    if temp:
        product_out[u'digital_object_identifier'] = temp

    if in_and_def('extauthor_bi_txtm', data_set):
        result = listify(data_set[u'extauthor_bi_txtm'])
        if result:
            product_out[u'external_authors'] = result

    if in_and_def('featureweight_bi_ints', data_set):
        product_out[u'feature_weight'] = int(data_set[u'featureweight_bi_ints'])

    if in_and_def('frccode_bi_strs', data_set):
        product_out[u'frc'] = data_set[u'frccode_bi_strs']

    if in_and_def('freqcode_bi_txtm', data_set):
        result = listify(data_set[u'freqcode_bi_txtm'])
        if result:
            product_out[u'frequency_codes'] = result

    if in_and_def('geolevel_en_txtm', data_set):
        result = code_lookup('geolevel_en_txtm', data_set, geolevel_list)
        if result:
            product_out[u'geolevel_codes'] = result

    if in_and_def('hierarchyid_bi_strm', data_set):
        result = listify(data_set[u'hierarchyid_bi_strm'])
        if result:
            product_out[u'parent_product'] = result[0]

    if in_and_def('hierarchyid_bi_strs', data_set):
        result = listify(data_set[u'hierarchyid_bi_strs'])
        if result:
            product_out[u'parent_product'] = result[0]

    temp = {}
    if in_and_def('histnotes_en_txts', data_set):
        temp[u'en'] = data_set[u'histnotes_en_txts']
    if in_and_def('histnotes_fr_txts', data_set):
        temp[u'fr'] = data_set[u'histnotes_fr_txts']
    if temp:
        product_out[u'history_notes'] = temp

    if in_and_def('intauthor_bi_txtm', data_set):
        result = listify(data_set[u'intauthor_bi_txtm'])
        if result:
            product_out[u'internal_authors'] = result

    if in_and_def('interncontactname_bi_txts', data_set):
        result = listify(data_set[u'interncontactname_bi_txts'])
        if result:
            product_out[u'internal_contacts'] = result

    temp = {}
    if in_and_def('keywordsuncon_en_txtm', data_set):
        result = listify(data_set[u'keywordsuncon_en_txtm'])
        if result:
            temp[u'en'] = result
    if in_and_def('keywordsuncon_fr_txtm', data_set):
        result = listify(data_set[u'keywordsuncon_fr_txtm'])
        if result:
            temp[u'fr'] = result
    if temp:
        product_out[u'keywords'] = temp

    if in_and_def('lastpublishstatus_en_strs', data_set):
        result = code_lookup('lastpublishstatus_en_strs', data_set, publish_list)
        if result:
            product_out[u'last_publish_status_code'] = result[0]

    if in_and_def('legacydate_bi_txts', data_set):
        product_out[u'legacy_date'] = data_set[u'legacydate_bi_txts']

    if in_and_def('license_id', data_set):
        product_out[u'license_id'] = data_set[u'license_id']

    if in_and_def('license_title', data_set):
        product_out[u'license_title'] = data_set[u'license_title']

    if in_and_def('license_url', data_set):
        product_out[u'license_url'] = data_set[u'license_url']

    if in_and_def('pecode_bi_strs', data_set):
        product_out[u'pe_code'] = data_set[u'pecode_bi_strs']

    if in_and_def('price_bi_txts', data_set):
        product_out[u'price'] = data_set[u'price_bi_txts']

    temp = {}
    if in_and_def('pricenote_en_txts', data_set):
        temp[u'en'] = data_set[u'pricenote_en_txts']
    if in_and_def('pricenote_fr_txts', data_set):
        temp[u'fr'] = data_set[u'pricenote_fr_txts']
    if temp:
        product_out[u'price_notes'] = temp

    if in_and_def('productidnew_bi_strs', data_set):
        product_out[u'product_id_new'] = data_set[u'productidnew_bi_strs']

    if in_and_def('productidold_bi_strs', data_set):
        product_out[u'product_id_old'] = data_set[u'productidold_bi_strs']

    if in_and_def('producttypecode_bi_strs', data_set):
        product_out[u'product_type_code'] = data_set[u'producttypecode_bi_strs']

    if in_and_def('pubyear_bi_intm', data_set):
        product_out[u'publication_year'] = data_set[u'pubyear_bi_intm']

    if in_and_def('related_bi_strm', data_set):
        result = listify(data_set[u'related_bi_strm'])
        if result:
            product_out[u'related_products'] = result

    temp = {}
    if in_and_def('relatedcontent_en_txtm', data_set):
        result = listify(data_set[u'relatedcontent_en_txtm'])
        if result:
            temp[u'en'] = result
    if in_and_def('relatedcontent_fr_txtm', data_set):
        result = listify(data_set[u'relatedcontent_fr_txtm'])
        if result:
            temp[u'fr'] = result
    if temp:
        product_out[u'related_content'] = temp

    if in_and_def('replaces_bi_strm', data_set):
        result = listify(data_set[u'replaces_bi_strm'])
        if result:
            product_out[u'replaced_products'] = result

    if in_and_def('replaces_bi_txtm', data_set):
        result = listify(data_set[u'replaces_bi_txtm'])
        if result:
            product_out[u'replaced_products'] = result

    if in_and_def('sourcecode_bi_txtm', data_set):
        result = listify(data_set[u'sourcecode_bi_txtm'])
        if result:
            product_out[u'survey_source_codes'] = result

    if in_and_def('specificgeocode_bi_txtm', data_set):
        result = listify(data_set[u'specificgeocode_bi_txtm'])
        if result:
            product_out[u'geodescriptor_codes'] = result

    if in_and_def('statusfcode_bi_strs', data_set):
        result = listify(data_set[u'statusfcode_bi_strs'])
        if result:
            product_out[u'status_codes'] = result

    temp = {}
    if in_and_def('stcthesaurus_en_txtm', data_set):
        result = listify(data_set[u'stcthesaurus_en_txtm'])
        if result:
            temp[u'en'] = result
    if in_and_def('stcthesaurus_fr_txtm', data_set):
        result = listify(data_set[u'stcthesaurus_fr_txtm'])
        if result:
            temp[u'fr'] = result
    if temp:
        product_out[u'thesaurus'] = temp

    if in_and_def('subjnewcode_bi_txtm', data_set):
        result = listify(data_set[u'subjnewcode_bi_txtm'])
        if result:
            product_out[u'subject_codes'] = result

    if in_and_def('subjoldcode_bi_txtm', data_set):
        result = listify(data_set[u'subjoldcode_bi_txtm'])
        if result:
            product_out[u'subjectold_codes'] = result

    temp = {}
    if in_and_def('title_en_txts', data_set):
        temp[u'en'] = data_set[u'title_en_txts']
    if in_and_def('title_fr_txts', data_set):
        temp[u'fr'] = data_set[u'title_fr_txts']
    if temp:
        product_out[u'title'] = temp

    if in_and_def('volumeandnum_bi_txts', data_set):
        product_out[u'volume_and_number'] = data_set[u'volumeandnum_bi_txts']

    return product_out


def do_format(data_set):
    format_out = {
        u'owner_org': u'statcan',
        u'private': False,
        u'type': u'format',
        u'name': (u'format-{0}_{1}'.format(
            data_set[u'productidnew_bi_strs'],
            data_set[u'formatcode_bi_txtm'])).lower(),
        u'title': (u'format-{0}_{1}'.format(
            data_set[u'productidnew_bi_strs'],
            data_set[u'formatcode_bi_txtm'])).lower()
    }

    if in_and_def('display_bi_txtm', data_set):
        result = code_lookup('display_bi_txtm', data_set, display_list)
        if result:
            format_out[u'display_code'] = result[0]

    if in_and_def('formatcode_bi_txtm', data_set):
        format_out[u'format_code'] = data_set[u'formatcode_bi_txtm']
    # else:
    #     sys.stderr.write(u'{0} missing format\n'.format(data_set[u'name']))
        # return None

    temp = {}
    if in_and_def('isbnnum_en_strs', data_set):
        temp[u'en'] = data_set[u'isbnnum_en_strs']
    if in_and_def('isbnnum_fr_strs', data_set):
        temp[u'fr'] = data_set[u'isbnnum_fr_strs']
    if temp:
        format_out[u'isbn_number'] = temp

    temp = {}
    if in_and_def('issnnum_en_strs', data_set):
        temp[u'en'] = data_set[u'issnnum_en_strs']
    if in_and_def('issnnum_fr_strs', data_set):
        temp[u'fr'] = data_set[u'issnnum_fr_strs']
    if temp:
        format_out[u'issn_number'] = temp

    local_temp = {}
    if in_and_def('url_en_strs', data_set):
        local_temp[u'en'] = data_set[u'url_en_strs']
    if in_and_def('url_fr_strs', data_set):
        local_temp[u'fr'] = data_set[u'url_fr_strs']
    if local_temp:
        format_out[u'url'] = local_temp

    return format_out


def do_release(data_set):

    release_out = {
        u'owner_org': u'statcan',
        u'private': False,
        u'type': u'release',
        u'is_correction': '0',
        u'name': (u'release-{0}_{1}'.format(
            data_set[u'productidnew_bi_strs'],
            data_set[u'releasedate_bi_strs'])).lower(),
        u'title': (u'release-{0}_{1}'.format(
            data_set[u'productidnew_bi_strs'],
            data_set[u'releasedate_bi_strs'])).lower()
    }

    if in_and_def('releasedate_bi_strs', data_set):
        release_out[u'release_date'] = data_set[u'releasedate_bi_strs']

    temp = {}
    if in_and_def('refperiod_en_txtm', data_set):
        temp[u'en'] = data_set['refperiod_en_txtm']
    if in_and_def('refperiod_fr_txtm', data_set):
        temp[u'fr'] = data_set['refperiod_fr_txtm']
    if temp:
        release_out[u'reference_period'] = temp

    if in_and_def('lastpublishstatuscode_bi_strs', data_set):
        release_out[u'publish_status_code'] = data_set[u'lastpublishstatuscode_bi_strs']

    if in_and_def('issueno_bi_strs', data_set):
        release_out[u'issue_number'] = data_set[u'issueno_bi_strs']

    if in_and_def('hierarchyid_bi_strm', data_set):
        result = listify(data_set[u'hierarchyid_bi_strm'])
        if result:
            release_out[u'parent_product'] = result[0]

    if in_and_def('hierarchyid_bi_strs', data_set):
        result = listify(data_set[u'hierarchyid_bi_strs'])
        if result:
            release_out[u'parent_product'] = result[0]

    return release_out

f = open('../schemas/presets.yaml')
presetMap = yaml.safe_load(f)
f.close()

archive_status_list = []
display_list = []
publish_list = []
status_list = []
tracking_list = []

for preset in presetMap[u'presets']:
    if preset[u'preset_name'] == 'ndm_archive_status':
        archive_status_list = preset[u'values'][u'choices']
        if not archive_status_list:
            raise ValueError('could not find archive status preset')
    if preset[u'preset_name'] == 'ndm_collection_methods':
        collection_method_list = preset[u'values'][u'choices']
        if not collection_method_list:
            raise ValueError('could not find collection method preset')
    if preset[u'preset_name'] == 'ndm_survey_status':
        survey_status_list = preset[u'values'][u'choices']
        if not survey_status_list:
            raise ValueError('could not find survey status preset')
    if preset[u'preset_name'] == 'ndm_survey_participation':
        survey_participation_list = preset[u'values'][u'choices']
        if not survey_participation_list:
            raise ValueError('could not find survey participation preset')
    if preset[u'preset_name'] == 'ndm_survey_owner':
        survey_owner_list = preset[u'values'][u'choices']
        if not survey_owner_list:
            raise ValueError('could not find survey owner preset')
    # if preset[u'preset_name'] == 'ndm_format':
    #     format_list = preset[u'values'][u'choices']
    #     if not format_list:
    #         raise ValueError('could not find format preset')
    if preset[u'preset_name'] == 'ndm_tracking':
        tracking_list = preset[u'values'][u'choices']
        if not tracking_list:
            raise ValueError('could not find tracking preset')
    if preset[u'preset_name'] == 'ndm_status':
        status_list = preset[u'values'][u'choices']
        if not status_list:
            raise ValueError('could not find ndm_status preset')
    if preset[u'preset_name'] == 'ndm_display':
        display_list = preset[u'values'][u'choices']
        if not display_list:
            raise ValueError('could not find display preset')
    if preset[u'preset_name'] == 'ndm_publish_status':
        publish_list = preset[u'values'][u'choices']
        if not publish_list:
            raise ValueError('could not find display preset')

geolevel_list = []
rc = ckanapi.RemoteCKAN('http://127.0.0.1:5000')
results = rc.action.package_search(
    q='type:codeset',
    rows=1000)
for codeset in results[u'results']:
    if codeset[u'codeset_type'] == 'geolevel':
        geolevel_list.append({
            'label': codeset[u'title'],
            'value': codeset[u'codeset_value']
        })
