#!/usr/bin/env/python
from setuptools import setup

setup(
    name='ckanext-stcndm',
    version='0.1',
    description='',
    license='MIT',
    author='',
    author_email='',
    url='',
    namespace_packages=['ckanext'],
    packages=['ckanext.stcndm'],
    zip_safe=False,
    entry_points = """
        [ckan.plugins]
        stcndm = ckanext.stcndm.plugins:STCNDMPlugin
        stcndm_report_generator = ckanext.report_generator.plugins:STCNDMReportGenerator
    """
)
