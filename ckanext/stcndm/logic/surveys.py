#!/usr/bin/env python
# encoding: utf-8
import ckanapi
import ckan.logic as logic


@logic.side_effect_free
def get_survey_codesets(context, data_dict):
    """
    Returns all survey codesets.

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
        q='dataset_type:survey',
        rows=limit,
        start=start,
        fl=(
            'name',
            'title'
        )
    )

    return {
        'count': results['count'],
        'limit': limit,
        'start': start,
        'results': [{
            'survey_code': r['product_id_new'],
            'title': r['title'],
        } for r in results['results']]
    }
