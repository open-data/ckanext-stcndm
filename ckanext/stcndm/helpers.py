#!/usr/bin/env python
# encoding: utf-8
import re
import ast
import json
import requests
from datetime import datetime, timedelta
from functools import wraps

import ckanapi
import ckan.model as model
import pylons.config as config
from ckan.logic import _, ValidationError, get_action
from ckan.common import c
from ckanext.scheming.helpers import (
    scheming_get_preset,
    scheming_dataset_schemas
)
import logging
log = logging.getLogger('ckan.logic')
__author__ = 'matt'

ndm_audit_log_component_id = 10


class NotValidProduct(Exception):
    pass


def dict_list2dict(dict_list):
    d = dict()

    for dict_item in dict_list:
        d[dict_item['key']] = dict_item['value']

    return d


def x2list(value):
    if isinstance(value, list):
        return value
    if isinstance(value, str):
        return map(unicode.strip, unicode(value).split(';'))
    if isinstance(value, unicode):
        return map(unicode.strip, value.split(';'))
    if isinstance(value, dict):
        return dict2dict_list(value)
    return []


def dict2dict_list(dictionary):
    dl = list()

    for key in dictionary.keys():
        dl.append({'key': key, 'value': dictionary[key]})

    return dl


def get_schema(org, dataset):
    """
    Return a dict having fields in a given org for keys and the values stored
    for that field in the tmschema organization as a dict.

    :param org:
    :param dataset:
    :return: dict of dicts
    """

    context = {'model': model, 'session': model.Session, 'user': c.user}

    data_dict = {'org': org, 'dataset': dataset}

    result = get_action('ndm_get_schema')(context, data_dict)

    return result


def get_dataset_types():
    lc = ckanapi.LocalCKAN()
    types = lc.action.package_search(
        q='*:*',
        rows=0,
        facet='true',
        **{"facet.field": ["dataset_type"]}
    )['search_facets']['dataset_type']['items']
    schemas = scheming_dataset_schemas()
    result = {}

    for schema in schemas:
        result[schema] = {
            'title': schemas[schema]['catalog_type_label'],
            'count': 0
        }

        for type in types:
            if schema == type['name']:
                result[schema]['count'] = type['count']
                break

    return sorted(result.iteritems(), key=lambda type: type[1], reverse=True)


def get_parent_dataset(top_parent_id, dataset_id):
    lc = ckanapi.LocalCKAN()

    q = 'product_id_new:{parent_id}'.format(parent_id=top_parent_id)

    if dataset_id:
        q += 'AND NOT product_id_new:{id}'.format(id=dataset_id)

    parents = lc.action.package_search(
        q=q,
        sort='metadata_created ASC',
        rows=1000
    )['results']

    if parents:
        return parents[0]


def get_child_datasets(dataset_id):
    lc = ckanapi.LocalCKAN()
    return lc.action.package_search(
        q='top_parent_id:{pid} AND NOT product_id_new:{pid}'.format(
            pid=dataset_id
        ),
        rows=1000
    )['results']


def generate_revision_list(data_set):
    """
    :param data_set:
    :return:
    """
    # FIXME: Placeholder? What is this method for.
    # context = {'model': model, 'session': model.Session, 'user': c.user}


# TODO: rename this
def show_fields_changed_between_revisions(pkg_name, pkg_revisions):
    """
    :param pkg_name: name or id of package
    :type pkg_name: str
    :param pkg_revisions: revision details
    :type pkg_revisions: list of dicts

    :return: string
    """

    context = {'model': model, 'session': model.Session, 'user': c.user}

    revisions_dict = {}

    revision_order = []
    for revision in pkg_revisions:

        # The revision id needs to be passed through the context rather than
        # data_dict (base CKAN quirk)
        context['revision_id'] = revision['id']

        revision_pkg = get_action('package_show')(context, {'id': pkg_name})

        revision_extras_dict = {}

        # TODO: This will change when we move to scheming, but presently only
        # extras are important

        for extra in revision_pkg['extras']:
            revision_extras_dict[extra['key']] = extra['value']

        revisions_dict[revision['id']] = revision_extras_dict

        revision_order.append(revision['id'])

    def _pairs(lst):
        i = iter(lst)
        prev = i.next()
        for item in i:
            yield prev, item
            prev = item

    revisions_to_compare = _pairs(revision_order)

    next_record = {}
    modified_fields_dict = {}

    for pair in revisions_to_compare:

        new_dict = revisions_dict[pair[0]]
        old_dict = revisions_dict[pair[1]]

        modified_fields_dict[pair[0]] = []
        for k, v in new_dict.iteritems():

            try:
                if old_dict[k] != new_dict[k]:
                    modified_fields_dict[pair[0]].append(k)
            except KeyError:
                # also include added and deleted fields
                modified_fields_dict[pair[0]].append(k)

        modified_fields_dict[pair[0]].sort()

        next_record[pair[0]] = pair[1]

    return {
        'modified_fields': modified_fields_dict,
        'next_record': next_record
    }


