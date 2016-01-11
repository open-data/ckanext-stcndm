# --coding: utf-8 --
import ckanapi
import datetime
import ckan.logic as logic
import ckan.plugins.toolkit as toolkit
import ckanext.stcndm.helpers as stcndm_helpers
import pylons.config as config
import json

_get_or_bust = logic.get_or_bust
_stub_msg = {
    'result': 'This method is just a stub for now. Please do not use.'
}
_ValidationError = toolkit.ValidationError
_NotFound = toolkit.ObjectNotFound
_NotAuthorized = toolkit.NotAuthorized


# noinspection PyIncorrectDocstring
@logic.side_effect_free
def register_release(context, data_dict):
    # noinspection PyUnresolvedReferences
    """
    Register a release.

    Automatically populate fields based on provided parameters.

    :param releasedProductId:
    :type releasedProductId: str
    :param parentProduct:
    :type parentProduct: str
    :param lastPublishStatusCode: 1 or 2 digit number
    :type lastPublishStatusCode: str
    :param releaseDate: e.g. 2015-06-30T09:45
    :type releaseDate: str

    :return: new package
    :rtype: dict

    :raises: ValidationError
    """
    lc = ckanapi.LocalCKAN(context=context)

    released_product_id = _get_or_bust(data_dict, 'releasedProductId')

    # determine release_id
    result = lc.action.package_search(
        q='name:release-{product_id}_{year}*'.format(
            product_id=released_product_id,
            year=datetime.date.today().year
        ),
        sort='release_id DESC'
    )
    if result['count'] and \
            u'release_id' in result['results'][0] and \
            result['results'][0]['release_id']:
        release_id = unicode(
            int(result['results'][0]['release_id']) + 1
        ).zfill(3)
    else:
        release_id = '001'

    release_date_str = _get_or_bust(data_dict, 'releaseDate')
    try:
        release_date = datetime.datetime.strptime(
            release_date_str[:16],
            '%Y-%m-%dT%H:%M')
    except ValueError:
        raise _ValidationError(
            {u'releaseDate':
                u'Invalid ({releaseDate}), '
                u'expected releaseDate in YYYY-MM-DDTHH:MM format'.format(
                     releaseDate=release_date_str)})

    if 'parentProduct' in data_dict and data_dict['parentProduct']:
        parent_product = data_dict['parentProduct']
    else:
        parent_product = released_product_id

    publish_status_code = _get_or_bust(data_dict, 'lastPublishStatusCode')

    release_name = u'release-{product_id}_{year}_{release_id}'.format(
        product_id=released_product_id,
        year=datetime.date.today().year,
        release_id=release_id
    )

    release_dict = {
        'owner_org': u'statcan',
        'private': False,
        'type': u'release',
        'name': release_name,
        'title': release_name,
        'release_id': release_id,
        'release_date': release_date.isoformat(),
        'publish_status_code': publish_status_code,
        'parent_id': parent_product,
    }
    if 'referencePeriod' in data_dict and data_dict['referencePeriod']:
        release_dict['reference_period'] = data_dict['referencePeriod']
    if 'issueNumber' in data_dict and data_dict['issueNumber']:
        release_dict['issue_number'] = data_dict['issueNumber']
    if 'isCorrection' in data_dict and data_dict['isCorrection']:
        release_dict['is_correction'] = data_dict['isCorrection']
    else:
        release_dict['is_correction'] = '0'

    lc.action.package_create(**release_dict)
    return lc.action.GetRelease(releaseName=release_name)


# noinspection PyIncorrectDocstring
@logic.side_effect_free
def get_release(context, data_dict):
    # noinspection PyUnresolvedReferences
    """
    Return a dict representation of a release, given a releaseName,
    if it exists.

    :param releaseName: slug of the release to retrieve. (i.e.
                        release-10230123_2015_1)
    :type releaseName: str

    :return: requested release
    :rtype: dict

    :raises: ValidationError, ObjectObjectNotFound
    """
    release_name = _get_or_bust(data_dict, 'releaseName')
    lc = ckanapi.LocalCKAN(context=context)
    result = lc.action.package_search(
        q=(
            'dataset_type:release AND '
            'name:{release_name}'
        ).format(release_name=release_name),
        rows=1
    )

    if not result['count']:
        raise _NotFound('Release not found')
    elif result['count'] > 1:
        raise _ValidationError(
            'More than one release with given releaseName found'
        )
    else:
        return result['results'][-1]


