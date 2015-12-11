import setup_test

from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver import PhantomJS


phantom = PhantomJS(service_args=['--proxy-type=none', '--load-images=false'])
phantom.set_window_size(1024, 768)


def login_or_pass(driver):
    try:
        driver.find_element_by_class_name('username')
    except NoSuchElementException:
        driver.get(setup_test.ckan_base)
        driver.find_element_by_link_text('Log in').click()
        driver.find_element_by_name('login').send_keys(setup_test.ckan_user)
        driver.find_element_by_name('password').send_keys(setup_test.ckan_pass)
        driver.find_element_by_xpath('//*[@id="wb-auto-1"]/div/div/div/form/div[4]/button').click()
        driver.find_element_by_class_name('username')
    else:
        return driver
