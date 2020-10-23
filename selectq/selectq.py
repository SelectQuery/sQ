from lxml import etree


class Browser:
    def __init__(self):
        pass

    def new_selector(self):
        return Selector(self)

    def get(self, url):
        raise NotImplementedError()


class FileBrowser(Browser):
    def get(self, url):
        with open(url, 'rt') as f:
            html = f.read()

        parser = etree.HTMLParser(remove_blank_text=True)
        self.tree = etree.fromstring(html, parser)


class Selection:
    def __init__(self, browser, xpath):
        self.browser = browser
        self.xpath = xpath

    def _elems(self):
        return self.browser.tree.xpath(self.xpath)  # TODO cache?

    def pprint(self):
        elems = self._elems()
        for el in elems:
            _indent(el)  # TODO cache?
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

    def _select_xpath_for(self, tag, *predicates, cls=None, **attrs):
        if all(
            arg is None for arg in [tag, cls]
        ) and not attrs and not predicates:
            raise ValueError(
                "You need to specify a tag or keyword-selector like 'cls'"
            )

        xpath = ''
        if tag is not None:
            if isinstance(tag, (Selection, Value, Attr)):
                # explicit "!s" convertion to ignore any parentesis
                tag = '{!s}'.format(tag)
            xpath += tag
        else:
            xpath += '*'

        if cls is not None:
            xpath += "[@class='{}']".format(cls)

        for predicate in predicates:
            if not isinstance(predicate, (Selection, Value, Attr)):
                raise ValueError(
                    "Invalid object as predicate: {}".format(repr(predicate))
                )

            # explicit "!s" convertion to ignore any parentesis
            xpath += "[{!s}]".format(predicate)

        for attr_name, attr_value in attrs.items():
            if attr_value is None:
                xpath += "[@{}]".format(attr_name)
            else:
                if isinstance(attr_value, (Value, Attr)):
                    xpath += "[@{}={}]".format(attr_name, attr_value)
                else:
                    xpath += "[@{}='{}']".format(attr_name, attr_value)

        return xpath

    def select(self, tag=None, *predicates, cls=None, **attrs):
        xpath = self._select_xpath_for(tag, *predicates, cls=cls, **attrs)
        xpath = self.xpath + '//' + xpath
        return Selection(self.browser, xpath)

    def children(self, tag=None, *predicates, cls=None, **attrs):
        if tag is None:
            tag = '*'
        xpath = self._select_xpath_for(tag, *predicates, cls=cls, **attrs)
        xpath = self.xpath + '/' + xpath
        return Selection(self.browser, xpath)

    def has_children(self, selection=None):
        if selection is None:
            selection = '*'
        return self.that(selection)

    def that(self, predicate):
        xpath = self.xpath + "[{!s}]".format(predicate)
        return Selection(self.browser, xpath)

    def _predicate_from_index(self, key):
        if isinstance(key, slice):
            start, stop, step = key.start, key.stop, key.step
            if step is not None and step != 1:
                raise NotImplementedError("Only step of '1' is supported")

            if start is None:
                start_cond = None
            elif start == 0:
                start_cond = None
            elif start > 0:
                start_cond = "position() >= {}".format(start + 1)
            elif start == -1:
                start_cond = "position() >= last()"
            elif start < 0:
                start_cond = "position() >= (last(){})".format(start + 1)
            else:
                assert False

            if stop is None:
                stop_cond = None
            elif stop >= 0:
                stop_cond = "position() < {}".format(stop + 1)
            elif stop < 0:
                stop_cond = "position() <= (last(){})".format(stop)
            else:
                assert False

            if start_cond and stop_cond:
                cond = "({}) and ({})".format(start_cond, stop_cond)
            elif start_cond:
                cond = start_cond
            elif stop_cond:
                cond = stop_cond
            else:
                assert False

        elif isinstance(key, int):
            if key >= 0:
                cond = "{}".format(key + 1)
            elif key == -1:
                cond = "last()"
            else:
                cond = "last(){}".format(key + 1)
        else:
            raise ValueError("Invalid index. Expected an integer or a slice")

        return cond

    def __getitem__(self, key):
        cond = self._predicate_from_index(key)
        xpath = "({})[{}]".format(self.xpath, cond)
        return Selection(self.browser, xpath)

    def at(self, key):
        cond = self._predicate_from_index(key)
        xpath = "{}[{}]".format(self.xpath, cond)
        return Selection(self.browser, xpath)

    def attr(self, name):
        xpath = "{}/{}".format(self.xpath, Attr(name))
        return Selection(self.browser, xpath)

    def query(self, what):
        xpath = "{}/{}".format(self.xpath, what)
        return Selection(self.browser, xpath)

    def parent(self):
        xpath = "{}/..".format(self.xpath)
        return Selection(self.browser, xpath)

    def __or__(self, other):
        xpath = "({}) | ({})".format(self.xpath, other.xpath)
        return Selection(self.browser, xpath)

    def __str__(self):
        return self.xpath

    def __repr__(self):
        return 'sQ ' + str(self)