def codeset_choices(codeset_type):
    """
    Return a dictionary of {codeset_value: title} for the codeset_type
    passed
    :param codeset_type:
    :type codeset_type: str
    :return dict
    """
    lc = ckanapi.LocalCKAN()
    results = lc.action.package_search(
        q='type:codeset',
        fq='-display_in_form:"0" +codeset_type:' + codeset_type,
        rows=1000)
    return dict((r['codeset_value'], r['title']) for r in results['results'])


def lookup_label(field_name, field_value, lookup_type):
    """
    Given the name of a field, the value of the field, and the type of lookup
    to perform, resolve the code and return the label.

    :param field_name: The name of the field being resolved (ex: format_code).
    :param field_value: The value of the field being resolved. (ex: '33')
    :param lookup_type: The type of field being resolved (ex: codeset)

    :return dict
    """
    lc = ckanapi.LocalCKAN()

    if not field_value:
        return {u'en': '', u'fr': ''}

    default = {
        u'en': 'label for ' + field_value,
        u'fr': 'description de ' + field_value,
        u'found': False
    }

    if not lookup_type:
        return default

    if lookup_type == 'preset':
        preset = scheming_get_preset('ndm_{f}'.format(f=field_name))
        if not preset:
            return default

        choices = preset['choices']
        for choice in choices:
            if choice['value'] == field_value:
                return choice['label']

        return default
    elif lookup_type == 'codeset':
        results = lc.action.package_search(
            q=(
                u'dataset_type:codeset AND '
                'codeset_type:{f} AND '
                'codeset_value:{v}'
            ).format(
                f=field_name,
                v=field_value
            )
        )

        if not results[u'count']:
            return default

        result = results[u'results'][-1][u'title']
        if isinstance(result, basestring):
            try:
                result = ast.literal_eval(result)
            except SyntaxError:
                pass

        return result
    else:
        results = lc.action.package_search(
            q=(
                u'dataset_type:{lookup_type} AND '
                'name:{lookup_type}-{field_value}'
            ).format(
                lookup_type=lookup_type,
                field_value=field_value.lower()
            )
        )
        if not results[u'count']:
            return default

        result = results[u'results'][-1][u'title']
        if isinstance(result, basestring):
            try:
                result = ast.literal_eval(result)
            except SyntaxError:
                pass

        return result


def next_correction_id():
    """
    :return next available correction id
    """
    lc = ckanapi.LocalCKAN()
    result = lc.action.package_search(
        q='correction_id:*',
        fq='type:correction',
        sort='correction_id_int DESC',
        rows=1
    )

    last_id = 0
    if result['count'] and 'correction_id' in result['results'][0]:
        try:
            last_id = int(result['results'][0]['correction_id'])
        except ValueError:
            pass
    if last_id >= 2000:
        return unicode(last_id + 1)
    else:
        return u'2000'


