# --coding: utf-8 --
import re
import json
import textwrap
import datetime
from datetime import datetime as dt

from ckan.common import _
from ckan.lib.search.common import make_connection
import ckan.logic as logic
import ckan.plugins.toolkit as toolkit
from ckan.plugins.toolkit import missing

import ckanapi
from ckanext.stcndm.logic.common import get_product
from ckanext.stcndm.helpers import set_related_id
from dateutil.parser import parse
from dateutil.tz import gettz
from ckanext.stcndm.helpers import to_utc, default_release_date

__author__ = 'Statistics Canada'

_get_or_bust = logic.get_or_bust
_stub_msg = {
    'result': 'This method is just a stub for now. Please do not use.'
}
# noinspection PyUnresolvedReferences
_get_action = toolkit.get_action
# noinspection PyUnresolvedReferences
_ValidationError = toolkit.ValidationError
# noinspection PyUnresolvedReferences
_NotFound = toolkit.ObjectNotFound
# noinspection PyUnresolvedReferences
_NotAuthorized = toolkit.NotAuthorized


# noinspection PyIncorrectDocstring
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
        dt.strptime(start_date_str, '%Y-%m-%d')
    except ValueError:
        raise _ValidationError(
            'startDate \'{0}\' not in YYYY-MM-DD format'.format(start_date_str)
        )
    start_date = parse(start_date_str,
                       default=default_release_date).astimezone(gettz('UTC'))

    if 'endDate' in data_dict:
        end_date_str = data_dict['endDate']
        try:
            dt.strptime(end_date_str, '%Y-%m-%d')
        except ValueError:
            raise _ValidationError(
                'endDate \'{0}\' not in YYYY-MM-DD format'.format(end_date_str)
            )
        end_date = parse(end_date_str,
                         default=default_release_date).astimezone(gettz('UTC'))
        days = (end_date - start_date).days + 1
        if days < 1:
            raise _ValidationError(_(
                'endDate \'{0}\' must be greater '
                'than startDate \'{1}\''.format(
                    end_date_str,
                    start_date_str
                )
            ))
    else:
        days = 1

    for day in range(days):
        single_date = (start_date + datetime.timedelta(days=day))
        single_date_str = single_date.replace(tzinfo=None).isoformat()
        q = {
            'q': (
                'product_type_code:24 AND '
                'last_release_date:"{release_date}Z"'.format(
                    release_date=single_date_str
                )
            )
        }

        results = _get_action('package_search')(context, q)

        count = results['count']
        if count > 1:
            raise _ValidationError(
                'More than one Daily for date \'{0}\''.format(single_date_str)
            )

        for result in results['results']:
            children = []

            for child in result.get('child_list', []):
                children.append(
                    get_product(context, {
                        'productId': child
                    })
                )

            result['children'] = children
            output.append(result)

    return output


# noinspection PyIncorrectDocstring
def register_daily(context, data_dict):
    # noinspection PyUnresolvedReferences
    """
    Register a Daily.

    Automatically populate fields based on provided parameters.

    :param releaseDate: e.g. 2015-06-30T09:45
    :type releaseDate: datetime - required
    :param productId: 00240001 followed by 3 - 6 digit
        sequence id (i.e. 00240001654321)
    :type productId: str - required
    :param statsInBrief: 0 - do not display in navigation
                         1 - display in navigation
    :type statsInBrief: str - required
    :param productTitle: EN/FR title
    :type productTitle: dict - required
    :param referencePeriod: EN/FR reference period
    :type referencePeriod: dict - required
    :param themeList: list of theme IDs
    :type themeList: list - required
    :param cubeList: list of related cube IDs
    :type cubeList: list - optional
    :param surveyList: list of theme IDs
    :type surveyList: list - optional
    :param productList: list of IDs of child products
    :type productList: list - optional
    :param url: EN/FR url
    :type url: dict - required

    :return: new package
    :rtype: dict

    :raises: ValidationError
    """

    def my_get(a_data_dict, key, expected, required=True):
        value = a_data_dict.get(key)
        if value:
            if not isinstance(value, expected):
                raise _ValidationError(
                    {key: u'Invalid format ({value}), '
                          u'expecting a {type}'.format(
                            value=value,
                            type=expected.__name__)})
        elif required:
            raise _ValidationError({key: u'Missing value'})
        return value

    release_date_str = my_get(data_dict, u'releaseDate', basestring)
    product_id = my_get(data_dict, u'productId', basestring)
    if not re.match('^00240001[0-9]{3,6}$', product_id):
        raise _ValidationError(
            {u'product_id':
                u'Invalid ({product_id}), '
                u'expected 00240001 followed by '
                u'3 - 6 digit sequence number'.format(
                    product_id=product_id)})

    lc = ckanapi.LocalCKAN(context=context)
    stats_in_brief = my_get(data_dict, u'statsInBrief', basestring)
    if stats_in_brief not in [u'0', u'1']:
        raise _ValidationError(
            {u'stats_in_brief':
                u'Invalid ({value}), expecting 0 or 1 '.format(
                    value=stats_in_brief)})
    if stats_in_brief == u'0':
        display_code = u'3'  # Hide Product Info page & Navigation Link
        content_type_codes = [u'2015']  # Other
    else:
        display_code = u'1'  # Show Product Info Page
        content_type_codes = [u'2016']  # Analysis/Stats in brief
    product_title = my_get(data_dict, u'productTitle', dict)
    reference_period = my_get(data_dict, u'referencePeriod', dict)
    theme_list = my_get(data_dict, u'themeList', list)
    related = []
    cube_list = my_get(data_dict, u'cubeList', list, required=False)
    if cube_list:
        related.extend(cube_list)
    survey_list = my_get(data_dict, u'surveyList', list, required=False)
    if survey_list:
        related.extend(survey_list)
    product_list = my_get(data_dict, u'productList', list, required=False)
    if product_list:
        related.extend(product_list)
    url = my_get(data_dict, u'url', dict)

    daily_dict = {
        u'name': u'daily-{0}'.format(product_id),
        u'owner_org': u'statcan',
        u'private': False,
        u'product_type_code': u'24',
        u'type': u'daily',
        u'content_type_codes': content_type_codes,
        u'last_release_date': to_utc(release_date_str,
                                     def_date=default_release_date),
        u'product_id_new': product_id,
        u'display_code': display_code,
        u'title': product_title,
        u'reference_period': reference_period,
        u'subject_codes': theme_list,
        u'related_products': related if related else missing,
        u'url': url
    }
    try:
        new_product = lc.action.package_create(**daily_dict)
    except _ValidationError as e:
        if e.error_dict.get('name', []) == [u'That URL is already in use.']:
            new_product = lc.action.package_update(**daily_dict)
        else:
            raise

    new_product = lc.action.GetProduct(
        productId=new_product['product_id_new'],
        fl='product_id_new'
    )
    set_related_id(product_id, related)

    return new_product


