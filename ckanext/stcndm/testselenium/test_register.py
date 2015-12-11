import unittest

import setup_test

from nose.tools import assert_equals
from selenium_base import phantom


class TestAuthNav(unittest.TestCase):

    def tearDown(self):
        phantom.close()

    def test_register(self):
        phantom.get(setup_test.ckan_base)
        phantom.find_element_by_link_text('Register').click()
        phantom.find_element_by_name('name').send_keys(setup_test.ckan_reg_user)
        phantom.find_element_by_name('fullname').send_keys(setup_test.ckan_reg_user)
        phantom.find_element_by_name('email').send_keys(setup_test.ckan_reg_email)
        phantom.find_element_by_name('password1').send_keys(setup_test.ckan_reg_pass)
        phantom.find_element_by_name('password2').send_keys(setup_test.ckan_reg_pass)
        phantom.find_element_by_name('save').click()
        assert_equals(phantom.title, 'Dashboard - CKAN')
