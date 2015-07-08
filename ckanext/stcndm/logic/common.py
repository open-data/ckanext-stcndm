# coding=utf-8
__author__ = 'Statistics Canada'

import ckan.logic as logic
import ckan.plugins.toolkit as toolkit
import ckanext.stcndm.logic.helpers as helpers
import json
import datetime

_get_or_bust = logic.get_or_bust
# noinspection PyUnresolvedReferences
_get_action = toolkit.get_action
# noinspection PyUnresolvedReferences
_ValidationError = toolkit.ValidationError
# noinspection PyUnresolvedReferences
_NotFound = toolkit.ObjectNotFound
# noinspection PyUnresolvedReferences
_NotAuthorized = toolkit.NotAuthorized


@logic.side_effect_free
def get_next_product_id(context, data_dict):
    # noinspection PyUnresolvedReferences
    """
    Returns the next available ProductId (without registering it).

    :param parentProductId: Cube Id
    :type parentProductId: str
    :param productType:
    :type productType: str

    :return: next available ProductId
    :rtype: str

    :raises ValidationError, ObjectNotFound
    """

    product_id = _get_or_bust(data_dict, 'parentProductId')
    data_dict['productId'] = product_id
    # TODO: we need to standardize these. This is a result of swapping everything to java-style params

    if not len(str(product_id)) == 8:
        raise _ValidationError('invalid ParentProductId length')

    product_type = _get_or_bust(data_dict, 'productType')

    _get_action('ndm_get_cube')(context, data_dict)  # testing for existance of cubeid

    subject_code = str(product_id)[:2]
    # TODO Do we want to rely on the subject_code in the cube dict? probably not...
    # TODO this is actually going to be a problem because cubes do not have good data in subj
    sequence_id = str(product_id)[4:8]

    product_family = '{subject_code}{product_type}{sequence_id}'.format(subject_code=subject_code,
                                                                        product_type=product_type,
                                                                        sequence_id=sequence_id)

    query = {'q': 'extras_productidnew_bi_strs:{product_family}*'.format(product_family=product_family),
             'sort': 'extras_productidnew_bi_strs desc'}

    response = _get_action('package_search')(context, query)

    product_id_new = "{subject_code}{product_type}{sequence_id}01".format(subject_code=subject_code,
                                                                          product_type=product_type,
                                                                          sequence_id=sequence_id)
    try:
        for extra in response['results'][0]['extras']:
            if extra['key'] == 'productidnew_bi_strs':
                product_id_response = extra['value']
                # TODO: implement reusing unused IDs
                if product_id_response.endswith('99'):
                    raise _ValidationError(
                        'All Product IDs have been used. Reusing IDs is in development.')
                else:
                    try:
                        product_id_new = str(int(product_id_response) + 1)
                    except ValueError:
                        raise _ValidationError('Invalid product_id {0}'.format(product_id_response))
    except KeyError:
        pass

    return product_id_new


def get_product(context, data_dict):  # this one is for external use. just use package_show internally
    # noinspection PyUnresolvedReferences
    """Return a JSON dict representation of a product, given a ProductId, if it exists.

    :param productId: product id (i.e. 2112002604)
    :type productId: str
    :param fields: desired output fields. (i.e. "title_en_txts,title_fr_txts,ProductIdnew_bi_strs") Default: *
    :type fields: str

    :return: requested product fields and values
    :rtype: list of dict

    :raises ObjectNotFound, ValidationError
    """

    product_id = _get_or_bust(data_dict, 'productId')

    desired_fields_list = []
    if 'fields' in data_dict:
        desired_fields = data_dict['fields']
        for field in desired_fields.split(','):
            desired_fields_list.append(field)

    q = {'q': 'extras_productidnew_bi_strs:{product_id}'.format(product_id=product_id)}

    result = _get_action('package_search')(context, q)

    count = result['count']
    if count == 0:
        raise _NotFound('product not found')
    #   removed to allow for finding more than one product with same productid_new
    #    elif count > 1:
    #        raise toolkit.Invalid('More than one product with given productId found')
    #    else:
    output = []
    for a_result in result['results']:
        an_output = {}
        extras = a_result['extras']
        for extra in extras:
            if not (desired_fields_list and extra['key'] not in desired_fields_list):
                an_output[extra['key']] = extra['value']
        output.append(an_output)
    return output


