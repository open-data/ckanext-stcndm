#!/usr/bin/env python
# encoding: utf-8
from datetime import datetime

import ckanapi
from ckan.lib import base
from ckan.plugins import toolkit


class CloneDatasetController(base.BaseController):
    PURGE_FIELDS = (
        'id',
        'revision_id',
        'revision_timestamp'
    )

    def clone(self, ds_id):
        context = {
            'model': base.model,
            'session': base.model.Session,
            'user': base.c.user or base.c.author
        }

        lc = ckanapi.LocalCKAN(context=context)
        pkg = lc.action.package_show(id=ds_id)

        # Remove any fields that need to be reset between
        # clones, such as unique IDs.
        for field in self.PURGE_FIELDS:
            if field in pkg:
                del pkg[field]

        now = datetime.now()

        pkg.update({
            'title': {
                u'en': '{0} - Clone'.format(pkg['title'].get('en', '')),
                u'fr': '{0} - Cloner'.format(pkg['title'].get('fr', '')),
            },
            'name': '{0} - Clone'.format(pkg['name']),
            'metadata_created': now,
            'metadata_modified': now,
            'notes': {
                u'en': (pkg.get('notes') or {}).get('en') or '',
                u'fr': (pkg.get('notes') or {}).get('fr') or ''
            }
        })

        new_pkg = lc.action.package_create(**pkg)
        toolkit.redirect_to(
            controller='package',
            action='edit',
            id=new_pkg['id']
        )
