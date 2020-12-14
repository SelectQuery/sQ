sQ requires a web browser and [Selenium](http://seleniumhq.org/) to be
installed.

```shell
$ pip install selenium      # byexample: +skip
```

For the given web browser of your preference, you will need to install
the appropriate [web driver](https://pypi.org/project/selenium/)

In the case of Firefox, it is
[geckodriver](https://github.com/mozilla/geckodriver/releases)

Check also [Selenium quick reference](https://www.selenium.dev/documentation/en/webdriver/driver_requirements/#quick-reference)

```python
>>> from selectq import open_browser, Value as val, Attr as attr
>>> import os.path

>>> url = 'file://' + os.path.abspath('./test/ds/dashboard.html')

>>> sQ = open_browser(
...         url,
...         'firefox',
...         headless=True,
...         executable_path='./driver/geckodriver',
...         firefox_binary="/usr/bin/firefox-esr")  # byexample: +timeout=60
```

> `open_browser` is just a shortcut to open a Firefox webdriver
> (Selenium), create a `Selector` (selectq) and open the given url.
> The `sQ` returned is the `Selector` bound to the driver.

With the *bound* `sQ` object we can query the DOM.

For example, retrieve the text of the first 5 `td` elements that
are the first of each row (`at(0)`):

```python
>>> sQ.select('td').at(0)[:5].pluck('textContent')
['1,001', '1,002', '1,003', '1,003', '1,004']
```

In this other example, pretty print all the links (`a`) which
has the substring `'Nav'`:

```python
>>> sQ.select('a', val('text()').contains('Nav')).pprint()
<a href="">Nav item</a>
<a href="">Nav item again</a>
<a href="">Nav item again</a>
```

`pprint` is useful to explore the DOM but sometimes can be hard to see
what are you really selecting.

`highlight` does that: it highlight the elements. Of course you need to
open the browser with `headless=False` to see something!

```python
>>> sQ.select('a', val('text()').contains('Nav')).highlight()
```

Internally this works modifying the web page adding the CSS class
`sQ-highlight`. You can retrieve them later selecting by class:

```python
>>> sQ.select(class_='sQ-highlight').pprint()
<a href="" class="sQ-highlight">Nav item</a>
<a href="" class="sQ-highlight">Nav item again</a>
<a href="" class="sQ-highlight">Nav item again</a>

>>> sQ.select(class_='sQ-highlight').count()
3
```

To remove all the highlight just run

```python
>>> sQ.browser.highlight_off()
>>> sQ.select(class_='sQ-highlight').pprint() # and nothing is found
>>> sQ.select(class_='sQ-highlight').count()
0
```

Don't forget to close the browser at the end:

```python
>>> sQ.browser.quit()   # byexample: -skip +pass +timeout=60
```