@logic.side_effect_free
def get_field_list(context, data_dict):
    # noinspection PyUnresolvedReferences
    """
    Return a list of all fields for a given org (based on the contents of the maschema organization).

    Used for determining which fields should be used when creating new records.

    :param org: Organization name (i.e. maprimary)
    :type org: string

    :return: list of all fields in a given organization based on the maschema organization.
    :rtype:  list of strings

    :raises
    """

    # TODO: Services which use this should possibly rely on get_fielddict instead, since it

    org = _get_or_bust(data_dict, 'org')

    field_list_dict = _get_action('package_search')(context, {
        'q': 'extras_tmregorg_bi_tmtxtm:{org}'.format(org=org),
        'rows': 100
    })

    field_list = []

    for field in field_list_dict['results']:
        field_list.append(field['name'])

    output = {'fields': field_list}

    return output


# noinspection PyUnusedLocal
@logic.side_effect_free
def get_product_type(context, data_dict):
    # noinspection PyUnresolvedReferences
    """Return the French and English titles for the given product_type_code.

    :param productType: Product Type Code (i.e. '10') or '*' to receive a list of all product_types
    :type productType str

    :return: English, French and code values for given product_type
    :rtype: dict

    :raises ValidationError
    """

    product_types = {  # TODO: these should be in the dropdown menu org in ckan until we set up schemas properly
        '10': {
            'en': u'Cube',
            'fr': u'Cube'
        },
        '11': {
            'en': u'Table',
            'fr': u'Tableau'
        },
        '12': {
            'en': u'Indicator',
            'fr': u'Indicateur'
        },
        '13': {
            'en': u'Chart',
            'fr': u'Graphique'
        },
        '14': {
            'en': u'Map',
            'fr': u'Carte'
        },
        '20': {
            'en': u'Analytical Product',
            'fr': u'Produit Analytique'
        },
        '21': {
            'en': u'Video',
            'fr': u'Vidéo'
        },
        '22': {
            'en': u'Conference',
            'fr': u'Conférence'
        },
        '23': {
            'en': u'Service',
            'fr': u'Service'
        },
        '24': {
            'en': u'Daily',
            'fr': u'Quotidien'
        },
        '25': {
            'en': u'Public use microdata files (PUMFs)',
            'fr': u'Les fichiers de microdonnées à grande diffusion (FMGD)'
        },
        '26': {
            'en': u'Publications with repeating titles (Generic)',
            'fr': u'Publications avec des titres répétitifs (générique)'
        },
    }
    product_type = _get_or_bust(data_dict, 'productType')

    try:
        output = {'producttypecode_bi_strs': product_type,
                  'producttype_en_strs': product_types[product_type]['en'],
                  'producttype_fr_strs': product_types[product_type]['fr']}
    except KeyError:
        if product_type == '*':
            return product_types
        raise logic.ValidationError('productType: \'{0}\' not valid'.format(product_type))

    return output


