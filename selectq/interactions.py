import json
import requests
import os.path
import operator


class InteractionMixin:
    def highlight(self):
        ''' Modify the elements selected to highlight them. '''
        js = 'return selectq.highlight(elems);'
        return self.browser.js_call(self.xpath, js)

    # TODO support for 'foo.bar.baz' properties and for 'invoking' methods
    def pluck(self, *properties):
        ''' Retrieve one or more properties of each element selected
            by the xpath.

            If <properties> is a list with a single property name,
            pluck will return a list of values where each value is
            the value of the named property.

            If <properties> is a list with more than one name, return
            a list of lists where each sublist will have the value of each
            named property.
            '''
        if not properties:
            raise ValueError('The property list is empty.')

        if not isinstance(properties, (list, tuple)):
            raise TypeError(
                "Invalid type for the property list. Expected 'list' or 'tuple' but found '{}'."
                .format(type(properties))
            )

        is_single_prop = len(properties) == 1

        properties = json.dumps(properties)
        jscall = 'selectq.pluck(el, {properties});'.format(
            properties=properties
        )
        results = self.browser.js_map(self.xpath, jscall)

        if is_single_prop:
            return [arr[0] for arr in results]

        return results

    def click(self, single=True):
        ''' Click in the selected Selenium WebElement.

            Click in a single element selected. If no element was
            selected or more than one was selected, an exception
            will be raised.

            If <single> is False, the restriction is relaxed: all
            the elements selected (zero, one or more) will be clicked.
            '''

        if False:
            js = 'return selectq.click(elems, {});'.format(str(single).lower())
            return self.browser.js_call(self.xpath, js)

        if True:
            elems = self.web_elements()
            elem_cnt = len(elems)
            if single and elem_cnt != 1:
                raise Exception(
                    'Unexpected count. Expected 1 but selected {}.'.
                    format(elem_cnt)
                )

            for el in elems:
                el.click()

    def send_keys(self, values):
        ''' Send keys to the selected elements.

            <values> can be a single string in which case the selected
            Selenium WebElement must be a single one.

            <values> can be also be a list of strings in which case the
            count of selected Selenium WebElements must be equal to the
            count of <values>.

            Each string then will be send to each WebElement.
            '''
        elems = self.web_elements()
        elem_cnt = len(elems)
        if isinstance(values, (list, tuple)):
            val_cnt = len(values)
            if elem_cnt != val_cnt:
                raise Exception()

            for el, val in zip(elems, values):
                el.send_keys(val)
        else:
            if elem_cnt != 1:
                raise Exception()

            elems[0].send_keys(values)

    def clear(self):
        ''' Clear the selected elements. Use this to clear a text input
            for example.
            '''
        elems = self.web_elements()
        for el in elems:
            el.clear()

        # Return self to support sQ(...).clear().send_keys(...)
        # (aka clear and set a new text)
        return self

    def web_elements(self):
        ''' Retrieve the Selenium WebElements found by the current selection.

            Note: because the web page may change later, interacting
            with a WebElement may end in an error (exception) if the element
            is not available after the selection.
            '''
        return self.browser.driver.find_elements('xpath', self.xpath)

    def download(self, dest_folder='.'):
        ''' Pluck the href or src attributes of the selected elements
            and download the content of those urls and save them in
            the given destination folder.

            '''
        # "copy" the selenium's session into the requests' session
        cookies = self.browser.driver.get_cookies()
        s = requests.Session()
        for c in cookies:
            # TODO add more things? https://github.com/tryolabs/requestium/blob/9533932ae688da26f3fb78b97b3c0b05c6f24934/requestium/requestium.py#L111-L114
            s.cookies.set(c['name'], c['value'], domain=c['domain'])

        # TODO add more things like proxy? host?
        user_agent = self.browser.driver.execute_script(
            "return navigator.userAgent;"
        )
        s.headers.update({'user-agent': user_agent})

        urls = [
            href if href else src for href, src in self.pluck('href', 'src')
        ]
        fnames = []
        for url in urls:
            if not url:
                continue

            res = s.get(url)
            # TODO make the file name safer
            fname = os.path.join(
                dest_folder,
                url.replace(':', '').replace('/', '_')
            )
            with open(fname, 'wb') as f:
                f.write(res.content)

            fnames.append(fname)

        return fnames

    def text(self, inner=False):
        ''' Return all the text elements inside the selected nodes
            concatenated (one single string per node).

            This text includes the text of all the elements inside
            the selected nodes.

            If only the text of the selected nodes are needed (and
            not of the children's), pass inner=True.
        '''
        return self.pluck('innerText' if inner else 'textContent')

    def html(self):
        return self.pluck('outerHTML')

    def describe(self, props=['id', 'name', 'type', 'className', 'href']):
        ''' Describe the selected node reading some of its attributes and
            pretty printing them.

            Under the hood this calls `self.pluck` so the same
            attributes can be obtained separately.

            By default a set of predefined properties/attributes are read.
            You can change them if needed.
        '''
        ret = []
        for tag, *vals in self.pluck('tagName', *props):
            desc = [f"tag: {tag}"]
            for p, v in zip(props, vals):
                if not v:
                    continue

                if p == 'className':
                    p = 'class'

                desc.append(f' - {p}: <{v}>')

            ret.extend(desc)

        print('\n'.join(ret))

    def count(self):
        jscall = 'return elems.length;'
        return self.browser.js_call(self.xpath, jscall)

    def expects(self, expected_count):
        cnt = self.count()

        if isinstance(expected_count, int):
            is_good = cnt == expected_count

        elif isinstance(expected_count, str):
            expected_count = expected_count.strip()
            prefix2 = expected_count[:2]
            op2 = {
                '<=': operator.le,
                '>=': operator.ge,
                '==': operator.eq,
                '!=': operator.ne,
            }

            op2 = op2.get(prefix2)

            prefix1 = expected_count[:1]
            op1 = {
                '<': operator.lt,
                '=': operator.eq,
                '>': operator.gt,
            }

            op1 = op1.get(prefix1)

            # The order of these checks is important. We need to check
            # op2 first because it has the longest prefix.
            # If we match op1 first, the '<' will match '<=3' and it shouldn't
            if op2:
                op = op2
                val = expected_count[2:]
            else:
                op = op1
                val = expected_count[1:]

            if op is None:
                raise ValueError(f"Unknown expected value '{expected_count}'.")

            val = int(val)

            is_good = op(cnt, val)
        else:
            raise TypeError(
                f"Unknown expected object '{type(expected_count)}'. Expected an integer for exact count or a string like '<=3' or '> 42'."
            )

        if not is_good:
            raise Exception(
                f"Expected a count of {expected_count} but we found {cnt} for {self}."
            )

        return self
