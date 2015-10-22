#!/usr/bin/env python
# encoding: utf-8

import httplib
from urlparse import urlparse

import ckan.plugins as p
import ckan.lib.helpers as h
from ckan.lib.base import BaseController, config

class SolrProxyController(BaseController):

    solr_url = urlparse(config.get('solr_url',
                'http://127.0.0.1:8983/solr/ckan'))

    def select(self):
        self.proxy_solr('select')

    def proxy_solr(self, action):
        url = h.full_current_url()
        query = ''

        if url.find('?') != -1:
            query = url.split('?')[1]

        conn = httplib.HTTPConnection(self.solr_url.netloc)
        conn.request('GET', self.solr_url.path + '/' + action + '?' + query)

        response = conn.getresponse()

        data = response.read()

        ckan_response = p.toolkit.response

        ckan_response.status_int = response.status
        ckan_response.status = str(response.status) + ' ' + response.reason
        ckan_response.content_type = response.getheader('content-type')

        ckan_response.body = data

        conn.close()

