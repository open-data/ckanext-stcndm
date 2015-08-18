#!/usr/bin/env python
# encoding: utf-8
import datetime

import ckanapi
import ckan.logic as logic
import ckan.plugins.toolkit as toolkit
import ckanext.scheming.helpers as scheming_helpers

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

    :raises: ValidationError, ObjectNotFound
    """

    lc = ckanapi.LocalCKAN(context=context)
    product_id = _get_or_bust(data_dict, 'parentProductId')

    # TODO: we need to standardize these. This is a result of swapping
    # everything to java-style params
    data_dict['productId'] = product_id

    if not len(str(product_id)) == 8:
        raise _ValidationError('invalid ParentProductId length')

    product_type = _get_or_bust(data_dict, 'productType')

    # testing for existance of cubeid
    lc.actions.ndm_get_cube(**data_dict)

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


@logic.side_effect_free
def get_product(context, data_dict):
    """
    Returns a product given its `productId`, if it exists.

    :param productId: product id (i.e. 2112002604)
    :type productId: str
    :return: product or 404 if not found.
    :rtype: dict
    :raises: ObjectNotFound, ValidationError
    """
    product_id = _get_or_bust(data_dict, 'productId')

    lc = ckanapi.LocalCKAN(context=context)
    result = lc.action.package_search(
        q='extras_product_id_new:{product_id}'.format(
            product_id=product_id
        ),
        rows=1
    )

    if not result['count']:
        raise _NotFound('product {product_id} not found'.format(
            product_id=product_id
        ))

    # If we're getting more than one result for a given product_id
    # something has gone terribly wrong with the database.
    assert(not result['count'] > 1)
    return result['results'][0]


@logic.side_effect_free
def get_dataset_schema(context, data_dict):
    """
    Returns full schema definition for the dataset `name`.

    :param name: The name of the schema to return.
    :param expanded: Expand schema presets. Defaults to `True`.
    :returns:  A complete dataset schema or 404 if not found.
    :rtype: dict
    """
    schema_name = _get_or_bust(data_dict, 'name')

    expanded = data_dict.get('expanded', True)
    if isinstance(expanded, basestring):
        expanded = True if expanded == 'true' else False

    result = scheming_helpers.scheming_get_dataset_schema(
        schema_name,
        expanded=expanded
    )

    if result is None:
        raise _NotFound('no schema by the name {name}'.format(
            name=schema_name
        ))

    return result


@logic.side_effect_free
def get_group_schema(context, data_dict):
    """
    Returns full schema definition for the group `name`.

    :param name: The name of the schema to return.
    :param expanded: Expand schema presets. Defaults to `True`.
    :returns:  A complete dataset schema or 404 if not found.
    :rtype: dict
    """
    schema_name = _get_or_bust(data_dict, 'name')

    expanded = data_dict.get('expanded', True)
    if isinstance(expanded, basestring):
        expanded = True if expanded == 'true' else False

    result = scheming_helpers.scheming_get_group_schema(
        schema_name,
        expanded=expanded
    )

    if result is None:
        raise _NotFound('no schema by the name {name}'.format(
            name=schema_name
        ))

    return result


# noinspection PyUnusedLocal
@logic.side_effect_free
def get_product_type(context, data_dict):
    # noinspection PyUnresolvedReferences
    """Return the French and English titles for the given product_type_code.

    Example query:

    .. code:: python

        r = requests.get('/api/3/action/GetProductType?productType=13')
        print(r.json())

    Example response:

    .. code:: json

        {
            "success": true,
            "result": {
                "fr": "Graphique",
                "en": "Chart",
                "product_type_code": "13"
            }
        }


    :param productType: Product Type Code (i.e. '10') or '*' to receive a
        list of all product_types
    :type productType: str
    :return: English, French and code values for given product_type
    :rtype: dict
    :raises: ValidationError
    """
    massage = lambda in_: {
        'product_type_code': in_['value'],
        'en': in_['label'].get('en'),
        'fr': in_['label'].get('fr')
    }

    product_type = _get_or_bust(data_dict, 'productType')

    presets = scheming_helpers.scheming_get_preset('ndm_products')
    product_types = presets['choices']

    if product_type == '*':
        return [massage(pt) for pt in product_types]
    else:
        for pt in product_types:
            if unicode(pt['value']) == unicode(product_type):
                return massage(pt)
        else:
            raise logic.ValidationError(
                'productType: \'{0}\' not valid'.format(product_type)
            )


@logic.side_effect_free
def get_last_publish_status(context, data_dict):
    """
    Return the French and English values for the given lastpublishstatuscode.

    :param lastPublishStatusCode: Publishing Status Code (i.e. '10')
    :type lastPublishStatusCode: str
    :return: English, French and code values for given lastpublishstatuscode
    :rtype: dict
    :raises: ValidationError
    """
    massage = lambda in_: {
        'last_publish_status_code': in_['value'],
        'en': in_['label'].get('en'),
        'fr': in_['label'].get('fr')
    }

    publish_status = _get_or_bust(
        data_dict,
        'lastPublishStatusCode'
    ).zfill(2)

    presets = scheming_helpers.scheming_get_preset('ndm_publish_status')
    publish_statuses = presets['choices']

    for ps in publish_statuses:
        if unicode(ps['value']) == unicode(publish_status):
            return massage(ps)
    else:
        raise logic.ValidationError(
            'lastPublishStatusCode: \'{0}\' invalid'.format(publish_status)
        )


@logic.side_effect_free
def get_format_description(context, data_dict):
    """
    Return the French and English values for the given formatCode.

    :param formatCode: Format Code (i.e. '10')
    :type formatCode: str

    :return: English, French and code values for given formatCode
    :rtype: dict

    :raises: ValidationError
    """
    massage = lambda in_: {
        'format_code': in_['value'],
        'en': in_['label'].get('en'),
        'fr': in_['label'].get('fr')
    }

    format_code = _get_or_bust(
        data_dict,
        'formatCode'
    ).zfill(2)

    preset = scheming_helpers.scheming_get_preset(u'ndm_formats')
    format_codes = preset['choices']

    for fc in format_codes:
        if fc['value'] == format_code:
            return massage(fc)
    else:
        raise logic.ValidationError(
            'formatCode \'{0}\' invalid'.format(format_code)
        )


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