# noinspection PyIncorrectDocstring
@logic.side_effect_free
def get_default_views(context, data_dict):
    # noinspection PyUnresolvedReferences
    """
    Returns a list of the default views.

    :param frc: FRC code to filter on.
    :return: A dictionary containing the Product ID, English label, and French
             label in each default view.
    :rtype: dict
    """
    frc = _get_or_bust(data_dict, 'frc')

    lc = ckanapi.LocalCKAN(context=context)

    cube_results = lc.action.package_search(
        q=(
            'type:cube AND frc:{frc}'
        ).format(
            frc=frc
        ),
    )

    final_results = []

    for cube_result in cube_results.get('results') or []:
        if not cube_result.get('default_view_id'):
            # We don't care about cubes that have no default_view_id,
            # which may occur.
            continue

        view_results = lc.action.package_search(
            q=(
                'type:view AND product_id_new:{view_id} AND '
                '-discontinued_code:1'
            ).format(
                view_id=cube_result['default_view_id']
            ),
            rows=1
        )

        if not view_results['count']:
            continue

        view = view_results['results'][0]

        final_results.append({
            u'cube': {
                u'frequency': cube_result.get('frequency_codes') or []
            },
            u'view': {
                u'title': view['title'],
                u'id': view['product_id_new']
            }
        })

    return final_results


# noinspection PyIncorrectDocstring
@logic.side_effect_free
def get_product_issues(context, data_dict):
    # noinspection PyUnresolvedReferences
    """
    Returns a list of the issues for the product ID
    :param: productId: A non-data product ID.

    :return: A dictionary containing the issues for the specified product
    :rtype: dict
    """
    product_id = _get_or_bust(data_dict, 'productId')

    slr = make_connection()

    response = json.loads(
        slr.raw_query(
            q='top_parent_id:{pid}'.format(
                pid=product_id
            ),
            group='true',
            group_field='issue_number_int',
            wt='json',
            sort='issue_number_int desc',
            # FIXME: We need to actually paginate on this, but the daily
            #        team will not accept it (yet).
            rows='2000000'
        )
    )

    issue_no_group = response['grouped']['issue_number_int']

    return [{
        'issue': group['groupValue'],
        'number_articles': group['doclist']['numFound']
    } for group in issue_no_group['groups']]


# noinspection PyIncorrectDocstring
@logic.side_effect_free
def get_product_issue_articles(context, data_dict):
    # noinspection PyUnresolvedReferences
    """
    Returns a list of the articles for the specific product/issue number
    :param: productId: A non-data product ID.
    :param: issueNo: The issue number

    :return: A dictionary containing the articles for the specified product and
             issue
    :rtype: dict
    """

    product_id = _get_or_bust(data_dict, 'productId')
    issue_number = _get_or_bust(data_dict, 'issueNo')

    lc = ckanapi.LocalCKAN(context=context)

    results = lc.action.package_search(
        q=(
            'top_parent_id:{pid} AND '
            'issue_number_int:{issue_number} AND '
            'type:article'
        ).format(
            pid=product_id,
            issue_number=issue_number
        ),
        # FIXME: We need to actually paginate on this, but the daily
        #        team will not accept it (yet).
        rows='2000000',
        fl=[
            'title',
            'product_id_new'
        ]
    )

    return [{
        'title': result['title'],
        'article_id': result['product_id_new'],
        'release_date': result['last_release_date']
    } for result in results['results']]