# noinspection PyUnusedLocal
@logic.side_effect_free
def get_last_publish_status(context, data_dict):
    # noinspection PyUnresolvedReferences
    """Return the French and English values for the given lastpublishstatuscode.

    :param lastPublishStatusCode: Publishing Status Code (i.e. '10')
    :type lastPublishStatusCode str

    :return: English, French and code values for given lastpublishstatuscode
    :rtype: dict

    :raises ValidationError
    """

    publish_statuses = {
        '0': {
            'en': u'None',
            'fr': u'Aucune'
        },
        '2': {
            'en': u'Draft',
            'fr': u'Ébauche'
        },
        '4': {
            'en': u'Working Copy',
            'fr': u'Copie de travail'
        },
        '6': {
            'en': u'Authorized',
            'fr': u'Autorisé'
        },
        '8': {
            'en': u'Verified',
            'fr': u'Vérifié'
        },
        '10': {
            'en': u'Loaded',
            'fr': u'Chargé'
        },
        '12': {
            'en': u'Released',
            'fr': u'Diffusé'
        },
        '99': {
            'en': u'Frozen',
            'fr': u'Figé'
        }
    }

    publish_status = _get_or_bust(data_dict, 'lastPublishStatusCode')
    try:
        output = {'lastpublishstatuscode_bi_strs': publish_status,
                  'lastpublishstatus_en_strs': publish_statuses[publish_status]['en'],
                  'lastpublishstatus_fr_strs': publish_statuses[publish_status]['fr']}
    except KeyError:
        raise logic.ValidationError('lastPublishStatusCode: \'{0}\' invalid'.format(publish_status))

    return output


# noinspection PyUnusedLocal
@logic.side_effect_free
def get_format_description(context, data_dict):
    # noinspection PyUnresolvedReferences
    """Return the French and English values for the given formatCode.

        :param formatCode: Format Code (i.e. '10')
        :type formatCode str

        :return: English, French and code values for given formatCode
        :rtype: dict

        :raises ValidationError
        """

    format_codes = {
        '2': {
            'en': u'Database',
            'fr': u'Base de données'
        },
        '3': {
            'en': u'CD-ROM',
            'fr': u'CD-ROM'
        },
        '4': {
            'en': u'Diskette',
            'fr': u'Disquette'
        },
        '5': {
            'en': u'Fax/email',
            'fr': u'Télécopieur'
        },
        '8': {
            'en': u'PDF',
            'fr': u'PDF'
        },
        '10': {
            'en': u'Microfiche',
            'fr': u'Microfiche'
        },
        '12': {
            'en': u'Paper',
            'fr': u'Imprimé'
        },
        '13': {
            'en': u'Symposium/Workshop',
            'fr': u'Symposium/Atelier'
        },
        '14': {
            'en': u'Tape/Cassette',
            'fr': u'Bande magnétique/Cassette'
        },
        '15': {
            'en': u'DVD',
            'fr': u'DVD'
        },
        '17': {
            'en': u'HTML',
            'fr': u'HTML'
        },
        '18': {
            'en': u'Video',
            'fr': u'Vidéo'
        },
        '19': {
            'en': u'ETF',
            'fr': u'ETF'
        },
    }

    format_code = _get_or_bust(data_dict, 'formatCode')
    try:
        output = {'formatcode_bi_txtm': format_code,
                  'format_en_txtm': format_codes[format_code]['en'],
                  'format_fr_txtm': format_codes[format_code]['fr']}
    except KeyError:
        raise logic.ValidationError('formatCode \'{0}\' invalid'.format(format_code))

    return output


@logic.side_effect_free
def get_upcoming_releases(context, data_dict):
    # noinspection PyUnresolvedReferences
    """
    Return all records with a lastpublishstatuscode of Verified (8) and a release date between the two parameters.

    :param startDate: Beginning of date range
    :param endDate: End of date range

    :return: productId, issueno, correctionid, French refperiod, English refperiod, releasedate for each matching record
    :rtype: list of dicts
    """
    # TODO: date validation? anything else?

    start_date = _get_or_bust(data_dict, 'startDate')
    end_date = _get_or_bust(data_dict, 'endDate')

    q = {'q': 'releasedate_bi_strs:[{startDate}:00Z TO {endDate}:00Z] AND lastpublishstatuscode_bi_strs:8'.format(
        startDate=start_date,
        endDate=end_date),
        'rows': 500}

    result = _get_action('package_search')(context, q)

    count = result['count']

    if count == 0:
        raise _NotFound
    else:
        desired_extras = ['productidnew_bi_strs',
                          'issueno_bi_strs',
                          'correctionidcode_bi_strs',
                          'refperiod_en_txtm',
                          'refperiod_fr_txtm',
                          'releasedate_bi_strs',
                          'url_en_strs',
                          'url_fr_strs',
                          'producttypecode_bi_strs',
                          'lastpublishstatuscode_bi_strs']

        output = []

        for result in result['results']:
            result_dict = {}
            for extra in result['extras']:
                if extra['key'] in desired_extras:
                    result_dict[extra['key']] = extra['value'] or ''
            output.append(result_dict)

        return {'count': count, 'results': output}


