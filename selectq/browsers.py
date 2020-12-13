from lxml import etree

from selenium.webdriver.common.by import By as SeleniumBy
from selenium.webdriver.remote.webdriver import WebDriver as RemoteWebDriver
from selenium.common.exceptions import JavascriptException

import weakref
import json
import os.path

GADGETS_DIR = os.path.join(os.path.dirname(__file__), 'gadgets')


class Browser:
    def get(self, url):
        raise Exception(
            "The selection is unbound. Call sel.bind(browser) to bind it to a browser."
        )


class FileBrowser(Browser):
    ''' Simple browser to load a file-based HTML. '''
    def get(self, url):
        self._url = url
        self._fetch_xml_str_and_build_tree()

    def pprint(self, xpath):
        elems = self.tree.xpath(xpath)
        for el in elems:
            _indent(el)
            print(
                etree.tostring(
                    el,
                    encoding='unicode',
                    pretty_print=True,
                    method='html',
                    with_tail=False
                ),
                end=''
            )

    def _fetch_xml_str_and_build_tree(self):
        ''' Fetch (if needed) and build a XML tree representing
            the html file.
            '''
        with open(self._url, 'rt') as f:
            html = f.read()

        parser = etree.HTMLParser(remove_blank_text=True)
        self.tree = etree.fromstring(html, parser)


def _quit_driver(driver):
    if driver is not None:
        driver.quit()