def next_non_data_product_id(subject_code, product_type_code):
    """
    Get next available product ID
    :param subject_code:
    :type subject_code: 2 digit str
    :param product_type_code:
    :type product_type_code: 2 digit str
    :return:
    """
    valid_product_codes = [
        '20',
        '21',
        '22',
        '23',
        '25',
        '26'
    ]

    if not isinstance(subject_code, basestring) or \
            not re.match('^\d\d$', subject_code):
        raise ValidationError((_('Invalid subject code.'),))

    if isinstance(product_type_code, basestring):
        if product_type_code not in valid_product_codes:
            error_message = 'Invalid product type code. ' \
                            'Expected one of {codes!r}'.format(
                                codes=valid_product_codes,
                            )
            raise ValidationError((_(error_message),))

    i = 0
    n = 1
    product_sequence_number = 1
    while i < n:
        lc = ckanapi.LocalCKAN()
        results = lc.action.package_search(
            q='product_id_new:{subject_code}{product_type_code}????'.format(
                subject_code=subject_code,
                product_type_code=product_type_code
            ),
            sort='product_id_new ASC',
            rows=1000,
            start=i*1000
        )
        n = results['count'] / 1000.0
        i += 1
        for result in results['results']:
            if product_sequence_number < int(result['product_id_new'][5:8]):
                return (
                    u'{subject_code}'
                    '{product_type_code}'
                    '{sequence_number}'
                ).format(
                    subject_code=subject_code,
                    product_type_code=product_type_code,
                    sequence_number=unicode(product_sequence_number).zfill(4)
                )
            else:
                product_sequence_number += 1

    return u'{subject_code}{product_type_code}{sequence_number}'.format(
        subject_code=subject_code,
        product_type_code=product_type_code,
        sequence_number=unicode(product_sequence_number).zfill(4)
    )


def next_article_id(top_parent_id, issue_number):
    """
    Get next available product ID

    :param top_parent_id:
    :type top_parent_id: 8 digit str
    :param issue_number
    :type issue_number: 7 digit str
    :return: 19 or 20 digit str
    """
    if not isinstance(top_parent_id, basestring) or len(top_parent_id) != 8:
        raise ValidationError(
            (_('Invalid top parent ID. Expected 8 digit string'),)
        )
    if not isinstance(issue_number, basestring) or len(issue_number) != 7:
        raise ValidationError(
            (_('Invalid issue number. Expected 7 digit string'),)
        )

    i = 0
    n = 1
    article_sequence_number = 1
    lc = ckanapi.LocalCKAN()
    while i < n:
        results = lc.action.package_search(
            q=(
                'type:article AND '
                'product_id_new:{top_parent_id}{issue_number}*'
            ).format(
                top_parent_id=top_parent_id,
                issue_number=issue_number
            ),
            sort='product_id_new ASC',
            rows=1000,
            start=i*1000
        )
        if results['count'] == 0:
            return u'{top_parent_id}{issue_number}{sequence_number}'.format(
                top_parent_id=top_parent_id,
                issue_number=issue_number,
                sequence_number=unicode(article_sequence_number).zfill(5)
            )

        n = results['count'] / 1000.0
        i += 1
        for result in results['results']:
            old_id = int(result['product_id_new'][15:])
            article_sequence_number = max(
                article_sequence_number,
                old_id
            )

    return (
        u'{top_parent_id}'
        '{issue_number}'
        '{sequence_number}'
    ).format(
        top_parent_id=top_parent_id,
        issue_number=issue_number,
        sequence_number=unicode(article_sequence_number + 1).zfill(5)
    )


def ensure_release_exists(product_id, context=None, ref_period=None):
    """
    Ensure that a release exists for the given product_id.

    :param product_id: The parent product ID.
    :type product_id: str
    :param context: The CKAN request context (if it exists)
    :type context: dict or None
    :param ref_period: The (data) reference period for the release, if one
                       exists.
    """
    # FIXME: the following test is a kludge which exits if loading from ckanapi
    #        need to at least compare to site_id instead of fixed value stcndm
    if context['auth_user_obj'].name == u'stcndm':
        return

    rsu = config.get('ckanext.stcndm.release_service_url')
    if not rsu:
        # The release service isn't always available depending on where
        # CKAN is deployed.
        return

    lc = ckanapi.LocalCKAN(context=context)

    response = lc.action.package_search(
        q='product_id_new:{pid} OR format_id:{pid}'.format(
            pid=product_id
        ),
        rows=1
    )

    results = response['results']

    if not results:
        # API might have deleted the product before we had a chance to push
        # it out.
        return

    product = results[0]

    record = {
        'ProductId': product_id,
        'PublishStatus': 2,
        'IsMetadata': product.get('type', u'') == u'cube',
    }

    last_release_date = product.get('last_release_date')
    if last_release_date:
        # The cloning extension causes this to be a string for some reason,
        # possibly a bug in the extension.
        if isinstance(last_release_date, basestring):
            last_release_date = datetime.strptime(
                last_release_date,
                '%Y-%m-%d %H:%M:%S'
            )

        record['ReleaseDate'] = {
            'year': last_release_date.year,
            'month': last_release_date.month,
            'day': last_release_date.day,
            'hour': last_release_date.hour,
            'minute': last_release_date.minute
        }

    cp_fields = [
        ('PublishStatus', 'last_publish_status_code', int),
        ('Format', 'format_code', int),
        ('Issue', 'issue_number', None),
        ('DataReferencePeriod', 'reference_period', None),
        ('ProductCode', 'product_type_code', int),
    ]

    for field_dst, field_src, cast_to in cp_fields:
        val = product.get(field_src)
        if not val:
            continue
        record[field_dst] = cast_to(val) if cast_to is not None else val

    try:
        r = requests.post(rsu, params={
            'productType':  str(product['type']).capitalize(),
        }, data=json.dumps({
            'recordInfo': record
        }), headers={
            'Content-Type': 'application/json'
        }, timeout=5)
        if not r.status_code == 200:
            write_audit_log("ensure_release_exists", str(r))
    except requests.exceptions.RequestException as e:
        audit_log_exception("ensure_release_exists")
        log.warning('ensure_release_exists: %s', e)