def get_derived_product_list(context, data_dict):
    # noinspection PyUnresolvedReferences
    """
    Return a dict with all ProductIDs and French/English titles that are associated with a given SubjectCode and
    ProductType.

    Note that this relies on the subjnewcode_bi_strs field rather than the subject code in the cubeid.

    :param parentProductId: cube id
    :type parentProductId: str
    :param productType: two-digit producttype code
    :type productType: str

    :return: registered cubes for the SubjectCode and their French/English titles
    :rtype: list of dicts
    """

    product_id = _get_or_bust(data_dict, 'parentProductId')
    product_type = _get_or_bust(data_dict, 'productType')
    # if product_type not in ['10', '11', '12', '13', '14', ]

    subject_code = product_id[:2]
    sequence_id = product_id[-4:]

    q = 'productidnew_bi_strs:{subjectcode}??{seqid}* AND producttypecode_bi_strs:{producttype}'.format(
        subjectcode=subject_code,
        seqid=sequence_id,
        producttype=product_type)
    query = {'q': q, 'rows': '1000'}

    response = _get_action('package_search')(context, query)

    # TODO: raise error if the cube cannot be located.

    output = []

    for result in response['results']:
        result_dict = {}
        for extra in result['extras']:
            if extra['key'] == 'productidnew_bi_strs':
                result_dict['productidnew_bi_strs'] = extra['value']
            elif extra['key'] == 'title_en_txts':
                result_dict['title_en_txts'] = extra['value']
            elif extra['key'] == 'title_fr_txts':
                result_dict['title_fr_txts'] = extra['value']

        output.append(result_dict)

    return output


# noinspection PyUnusedLocal
def get_drop_downs(context, data_dict):
    # noinspection PyUnresolvedReferences
    """
    Return a dict containing all dropdown options for all fields in a given org.

    :param owner_org: organization name
    :type owner_org: str

    :return:
    :rtype: dict of lists of dicts
    """

    q = 'zckownerorg_bi_strs:tmshortlist'

    query = {'q': q, 'rows': '1000'}

    response = _get_action('package_search')(context, query)

    output_dict = {}

    for result in response['results']:
        result_dict = {}

        for extra in result['extras']:
            result_dict[extra['key']] = extra['value']

        field_name = result_dict['tmdroplfld_bi_tmtxtm'][7:]  # Stripping off "extras_"

        # check field_name to determine how many fields to return for this field
        if field_name == 'dispandtrack_bi_txtm':
            split_values = [result_dict['tmdroplopt_bi_tmtxtm']]  # create single element list
        elif field_name == 'geolevel_en_txtm':
            split_values = result_dict['tmdroplopt_bi_tmtxtm'].split('|')[:2]  # don't send the code
        else:
            split_values = result_dict['tmdroplopt_bi_tmtxtm'].split('|')

        value_dict = {}

        # This is a bit annoying but required with how dropdown org stores
        # pipe-delimited values in inconsistent order depending on the number
        # of values (en, fr, bi) for each base field
        if len(split_values) == 3:
            value_dict['en'] = split_values[0].strip()
            value_dict['fr'] = split_values[1].strip()
            value_dict['bi'] = split_values[2].strip()
        elif len(split_values) == 2:
            value_dict['en'] = split_values[0].strip()
            value_dict['fr'] = split_values[1].strip()
        elif len(split_values) == 1:
            value_dict['bi'] = split_values[0].strip()

        values = {'text': result_dict['tmdroplopt_bi_tmtxtm'],
                  'value': json.dumps(value_dict)}

        try:
            output_dict[field_name].append(values)
        except KeyError:
            output_dict[field_name] = [values]

    for key in output_dict:
        output_dict[key].sort()
        output_dict[key] = [{"text": "", "value": ""}] + output_dict[key]

    return output_dict


