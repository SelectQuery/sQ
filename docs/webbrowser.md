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
>>> from selectq import open_browser, Value as val, Attr as attr, Text
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

<!--
This extra wait is needed because after the highlight() we will search
for the highlight's class. This class is added by highlight() but it is
also removed and re-added repeatedly so any subsequent check may or may
not find the class.
Adding a little wait fixes this.
>>> import time; time.sleep(2) # byexample: +timeout=5
-->

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

What about AJAX? Modern web pages are asynchronous so we cannot click in
a button to open a form and expect to interact with it immediately.

The page needs time to load the form!

That is where `wait_for` comes in:

```python
>>> from selectq import wait_for
>>> sQ.select(Text.lower() == 'reports').click()

>>> wait_for(sQ.select(Text.lower() == 'section title') >= 1)      # byexample: +timeout=35
```

Don't forget to close the browser at the end:

```python
>>> sQ.browser.quit()   # byexample: -skip +pass +timeout=60
```