def get_parent_content_types(product_id):
    """
    Return content_type_codes for parent publication of product_id

    :param product_id:
    :type product_id: str
    :return: list
    """
    lc = ckanapi.LocalCKAN()
    results = lc.action.package_search(
        q='product_id_new:{parent_id}'.format(parent_id=product_id[:8])
    )
    if 'results' in results and len(results['results']) == 1:
        return results['results'][0].get(u'content_type_codes', [])
    else:
        return []


def set_previous_issue_archive_date(product_id, archive_date):
    """
    Set the archive date of the previous issue of product_id

    :param product_id:
    :type product_id: str
    :param archive_date:
    :type archive_date: datetime.datetime
    :return:
    """
    if len(product_id) < 15:
        raise ValidationError((_('{product_id}: expected product ID and issue '
                                 'number'.format(product_id=product_id)),))
    lc = ckanapi.LocalCKAN()
    results = lc.action.package_search(
        q='product_id_new:{parent_id}???????'.format(
            parent_id=product_id[:8]
        ),
        sort='product_id_new desc'
    )
    for result in results['results']:
        if result['product_id_new'] < product_id:
            if not result.get('archive_date'):
                result['archive_date'] = archive_date
                lc.action.package_update(**result)
                return


def set_related_id(product_id, related_product_ids):
    """
    Add product_id to related_products field for each related_product_id

    :param product_id: ID of product to add
    :type product_id: str
    :param related_product_ids: IDs of products to update
    :type related_product_ids: list

    :return:
    """
    if not related_product_ids or not isinstance(related_product_ids, list):
        return
    q = u'product_id_new:' + u' OR product_id_new:'.join(related_product_ids)
    lc = ckanapi.LocalCKAN()
    search_result = lc.action.package_search(
        q=q
    )
    results = search_result.get('results', [])
    for result in results:
        related_products = result.get(u'related_products', [])
        if product_id not in related_products:
            related_products.append(product_id)
            result.update({u'related_products': related_products})
            try:
                lc.action.package_update(**result)
            except ValidationError:
                pass  # fail quietly if best effort unsuccessful


def write_audit_log(event, data=None, level=1):
    endpoint = config.get('ckanext.stcndm.auditlog_service_url')
    if not endpoint:
        return

    payload = {
        'componentId': ndm_audit_log_component_id,
        'shortDescription': event,
        'auditLevel': level
    }

    if data and isinstance(data, dict):
        payload['userDefinedFields'] = [{
            'Key': k,
            'Value': json.dumps(v)
        } for k, v in data.iteritems()]

    requests.post(
        endpoint,
        headers={
            'Content-Type': 'application/json'
        },
        data=json.dumps(payload)
    )


def audit_log_exception(event):
    def _logit(f):
        @wraps(f)
        def _wrapped(*args, **kwargs):
            try:
                results = f(*args, **kwargs)
            except Exception as ex:
                write_audit_log(event, data=ex, level=3)
                raise

            write_audit_log(event, level=1)
            return results
        return _wrapped
    return _logit