@logic.side_effect_free
def get_autocomplete(context, data_dict):
    # noinspection PyUnresolvedReferences
    """
    Return a list of datasets (packages) that match a string.

    Datasets with names or titles that contain the query string will be
    returned.

    This action implements business logic to handle which fields should be returned for which actions.

    :param q: query string
    :type q: str
    :param fieldName: name of field for autocomplete
    :type fieldName: str

    :return: English, French, code and type values for given query
    :rtype: List of dicts
    """

    query = _get_or_bust(data_dict, 'q')
    field_name = _get_or_bust(data_dict, 'fieldName')
    limit = data_dict.get('limit', 100)
    sort_field = None

    if field_name not in ['subjnew_en_txtm', 'dimgroup_en_txtm', 'source_en_txtm', 'specificgeo_en_txtm']:
        raise _ValidationError('Invalid fieldName')

    query_split = query.replace('/', '').split()
    query = ' '.join([word + '*' for word in query_split])

    if field_name == 'subjnew_en_txtm':
        data_dict = {'q': u'tmtaxsubj_autotext:({query})'.format(query=query)}
        output_dict = {'tmtaxsubj_en_tmtxtm': 'subjnew_en_txtm',
                       'tmtaxsubj_fr_tmtxtm': 'subjnew_fr_txtm',
                       'tmtaxsubjcode_bi_tmtxtm': 'subjnewcode_bi_txtm',
                       'tmtaxdisp_en_tmtxtm': 'subjnewcode_bi_txtm'}
        sort_field = 'subjnewcode_bi_txtm'

    elif field_name == 'dimgroup_en_txtm':
        data_dict = {'q': u'tmdimen_autotext:({query})'.format(query=query)}
        output_dict = {'tmdimenalias_bi_tmtxtm': 'dimalias_en_txtm',
                       'tmdimentext_en_tmtxtm': 'dimgroup_en_txtm',
                       'tmdimentext_fr_tmtxtm': 'dimgroup_fr_txtm',
                       'tmdimencode_bi_tmtxtm': 'dimgroupcode_bi_txtm'}
        sort_field = None

    elif field_name == 'source_en_txtm':
        data_dict = {'q': u'source_autotext:({query})'.format(query=query), 'fq': 'zckownerorg_bi_strs:maimdb'}
        output_dict = {'title_en_txts': 'source_en_txtm',
                       'title_fr_txts': 'source_fr_txtm',
                       'productidnew_bi_strs': 'sourcecode_bi_txtm'}
        sort_field = None

    elif field_name == 'specificgeo_en_txtm':
        data_dict = {'q': u'tmsgc_autotext:({query})'.format(query=query)}
        output_dict = {'tmsgcname_en_tmtxtm': 'specificgeo_en_txtm',
                       'tmsgcname_fr_tmtxtm': 'specificgeo_fr_txtm',
                       'tmsgcspecificcode_bi_tmtxtm': 'specificgeocode_bi_txtm'}
        sort_field = None

    data_dict['rows'] = limit  # limit the number of returned rows
    response = _get_action('package_search')(context, data_dict)

    output_list = []

    for result in response['results']:
        result_dict = {}
        result_list = []

        for extra in result['extras']:
            if extra['key'] in output_dict:
                result_dict[output_dict[extra['key']]] = extra['value']

                result_list.append(extra['value'])

        output_list.append({'value': ' | '.join(result_list),
                            'key': json.dumps(result_dict),  # TODO: I think these are backwards (key should be value)
                            'ord': result_dict.get(sort_field,
                                                   None)})  # but it's an issue with the autocomplete js module

    # sort returned list based on field name (if sort field specified)
    if sort_field:
        output_list = sorted(output_list, key=lambda k: k['ord'])

    return output_list[:limit]