# noinspection PyIncorrectDocstring
@logic.side_effect_free
def get_releases_for_product(context, data_dict):
    # noinspection PyUnresolvedReferences
    """
    Returns all of the releases for the given `productId`.

    :param productId: ID of the parent product.
    :type productId: str
    """
    product_id = _get_or_bust(data_dict, 'productId')

    lc = ckanapi.LocalCKAN(context=context)

    results = lc.action.package_search(
        q='parent_product:{pid}'.format(pid=product_id)
    )

    return {
        'count': results['count'],
        'results': [r for r in results['results']]
    }


# noinspection PyIncorrectDocstring
def ensure_release_exists(context, data_dict):
    # noinspection PyUnresolvedReferences
    """
    Ensure a release exists for the given `productId`.

    :param productId: The parent product ID.
    :type productId: str
    """
    product_id = _get_or_bust(data_dict, 'productId')
    stcndm_helpers.ensure_release_exists(product_id, context=context)


# noinspection PyIncorrectDocstring
@logic.side_effect_free
def consume_transaction_file(context, data_dict):
    # noinspection PyUnresolvedReferences
    """
    Triggers a background task to start consuming the transaction file.

    :param transactionFile: Daily registration transactions
    :type transactionFile: dict
    """
    try:
        def my_get(a_data_dict, key, expected):
            value = a_data_dict.get(key)
            if not value:
                raise _ValidationError({key: u'Missing value'})
            if not isinstance(value, expected):
                raise _ValidationError(
                    {key:
                        u'Invalid format ({value}), expecting a {type}'.format(
                        value=value,
                        type=expected.__name__)})
            return value

        if u'transactionFile' not in data_dict:
            transaction_file = config.get('ckanext.stcndm.transaction_file')
            if not transaction_file:
                raise _ValidationError({
                    u'transactionFile': u'Path to transactionFile missing from'
                                        u'CKAN config file'})
            try:
                transaction_file = open(transaction_file)
                data_dict = json.load(transaction_file)
            except (IOError, ValueError) as e:
                raise _ValidationError({
                    u'transactionFile': e.message
                })

        transaction_dict = my_get(data_dict, u'transactionFile', dict)
        daily_dict = my_get(transaction_dict, u'daily', dict)
        release_date_text = my_get(daily_dict, u'release_date', basestring)
        try:
            release_date = datetime.datetime.strptime(
                release_date_text,
                u'%Y-%m-%dT%H:%M:%S'
            )
        except ValueError:
            raise _ValidationError(
                {u'release_date':
                    u'Invalid format ({date_text}), '
                    u'expecting YYYY-MM-DDTHH:MM:SS'.format(
                        date_text=release_date_text)})
        releases = my_get(daily_dict, u'release', list)
        lc = ckanapi.LocalCKAN(context=context)
        results = []
        for release in releases:
            if not isinstance(release, dict):
                raise _ValidationError({
                    u'release': u'Invalid format, '
                    u'expecting a list of dict'
                })
            product_id = my_get(release, u'id', basestring)
            letter_id = my_get(release, u'letter_id', basestring)
            stats_in_brief = my_get(release, u'stats_in_brief', basestring)
            title = {
                u'en': my_get(release, u'title_en', basestring),
                u'fr': my_get(release, u'title_fr', basestring)
            }
            reference_period = {
                u'en': release.get(u'refper_en'),
                u'fr': release.get(u'refper_fr')
            }
            theme_list = my_get(release, u'theme', list)
            cube_list = release.get(u'cube', [])
            survey_list = release.get(u'survey', [])
            product_list = release.get(u'product', [])
            url = {
                u'en': u'/daily-quotidien/{release_date}/dq{release_date}'
                       u'{letter_id}-eng.htm'.format(
                         release_date=release_date.strftime(u'%y%m%d'),
                         letter_id=letter_id
                       ),
                u'fr': u'/daily-quotidien/{release_date}/dq{release_date}'
                       u'{letter_id}-fra.htm'.format(
                         release_date=release_date.strftime(u'%y%m%d'),
                         letter_id=letter_id
                       )
            }
            try:
                results.append(lc.action.RegisterDaily(
                    ** {
                        u'releaseDate': release_date_text,
                        u'productId': u'00240001' + product_id,
                        u'statsInBrief': stats_in_brief,
                        u'productTitle': title,
                        u'referencePeriod': reference_period,
                        u'themeList': theme_list,
                        u'cubeList': cube_list,
                        u'surveyList': survey_list,
                        u'productList': product_list,
                        u'url': url
                    }
                ))
            except _ValidationError as ve:
                results.append({
                    u'product_id_new': u'00240001'+product_id,
                    u'error': ve.error_dict})
        stcndm_helpers.write_audit_log("consume_transaction_file", results)
    except _ValidationError as ve:
        stcndm_helpers.write_audit_log("consume_transaction_file", ve, 3)
        raise ve
    return results
