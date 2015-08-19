# --coding: utf-8 --
__author__ = 'Statistics Canada'

import datetime
from datetime import datetime as dt
import re
from ckan.common import _
import ckan.logic as logic
import ckan.plugins.toolkit as toolkit
from ckanext.stcndm.logic.common import get_product

_get_or_bust = logic.get_or_bust
_stub_msg = {"result": "This method is just a stub for now. Please do not use."}
# noinspection PyUnresolvedReferences
_get_action = toolkit.get_action
# noinspection PyUnresolvedReferences
_ValidationError = toolkit.ValidationError
# noinspection PyUnresolvedReferences
_NotFound = toolkit.ObjectNotFound
# noinspection PyUnresolvedReferences
_NotAuthorized = toolkit.NotAuthorized


@logic.side_effect_free
def get_daily_list(context, data_dict):
    # noinspection PyUnresolvedReferences
    """
    Return a JSON dict representation of one or more instances of Daily.


    :param startDate: required, date of first Daily to return
    :type startDate: str
    :param endDate: optional, if omitted, only return Daily of startDate
    :type endDate: str

    :return: requested Daily or list of Daily
    :rtype: list of dict

    :raises:  ValidationError
    """

    output = []
    start_date_str = _get_or_bust(data_dict, 'startDate')
    try:
        start_date = dt.strptime(start_date_str, '%Y-%m-%d')
    except ValueError:
        raise _ValidationError('startDate \'{0}\' not in YYYY-MM-DD format'.format(start_date_str))

    if 'endDate' in data_dict:
        end_date_str = data_dict['endDate']
        try:
            end_date = dt.strptime(end_date_str, '%Y-%m-%d')
        except ValueError:
            raise _ValidationError('endDate \'{0}\' not in YYYY-MM-DD format'.format(end_date_str))
        days = (end_date - start_date).days + 1
        if days < 1:
            raise _ValidationError(
                _('endDate \'{0}\' must be greater than startDate \'{1}\''.format(end_date_str, start_date_str)))
    else:
        days = 1

    for day in range(days):
        single_date = (start_date + datetime.timedelta(days=day)).date()
        single_date_str = single_date.strftime('%Y-%m-%d')
        q = {'q': 'product_type_code:24 AND release_date:{0}T08\:30'.format(single_date_str)}

        result = _get_action('package_search')(context, q)

        count = result['count']
        if count == 0:
            raise _NotFound('Daily not found for date \'{0}\''.format(single_date_str))
        elif count > 1:
            raise _ValidationError('More than one Daily for date \'{0}\''.format(single_date_str))
        else:
            daily_output = {}
            extras = result['results'][0]['extras']
            for extra in extras:
                daily_output[extra['key']] = extra['value']
                if extra['key'] == 'child_list':
                    children = []
                    child_ids = extra['value'].split('; ')
                    for child_id in child_ids:
                        child_result = get_product(context, {'productId': child_id})
                        for a_child_result in child_result:
                            children.append(a_child_result)
                    daily_output['children'] = children

        output.append(daily_output)

    return output


def register_daily(context, data_dict):
    # noinspection PyUnresolvedReferences
    """
    Register a Daily in the maprimary organization.

    Automatically populate fields based on provided parameters.

    :param productId: 00240001 followed by 3 - 6 digit
        sequence id (i.e. 00240001654321)
    :type productId: str
    :param productTitle: EN/FR title
    :type productTitle: dict
    :param lastPublishStatusCode: 1 or 2 digit number
    :type lastPublishStatusCode: str
    :param releaseDate: e.g. 2015-06-30T09:45
    :type releaseDate: str
    :param uniqueId: e.g. daily3456
    :type uniqueId: str
    :param childList: list of IDs of child products
    :type childList: str

    :return: new package
    :rtype: dict

    :raises: ValidationError
    """

    my_org_type = 'maprimary'
#    time = datetime.datetime.today()

    product_id = _get_or_bust(data_dict, 'productId')
    if not re.match('^00240001[0-9]{3,6}$', product_id):
        raise _ValidationError(_('Invalid product id for Daily: {0}'.format(product_id)))

    #  check whether the product ID we were given is already in use
    q = {'q': 'product_id_new:{0}'.format(product_id)}
    result = _get_action('package_search')(context, q)
    count = result['count']
    if count:
        raise _ValidationError(_("product Id '{0}' already in use".format(product_id)))

    title = _get_or_bust(data_dict, 'productTitle')

    release_date_str = _get_or_bust(data_dict, 'releaseDate')
    try:
        release_date = datetime.datetime.strptime(release_date_str, '%Y-%m-%d')
    except ValueError:
        raise _ValidationError(
            _("Incorrect format for releaseDate '{0}', should be YYYY-MM-DD".format(release_date_str)))