@logic.side_effect_free
def get_schema(context, data_dict):
    # noinspection PyUnresolvedReferences
    """
    Return a dict containing the field mappings for the fields for the given organization, as well as the
    pkg_dict containing the ordered extras.

    :param org: organization name
    :type org: str
    :param dataset: dataset name
    :type dataset: str

    :return: Dict
    """

    org = _get_or_bust(data_dict, 'org')
    data_set = _get_or_bust(data_dict, 'dataset')

    response = _get_action('package_search')(context, {
        'q': 'extras_tmregorg_bi_tmtxtm:{org}'.format(org=org),
        'rows': 100
    })

    pkg_dict = _get_action('package_show')(context, {'name_or_id': data_set})

    extras_dict = {}
    for extra in pkg_dict['extras']:
        extras_dict[extra['key']] = extra['value']

    output_dict = {}

    unsorted_count = 0

    for result in response['results']:
        result_dict = {}
        for extra in result['extras']:
            if extra['key'] == 'tmorder_bi_tmstrs':
                try:
                    extra['value'] = int(extra['value'])
                except ValueError:
                    extra['value'] = 999
                    unsorted_count += 1
            result_dict[extra['key']] = extra['value']
        output_dict[result['name']] = result_dict

    sorted_output = sorted(output_dict.iteritems(), key=lambda sub_dict: sub_dict[1]['tmorder_bi_tmstrs'])

    sorted_extras_list = [k[0] for k in sorted_output]

    explicitly_sorted_extras = sorted_extras_list[:-unsorted_count]
    alpha_sorted_extras = sorted(sorted_extras_list[-unsorted_count:])

    final_sorting = explicitly_sorted_extras + alpha_sorted_extras

    package_extras_ordered_list_of_dicts = []

    for field in final_sorting:
        try:
            package_extras_ordered_list_of_dicts.append({'key': field, 'value': extras_dict[field]})
        except KeyError:
            package_extras_ordered_list_of_dicts.append({'key': field, 'value': ''})

    output = {'sorted_extras': package_extras_ordered_list_of_dicts,
              'field_schema': output_dict}

    return output


