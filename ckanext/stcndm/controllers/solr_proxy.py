#!/usr/bin/env python
# encoding: utf-8
import urllib
import urlparse
import codecs
import ast

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
        if url.query != '':
            data = urlparse.parse_qs(urllib.unquote(url.query).decode('utf-8'))
        else:
            data = ast.literal_eval(p.toolkit.request.body)
        content_type = data.get('wt', 'xml')
        if isinstance(content_type, list):
            content_type = content_type[0]
        ckan_response = p.toolkit.response
        ckan_response.content_type = CONTENT_TYPES[content_type]
        solr_response = ''

        if content_type == 'csv':
            ckan_response.headers['Content-Disposition'] = 'attachment; filename=query.csv'
            solr_response = str(codecs.BOM_UTF8)

        conn = make_connection()
        try:
            solr_response += conn.raw_query(**data)
            ckan_response.body = solr_response
        except SolrException, e:
            ckan_response.status_int = e.httpcode
            ckan_response.status = str(e.httpcode) + ' ' + e.reason
            ckan_response.body = e.body

        conn.close()
