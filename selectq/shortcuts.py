from selenium import webdriver
from selenium.webdriver import Proxy

FIREFOX_PREFERENCES = {
    "dom.popup_maximum": 0,
    "browser.download.folderList": 2,
    "browser.download.panel.shown": False,
    "privacy.popups.showBrowserMessage": False,
    "browser.download.manager.showWhenStarting": False,
    "browser.helperApps.neverAsk.saveToDisk": ".mp3 audio/mpeg",
}


def _browser_class_and_options(browser_type):
    Options = None
    if browser_type == 'firefox':
        from selenium.webdriver.firefox.webdriver import WebDriver
        from selenium.webdriver.firefox.options import Options
    elif browser_type == 'chrome':
        from selenium.webdriver.chrome.webdriver import WebDriver
        from selenium.webdriver.chrome.options import Options
    elif browser_type == 'ie':
        from selenium.webdriver.ie.webdriver import WebDriver
        from selenium.webdriver.ie.options import Options
    elif browser_type == 'webkitgtk':
        from selenium.webdriver.webkitgtk.webdriver import WebDriver
        from selenium.webdriver.webkitgtk.options import Options
    elif browser_type == 'edge':
        from selenium.webdriver.edge.webdriver import WebDriver
    elif browser_type == 'opera':
        from selenium.webdriver.opera.webdriver import WebDriver
    elif browser_type == 'safari':
        from selenium.webdriver.safari.webdriver import WebDriver
    elif browser_type == 'blackberry':
        from selenium.webdriver.blackberry.webdriver import WebDriver
    elif browser_type == 'phantomjs':
        from selenium.webdriver.phantomjs.webdriver import WebDriver
    elif browser_type == 'android':
        from selenium.webdriver.android.webdriver import WebDriver
    elif browser_type == 'remote':
        from selenium.webdriver.remote.webdriver import WebDriver
    else:
        raise ValueError("Unsupported browser type '{}'.".format(browser_type))

    return WebDriver, Options


def open_browser(
    url, browser_type, headless=False, proxy_conf={}, **browser_kargs
):
    ''' Quick shortcut to open a <url> using a particular
        <browser_type>.

        Return a Selector (sQ) object bound to the browser.
        '''
    # make 'driver' and alias of the standard 'executable_path'
    tmp = browser_kargs.pop('driver', None)
    if tmp is not None and 'executable_path' not in browser_kargs:
        browser_kargs['executable_path'] = tmp

    from .selectq import Selector
    WebDriver, Options = _browser_class_and_options(browser_type)
    if Options is None:
        warnings.warn(
            "The browser '{}' does not support custom options.".
            format(browser_type)
        )

    if 'options' not in browser_kargs and Options is not None:
        proxy = Proxy(proxy_conf)

        options = Options()
        options.headless = headless
        if proxy_conf:
            options.proxy = proxy

        browser_kargs['options'] = options

    driver = WebDriver(**browser_kargs)

    sQ = Selector(driver)
    sQ.browser.get(url)

    return sQ