def tv_register_product(context, data_dict):
    # noinspection PyUnresolvedReferences
    """
    Register a new product based on a given cubeid and desired producttypecode.
    Populate the new product's fields based on the cube record and producttype mapping.

    :param parentProductId: 8-digit cube id
    :type parentProductId: str
    :param productType: 2-digit product type code
    :type productType: str
    :param productTitleEnglish: english title
    :type productTitleEnglish: str
    :param productTitleFrench: french title
    :type productTitleFrench: str

    :return: newly-registered product id
    :rtype: dict
    """

    cubeid = _get_or_bust(data_dict, 'parentProductId')
    data_dict['productId'] = cubeid  # TODO: this is for Java-style stuff, and needs to be tidied up.
    producttype = _get_or_bust(data_dict, 'productType')

    if str(producttype) == '10':
        raise _ValidationError('Please use the RegisterCube to register a cube')
    if str(producttype) not in ['11', '12', '13', '14']:
        raise _ValidationError('Invalid data producttype, only data products may be registered with this service')

    title_en = _get_or_bust(data_dict, 'productTitleEnglish')
    title_fr = _get_or_bust(data_dict, 'productTitleFrench')

    producttype_dict = _get_action('ndm_get_producttype')(context, data_dict)
    cube_dict = _get_action('ndm_get_cube')(context, data_dict)
    fieldlist = _get_action('ndm_get_fieldlist')(context, {'org': 'rgtabv'})
    productid = _get_action('ndm_get_next_productid')(context, data_dict)

    extras_dict = {}

    time = datetime.datetime.today()

    for field in fieldlist['fields']:
        if field in cube_dict:
            extras_dict[field] = cube_dict[field]
        elif str(field).endswith('ints'):
            extras_dict[field] = 0
        else:
            extras_dict[field] = ''

    extras_dict['10uid_bi_strs'] = productid
    extras_dict['productidnew_bi_strs'] = productid

    for key in producttype_dict:
        extras_dict[key] = unicode(producttype_dict[key])

    extras_dict['hierarchyid_bi_strs'] = cubeid
    extras_dict['title_en_txts'] = title_en
    extras_dict['title_fr_txts'] = title_fr
    extras_dict['zckcapacity_bi_strs'] = 'public'
    extras_dict['zckdbname_bi_strs'] = 'rgproduct'
    extras_dict['zckownerorg_bi_strs'] = 'rgtabv'
    extras_dict['zckpubdate_bi_strs'] = time.strftime("%Y-%m-%d")
    extras_dict['zckpushtime_bi_strs'] = time.strftime("%Y-%m-%d %H:%M")
    extras_dict['zckstatus_bi_txtm'] = 'ndm_tv_register_product_api'

    extras = []

    for key in extras_dict:
        extras.append({'key': key, 'value': extras_dict[key]})

    package_dict = {'name': productid,
                    'owner_org': 'rgtabv',
                    'extras': extras}

    new_product = _get_action('package_create')(context, package_dict)

    if productid.endswith('01') and str(producttype) == '11':
        _get_action('ndm_update_default_view')(context, {'cubeId': str(cubeid), 'defaultView': str(productid)})

    output = _get_action('ndm_get_product')(context, {'productId': new_product['name'],
                                                      'fl': 'productidnew_bi_strs'})

    return output


def delete_product(context, data_dict):
    # noinspection PyUnresolvedReferences
    """
    Set the status of a record to 'Deleted' and remove all metadata associated with that record. This
    will make the productid available for reuse.

    This web service is presently being mocked (i.e. it will return a success if a valid productid is passed in,
    but the exact implementation is still being discussed.)

    :param productId: product id of record to be deleted
    :type productId: str
    :param issueno:

    :return: success or failure
    :rtype: dict
    """

    product_id = _get_or_bust(data_dict, 'productId')

    result = _get_action('ndm_get_product')(context, data_dict)

    deleted_id = result['productidnew_bi_strs']

    return {'message': 'Product successfully deleted', 'productidnew_bi_strs': deleted_id}


# noinspection PyUnusedLocal
def purge_data_set(context, data_dict):
    # noinspection PyUnresolvedReferences
    """
    Purges a data_set from the database.

    :param productId: Product ID
    :type productId: str

    :return: success or failure
    :rtype: dict
    """

    # TODO: Implement user permission validation before deploying this.
    product_id = _get_or_bust(data_dict, 'productId')

    import ckan.model as model

    data_set = model.Package.get(unicode(product_id))

    # rev = model.repo.new_revision()

    model.Package.purge(data_set)

    # data_set.purge()
    model.repo.commit_and_remove()
    return {'success': True, 'message': '%s purged' % product_id}


