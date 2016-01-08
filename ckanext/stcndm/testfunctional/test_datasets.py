import unittest

from nose.tools import assert_equals
from selenium_base import phantom, login_or_pass, ckan_base
from selenium.common.exceptions import NoSuchElementException


release = {'name': 'Release', 'url': '/release/'}
cube = {'name': 'Cube', 'url': '/cube/'}
article = {'name': 'Article', 'url': '/article/'}
view = {'name': 'Cube', 'url': '/cube/'}
survey_source = {'name': 'Survey Source', 'url': '/survey/'}
subject = {'name': 'Subject', 'url': '/subject/'}
publication = {'name': 'Publication', 'url': '/publication/'}
service = {'name': 'Service', 'url': '/service/'}
the_daily = {'name': 'The Daily', 'url': '/daily/'}
conference = {'name': 'Conference', 'url': '/conference/'}
code = {'name': 'Code', 'url': '/codeset/'}
indicator = {'name': 'Indicator', 'url': '/indicator/'}
pumf = {'name': 'PUMF', 'url': '/pumf/'}
correction = {'name': 'Correction', 'url': '/correction/'}
province = {'name': 'Province', 'url': '/province/'}
chart = {'name': 'Chart', 'url': '/chart/'}
generic_publication = {'name': 'Generic Publication', 'url': '/generic/'}
video = {'name': 'Video', 'url': '/video/'}
geodescriptor = {'name': 'Geodescriptor', 'url': '/geodescriptor/'}
formatd = {'name': 'Format', 'url': '/format/'}


def dataset_read(driver, dataset):
    driver.get(ckan_base + dataset)
    assert_equals(driver.title, 'Datasets - CKAN')
    try:
        driver.find_element_by_class_name('text-warning')
    except NoSuchElementException:
        entry = driver.find_element_by_class_name('dataset-heading')
        entry_text = entry.text[:30]
        driver.find_element_by_link_text(entry.text).click()
        header = driver.find_element_by_css_selector('h1')
        assert_equals(entry_text, header.text[:30])
        return driver
    else:
        return driver


class TestDatasets(unittest.TestCase):

    def setUp(self):
        login_or_pass(phantom)

    def test_dataset_release_read(self):
        dataset_read(phantom, release['url'])

    def test_dataset_cube_read(self):
        dataset_read(phantom, cube['url'])

    def test_dataset_article_read(self):
        dataset_read(phantom, article['url'])

    def test_dataset_view_read(self):
        dataset_read(phantom, view['url'])

    def test_dataset_survey_source_read(self):
        dataset_read(phantom, survey_source['url'])

    def test_dataset_subject_read(self):
        dataset_read(phantom, subject['url'])

    def test_dataset_publication_read(self):
        dataset_read(phantom, publication['url'])

    def test_dataset_service_read(self):
        dataset_read(phantom, service['url'])

    def test_dataset_the_daily_read(self):
        dataset_read(phantom, the_daily['url'])

    def test_dataset_conference_read(self):
        dataset_read(phantom, conference['url'])

    def test_dataset_code_read(self):
        dataset_read(phantom, code['url'])

    def test_dataset_indicator_read(self):
        dataset_read(phantom, indicator['url'])

    def test_dataset_pumf_read(self):
        dataset_read(phantom, pumf['url'])

    def test_dataset_correction_read(self):
        dataset_read(phantom, correction['url'])

    def test_dataset_province_read(self):
        dataset_read(phantom, province['url'])

    def test_dataset_chart_read(self):
        dataset_read(phantom, chart['url'])

    def test_dataset_generic_publication_read(self):
        dataset_read(phantom, generic_publication['url'])

    def test_dataset_video_read(self):
        dataset_read(phantom, video['url'])

    def test_dataset_geodescriptor_read(self):
        dataset_read(phantom, geodescriptor['url'])

    def test_dataset_formatd_read(self):
        dataset_read(phantom, formatd['url'])
