# --coding: utf-8 --

import ckan.plugins.toolkit as toolkit
import ckan.logic as logic
import ckan.logic.validators as validators
import ckanapi

__author__ = 'Statistics Canada'

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
        validators.package_name_exists('cube-'+cube_id, context)
    except validators.Invalid, e:
        raise _ValidationError({'cubeId': e.error})

    # TODO: can't check for the default view before the view is registered
    # try:
    #     validators.package_name_exists(default_view, context)
    # except validators.Invalid, e:
    #     raise _ValidationError({'defaultView': e.error})

    lc = ckanapi.LocalCKAN(context=context)
    pkg_dict = lc.action.package_show(**{'name_or_id': 'cube-'+str(cube_id)})

    pkg_dict['default_view_id'] = default_view

    result = lc.action.package_update(**pkg_dict)

    return lc.action.GetCube(**{'cubeId': result['product_id_new']})
