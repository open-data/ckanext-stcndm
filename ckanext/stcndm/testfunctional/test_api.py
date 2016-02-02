import json
import unittest

import requests

from nose.tools import assert_equals

from functional_base import headers, ckan_url


session = requests.Session()
session.trust_env = False


class TestAPI(unittest.TestCase):

    def test_getproduct(self):
        payload = {"productId": "88-003-X200700210322"}
        r = session.get(ckan_url + '/api/3/action/GetProduct',
                        headers=headers, params=payload)
        assert_equals(r.status_code, 200)

    def test_getparentproductid(self):
        payload = {"productType": "20", "parentProductId": "89-649-X"}
        r = session.get(ckan_url + '/api/3/action/GetDerivedProductList',
                        headers=headers, params=payload)
        assert_equals(r.status_code, 200)

    def test_getsubject(self):
        payload = {"subjectCode": "21"}
        r = session.get(ckan_url + '/api/3/action/GetSubject',
                        headers=headers, params=payload)
        assert_equals(r.status_code, 200)

    def test_getdatasetschema(self):
        payload = {"name": "subject"}
        r = session.get(ckan_url + '/api/3/action/GetDatasetSchema',
                        headers=headers, params=payload)
        assert_equals(r.status_code, 200)

    def test_getsurveycodesets(self):
        payload = {"start": "0", "limit": "5"}
        r = session.get(ckan_url + '/api/3/action/GetSurveyCodesets',
                        headers=headers, params=payload)
        assert_equals(r.status_code, 200)

    def test_getcubelist(self):
        payload = {"subjectCode": "27"}
        r = session.get(ckan_url + '/api/3/action/GetCubeList',
                        headers=headers, params=payload)
        assert_equals(r.status_code, 200)

    def test_getproducttype(self):
        payload = {"productType": "10"}
        r = session.get(ckan_url + '/api/3/action/GetProductType',
                        headers=headers, params=payload)
        assert_equals(r.status_code, 200)

    def test_getcube(self):
        payload = {"cubeId": "24100004"}
        r = session.get(ckan_url + '/api/3/action/GetCube',
                        headers=headers, params=payload)
        assert_equals(r.status_code, 200)

    def test_getautocomplete(self):
        payload = {"type": "geodescriptor", "q": "Quebec"}
        r = session.get(ckan_url + '/api/3/action/GetAutocomplete',
                        headers=headers, params=payload)
        assert_equals(r.status_code, 200)

    def test_getbookablereleases(self):
        payload = {"frc": "82300"}
        r = session.get(ckan_url + '/api/3/action/GetBookableProducts',
                        headers=headers, params=payload)
        assert_equals(r.status_code, 200)

    def test_getnextcubeid(self):
        payload = {"subjectCode": "27"}
        r = session.get(ckan_url + '/api/3/action/GetNextCubeId',
                        headers=headers, params=payload)
        assert_equals(r.status_code, 200)

    def test_getnextnondataproductid(self):
        payload = {"subjectCode": "17", "productTypeCode": "20"}
        r = session.get(ckan_url + '/api/3/action/GetNextNonDataProductId',
                        headers=headers, params=payload)
        assert_equals(r.status_code, 200)

    def test_getthemes(self):
        payload = {"start": "0", "limit": "5"}
        r = session.get(ckan_url + '/api/3/action/GetThemes',
                        headers=headers, params=payload)
        assert_equals(r.status_code, 200)

    def test_getdailylist(self):
        payload = {"startDate": "2013-01-10", "endDate": "2013-02-10"}
        r = session.get(ckan_url + '/api/3/action/GetDailyList',
                        headers=headers, params=payload)
        assert_equals(r.status_code, 200)

    def test_getdefaultviews(self):
        payload = {"frc": "53300"}
        r = session.get(ckan_url + '/api/3/action/GetDefaultViews',
                        headers=headers, params=payload)
        assert_equals(r.status_code, 200)

    def test_getformatdescription(self):
        payload = {"formatCode": "12"}
        r = session.get(ckan_url + '/api/3/action/GetFormatDescription',
                        headers=headers, params=payload)
        assert_equals(r.status_code, 200)

    def test_getlastpublishstatus(self):
        payload = {"lastPublishStatusCode": "12"}
        r = session.get(ckan_url + '/api/3/action/GetLastPublishStatus',
                        headers=headers, params=payload)
        assert_equals(r.status_code, 200)

    def test_getnextproductid(self):
        payload = {"parentProductId": "24100004", "productType": "10"}
        r = session.get(ckan_url + '/api/3/action/GetNextProductId',
                        headers=headers, params=payload)
        assert_equals(r.status_code, 200)

    def test_getnextlegacyarticleid(self):
        payload = {"parentProduct": "82-625-X"}
        r = session.get(ckan_url + '/api/3/action/GetNextLegacyArticleId',
                        headers=headers, params=payload)
        assert_equals(r.status_code, 200)

    def test_getnextlegacyproductid(self):
        payload = {"parentProduct": "62M0001X", "productType": "25"}
        r = session.get(ckan_url + '/api/3/action/GetNextLegacyProductId',
                        headers=headers, params=payload)
        assert_equals(r.status_code, 200)

    def test_getproductissuearticles(self):
        payload = {"productId": "88-003-X", "issueNo": "200700210322"}
        r = session.get(ckan_url + '/api/3/action/GetProductIssueArticles',
                        headers=headers, params=payload)
        assert_equals(r.status_code, 200)

    def test_getproductissues(self):
        payload = {"productId": "88-003-X"}
        r = session.get(ckan_url + '/api/3/action/GetProductIssues',
                        headers=headers, params=payload)
        assert_equals(r.status_code, 200)

    def test_getsubjectlist(self):
        r = session.get(ckan_url + '/api/3/action/GetSubjectList',
                        headers=headers)
        assert_equals(r.status_code, 200)

    def test_getupcomingreleases(self):
        payload = {"startDate": "2013-01-10", "endDate": "2013-02-10"}
        r = session.get(ckan_url + '/api/3/action/GetUpcomingReleases',
                        headers=headers, params=payload)
        assert_equals(r.status_code, 200)

    def test_getproductformats(self):
        payload = {"productId": "62M0001X", "issueNo": "200700210322"}
        r = session.get(ckan_url + '/api/3/action/GetProductFormats',
                        headers=headers, params=payload)
        assert_equals(r.status_code, 200)

    def test_getsubjectcodesets(self):
        payload = {"start": "0", "limit": "5"}
        r = session.get(ckan_url + '/api/3/action/GetSubjectCodesets',
                        headers=headers, params=payload)
        assert_equals(r.status_code, 200)

    def test_deleteproduct(self):
        payload = {"productId": "3204"}
        r = session.post(ckan_url + '/api/3/action/DeleteProduct',
                         headers=headers, data=json.dumps(payload))
        assert_equals(r.status_code, 200)

    def test_purgedataset(self):
        payload = {"id": "survey-5110"}
        r = session.post(ckan_url + '/api/3/action/PurgeDataset',
                         headers=headers, data=json.dumps(payload))
        assert_equals(r.status_code, 200)

    def test_updatecube(self):
        payload = {"cubeId": "24100004", "cubeData": {'author': 'The Camel'}}
        r = session.post(ckan_url + '/api/3/action/UpdateCube',
                         headers=headers, data=json.dumps(payload))
        assert_equals(r.status_code, 200)

    def test_registercube(self):
        payload = {
            "subjectCode": "16",
            "productTitleEnglish": "English Title for API Test",
            "productTitleFrench": "French Title for API Test"
        }
        r = session.post(ckan_url + '/api/3/action/RegisterCube',
                         headers=headers, data=json.dumps(payload))
        assert_equals(r.status_code, 200)

    def test_registerdaily(self):
        payload = {
            "productId": "00240001777777",
            "productTitle":
                {"en": "English Title for RegisterDaily API Test",
                 "fr": "French Title for RegisterDaily API Test"},
            "lastPublishStatusCode": "8",
            "releaseDate": "2015-12-15T09:45",
            "uniqueId": "daily3456789123",
            "childList": ["99-003-X"],
        }
        r = session.post(ckan_url + '/api/3/action/RegisterDaily',
                         headers=headers, data=json.dumps(payload))
        assert_equals(r.status_code, 200)

    def test_registerdataproduct(self):
        payload = {
            "productType": "11",
            "productTitle":
                {"en": "English Title for RegisterDataProduct API Test",
                 "fr": "French Title for RegisterDataProduct API Test"},
            "parentProductId": "27100200"
        }
        r = session.post(ckan_url + '/api/3/action/RegisterDataProduct',
                         headers=headers, data=json.dumps(payload))
        assert_equals(r.status_code, 200)

    def test_registernondataproduct(self):
        payload = {
            "productId": "82-625-X201400114126",
            "productType": "article",
            "productTitle":
                {"en": "English Title for RegisterNonDataProduct API Test",
                 "fr": "French Title for RegisterNonDataProduct API Test"},
            "parentProduct": "82-625-X"
        }
        r = session.post(ckan_url + '/api/3/action/RegisterNonDataProduct',
                         headers=headers, data=json.dumps(payload))
        assert_equals(r.status_code, 200)

    def test_registerlegacynondataproduct(self):
        payload = {
            "productType": "25",
            "productTitle":
                {"en": "English Title for RegisterLegacyNonDataProduct API Test",
                 "fr": "French Title for RegisterLegacyNonDataProduct API Test"},
            "parentProduct": "62M0001X"
        }
        r = session.post(ckan_url + '/api/3/action/RegisterLegacyNonDataProduct',
                         headers=headers, data=json.dumps(payload))
        assert_equals(r.status_code, 200)

    def test_registersurvey(self):
        payload = {
            "productId": "5000",
            "subjectCodes": ["171001"],
            "titleEn": "English Title for RegisterSurvey API Test",
            "titleFr": "French Title for RegisterSurvey API Test"
        }
        r = session.post(ckan_url + '/api/3/action/RegisterSurvey',
                         headers=headers, data=json.dumps(payload))
        assert_equals(r.status_code, 200)

    def test_updatedefaultview(self):
        payload = {
            "cubeId": "24100004",
            "defaultView": "2411000401"
        }
        r = session.post(ckan_url + '/api/3/action/UpdateDefaultView',
                         headers=headers, data=json.dumps(payload))
        assert_equals(r.status_code, 200)

    def test_updateproductgeo(self):
        payload = {
            "productId": "2411000401",
            "dguids": ["A0000"]
        }
        r = session.post(ckan_url + '/api/3/action/UpdateProductGeo',
                         headers=headers, data=json.dumps(payload))
        assert_equals(r.status_code, 200)