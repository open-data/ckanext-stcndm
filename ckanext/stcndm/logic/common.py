__author__ = 'Statistics Canada'

import ckan.logic as logic
import ckan.plugins.toolkit as toolkit

_get_or_bust = logic.get_or_bust

def get_product(context, data_dict):  # this one is for external use. just use package_show internally
    """
    Return a JSON dict representation of a product, given a ProductId, if it exists.

    :param productId: product id (i.e. 2112002604)
    :type productId: str
    :param fields: desired output fields. (i.e. "title_en_txts,title_fr_txts,ProductIdnew_bi_strs") Default: *
    :type fields: str

    :return: requested product fields and values
    :rtype: dict
    """

    productid = _get_or_bust(data_dict, 'productId')

    try:
        desired_fields = data_dict['fields']
        desired_fields_list = []
        for field in desired_fields.split(','):
            desired_fields_list.append(field)
        limit_fields = True
    except KeyError:
        limit_fields = False

    q = {'q': 'extras_productidnew_bi_strs:{productid}'.format(productid=productid)}

    result = toolkit.get_action('package_search')(context, q)

    count = result['count']
    if count == 0:
        raise toolkit.ObjectNotFound('product not found')
    elif count > 1:
        raise toolkit.Invalid('More than one product with given productId found')
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
