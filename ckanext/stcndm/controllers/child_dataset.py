#!/usr/bin/env python
# encoding: utf-8

import ckanapi
from ckan.lib import base
from ckan.plugins import toolkit
from ckanext.stcndm.logic.legacy import is_legacy_product
from ckanext.scheming.helpers import scheming_get_dataset_schema

import ckan.plugins as p

PRODUCT_ID = 'product_id_new'

class ChildDatasetController(base.BaseController):

    def new(self, ds_id, ds_type):
        lc = ckanapi.LocalCKAN()
        pkg = lc.action.package_show(id=ds_id)
        pkg_id = pkg['product_id_new']

        parent_schema = scheming_get_dataset_schema(pkg['type'])

        new_payload = {
            'top_parent_id': pkg.get('top_parent_id', pkg_id)
        }

        id_payload = {
            'parentProductId': pkg['product_id_new'],
            'parentProduct': pkg['product_id_new'],
            'productType': str(
                parent_schema['dataset_type_code']
            )
        }

        if ds_type == 'format':
            new_payload['parent_id'] = pkg_id
        elif 'non_data_product' in parent_schema and parent_schema['non_data_product'] == True:
            if is_legacy_product(pkg['product_id_new']):
                new_payload[PRODUCT_ID] = lc.action.GetNextLegacyProductId(**id_payload)
            else:
                new_payload[PRODUCT_ID] = lc.action.GetNextNonDataProduct(**payload)
        else:
            new_payload[PRODUCT_ID] = lc.action.GetNextProductId(**id_payload)

        toolkit.redirect_to( '%s_new' % ds_type,
            **new_payload
        )