#    publish_status_dict = _get_action('ndm_get_last_publish_status')(context, data_dict)

    unique_id = _get_or_bust(data_dict, 'uniqueId')
    if not re.match('^daily[0-9]{3,4}$', unique_id):
        raise _ValidationError(_("Invalid unique ID for Daily: '{0}'".format(unique_id)))

    product_type_code = '24'
    data_dict['productType'] = product_type_code  # Daily always has productCode 24
#    product_type_dict = _get_action('ndm_get_product_type')(context, data_dict)
    last_publish_status_code = _get_or_bust(data_dict, 'lastPublishStatusCode')

    child_list = _get_or_bust(data_dict, 'childList')
    if not child_list:
        raise _ValidationError(_('childList must contain at least one child ID'))
    for child in child_list:
        if not isinstance(child, basestring):
            raise _ValidationError(_('Items in childList must all be strings'))

    extras_dict = {}

    """ for now we won't instantiate all fields to avoid giving unintended meaning to empty fields
    field_list = _get_action('ndm_get_fieldlist')(context, {'org': my_org_type})
    for field in field_list['fields']:
        if str(field).endswith('ints'):
            extras_dict[field] = 0
        else:
            extras_dict[field] = ''
    """

#    extras_dict['10uid_bi_strs'] = product_id
    extras_dict['product_id_new'] = product_id
#    for key in product_type_dict:
#        extras_dict[key] = unicode(product_type_dict[key])
    extras_dict['product_type_code'] = product_type_code
#    for key in publish_status_dict:
#        extras_dict[key] = unicode(publish_status_dict[key])
    extras_dict['last_publish_status_code'] = last_publish_status_code
    extras_dict['parent_product'] = product_id
    extras_dict['title'] = title
#    extras_dict['zckcapacity_bi_strs'] = 'public'
#    extras_dict['zckownerorg_bi_strs'] = my_org_type
#    extras_dict['zckpubdate_bi_strs'] = time.strftime("%Y-%m-%d")
#    extras_dict['zckpushtime_bi_strs'] = time.strftime("%Y-%m-%d %H:%M")
#    extras_dict['zckstatus_bi_txtm'] = 'ndm_register_daily_api'
    extras_dict['release_date'] = release_date.strftime("%Y-%m-%dT08:30")
#    extras_dict['pkuniqueidcode_bi_strs'] = unique_id
    extras_dict['child_list'] = '; '.join(child_list)

    extras = []
    for key in extras_dict:
        extras.append({'key': key, 'value': extras_dict[key]})

    package_dict = {'name': product_id,
                    'owner_org': my_org_type,
                    'extras': extras,
                    'title': unique_id}
    new_product = _get_action('package_create')(context, package_dict)
    output = _get_action('ndm_get_product')(context, {'productId': new_product['name'],
                                                      'fl': 'product_id_new'})
    return output


@logic.side_effect_free
def get_themes(context, data_dict):
    """
    Returns a dict of themes (subjects) with ID, English label, French label, code values and
    hierarchy information for each theme.

    :return: A dictionary containing the English, French and code values for given subjectCode for each entry
    :rtype: dict
    """

    output = _stub_msg

    return output


@logic.side_effect_free
def get_surveys(context, data_dict):
    """
    Returns a list of surveys with ID, English label, and French label for each survey.

    :return: A dictionary containing the ID, English label, and French label for each survey.
    :rtype: dict
    """

    output = _stub_msg

    return output


@logic.side_effect_free
def get_default_views(context, data_dict):
    """
    Returns a list of the default views with the Product ID, English label, and French label for each default view.

    :return: A dictionary containing the Product ID, English label, and French label in each default view.
    :rtype: dict
    """

    output = _stub_msg

    return output


@logic.side_effect_free
def get_product_issues(context, data_dict):
    """
    Returns a list of the issues for the product ID
    :param: productId: A non-data product ID.

    :return: A dictionary containing the issues for the specified product
    :rtype: dict
    """

    product_id = _get_or_bust(data_dict, 'productId')

    output = _stub_msg

    return output


@logic.side_effect_free
def get_product_issue_articles(context, data_dict):
    """
    Returns a list of the articles for the specific product/issue number
    :param: productId: A non-data product ID.
    :param: issueNo: The issue number

    :return: A dictionary containing the articles for the specified product and issue
    :rtype: dict
    """

    product_id = _get_or_bust(data_dict, 'produc:tId')
    issue_no = _get_or_bust(data_dict, 'issueNo')

    output = _stub_msg

    return output


@logic.side_effect_free
def get_bookable_releases(context, data_dict):
    """
    Returns a list of the products, issues and formats that a user
    may edit, based on the provided FRC codes

    :param frcCodes: A list of FRC Codes
    :return: A dictionary containing the products, associated issues
        and formats for articles for the specified
        product and issue
    :rtype: dict
    """

    output = _stub_msg

    return output