def changes_since(since_ts=None, before_ts=None, limit=None):
    """
    Returns an iterable of all activity stream changes (dataset creation,
    edits, and deletes) from all users between the given date(s).

    :param since_ts: Earliest date for changes.
    :type since_ts: datetime or `None`
    :param before_ts: Latest date for changes.
    :type before_ts: datetime or `None`
    :param limit: Maximum number of results to return.
    :type limit: long or `None`
    """
    before_ts = before_ts or datetime.utcnow()
    since_ts = since_ts or datetime.min

    return ({
        'id': record.id,
        'timestamp': record.timestamp,
        'user_id': record.user_id,
        'object_id': record.object_id,
        'revision_id': record.revision_id,
        'activity_type': record.activity_type
    } for record in (
        model.activity._changed_packages_activity_query().order_by(
            model.Activity.timestamp
        ).filter(
            model.Activity.timestamp >= since_ts,
            model.Activity.timestamp <= before_ts
        ).limit(
            limit
        )
    ))


def sync_dataset(source, target, package_id):
    """
    Sync the dataset given by `package_id` from `source` to `dest`.

    :param source: A LocalCKAN or RemoteCKAN instance.
    :param target: A LocalCKAN or RemoteCKAN instance.
    :param package_id: A CKAN package UUID.
    """
    try:
        source_package = source.action_package_show(id=package_id)
    except (ckanapi.NotFound, ckanapi.NotAuthorized):
        source_package = None

    try:
        target_package = target.action_package_show(id=package_id)
    except (ckanapi.NotFound, ckanapi.NotAuthorized):
        target_package = None

    if source_package is None:
        # Original package has been deleted. Ensure it's also removed from
        # the remote.
        target.action.package_delete(id=package_id)
    elif target_package is None:
        # The package does not exist at all on the remote.
        target.action.package_create(**source_package)
    else:
        # Update a package that exists on the local and the remote.
        target.action.package_update(**source_package)


def sync_ckan(target, since_ts=None, before_ts=None):
    """
    Sync this CKAN instance with a remote CKAN instance.

    :param target: A RemoteCKAN instance.
    """
    since_ts = since_ts or datetime.utcnow() - timedelta(days=1)
    before_ts = before_ts or datetime.utcnow()
    lc = ckanapi.LocalCKAN()

    for activity in changes_since(since_ts=since_ts, before_ts=before_ts):
        sync_dataset(lc, target, activity['object_id'])


def is_dguid(dguid_or_geodescriptor):
    """
    test whether submitted value is a valid dguid

    :param dguid_or_geodescriptor:
    :return: boolean
    """
    if (
        isinstance(dguid_or_geodescriptor, basestring) and
        re.match('^\d{4}[AS]\d{4}.*', dguid_or_geodescriptor)
       ):
        return True
    else:
        return False


def is_geodescriptor(dguid_or_geodescriptor):
    """
    test whether submitted value is a valid geodescriptor

    :param dguid_or_geodescriptor:
    :return: boolean
    """
    if (
        isinstance(dguid_or_geodescriptor, basestring) and
        re.match('^[AS]\d{4}.*', dguid_or_geodescriptor)
       ):
        return True
    else:
        return False


def get_geolevel(dguid_or_geodescriptor):
    """
    extract the geolevel from the given dguid or geodescriptor

    :param dguid_or_geodescriptor:
    :type dguid_or_geodescriptor: unicode
    :return: unicode
    :raises: ValidationError
    """
    if is_dguid(dguid_or_geodescriptor):
        return dguid_or_geodescriptor[4:9]
    elif is_geodescriptor(dguid_or_geodescriptor):
        return dguid_or_geodescriptor[:5]
    else:
        raise ValidationError({
            u'geodescriptor_code': u'Unable to get geolevel '
                                   u'from {code}'.format(
                                    code=dguid_or_geodescriptor
                                    )
        })


def get_dguid_from_pkg_id(pkg_id):
    """
    Given the package id, return the dguid of the package

    :param pkg_id:
    :return:
    """
    lc = ckanapi.LocalCKAN()
    result = lc.action.package_show(**{u'id': pkg_id})
    return result.get(u'geodescriptor_code')
