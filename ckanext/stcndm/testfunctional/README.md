# Headless UI Test for STCNDM-CKAN #

## Requirements ##

- Selenium
- Phantomjs

## Installation ##

1. Install the following python package using pip

	```
    pip install selenium
	```

1. Install the following package using your OS package manager

    ```
	fontconfig freetype freetype-devel fontconfig-devel libstdc++
    ```

1. Install the phantomsjs

    ```
    wget https://bitbucket.org/ariya/phantomjs/downloads/phantomjs-1.9.8-linux-x86_64.tar.bz2
    tar -xjvf phantomjs-1.9.8-linux-x86_64.tar.bz2 -C /usr/local/bin/ phantomjs-1.9.8-linux-x86_64/bin/phantomjs --strip-components 2
    ```

1. Setup the test database

    ```
    sudo -u postgres createdb -O ckan_default stcndm_ckan_test -E utf-8
    ```

1. Create /etc/ckan/stcndm/test.ini and add

    ```
    [app:main]
    use = config:/etc/ckan/stcndm/development.ini
    sqlalchemy.url = postgresql://ckan_default:pass@localhost/stcndm_ckan_test
    ```

1. 