class WebBrowser(Browser):
    def __init__(self, driver):
        super().__init__()
        self.driver = driver
        # ensure that we quit the driver eventually
        self._finalizer = weakref.finalize(self, _quit_driver, driver)

        self._gadgets_files = [
            ('css', os.path.join(GADGETS_DIR, 'selectq.css')),
            ('js', os.path.join(GADGETS_DIR, 'selectq.js')),
        ]

    def get(self, url):
        self.driver.get(url)

    def __del__(self):
        try:
            # Ensure that we quit the driver/browser.
            # If we don't do this the browser may not quit
            # automatically
            _quit_driver(self.driver)
            self.driver = None
        except:
            pass

    def quit(self):
        _quit_driver(self.driver)
        self.driver = None

    def load_js_file(self, filepath):
        ''' Load a local javascript file and inject it into the current
            window/frame.
            '''
        with open(filepath, 'rt') as f:
            self.driver.execute_script(f.read())

    def _load_gadgets(self):
        ''' Load CSS/JS files into the current web page. These files are
            known as 'gadgets' because they extend the ability of the
            browser to query/manipulate the web page.

            This is called automatically once per web page by
            the methods of this class that use them.

            More CSS/JS files can be added as default gadgets with the
            _gadgets_files property.

            If a CSS/JS files needs to be added not by default you can
            call load_css_file()/load_js_file() explicitly.
            '''
        for type, filename in self._gadgets_files:
            if type == 'css':
                self.load_css_file(os.path.join(GADGETS_DIR, 'selectq.css'))
            elif type == 'js':
                self.load_js_file(os.path.join(GADGETS_DIR, 'selectq.js'))
            else:
                raise ValueError(
                    "Gadget type '{}' is not supported.".format(type)
                )

    def load_css_file(self, filepath):
        with open(filepath, 'rt') as f:
            css = json.dumps(f.read())

        jsstyle = '''
        var style = document.createElement('style');
        style.type = 'text/css';
        style.innerHTML = {css};
        document.getElementsByTagName('head')[0].appendChild(style);
        '''.format(css=css)

        self.driver.execute_script(jsstyle)

    def js_process_elems(self, xpath, jsbegin, jsforeach, jsend):
        ''' Retrieve the elements selected by <xpath> and iterate
            over them injecting snippets of javascript code at the begin,
            in the middle and at the end of the iteration.

            Basically you can do a for-each call or a for-all call.

            In a for-each or "map" you should have the following setup:

            jsbegin = 'var elems = []; var results = [];'
            jsforeach = 'results.push(your_function(el));'
            jsend = 'return results;'

            In a for-all call you should have the following instead:

            jsbegin = 'var elems = [];'
            jsforeach = 'elems.push(el);'
            jsend = 'return your_function(elems);'

            Note that in all the cases the injected javascript code
            must be statements ended in semicolons.

            This is a low-level method, prefer pluck() and other
            high-level methods.
        '''

        not_gadgets_loaded_msj = 'selectq undefined - ijs98uduh'

        xpath = json.dumps(xpath)
        context_node = 'document'
        namespace_resolver = 'null'
        result_type = 'XPathResult.ANY_TYPE'
        existing_result = 'null'

        jsexecute = '''
        if (typeof window.selectq === 'undefined') {{
            throw new Error("{not_gadgets_loaded_msj}");
        }}

        var elems_iter = document.evaluate({xpath}, {context_node},
        {namespace_resolver}, {result_type}, {existing_result});

        {jsbegin}
        var el = elems_iter.iterateNext();
        while (el) {{
            {jsforeach}
            el = elems_iter.iterateNext();
        }}

        {jsend}
        '''.format(
            not_gadgets_loaded_msj=not_gadgets_loaded_msj,
            xpath=xpath,
            context_node=context_node,
            namespace_resolver=namespace_resolver,
            result_type=result_type,
            existing_result=existing_result,
            jsbegin=jsbegin,
            jsforeach=jsforeach,
            jsend=jsend
        )

        try:
            return self.driver.execute_script(jsexecute)
        except JavascriptException as e:
            if not_gadgets_loaded_msj not in str(e):
                raise

            self._load_gadgets()
            return self.driver.execute_script(jsexecute)

    def js_map(self, xpath, jscall):
        ''' Execute the javascript function call <jscall> for each
            element selected by <xpath> and return a list of results.

            <jscall> must be a function call. The 'el' variable will
            be pointing to the current element of the iteration.

            Eg: jscall = 'your_function(el);'

            Note that the <jscall> must end in a semicolon.
            '''
        jsbegin = 'var elems = []; var results = [];'
        jsend = 'return results;'

        jsforeach = '''
        var tmp = {jscall}
        results.push(tmp);
        '''.format(jscall=jscall)

        return self.js_process_elems(xpath, jsbegin, jsforeach, jsend)

    def js_call(self, xpath, jscall):
        ''' Execute the javascript function call <jscall> once over an array
            of the elements selected by <xpath>.

            <jscall> can be a sequence of javascript statements.
            The 'elems' variable will be pointing to the array.

            <jscall> may end with a 'return' statement to return some
            value.

            Eg: jscall = 'return your_function(elems);'

            Note that the <jscall> must end in a semicolon.
            '''
        jsbegin = 'var elems = [];'
        jsforeach = 'elems.push(el);'

        jsend = jscall

        return self.js_process_elems(xpath, jsbegin, jsforeach, jsend)

    def pluck(self, xpath, properties):
        if not properties:
            raise ValueError('The property list is empty.')

        if not isinstance(properties, (list, tuple)):
            raise TypeError(
                "Invalid type for the property list. Expected 'list' or 'tuple' but found '{}'."
                .format(type(properties))
            )

        jscall = 'selectq.pluck(el, {properties});'.format(
            properties=properties
        )

        return self.js_map(xpath, jscall)

    def highlight_off(self):
        xpath = '.'
        js = 'return selectq.highlight_off();'
        return self.js_call(xpath, js)

    def pprint(self, xpath):
        ''' Pretty print the html elements selected by xpath.

            The optional <sep> cna be used to separate the elements
            but keep in mind that a newline is always enforced.

            Note: if xpath selects the tags "html" or "body" the
            result pretty print will have some mixed (undefined)
            strings in the print.
            '''
        html = ''.join(arr[0] for arr in self.pluck(xpath, ['outerHTML']))
        if not html:
            return '[empty]'

        parser = etree.HTMLParser(remove_blank_text=True)
        tree = etree.fromstring(html, parser)

        _indent(tree)
        pretty = etree.tostring(
            tree,
            encoding='unicode',
            pretty_print=True,
            method='html',
            with_tail=False
        )

        # etree.fromstring adds a "html" and a "body" tags which
        # they are pretty printed in the first two and last two lines
        # we remove them and then we substract the indentation generated
        # by those.
        indent_lvl = 4
        print(
            '\n'.join(
                line[indent_lvl:] for line in pretty.strip().split('\n')[2:-2]
            )
        )


def _browser_wrapper(browser):
    ''' Wrap the given "browser" which can be a Browser instance
        or a RemoteWebDriver (Selenium) into a Browser.
        '''
    if isinstance(browser, Browser):
        return browser

    if isinstance(browser, RemoteWebDriver):
        return WebBrowser(browser)

    raise TypeError("Unknown browser type '{}'".format(type(browser)))


# http://effbot.org/zone/element-lib.htm#prettyprint
def _indent(elem, level=0):
    i = "\n" + level * "  "
    if len(elem):
        if not elem.text or not elem.text.strip():
            elem.text = i + "  "
        if not elem.tail or not elem.tail.strip():
            elem.tail = i
        for elem in elem:
            _indent(elem, level + 1)
        if not elem.tail or not elem.tail.strip():
            elem.tail = i
    else:
        if level and (not elem.tail or not elem.tail.strip()):
            elem.tail = i
