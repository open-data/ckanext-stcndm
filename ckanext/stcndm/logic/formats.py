# --coding: utf-8 --
import ckanapi
from ckan.common import _
import ckan.logic as logic
import ckan.plugins.toolkit as toolkit
# import ckanext.stcndm.helpers as stcndm_helpers

_get_or_bust = logic.get_or_bust
# noinspection PyUnresolvedReferences
_ValidationError = toolkit.ValidationError
# noinspection PyUnresolvedReferences
_NotFound = toolkit.ObjectNotFound
# noinspection PyUnresolvedReferences
_NotAuthorized = toolkit.NotAuthorized


def register_format(context, data_dict):
    # noinspection PyUnresolvedReferences
    """
    Register a format.

    Automatically populate fields based on provided parameters.

    :param releasedProductId:
    :type releasedProductId: str
    :param formatCode: 1 or 2 digit number
    :type formatCode: str
    :param releaseSlug: e.g. release-34567890_2015_001
    :param parentProduct
    :type str
    :type url: str
    :param url (optional): e.g. statcan.gc.ca:/product.html
    :type url: str
    :param issnNumber (optional): e.g.
    :type url: str

    :return: new package
    :rtype: dict

    :raises: ValidationError
    """

    lc = ckanapi.LocalCKAN(context=context)

    released_product_id = _get_or_bust(data_dict, 'releasedProductId')
    format_code = _get_or_bust(data_dict, 'formatCode')
    release_slug = _get_or_bust(data_dict, 'releaseSlug')
    if 'parentProduct' in data_dict and data_dict['parentProduct']:
        parent_product = data_dict['parentProduct']
    else:
        parent_product = released_product_id

    result = lc.action.package_search(
        q='name:format-{product_id}_{format_code} AND release_slug:{release_slug}'.format(
            product_id=released_product_id,
            format_code=format_code
        )
    )
    if result['count']:
        if 'release_slug' in result['results'] and result['results']['release_slug']:
            registered_release_slug = result['results']['release_slug']
        else:
            registered_release_slug = 'release_slug not specified'
        raise _ValidationError(
            _(
                "Format code {format_code} already registered to release {release_slug}".format(
                    format_code=format_code,
                    release_slug=registered_release_slug
                )
            )
        )

    format_name = 'format-{product_id}_{format_code}'.format(
        product_id=released_product_id,
        cormat_code=format_code
    )

    format_dict = {
        'owner_org': 'statcan',
        'private': False,
        'type': 'format',
        'format_code': format_code,
        'release_slug': release_slug,
        'parent_product': parent_product,
        'name': format_name,
        'title': format_name,
    }
    if 'url' in data_dict and data_dict['url']:
        format_dict['url'] = data_dict['url']
    if 'issnNumber' in data_dict and data_dict['issnNumber']:
        format_dict['issn_number'] = data_dict['issnNumber']

    lc.action.package_create(**format_dict)
    return lc.action.GetFormat(formatName=format_name)


@logic.side_effect_free
def get_format(context, data_dict):
    # noinspection PyUnresolvedReferences
    """
    Return a dict representation of a format, given a formatName, if it exists.

    :param formatName: slug of the format to retrieve. (i.e. format-10230123_17)
    :type releaseName: str

    :return: requested format
    :rtype: dict

    :raises: ValidationError, ObjectObjectNotFound
    """
    format_name = _get_or_bust(data_dict, 'formatName')
    lc = ckanapi.LocalCKAN(context=context)
    result = lc.action.package_search(
        q=(
            'dataset_type:format AND '
            'name:{format_name}'
        ).format(release_name=format_name),
        rows=1
    )

    if not result['count']:
        raise _NotFound('Format not found')
    elif result['count'] > 1:
        raise _ValidationError('More than one format with given formatName found')
    else:
        return result['results'][-1]
