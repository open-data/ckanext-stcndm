# Headless UI Test for STCNDM-CKAN #

Functional tests for the CKANEXT-STCNDM.  It does front-end and api based tests against test data.

## Requirements ##

- Selenium
- Phantomjs

## Installation ##

1. Install the following python package using pip

	```
    pip install selenium
	```

2. Install the following package using your OS package manager

    ```
	fontconfig freetype freetype-devel fontconfig-devel libstdc++
    ```

3. Install the phantomsjs

    ```
    wget https://bitbucket.org/ariya/phantomjs/downloads/phantomjs-1.9.8-linux-x86_64.tar.bz2
    tar -xjvf phantomjs-1.9.8-linux-x86_64.tar.bz2 -C /usr/local/bin/ phantomjs-1.9.8-linux-x86_64/bin/phantomjs --strip-components 2
    ```

4. Setup the test database

    ```
    sudo -u postgres createdb -O ckan_default stcndm_ckan_test -E utf-8
    ```

5. Copy development.ini to test-core.ini and add symbolyic link to /etc/ckan/stcndm/.  Update sqlalchemy.url.

    ```
    sqlalchemy.url = postgresql://ckan_default:pass@localhost/stcndm_ckan_test
    solr_url = http://127.0.0.1:8983/solr/stcndm_test
    ```

6. To run the tests.

    ```
    source functionaltest_runner.sh
    ```
