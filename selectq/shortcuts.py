from selenium import webdriver
from selenium.webdriver import Proxy

from .selectq import Selector


def open_browser(
    url, browser_type, headless=False, proxy_conf={}, **browser_kargs
):
    ''' Quick shortcut to open a <url> using a particular
        <browser_type>.

        Return a Selector (sQ) object bound to the browser.
        '''
    if browser_type == 'firefox':
        from selenium.webdriver.firefox.options import Options
        browser_class = webdriver.Firefox
    else:
        raise ValueError("Unsupported browser type '{}'.".format(browser_type))

    if 'options' not in browser_kargs:
        proxy = Proxy(proxy_conf)

        options = Options()
        options.headless = headless
        if proxy_conf:
            options.proxy = proxy

        browser_kargs['options'] = options

    driver = browser_class(**browser_kargs)

    sQ = Selector(driver)
    sQ.browser.get(url)

    return sQ
