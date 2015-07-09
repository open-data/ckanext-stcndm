# --coding: utf-8 --

__author__ = 'Statistics Canada'

import ckan.plugins.toolkit as toolkit
import ckan.logic as logic
import ckan.logic.validators as validators

_get_or_bust = logic.get_or_bust
# noinspection PyUnresolvedReferences
_get_action = toolkit.get_action
# noinspection PyUnresolvedReferences
_ValidationError = toolkit.ValidationError


def update_default_view(context, data_dict):
    # noinspection PyUnresolvedReferences
    """
    Updates the default view for a given cube

    :param cubeId: cube id
    :type cubeId: str
    :param defaultView: default view id
    :type defaultView: str

    :return: dict
    """

    cube_id = _get_or_bust(data_dict, 'cubeId')
    default_view = _get_or_bust(data_dict, 'defaultView')

    try:
        validators.package_name_exists(cube_id, context)
    except validators.Invalid, e:
        raise _ValidationError({'cubeId': e.error})

    # TODO: can't check for the default view before the view is registered
    # try:
    #     validators.package_name_exists(default_view, context)
    # except validators.Invalid, e:
    #     raise _ValidationError({'defaultView': e.error})

    pkg_dict = _get_action('package_show')(context, {'name_or_id': str(cube_id)})

    for extra in pkg_dict['extras']:
        if extra['key'] == 'default_view_id':
            extra['value'] = default_view

    result = _get_action('package_update')(context, pkg_dict)

    output = _get_action('ndm_get_cube')(context, {'productId': result['name']})

    return output