# noinspection PyIncorrectDocstring
@logic.side_effect_free
def get_bookable_releases(context, data_dict):
    # noinspection PyUnresolvedReferences
    """
    Returns a list of the products, issues and formats that a user
    may edit, based on the provided FRC codes

    :param frcCodes: A list of FRC Codes
    :return: A dictionary containing the products, associated issues
        and formats for articles for the specified
        product and issue
    :rtype: dict
    """
    frc = _get_or_bust(data_dict, 'frc')

    lc = ckanapi.LocalCKAN(context=context)

    results = lc.action.package_search(
        q='frc:{frc} AND type:publication'.format(
            frc=frc
        ),
        fl=[
            'product_id_new',
            'title'
        ]
    )

    final_results = []
    for result in results['results']:
        article_results = lc.action.package_search(
            q=(
                'top_parent_id:{pid} '
                # Only "Working Copy" results.
                'AND status_code:31 '
                # With a release_date set to anything (not blank)
                'AND last_release_date:[* TO *] '
                'AND type:article'
            ).format(
                pid=result['product_id_new']
            ),
            sort='issue_number_int asc',
            # FIXME: We need to actually paginate on this, but the daily
            #        team will not accept it (yet).
            rows=2000000
        )

        for art_result in article_results['results']:
            final_results.append({
                'productId': result['product_id_new'],
                'issue': art_result['issue_number_int'],
                'title': result['title'],
                'refper': result['reference_period']
            })

    return final_results


# noinspection PyIncorrectDocstring
@logic.side_effect_free
def get_themes(context, data_dict):
    # noinspection PyUnresolvedReferences
    """
    Returns all subject codesets.

    :param limit: Number of results to return.
    :type limit: int
    :param start: Number of results to skip.
    :type start: int

    :rtype: list of dicts
    """
    lc = ckanapi.LocalCKAN(context=context)

    # Sort would perform better, but this will be easier
    # for client to implement.
    limit = int(logic.get_or_bust(data_dict, 'limit'))
    start = int(logic.get_or_bust(data_dict, 'start'))

    results = lc.action.package_search(
        q='dataset_type:subject',
        rows=limit,
        start=start,
        fl=(
            'name',
            'title'
        )
    )

    def _massage(s):
        chunked = textwrap.wrap(s['subject_code'], 2)
        return (
            s['subject_code'],
            chunked[-2] if len(chunked) > 1 else None,
            s['title'],
            dict((k, v.split('/')[-1]) for k, v in s['title'].iteritems())
        )

    return {
        'count': results['count'],
        'limit': limit,
        'start': start,
        'results': [{
            'subject_code': rr[0],
            'parent_subject_code': rr[1],
            'title': rr[2],
            'subject_title': rr[3]
        } for rr in (_massage(r) for r in results['results'])]
    }


# noinspection PyIncorrectDocstring
@logic.side_effect_free
def get_product_formats(context, data_dict):
    # noinspection ,PyUnresolvedReferences
    """
    Returns a list of bookable formats for the specific product/issue number

    :param: productId: A non-data product ID.
    :param: issueNo: The issue number

    :return: A dictionary containing the formats for the specified product and
             issue
    :rtype: dict
    """
    product_id = _get_or_bust(data_dict, 'productId')
    issue_number = _get_or_bust(data_dict, 'issueNo')

    lc = ckanapi.LocalCKAN(context=context)

    art_results = lc.action.package_search(
        q=(
            'top_parent_id:{pid} AND '
            'issue_number_int:{issue_number} AND '
            'type:article'
        ).format(
            pid=product_id,
            issue_number=issue_number
        ),
        # FIXME: We need to actually paginate on this, but the daily
        #        team will not accept it (yet).
        rows=2000000
    )

    final_results = []

    for art_result in art_results['results']:
        fmt_results = lc.action.package_search(
            q=(
                'parent_id:{pid} AND '
                # We only want formats that have no release date set.
                '-last_release_date:[* TO *]'
            ).format(
                pid=art_result['product_id_new']
            ),
            rows=50
        )

        final_results.extend(fmt_results['results'])

    return final_results


# noinspection PyIncorrectDocstring
@logic.side_effect_free
def get_products_by_frc(context, data_dict):
    # noinspection PyUnresolvedReferences
    """

    :param frc:
    :type frc: str
    :param data_dict:

    :return: list of dict
    """
    frc = _get_or_bust(data_dict, 'frc')

    lc = ckanapi.LocalCKAN(context=context)

    results = lc.action.package_search(
        q='frc:{frc} AND type:publication'.format(frc=frc),
        rows=2000000
    )

    return [{
        'title': r['title'],
        'productId': r['product_id_new']
    } for r in results['results']]
