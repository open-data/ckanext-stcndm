#!/usr/bin/env python
# encoding: utf-8
import json
import yaml
import datetime
from pkgutil import get_data

import ckan.logic as logic
import ckan.plugins.toolkit as toolkit

_get_or_bust = logic.get_or_bust
_get_action = toolkit.get_action
_ValidationError = toolkit.ValidationError
_NotFound = toolkit.ObjectNotFound
_NotAuthorized = toolkit.NotAuthorized


@logic.side_effect_free
def get_next_product_id(context, data_dict):
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

    # TODO: we need to standardize these. This is a result of swapping
    # everything to java-style params
    data_dict['productId'] = product_id

    if not len(str(product_id)) == 8:
        raise _ValidationError('invalid ParentProductId length')

    product_type = _get_or_bust(data_dict, 'productType')

    # testing for existance of cubeid
    _get_action('ndm_get_cube')(context, data_dict)

    subject_code = str(product_id)[:2]
    # TODO Do we want to rely on the subject_code in the cube dict?
    #      probably not...
    # TODO this is actually going to be a problem because cubes do
    #      not have good data in subj
    sequence_id = str(product_id)[4:8]

    product_family = '{subject_code}{product_type}{sequence_id}'.format(
        subject_code=subject_code,
        product_type=product_type,
        sequence_id=sequence_id
    )

    query = {
        'q': 'extras_product_id_new:{product_family}*'.format(
            product_family=product_family
        ),
        'sort': 'extras_product_id_new desc'
    }

    response = _get_action('package_search')(context, query)

    product_id_new = "{subject_code}{product_type}{sequence_id}01".format(
        subject_code=subject_code,
        product_type=product_type,
        sequence_id=sequence_id
    )

    try:
        for extra in response['results'][0]['extras']:
            if extra['key'] == 'product_id_new':
                product_id_response = extra['value']
                # TODO: implement reusing unused IDs
                if product_id_response.endswith('99'):
                    raise _ValidationError(
                        'All Product IDs have been used. '
                        'Reusing IDs is in development.'
                    )
                else:
                    try:
                        product_id_new = str(int(product_id_response) + 1)
                    except ValueError:
                        raise _ValidationError(
                            'Invalid product_id {0}'.format(
                                product_id_response
                            )
                        )
    except KeyError:
        pass

    return product_id_new


# this one is for external use. just use package_show internally
def get_product(context, data_dict):
    """
    Return a JSON dict representation of a product, given a ProductId,
    if it exists.

    :param productId: product id (i.e. 2112002604)
    :type productId: str
    :param fields: desired output fields. (i.e. "title, product_id_new")
                   Default: *
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

    q = {
        'q': 'extras_product_id_new:{product_id}'.format(
            product_id=product_id
        )
    }

    result = _get_action('package_search')(context, q)

    count = result['count']
    if not count:
        raise _NotFound('product not found')

    output = []
    for a_result in result['results']:
        an_output = {}
        extras = a_result['extras']
        for extra in extras:
            if extra['key'] in desired_fields_list:
                an_output[extra['key']] = extra['value']
        output.append(an_output)
    return output


@logic.side_effect_free
def get_field_list(context, data_dict):
    # noinspection PyUnresolvedReferences
    """
    Return a list of all fields for a given org (based on the contents of
    the maschema organization).

    Used for determining which fields should be used when creating new records.

    :param org: Organization name (i.e. maprimary)
    :type org: string

    :return: list of all fields in a given organization based on the maschema
             organization.
    :rtype:  list of strings

    :raises
    """

    # TODO: Services which use this should possibly rely on
    #       get_fielddict instead, since it

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

    :param productType: Product Type Code (i.e. '10') or '*' to receive a
                        list of all product_types
    :type productType str

    :return: English, French and code values for given product_type
    :rtype: dict

    :raises ValidationError
    """
    massage = lambda in_: {
        'product_type_code': in_['value'],
        'en': in_['label'].get('en'),
        'fr': in_['label'].get('fr')
    }

    product_type = _get_or_bust(data_dict, 'productType')
    presets = yaml.safe_load(
        get_data(
            'ckanext.stcndm',
            'schemas/presets.yaml'
        )
    )

    for preset in presets['presets']:
        if preset['preset_name'] == 'ndm_products':
            product_types = preset['values']['choices']
            break
    else:
        raise _NotFound('no product types could be found')

    if product_type == '*':
        return [massage(pt) for pt in product_types]
    else:
        for pt in product_types:
            if str(pt['value']) == str(product_type):
                return massage(pt)
        else:
            raise logic.ValidationError(
                'productType: \'{0}\' not valid'.format(product_type)
            )


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
        output = {'last_publish_status_code': publish_status,
                  'en': publish_statuses[publish_status]['en'],
                  'fr': publish_statuses[publish_status]['fr']}
    except KeyError:
        raise logic.ValidationError(
            'lastPublishStatusCode: \'{0}\' invalid'.format(publish_status)
        )

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
        output = {'format_code': format_code,
                  'en': format_codes[format_code]['en'],
                  'fr': format_codes[format_code]['fr']}
    except KeyError:
        raise logic.ValidationError(
            'formatCode \'{0}\' invalid'.format(format_code)
        )

    return output


