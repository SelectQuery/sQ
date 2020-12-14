from lxml import etree
import contextlib
from .browsers import Browser, _browser_wrapper
from .predicates import Value, Attr
from .interactions import InteractionMixin
'''
>>> from selectq import FileBrowser, Selector, Attr as attr, Value as val
>>> browser = FileBrowser()
>>> sQ = Selector(browser)
'''


class Selection(InteractionMixin):
    def __init__(self, browser, xpath):
        self.browser = _browser_wrapper(browser)
        self.xpath = xpath

    def bind(self, browser):
        return Selection(browser, self.xpath)

    def pprint(self):
        self.browser.pprint(self.xpath)

    def _select_xpath_for(
        self, tag, *predicates, class_=None, for_=None, **attrs
    ):
        xpath = ''
        if tag is not None:
            # we accept a selection instead of a tag
            if isinstance(tag, Selection):
                # explicit "!s" conversion to ignore any parenthesis
                tag = '{!s}'.format(tag)

            # we also "accept" a Value/Attr. Internally we say
            # that the tag is '*' and we treat the Value/Attr as another
            # predicate
            elif isinstance(tag, (Value, Attr)):
                predicates = (tag, ) + predicates
                tag = '*'

            xpath += tag
        else:
            xpath += '*'

        if class_ is not None:
            xpath += "[@class='{}']".format(class_)

        if for_ is not None:
            xpath += "[@for='{}']".format(for_)

        for predicate in predicates:
            if not isinstance(predicate, (Selection, Value, Attr)):
                raise ValueError(
                    "Invalid object as predicate: {}".format(repr(predicate))
                )

            # explicit "!s" conversion to ignore any parenthesis
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

    def select(self, tag=None, *predicates, class_=None, for_=None, **attrs):
        ''' Select any children that have <tag> or '*' if None; from there,
            only select the ones that have all the predicates in true.

            The predicates are build from the position arguments <predicates>,
            the 'class' and 'for' attributes <class_> <for_> and the
            keyword attributes <attr>.

            >>> sQ.select()
            sQ .//*

            >>> sQ.select('li', attr('href').endswith('.pdf'), class_='cool', id='uniq')
            sQ .//li[@class='cool'][ends-with(@href, '.pdf')][@id='uniq']

            >>> sQ.select(for_='cool')
            sQ .//*[@for='cool']
        '''
        xpath = self._select_xpath_for(
            tag, *predicates, class_=class_, for_=for_, **attrs
        )
        xpath = self.xpath + '//' + xpath
        return Selection(self.browser, xpath)

    def children(self, tag=None, *predicates, class_=None, for_=None, **attrs):
        ''' Select any direct children.

            It works like `select` but it restricts the selection to
            only the direct children.

            >>> sQ.children()
            sQ ./*

            >>> sQ.children('li', attr('href').endswith('.pdf'), class_='cool', id='uniq')
            sQ ./li[@class='cool'][ends-with(@href, '.pdf')][@id='uniq']
        '''
        xpath = self._select_xpath_for(
            tag, *predicates, class_=class_, for_=for_, **attrs
        )
        xpath = self.xpath + '/' + xpath
        return Selection(self.browser, xpath)

    def has_children(self, selection=None):
        ''' Select the elements that have children specified by <selection>.
            If None, select the elements that have at least one child.
            '''
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
        ''' From the selection, subselect based on a position or range.
            The parameter <key> has the same semantics that any other
            indexing.
            '''
        cond = self._predicate_from_index(key)
        xpath = "({})[{}]".format(self.xpath, cond)
        return Selection(self.browser, xpath)

    def at(self, key):
        ''' Select those who are at the given position or range
            respect their parents.
            '''
        cond = self._predicate_from_index(key)
        xpath = "{}[{}]".format(self.xpath, cond)
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

    @contextlib.contextmanager
    def switched(self):
        ''' Context manager that switch to the selected frame when
            entering to the context and return to the previous frame on
            exit.

            The current selection must contain one and only one element
            and this element must be a valid frame like element like
            'iframe'.
            '''
        elems = self.web_elements()
        if len(elems) != 1:
            if len(elems) == 0:
                raise Exception(
                    "No frame was selected so you cannot switch to it."
                )
            else:
                raise Exception(
                    "More than one element was selected so you cannot switch to the frame."
                )

        self.browser.driver.switch_to.frame(elems[0])
        try:
            yield self
        finally:
            self.browser.driver.switch_to.parent_frame()


class Selector(Selection):
    def __init__(self, browser=Browser()):
        super().__init__(browser, '.')

    def abs_select(
        self, tag=None, *predicates, class_=None, for_=None, **attrs
    ):
        ''' Make the selection absolute.

            It works like `select` but it restricts the selection
            starting from the root.

            >>> sQ.abs_select()
            sQ /*

            >>> sQ.abs_select('li', attr('href').endswith('.pdf'), class_='cool', id='uniq')
            sQ /li[@class='cool'][ends-with(@href, '.pdf')][@id='uniq']
        '''
        xpath = self._select_xpath_for(
            tag, *predicates, class_=class_, for_=for_, **attrs
        )
        xpath = '/' + xpath
        return Selection(self.browser, xpath)

    def pprint(self):
        print("sQ - nothing selected")
