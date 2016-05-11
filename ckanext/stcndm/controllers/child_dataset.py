#!/usr/bin/env python
# encoding: utf-8

import ckanapi
from ckan.lib import base
from ckanext.stcndm.logic.legacy import is_legacy_product
from ckanext.scheming.helpers import scheming_get_dataset_schema
from ckanext.stcndm.helpers import next_issue_number, next_article_id
from ckan.controllers.package import PackageController
from ckan.common import request

PRODUCT_ID = 'product_id_new'


class ChildDatasetController(base.BaseController):

    def new(self, ds_id, ds_type):
        new_payload = None

        if 'save' not in request.params:
            lc = ckanapi.LocalCKAN()
            pkg = lc.action.package_show(id=ds_id)
            pkg_id = pkg[PRODUCT_ID]

            parent_schema = scheming_get_dataset_schema(pkg['type'])

            new_payload = {
                'type': ds_type,
                'top_parent_id': pkg.get('top_parent_id', pkg_id) or pkg_id
            }

            id_payload = {
                'parentProductId': pkg['product_id_new'],
                'parentProduct': pkg['product_id_new'],
                'productType': str(
                    parent_schema['dataset_type_code']
                ),
                'productTypeCode': str(
                    parent_schema['dataset_type_code']
                )
            }

            if ds_type == 'format':
                new_payload['parent_id'] = pkg_id
            elif ds_type == 'issue':
                issue_number = next_issue_number(pkg_id)
                issue_id = u'{pid}{issue_number}'.format(
                    pid=pkg_id,
                    issue_number=issue_number
                )
                new_payload['product_type_code'] = pkg.get('product_type_code')
                new_payload['issue_number'] = issue_number
                new_payload['product_id_new'] = issue_id
                new_payload['name'] = u'issue-{issue_id}'.format(
                    issue_id=issue_id
                )
                pass
            elif ds_type == 'article':
                article_id = next_article_id(
                    pkg.get('top_parent_id', pkg_id) or pkg_id,
                    pkg.get('issue_number')
                )
                new_payload['product_type_code'] = pkg.get('product_type_code')
                new_payload['issue_number'] = pkg.get('issue_number')
                new_payload['product_id_new'] = article_id
                new_payload['name'] = u'article-{article_id}'.format(
                    article_id=article_id
                )
                pass
            elif ('non_data_product' in parent_schema and
                    parent_schema['non_data_product'] == True):
                if is_legacy_product(pkg[PRODUCT_ID]):
                    new_payload[PRODUCT_ID] = lc.action.GetNextLegacyProductId(
                        **id_payload
                    )
                else:
                    id_payload['subjectCode'] = pkg['subject_codes'][0]
                    new_payload[PRODUCT_ID] = lc.action.GetNextNonDataProductId(
                        **id_payload
                    )
            else:
                new_payload[PRODUCT_ID] = lc.action.GetNextProductId(
                    **id_payload
                )

        return PackageController().new(new_payload)
