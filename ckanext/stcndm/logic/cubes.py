# --coding: utf-8 --

__author__ = 'Statistics Canada'

import datetime

import ckanapi
import ckan.logic as logic
import ckan.plugins.toolkit as toolkit
from ckan.plugins.toolkit import (
    ObjectNotFound,
    ValidationError
)

_get_or_bust = logic.get_or_bust
_get_action = toolkit.get_action


@logic.side_effect_free
def get_next_cube_id(context, data_dict):
    # noinspection PyUnresolvedReferences
    """
    Returns the next available cube_id (without registering it).

    :param subjectCode: two-digit subjectCode (i.e. '24')
    :type subjectCode: str

    :return: next available cube_id
    :rtype: str

    :raises ValidationError
    """

    subject_code = _get_or_bust(data_dict, 'subjectCode')
    if not len(str(subject_code)) == 2:
        raise ValidationError('invalid subject_code')

    query = {
        'q': (
            'extras_productidnew_bi_strs:{subject_code}* AND'
            'extras_producttype_en_strs:Cube'
        ).format(subject_code=subject_code),
        'sort': 'extras_productidnew_bi_strs desc'
    }

    response = _get_action('package_search')(context, query)

    product_id_new = "{subject_code}100001".format(subject_code=subject_code)
    if response['results']:
        for extra in response['results'][0]['extras']:
            if extra['key'] == 'productidnew_bi_strs':
                product_id_response = extra['value']
                if product_id_response.endswith('9999'):
                    # TODO: implement reusing unused IDs
                    raise ValidationError(
                        'All Cube IDs for this subject have been registered.'
                        'Reusing IDs is in development.'
                    )
                else:
                    try:
                        product_id_new = str(int(product_id_response) + 1)
                    except ValueError:
                        pass

    return product_id_new


@logic.side_effect_free
def get_cube(context, data_dict):
    """
    Return a dict representation of a cube, given a cube_id, if it exists.

    :param cube_id: ID of the cube to retrieve. (i.e. 1310001)
    :type cube_id: str
    :type fields: str

    :return: requested cube
    :rtype: dict

    :raises ValidationError, ObjectObjectNotFound
    """
    cube_id = _get_or_bust(data_dict, 'cube_id')
    lc = ckanapi.LocalCKAN(context=context)
    result = lc.action.package_search(
        q=(
            'dataset_type:cube AND '
            'extras_product_id_new:{cube_id}'
        ).format(cube_id=cube_id),
        rows=1
    )

    if not result['count']:
        raise ObjectNotFound('Cube not found')
    elif result['count'] > 1:
        raise ValidationError('More than one cube with given cubeid found')
    else:
        return result['results'][-1]


@logic.side_effect_free
def get_cube_list_by_subject(context, data_dict):
    """
    Return a dict with all Cube Ids and French/English titles based on a
    provided SubjectCode.

    :param subjectCode: two-digit subject code (i.e. 13)
    :type str

    :return: registered cubes for the SubjectCode and their
             French/English titles
    :rtype: list of dicts

    :raises ValidationError, ObjectObjectNotFound
    """
    subject_code = _get_or_bust(data_dict, 'subjectCode')

    if len(subject_code) != 2:
        raise ValidationError('invalid subjectcode')

    lc = ckanapi.LocalCKAN(context=context)
    result = lc.action.package_search(
        q=(
            'dataset_type:cube AND '
            '(extras_subject_codes:{code} OR '
            'extras_subject_codes:{code}*)'
        ).format(code=subject_code),
        rows=1000
    )

    count = result['count']
    if not count:
        raise ObjectNotFound(
            'Found no cubes with subject code {subject_code}'.format(
                subject_code=subject_code
            )
        )
    else:
        return [{
            u'title': r['title'],
            u'cube_id': r['product_id_new']
        } for r in result['results']]


def register_cube(context, data_dict):
    # noinspection PyUnresolvedReferences
    """
    Register a cube in the rgcube organization.  Automatically populate
    subjectcode fields based on provided parameters.

    :param subjectCode: two-digit subject_code code (i.e. 13)
    :type subjectCode: str
    :param productTitleEnglish: english title
    :type productTitleEnglish: str
    :param productTitleFrench: french title
    :type productTitleFrench: str

    :return: new package
    :rtype: dict

    :raises ValidationError
    """

    subject_code = _get_or_bust(data_dict, 'subjectCode')
    title_en = _get_or_bust(data_dict, 'productTitleEnglish')
    title_fr = _get_or_bust(data_dict, 'productTitleFrench')

    if not len(subject_code) == 2:
        raise ValidationError('subjectCode not valid')

    product_type = '10'  # Cube product_type is always 10

    subject_dict = _get_action('ndm_get_subject')(context, {
        'subjectCode': subject_code
    })
    product_type_dict = _get_action('ndm_get_producttype')(context, {
        'productType': product_type
    })
    product_id = _get_action('ndm_get_next_cubeid')(context, data_dict)

    name = '{product_id}'.format(product_id=product_id)
    org = 'statcan'
    extras = []

    time = datetime.datetime.today()

    field_list = _get_action('ndm_get_fieldlist')(context, {"org": org})

    # TODO: Refactor assignment of key-value pairs to a dict
    for field in field_list['fields']:
        if field == '10uid_bi_strs':
            value = product_id
        elif field == 'productidnew_bi_strs':
            value = product_id
        elif field == 'hierarchyid_bi_strs':
            value = product_id
        elif field == 'producttypecode_bi_strs':
            value = product_type_dict['producttypecode_bi_strs']
        elif field == 'producttype_en_strs':
            value = product_type_dict['producttype_en_strs']
        elif field == 'producttype_fr_strs':
            value = product_type_dict['producttype_fr_strs']
        elif field == 'subjnewcode_bi_txtm':
            value = subject_dict['tmtaxsubjcode_bi_tmtxtm']
        elif field == 'subjnew_en_txtm':
            value = subject_dict['tmtaxsubj_en_tmtxtm']
        elif field == 'subjnew_fr_txtm':
            value = subject_dict['tmtaxsubj_fr_tmtxtm']
        elif field == 'lastpublishstatuscode_bi_strs':
            value = 'draft_code'
        elif field == 'lastpublishstatus_en_strs':
            value = 'Draft'
        elif field == 'lastpublishstatus_fr_strs':
            value = 'French_for_draft'
        elif field == 'featureweight_bi_ints':
            value = 0
        elif field == 'title_en_txts':
            value = title_en
        elif field == 'title_fr_txts':
            value = title_fr
        elif field == 'zckcapacity_bi_strs':
            value = 'public'
        elif field == 'zckdbname_bi_strs':
            value = 'rgcube'
        elif field == 'zckownerorg_bi_strs':
            value = 'rgcube'
        elif field == 'zckpubdate_bi_strs':
            value = time.strftime("%Y-%m-%d")
        elif field == 'zckpushtime_bi_strs':
            value = time.strftime("%Y-%m-%d %H:%M")
        elif field == 'zckstatus_bi_txtm':
            value = 'ndm_register_cube_api'
        else:
            value = ''

        extras.append({'key': field, 'value': value})

    package_dict = {
        'name': name,
        'owner_org': 'rgcube',
        'extras': extras
    }

    new_cube = _get_action('package_create')(context, package_dict)

    output = _get_action('ndm_get_cube')(context, {
        'productId': new_cube['name']
    })

    return output
