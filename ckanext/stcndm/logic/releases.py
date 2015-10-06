# --coding: utf-8 --
import ckanapi
import datetime
from ckan.common import _
import ckan.logic as logic
import ckan.plugins.toolkit as toolkit
import ckanext.stcndm.helpers as stcndm_helpers

_get_or_bust = logic.get_or_bust
_stub_msg = {
    'result': 'This method is just a stub for now. Please do not use.'
}
_ValidationError = toolkit.ValidationError
_NotFound = toolkit.ObjectNotFound
_NotAuthorized = toolkit.NotAuthorized


@logic.side_effect_free
def register_release(context, data_dict):
    """
    Register a release.

    Automatically populate fields based on provided parameters.

    :param releasedProductId:
    :type releasedProductId: str
    :param parentProduct
    :type str
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
    if result['count'] and 'release_id' in result['results'][0] and result['results'][0]['release_id']:
        release_id = unicode(int(result['results'][0]['release_id']) + 1).zfill(3)
    else:
        release_id = '001'

    release_date_str = _get_or_bust(data_dict, 'releaseDate')
    try:
        release_date = datetime.datetime.strptime(release_date_str[:16], '%Y-%m-%dT%H:%M')
    except ValueError:
        raise _ValidationError(
            _("Incorrect format for releaseDate '{0}', should be YYYY-MM-DDTHH:MM".format(release_date_str)))

    if 'parentProduct' in data_dict and data_dict['parentProduct']:
        parent_product = data_dict['parentProduct']
    else:
        parent_product = released_product_id

    publish_status_code = _get_or_bust(data_dict, 'lastPublishStatusCode')

    release_name = 'release-{product_id}_{year}_{release_id}'.format(
        product_id=released_product_id,
        year=datetime.date.today().year,
        release_id=release_id
    )

    release_dict = {
        'owner_org': 'statcan',
        'private': False,
        'type': 'release',
        'name': release_name,
        'title': release_name,
        'release_id': release_id,
        'release_date': release_date.isoformat(),
        'publish_status_code': publish_status_code,
        'parent_product': parent_product,
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


@logic.side_effect_free
def get_release(context, data_dict):
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


@logic.side_effect_free
def get_releases_for_product(context, data_dict):
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


def ensure_release_exists(context, data_dict):
    """
    Ensure a release exists for the given `productId`.

    :param productId: The parent product ID.
    :type productId: str
    """
    product_id = _get_or_bust(data_dict, 'productId')
    stcndm_helpers.ensure_release_exists(product_id, context=context)