class Selector(Selection):
    def __init__(self, browser):
        super().__init__(browser, '.')

    def _elems(self):
        return [self.browser.tree]

    def get(self, url):
        self.browser.get(url)


class Value:
    def __init__(self, val, require_parentesis=False):
        self.val = val
        self.require_parentesis = require_parentesis

    def _group(self, s):
        if isinstance(s, Value):
            if s.require_parentesis:
                return '({})'.format(str(s))
            else:
                return '{}'.format(str(s))

        if isinstance(s, str):
            if "'" in s and '"' not in s:
                return '"{}"'.format(s)
            elif "'" not in s and '"' in s:
                return "'{}'".format(s)
            elif "'" not in s and '"' not in s:
                return "'{}'".format(s)

            raise ValueError(
                "The string contains single and double quotes. Ensure that you are escaping the quotes correctly and then put the string into a 'Value' object: {}"
                .format(repr(s))
            )

        return '{}'.format(s)

    def startswith(self, s):
        s = self._group(s)
        return Value("starts-with({}, {})".format(self, s))

    def endswith(self, s):
        s = self._group(s)
        return Value("ends-with({}, {})".format(self, s))

    def contains(self, s):
        s = self._group(s)
        return Value("contains({}, {})".format(self, s))

    def normalize_space(self):
        return Value("normalize-space({})".format(self))

    def has_word(self, s):
        if not isinstance(s, str):
            raise ValueError(
                "Expected a string but found other thing: {}".format(repr(s))
            )

        if ' ' in s:
            raise ValueError(
                "The word cannot contain a space: {}".format(repr(s))
            )

        # strip any trailing/leading whitespace and replace
        # two or more spaces into one
        tmp = self.normalize_space()

        # ensure now that the string will have a single
        # trailing/leading whitespace.
        tmp = Value("concat(' ', {}, ' ')".format(tmp))

        # the resulting string will have each word with a
        # space to its right and left so now we can check
        # for a particular word
        word = ' {} '.format(s)
        tmp = tmp.contains(word)

        return tmp

    def __gt__(self, s):
        s = self._group(s)
        return Value("{} > {}".format(self, s), require_parentesis=True)

    def __ge__(self, s):
        s = self._group(s)
        return Value("{} >= {}".format(self, s), require_parentesis=True)

    def __lt__(self, s):
        s = self._group(s)
        return Value("{} < {}".format(self, s), require_parentesis=True)

    def __le__(self, s):
        s = self._group(s)
        return Value("{} <= {}".format(self, s), require_parentesis=True)

    def __eq__(self, s):
        s = self._group(s)
        return Value("{} = {}".format(self, s), require_parentesis=True)

    def __ne__(self, s):
        s = self._group(s)
        return Value("{} != {}".format(self, s), require_parentesis=True)

    def __or__(self, s):
        s = self._group(s)
        return Value("{} or {}".format(self, s), require_parentesis=True)

    def __and__(self, s):
        s = self._group(s)
        return Value("{} and {}".format(self, s), require_parentesis=True)

    def __str__(self):
        return "{}".format(self.val)

    def __format__(self, format_spec):
        return self._group(self).__format__(format_spec)


class Attr(Value):
    def __str__(self):
        return "@{}".format(self.val)


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
