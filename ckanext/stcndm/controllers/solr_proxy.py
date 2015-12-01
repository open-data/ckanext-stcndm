#!/usr/bin/env python
# encoding: utf-8
import urllib
import urlparse

import ckan.plugins as p
import ckan.lib.helpers as h
from ckan.lib.search.common import make_connection
from solr import SolrException
from ckan.controllers.api import ApiController

CONTENT_TYPES = {
    'text': 'text/plain;charset=utf-8',
    'html': 'text/html;charset=utf-8',
    'json': 'application/json;charset=utf-8',
    'csv': 'text/csv;charset=utf-8',
    'xml': 'application/xml;charset=utf-8'
}


class SolrProxyController(ApiController):
    def select(self):
        self.proxy_solr('select')

    def proxy_solr(self, action):
        url = urlparse.urlparse(h.full_current_url())
        query = urlparse.parse_qs(urllib.unquote(url.query).decode('utf-8'))
        content_type = query.get('wt', ['xml'])[0]
        ckan_response = p.toolkit.response
        ckan_response.content_type = CONTENT_TYPES[content_type]

        conn = make_connection()
        try:
            solr_response = conn.raw_query(**query)
            ckan_response.body = solr_response
        except SolrException, e:
            ckan_response.status_int = e.httpcode
            ckan_response.status = str(e.httpcode) + ' ' + e.reason
            ckan_response.body = e.body

        conn.close()
