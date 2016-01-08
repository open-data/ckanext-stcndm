import unittest

import requests

from nose.tools import assert_equals

from functional_base import headers, ckan_url


session = requests.Session()
session.trust_env = False


class TestAPI(unittest.TestCase):

    def test_getproduct(self):
        payload = {"productId": "10H0001"}
        r = session.post(ckan_url + '/api/3/action/GetProduct', headers=headers, params=payload)
        assert_equals(r.status_code, 200)

    def test_getparentproductid(self):
        payload = {"productType": "25", "parentProductId": "75M0012X"}
        r = session.post(ckan_url + '/api/3/action/GetDerivedProductList', headers=headers, params=payload)
        assert_equals(r.status_code, 200)

    def test_getsubject(self):
        payload = {"subjectCode": "01"}
        r = session.post(ckan_url + '/api/3/action/GetSubject', headers=headers, params=payload)
        assert_equals(r.status_code, 200)

    def test_getdatasetschema(self):
        payload = {"name": "cube"}
        r = session.post(ckan_url + '/api/3/action/GetDatasetSchema', headers=headers, params=payload)
        assert_equals(r.status_code, 200)

    def test_getsurveycodesets(self):
        payload = {"start": "0", "limit": "5"}
        r = session.post(ckan_url + '/api/3/action/GetSurveyCodesets', headers=headers, params=payload)
        assert_equals(r.status_code, 200)

    def test_getcubelist(self):
        payload = {"subjectCode": "01"}
        r = session.post(ckan_url + '/api/3/action/GetCubeList', headers=headers, params=payload)
        assert_equals(r.status_code, 200)

    def test_getproducttype(self):
        payload = {"productType": "11"}
        r = session.post(ckan_url + '/api/3/action/GetProductType', headers=headers, params=payload)
        assert_equals(r.status_code, 200)

    def test_getcube(self):
        payload = {"cubeId": "10000001"}
        r = session.post(ckan_url + '/api/3/action/GetCube', headers=headers, params=payload)
        assert_equals(r.status_code, 200)