@logic.side_effect_free
def get_upcoming_releases(context, data_dict):
    # noinspection PyUnresolvedReferences
    """
    Return all records with a lastpublishstatuscode of Verified (8) and a
    release date between the two parameters.

    :param startDate: Beginning of date range
    :param endDate: End of date range

    :return: productId, issueno, correctionid, reference_period,
             release_date for each matching record.
    :rtype: list of dicts
    """
    # TODO: date validation? anything else?

    start_date = _get_or_bust(data_dict, 'startDate')
    end_date = _get_or_bust(data_dict, 'endDate')

    q = {
        'q': (
            'release_date:[{startDate}:00Z TO {endDate}:00Z] '
            'AND last_publish_status_code:8'
        ).format(
            startDate=start_date,
            endDate=end_date
        ),
        'rows': 500
    }

    result = _get_action('package_search')(context, q)

    count = result['count']

    if count == 0:
        raise _NotFound
    else:
        desired_extras = ['product_id_new',
                          'issue_no',
                          'correction_id_code',
                          'reference_period',
                          'release_date',
                          'url',
                          'product_type_code',
                          'last_publish_status_code']

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
    Return a dict with all ProductIDs and French/English titles that are
    associated with a given SubjectCode and ProductType.

    Note that this relies on the subject_code field rather than the
    subject code in the cube_id.

    :param parentProductId: cube id
    :type parentProductId: str
    :param productType: two-digit product type code
    :type productType: str

    :return: registered cubes for the SubjectCode and their French/English
             titles.
    :rtype: list of dicts
    """

    product_id = _get_or_bust(data_dict, 'parentProductId')
    product_type = _get_or_bust(data_dict, 'productType')
    # if product_type not in ['10', '11', '12', '13', '14', ]

    subject_code = product_id[:2]
    sequence_id = product_id[-4:]

    query = {
        'q': (
            'product_id_new:{subject_code}??{sequence_id}* '
            'AND product_type_code:{product_type}'
        ).format(
            subject_code=subject_code,
            sequence_id=sequence_id,
            product_type=product_type
        ),
        'rows': '1000'
    }

    response = _get_action('package_search')(context, query)

    # TODO: raise error if the cube cannot be located.

    output = []

    for result in response['results']:
        result_dict = {}
        for extra in result['extras']:
            if extra['key'] == 'product_id_new':
                result_dict['product_id_new'] = extra['value']
            elif extra['key'] == 'title':
                result_dict['title'] = extra['value']

        output.append(result_dict)

    return output


# noinspection PyUnusedLocal
def get_drop_downs(context, data_dict):
    # noinspection PyUnresolvedReferences
    """
    Return a dict containing all dropdown options for all fields
    in a given org.

    :param owner_org: organization name
    :type owner_org: str

    :return:
    :rtype: dict of lists of dicts
    """
    # TODO: zckownerorg_bi_strs is supposed to be no longer necessary.
    #       does that mean get_drop_downs is redundant?
    q = 'zckownerorg_bi_strs:tmshortlist'

    query = {'q': q, 'rows': '1000'}

    response = _get_action('package_search')(context, query)

    output_dict = {}

    for result in response['results']:
        result_dict = {}

        for extra in result['extras']:
            result_dict[extra['key']] = extra['value']

        # Stripping off "extras_"
        field_name = result_dict['tmdroplfld_bi_tmtxtm'][7:]
        # check field_name to determine how many fields to
        # return for this field
        if field_name == 'tracking_code':
            # create single element list
            split_values = [result_dict['tmdroplopt_bi_tmtxtm']]
        elif field_name == 'display_code':
            # create single element list
            split_values = [result_dict['tmdroplopt_bi_tmtxtm']]
        elif field_name == 'geo_level_code':
            # don't send the code
            split_values = result_dict['tmdroplopt_bi_tmtxtm'].split('|')[:2]
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

    This action implements business logic to handle which fields should be
    returned for which actions.

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

    valid_fieldnames = (
        'subject_code',
        'dimension_group_code',
        'imdb_source_code',
        'geodescriptor'
    )

    if field_name not in valid_fieldnames:
        raise _ValidationError('Invalid fieldName')

    query_split = query.replace('/', '').split()
    query = ' '.join([word + '*' for word in query_split])

    if field_name == 'subject_code':
        data_dict = {'q': u'tmtaxsubj_autotext:({query})'.format(query=query)}
        output_dict = {'tmtaxsubj_en_tmtxtm': 'subjnew_en_txtm',
                       'tmtaxsubj_fr_tmtxtm': 'subjnew_fr_txtm',
                       'tmtaxsubjcode_bi_tmtxtm': 'subject_code',
                       'tmtaxdisp_en_tmtxtm': 'subject_code'}
        sort_field = 'subject_code'

    elif field_name == 'dimension_group_code':
        data_dict = {'q': u'tmdimen_autotext:({query})'.format(query=query)}
        output_dict = {'tmdimenalias_bi_tmtxtm': 'dimalias_en_txtm',
                       'tmdimentext_en_tmtxtm': 'dimgroup_en_txtm',
                       'tmdimentext_fr_tmtxtm': 'dimgroup_fr_txtm',
                       'tmdimencode_bi_tmtxtm': 'dimension_group_code'}
        sort_field = None

    elif field_name == 'imdb_source_code':
        data_dict = {'q': u'source_autotext:({query})'.format(query=query)}
        output_dict = {'title': 'imdb_source',
                       'product_id_new': 'imdb_source_code'}
        sort_field = None

    elif field_name == 'geodescriptor':
        data_dict = {'q': u'tmsgc_autotext:({query})'.format(query=query)}
        output_dict = {'tmsgcname_en_tmtxtm': 'specificgeo_en_txtm',
                       'tmsgcname_fr_tmtxtm': 'specificgeo_fr_txtm',
                       'tmsgcspecificcode_bi_tmtxtm': 'geodescriptor'}
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

        # TODO: I think these are backwards (key should be value)
        #       but it's an issue with the autocomplete js module

        output_list.append({'value': ' | '.join(result_list),
                            'key': json.dumps(result_dict),
                            'ord': result_dict.get(sort_field,
                                                   None)})

    # sort returned list based on field name (if sort field specified)
    if sort_field:
        output_list = sorted(output_list, key=lambda k: k['ord'])

    return output_list[:limit]


def tv_register_product(context, data_dict):
    # noinspection PyUnresolvedReferences
    """
    Register a new product based on a given cubeid and desired producttypecode.
    Populate the new product's fields based on the cube record and producttype
    mapping.

    :param parentProductId: 8-digit cube id
    :type parentProductId: str
    :param productType: 2-digit product type code
    :type productType: str
    :param productTitle: EN/FR title dictionary
    :type productTitle: dict

    :return: newly-registered product id
    :rtype: dict
    """

    cube_id = _get_or_bust(data_dict, 'parentProductId')
    # TODO: this is for Java-style stuff, and needs to be tidied up.
    data_dict['productId'] = cube_id
    product_type = _get_or_bust(data_dict, 'productType')

    if str(product_type) == '10':
        raise _ValidationError(
            'Please use the RegisterCube to register a cube'
        )
    if str(product_type) not in ['11', '12', '13', '14']:
        raise _ValidationError(
            'Invalid data productType, only data products may be registered '
            'with this service'
        )

    title = _get_or_bust(data_dict, 'productTitle')

    cube_dict = _get_action('ndm_get_cube')(context, data_dict)
    field_list = _get_action('ndm_get_field_list')(context, {'org': 'rgtabv'})
    product_id = _get_action('ndm_get_next_product_id')(context, data_dict)

    extras_dict = {}

    time = datetime.datetime.today()

    for field in field_list['fields']:
        if field in cube_dict:
            extras_dict[field] = cube_dict[field]
        elif str(field).endswith('ints'):
            extras_dict[field] = 0
        else:
            extras_dict[field] = ''

    extras_dict['product_id_new'] = product_id
    extras_dict['product_type'] = product_type
    extras_dict['parent_product'] = cube_id
    extras_dict['title'] = title
    extras_dict['zckcapacity_bi_strs'] = 'public'
#    extras_dict['zckdbname_bi_strs'] = 'rgproduct'
#    extras_dict['zckownerorg_bi_strs'] = 'rgtabv'
    extras_dict['zckpubdate_bi_strs'] = time.strftime("%Y-%m-%d")
    extras_dict['zckpushtime_bi_strs'] = time.strftime("%Y-%m-%d %H:%M")
    extras_dict['zckstatus_bi_txtm'] = 'ndm_tv_register_product_api'

    extras = []

    for key in extras_dict:
        extras.append({'key': key, 'value': extras_dict[key]})

    package_dict = {'name': product_id,
                    'owner_org': 'rgtabv',
                    'extras': extras}

    new_product = _get_action('package_create')(context, package_dict)

    if product_id.endswith('01') and str(product_type) == '11':
        _get_action('ndm_update_default_view')(context, {
            'cubeId': str(cube_id),
            'defaultView': str(product_id)
        })

    output = _get_action('ndm_get_product')(context, {
        'productId': new_product['name'],
        'fl': 'product_id_new'
    })

    return output


def delete_product(context, data_dict):
    # noinspection PyUnresolvedReferences
    """
    Set the status of a record to 'Deleted' and remove all metadata associated
    with that record. This will make the productid available for reuse.

    This web service is presently being mocked (i.e. it will return a success
    if a valid productid is passed in, but the exact implementation is still
    being discussed.)

    :param productId: product id of record to be deleted
    :type productId: str
    :param issueno:

    :return: success or failure
    :rtype: dict
    """

    product_id = _get_or_bust(data_dict, 'productId')

    result = _get_action('ndm_get_product')(context, data_dict)

    deleted_id = result['product_id_new']

    return {
        'message': 'Product successfully deleted',
        'product_id_new': deleted_id
    }


# noinspection PyUnusedLocal
def purge_dataset(context, data_dict):
    # noinspection PyUnresolvedReferences
    """
    Purges a dataset from the database.

    :param productId: Product ID
    :type productId: str

    :return: success or failure
    :rtype: dict
    """

    # TODO: Implement user permission validation before deploying this.
    product_id = _get_or_bust(data_dict, 'productId')

    import ckan.model as model

    dataset = model.Package.get(unicode(product_id))

    # rev = model.repo.new_revision()

    model.Package.purge(dataset)

    # dataset.purge()
    model.repo.commit_and_remove()
    return {'success': True, 'message': '%s purged' % product_id}


# TODO: This is out of scope for FY2014.
def update_last_publish_status(context, data_dict):
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

    q = {
        'q': (
            'extras_product_id_new:{product_id} AND '
            'extras_issue_no:{issue_no}'
        ).format(
            product_id=product_id,
            issue_no=issue_no
        )
    }

    result = _get_action('package_search')(context, q)

    if result['count'] == 0:
        raise _ValidationError('Record not found.')
    elif result['count'] > 1:
        raise _ValidationError(
            'More than one record identified with these values. '
            'Please contact CKAN IT'
        )

    pkg_dict = result['results'][0]

    for extra in pkg_dict['extras']:
        if extra['key'] == 'last_publish_status_code':
            extra['value'] = str(last_publish_status_code)

    result = _get_action('package_update')(context, pkg_dict)

    # TODO: what do we actually want to return here? This is the full
    #       package with the k: v formatted extras.
    return result


def update_product_geo(context, data_dict):
    # noinspection PyUnresolvedReferences
    """
    Update the specificgeocode_bi_txtm value and sets the geo level
    (geolevel_*) accordingly.

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

    q = {
        'q': 'extras_product_id_new:{product_id}'.format(
            product_id=product_id
        )
    }
    response = _get_action('package_search')(context, q)

    if response['count'] == 0:
        raise _ValidationError('Record not found.')
    elif response['count'] > 1:
        raise _ValidationError(
            'More than one record identified with these values. '
            'Please contact CKAN IT'
        )

    pkg_dict = response['results'][0]

    # Set the geo level fields for each specific geo code.
