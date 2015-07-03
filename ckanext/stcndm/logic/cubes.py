# --coding: utf-8 --

__author__ = 'Statistics Canada'

import ckan.logic as logic
import ckan.plugins.toolkit as toolkit

_get_or_bust = logic.get_or_bust

@logic.side_effect_free
def get_cube(context, data_dict):  # this one is for external use. just use list_package internally
    """
    Return a dict representation of a cube, given a cubeid, if it exists.

    :param productId: cube id (i.e. 1310001)
    :type productId: str
    :param fields: desired output fields. (i.e. "title_en_txts,title_fr_txts,ProductIdnew_bi_strs") Default: *
    :type fields: str

    :return: requested cube fields and values
    :rtype: dict
    """

    cubeid = _get_or_bust(data_dict, 'productId')

    try:
        desired_fields = data_dict['fields']
        desired_fields_list = []
        for field in desired_fields.split(','):
            desired_fields_list.append(field)
        limit_fields = True
    except:
        limit_fields = False

    q = {'q': 'extras_productidnew_bi_strs:{cubeid} AND extras_producttype_en_strs:Cube'.format(cubeid=cubeid)}

    result = toolkit.get_action('package_search')(context, q)

    count = result['count']

    if count == 0:
        raise toolkit.ObjectNotFound('Cube not found')
    elif count > 1:
        raise toolkit.Invalid('More than one cube with given cubeid found')
    else:
        output = {}

        extras = result['results'][0]['extras']
        for extra in extras:

            if limit_fields:
                if extra['key'] in desired_fields_list:
                    output[extra['key']] = extra['value']
            else:
                output[extra['key']] = extra['value']
        return output