def update_last_publish_status(context, data_dict):  # TODO: This is out of scope for FY2014.
    # noinspection PyUnresolvedReferences
    """
    Update the publishing status code

    :param productId: publishing status code
    :type productId: str
    :param issueNo: publishing status code
    :type issueNo: str
    :param lastPublishStatusCode: publishing status code
    :type lastPublishStatusCode: str

    :return: updated package
    :rtype: dict
    """

    product_id = _get_or_bust(data_dict, 'productId')
    issue_no = _get_or_bust(data_dict, 'issueNo')
    last_publish_status_code = _get_or_bust(data_dict, 'lastPublishStatusCode')

    last_publish_status_code_dict = _get_action('ndm_get_lastpublishstatus')(context, data_dict)

    q = {
        'q': 'extras_productidnew_bi_strs:{productid} AND extras_issueno_bi_strs:{issueno}'.format(productid=product_id,
                                                                                                   issueno=issue_no),
        'fq': 'zckownerorg_bi_strs:maformat'}

    result = _get_action('package_search')(context, q)

    if result['count'] == 0:
        raise _ValidationError('Record not found.')
    elif result['count'] > 1:
        raise _ValidationError('More than one record identified with these values. Please contact CKAN IT')

    pkg_dict = result['results'][0]

    for extra in pkg_dict['extras']:
        if extra['key'] == 'lastpublishstatuscode_bi_strs':
            extra['value'] = str(last_publish_status_code)
        if extra['key'] == 'lastpublishstatus_en_strs':
            extra['value'] = last_publish_status_code_dict['producttype_en_strs']
        if extra['key'] == 'lastpublishstatus_fr_strs':
            extra['value'] = last_publish_status_code_dict['producttype_fr_strs']

    result = _get_action('package_update')(context, pkg_dict)

    # TODO: what do we actually want to return here? This is the full package with the k: v formatted extras.
    return result


def update_product_geo(context, data_dict):
    # noinspection PyUnresolvedReferences
    """
    Update the specificgeocode_bi_txtm value and sets the geo level (geolevel_*) accordingly.

    :param productId: product id
    :type productId: str

    :param dguids: Geo-code values status code
    :type list of DGUID: array of strs

    :return: updated package
    :rtype: dict
    """

    product_id = _get_or_bust(data_dict, 'productId')
    dguids = _get_or_bust(data_dict, 'dguids')

    #    @todo make this work
    #    try:
    #        validators.list_of_strings('dguids', data_dict)
    #    except validators.Invalid, e:
    #        raise _ValidationError({'dguids': e.error})
    #
    if type(dguids) == unicode:
        dguids = [x.strip() for x in dguids.split(';')]

    q = {'q': 'extras_productidnew_bi_strs:{productid}'.format(productid=product_id)}
    response = _get_action('package_search')(context, q)

    if response['count'] == 0:
        raise _ValidationError('Record not found.')
    elif response['count'] > 1:
        raise _ValidationError('More than one record identified with these values. Please contact CKAN IT')

    pkg_dict = response['results'][0]

    # Set the geo level fields for each specific geo code.
    geo_level = helpers.GeoLevel(context)
    geo_specific = helpers.GeoSpecific(context)
    unique_codes = dict()
    geo_level_en = list()
    geo_level_fr = list()
    geo_specific_en = list()
    geo_specific_fr = list()

    for specific_code in dguids:
        unique_codes[specific_code[:5]] = True  # store the codes in a dictionary to create a unique set

    for geo_code in sorted(unique_codes.keys()):  # get and append the text for geo levels
        (en_text, fr_text) = geo_level.get_by_code(geo_code)
        if en_text:
            geo_level_en.append(en_text)
        if fr_text:
            geo_level_fr.append(fr_text)

    for specific_geo_code in dguids:
        (en_text, fr_text) = geo_specific.get_by_code(specific_geo_code)
        if en_text:
            geo_specific_en.append(en_text)
        if fr_text:
            geo_specific_fr.append(fr_text)

    for extra in pkg_dict['extras']:  # update the package dictionary
        if extra['key'] == 'specificgeocode_bi_txtm':
            extra['value'] = '; '.join(dguids)
        elif extra['key'] == 'geolevel_en_txtm':
            extra['value'] = '; '.join(geo_level_en)
        elif extra['key'] == 'geolevel_fr_txtm':
            extra['value'] = '; '.join(geo_level_fr)
        elif extra['key'] == 'specificgeo_en_txtm':
            extra['value'] = '; '.join(geo_specific_en)
        elif extra['key'] == 'specificgeo_fr_txtm':
            extra['value'] = '; '.join(geo_specific_fr)

    result = _get_action('package_update')(context, pkg_dict)
    # TODO: check result?
    output = _get_action('package_show')(context, {'name_or_id': pkg_dict['name']})

    return output
