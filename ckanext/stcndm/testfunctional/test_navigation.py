import unittest

from nose.tools import assert_equals

from functional_base import ckan_url, phantom, login_or_pass


auth_urls = {
    'My Datasets': 'Dashboard - CKAN',
    'My Organizations': 'Dashboard - CKAN',
    'My Groups': 'Dashboard - CKAN',
    'Settings': 'Dashboard - CKAN'
}


class TestAuthNav(unittest.TestCase):

    def setUp(self):
        login_or_pass(phantom)

    def tearDown(self):
        phantom.close()

    def test_links(self):
        for text, title in auth_urls.iteritems():
            phantom.get(ckan_url + '/dashboard')
            phantom.find_element_by_link_text(text)
            assert_equals(phantom.title, title)
        phantom.get(ckan_url + '/user/_logout')