#    geo_level = helpers.GeoLevel(context)
#    geo_specific = helpers.GeoSpecific(context)
    unique_codes = dict()
#    geo_level_en = list()
#    geo_level_fr = list()
#    geo_specific_en = list()
#    geo_specific_fr = list()

    for specific_code in dguids:
        # store the codes in a dictionary to create a unique set
        unique_codes[specific_code[:5]] = True

# get and append the text for geo levels
#    for geo_code in sorted(unique_codes.keys()):
#        (en_text, fr_text) = geo_level.get_by_code(geo_code)
#        if en_text:
#            geo_level_en.append(en_text)
#        if fr_text:
#            geo_level_fr.append(fr_text)

#    for specific_geo_code in dguids:
#        (en_text, fr_text) = geo_specific.get_by_code(specific_geo_code)
#        if en_text:
#            geo_specific_en.append(en_text)
#        if fr_text:
#            geo_specific_fr.append(fr_text)

    for extra in pkg_dict['extras']:  # update the package dictionary
        if extra['key'] == 'geodescriptor':
            extra['value'] = '; '.join(dguids)
        elif extra['key'] == 'geo_level_code':
            extra['value'] = '; '.join(unique_codes.keys())
#        elif extra['key'] == 'geolevel_en_txtm':
#            extra['value'] = '; '.join(geo_level_en)
#        elif extra['key'] == 'geolevel_fr_txtm':
#            extra['value'] = '; '.join(geo_level_fr)
#        elif extra['key'] == 'specificgeo_en_txtm':
#            extra['value'] = '; '.join(geo_specific_en)
#        elif extra['key'] == 'specificgeo_fr_txtm':
#            extra['value'] = '; '.join(geo_specific_fr)

    # result = _get_action('package_update')(context, pkg_dict)
    # TODO: check result?
    output = _get_action('package_show')(context, {
        'name_or_id': pkg_dict['name']
    })

    return output
