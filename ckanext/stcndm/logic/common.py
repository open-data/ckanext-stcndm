#!/usr/bin/env python
# encoding: utf-8
import ckanapi
import ckan.logic as logic
import ckan.plugins.toolkit as toolkit
import ckanext.scheming.helpers as scheming_helpers
import arrow

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

    # testing for existence of cubeid
    lc.action.GetCube(cubeId=product_id)

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
        view_id = response['results'][0]['product_id_new'][-2:]
        if view_id == '99':
                # TODO: implement reusing unused IDs
            raise _ValidationError(
                'All Product IDs have been used. '
                'Reusing IDs is in development.'
            )
        else:
            try:
                product_id_new = (
                    '{subject_code}{product_type}{sequence_id}{view_id}'
                ).format(
                    subject_code=subject_code,
                    product_type=product_type,
                    sequence_id=sequence_id,
                    view_id=str(int(view_id)+1).zfill(2)
                )
            except ValueError:
                raise _ValidationError(
                    'Invalid product_id {0}'.format(
                        product_id_new
                    )
                )
    except (KeyError, IndexError) as e:
        raise e

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

    presets = scheming_helpers.scheming_get_preset('ndm_product')
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

    preset = scheming_helpers.scheming_get_preset(u'ndm_format')
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


@logic.side_effect_free
def get_issues_by_pub_status(context, data_dict):
    # noinspection PyUnresolvedReferences
    """
    Fields (listed below) for all product issues of type "productType" with a
    last_publish_status_code equal to that passed in with a release date
    between the two input parameters

    :param lastPublishStatusCode: Possible values are outlined on
        https://confluence.statcan.ca/display/NDMA/Publishing+workflow
    :param startReleaseDate: Beginning of date range
    :param endReleaseDate: End of date range
    :param productTypeCode: Possible values are outlined on
        https://confluence.statcan.ca/pages/viewpage.action?pageId=20416770.
        If no product type is passed in, assume all product types are
        requested.

    :rtype: list of dicts
    """
    # TODO: date validation? anything else?

    get_last_publish_status_code = _get_or_bust(
        data_dict,
        'lastPublishStatusCode'
    )
    start_release_date = _get_or_bust(data_dict, 'startReleaseDate')
    end_release_date = _get_or_bust(data_dict, 'endReleaseDate')
    if 'productType' in data_dict and data_dict['productType']:
        product_type_code = data_dict['productTypeCode']
    else:
        product_type_code = '["" TO *]'

    q = (
        'extras_release_date:[{startReleaseDate} TO {endReleaseDate}] AND '
        'extras_last_publish_status_code:{lastPublishStatusCode} AND '
        'extras_product_type_code:{productTypeCode}'
    ).format(
        startReleaseDate=arrow.get(
            start_release_date
        ).format('YYYY-MM-DDTHH:mm:ss')+'Z',
        endReleaseDate=arrow.get(
            end_release_date
        ).format('YYYY-MM-DDTHH:mm:ss')+'Z',
        lastPublishStatusCode=get_last_publish_status_code,
        productTypeCode=product_type_code
    )

    lc = ckanapi.LocalCKAN()

    i = 0
    n = 1
    while i < n:
        query_results = lc.action.package_search(
            q=q,
            rows=1000,
            start=i*1000)
        i += 1
        n = query_results['count'] / 1000.0
        count = query_results['count']
        if count == 0:
            raise _NotFound

        desired_extras = [
            'product_type_code',
            'product_id_new',
            'issue_no',
            'correction_id_code',
            'last_publish_status_code',
            'release_date',
            'reference_period',
            'url'
        ]

        output = []

        for result in query_results['results']:
            result_dict = {}
            for extra in desired_extras:
                if extra in result:
                    result_dict[extra] = result[extra] or ''
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
    """
    Register a new product based on a given `parentProductId` (the 8-digit ID
    of a cube) and the desired `productTypeCode`. The new product's fields will
    be populated based on the cube record.

    .. note::

        If the cube is missing English and French titles, the cube will be
        updated.

    .. note::

        As the schemas for tables, indicators, charts, and maps do not
        yet exist, this method is not thoroughly tested.

    :param parentProductId: 8-digit cube id
    :type parentProductId: str
    :param productType: 2-digit product type code
    :type productType: str
    :param productTitle: EN/FR title dictionary
    :type productTitle: dict
    :return: newly-registered product id
    :rtype: dict
    """
    # These are the only product types that can be registered using
    # this method as these are the only "data products".
    # TODO: Can we pull this from somewhere? Presets.yaml does not
    #       necessarily have the exact schema name in ndm_product_type.
    VALID_DATA_TYPES = {
        u'11': 'view',
        u'12': 'indicator',
        u'13': 'chart',
        u'14': 'map'
    }
    CUBE_PRODUCT_TYPE = u'10'

    cube_id = _get_or_bust(data_dict, 'parentProductId')
    title = _get_or_bust(data_dict, 'productTitle')
    product_type = _get_or_bust(data_dict, 'productType').zfill(2)

    if product_type == CUBE_PRODUCT_TYPE:
        raise _ValidationError(
            'Please use RegisterCube to register a cube'
        )
    elif product_type not in VALID_DATA_TYPES:
        raise _ValidationError(
            'Invalid data productType, only data products may be registered '
            'with this service'
        )

    lc = ckanapi.LocalCKAN(context=context)
    cube_dict = lc.action.GetCube(cubeId=cube_id)

    product_type_schema = lc.action.GetDatasetSchema(
        name=VALID_DATA_TYPES[product_type]
    )

    # Copy fields that overlap between the cubes and the destination
    # type.
    copied_fields = {}
    for field in product_type_schema['dataset_fields']:
        field_name = field['field_name']
        if field_name in cube_dict:
            copied_fields[field_name] = cube_dict[field_name]

    # FIXME: This is not atomic. If this API method is called quickly
    #        in parallel, this product ID could no longer be free.
    product_id = lc.action.GetNextProductId(
        parentProductId=cube_id,
        productType=product_type
    )

    # Overwrite/add some fields that we don't want to inherit
    # from the cube.
    copied_fields.update({
        'type': VALID_DATA_TYPES[product_type],
        'name': product_id,
        'owner_org': 'statcan',
        'product_id_new': product_id,
        'parent_product': cube_id,
        'title': title,
        'product_type_code': product_type
    })

    lc.action.package_create(**copied_fields)
    return {'product_id_new': product_id}


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

    :param productIds: publishing status code
    :type productIds: str
    :param issueNo: publishing status code
    :type issueNo: str
    :param lastPublishStatusCode: publishing status code
    :type lastPublishStatusCode: str

    :return: updated package
    :rtype: dict
    """
    return [
        _update_single_publish_status(
            context,
            {
                'productId': product_id,
                'issueNo': _get_or_bust(data_dict, 'issueNo'),
                'lastPublishStatusCode': _get_or_bust(
                    data_dict,
                    'lastPublishStatusCode'
                )
            }
        ) for product_id in _get_or_bust(data_dict, 'productIds')
    ]


def _update_single_publish_status(context, data_dict):
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
