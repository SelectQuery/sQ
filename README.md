
Interact with web pages programmatically and painless from Python.

`selectq`, or `sQ` for short, is a Python library that aims to simplify
the slow operation of interacting with a web page.

It has three level of operations:

 - *Browserless*: `sQ` helps you to build `xpath` expressions to select
   easily elements of a page but, as the name suggests, no browser is
   involved so `sQ` will not interact with the page. This is the
   operation mode that you want to use if you are using a third-party
   library to interact with the web page like
   [scrapy](https://scrapy.org/)
 - *FileBrowser*: `sQ` models the file based web page as a XML then
   allows you to inspect/extract any information that you want from it
   using `xpath`. If you want to practice your skills with `sQ`, this is
   the operation mode to do that. In fact, most of the tests of `sQ` are
   executed in this mode because no real browser is needed.
 - *WebBrowser*: open you favorite browser and control it from Python.
   `sQ` will allow you to extract information from the web page *and*
   you will be able to interact with it from doing a click to messing up
   with the page's javascript for dirty tricks. This is the operation
   mode where the fun begins. If you need a real environment, this is
   your operation mode.

In short: if you want to **scrap thousands** of web pages use
[scrapy](https://scrapy.org/) plus `sQ` in *Browserless* mode; if you
want to scrap / interact with a few web pages **as an human would do** use
`sQ` in *WebBrowser* mode.

## Tutorial: Scrap a book store

First, open a web page using a **browser** and get a `sQ` object bound to it:

```python
>>> from selectq import open_browser

>>> sQ = open_browser(
...         'https://books.toscrape.com/',
...         'firefox',
...         headless=True,
...         executable_path='./driver/geckodriver',
...         firefox_binary="/usr/bin/firefox-esr")      # byexample: +timeout=30
```

> Other browsers than Firefox are available. Consult the documentation of
> [selenium](https://selenium-python.readthedocs.io/installation.html#drivers)
> to read more about them and the drivers needed. You will have to
> download the driver of your browser and set the path to it with
> `executable_path`.
>
> In the case of Firefox, it is
> [geckodriver](https://github.com/mozilla/geckodriver/releases)


*Tip*: change `headless=True` by `headless=False` so you can see `selectq`
in action.

`sQ` is a `Selector`: an object that will allow us to **select** and
**interact** with the elements of the web page.

Let's open the `'Science Fiction'` section so we can access to the books
of that category:

```python
>>> from selectq.predicates import Text, Attr as attr, Value as val

>>> page_link = sQ.select('a', Text.normalize_space() == 'Science Fiction')
>>> page_link.click()
```

`sQ.select` is
[incredible flexible](https://github.com/SelectQuery/sQ/blob/master/docs/cheatsheet.md)
but in this example we are requiring
only a small subset of its features.

`sQ.select('a')` selects all the HTML *anchors* (tags `<a>`).

We are interested in the only one that has `'Science Fiction'` as its
text.

`Text.normalize_space() == 'Science Fiction'` is a **predicate**: a way
to *filter* results from a selection. In this case we are saying *"take
the text, normalize its space and compare it against 'Science
Fiction'"*.

Finally, `page_link.click()`, as you may guessed, it clicks in the link
and open the desired web page.

Let's choose one of the books.

```python
>>> book_link = sQ.select('a', attr('href').contains('william'))
```

Once again we are selecting the HTML *anchors* that have an HTML
*attribute* named `'href'` which value must *contain* the string
`'william'`.

Something like `<a href='bruce william'>foo</a>`.

Now we want to open it:

```python
>>> book_link.click()
<...>
Exception: Unexpected count. Expected 1 but selected 2.
```

What happen? Clicking requires to select one element but it seems that
we are selecting more than one.

Let's check that. Here a **pretty print** is very useful:

```python
>>> book_link.count()
2

>>> book_link.pprint()
<a href="../../../william-shakespeares-star-wars-verily-a-new-hope-william-shakespeares-star-wars-4_871/index.html">
  <img src="../../../../media/cache/02/37/0237b445efc18c5562355a5a2c40889c.jpg" alt="William Shakespeare's Star Wars: Verily, A New Hope (William Shakespeare's Star Wars #4)" class="thumbnail">
</a>
<a href="../../../william-shakespeares-star-wars-verily-a-new-hope-william-shakespeares-star-wars-4_871/index.html" title="William Shakespeare's Star Wars: Verily, A New Hope (William Shakespeare's Star Wars #4)">William Shakespeare's Star Wars: ...</a>
```

If you are ran the browser with `headless=False`, `selectq` can
**highlight** the selected elements so you can spot them in the
browser with `book_link.highlight()`. Quite handy uh?

Okay, let's pick one of the links and move on.

Both links will work, so we pick just the first and we move on

```python
>>> book_link[1].click()
```

`selectq` supports
[indexing, ranges and iterations](https://github.com/SelectQuery/sQ/blob/master/docs/cheatsheet.md)
too. See also an example of `FileBrowser` [here](https://github.com/SelectQuery/sQ/blob/master/docs/filebrowser.md).

The page of the book has a table that describes it.

We can get the headers of the table with:

```python
>>> sQ.select('tr').select('th').text()
['UPC',
 'Product Type',
 'Price (excl. tax)',
 'Price (incl. tax)',
 'Tax',
 'Availability',
 'Number of reviews']
```

Note that we are **chaining** selections: `select('tr').select('th')`
selects all the table rows (`tr` tag) and for each row select all the
table headers inside of it (`th` tag).

To retrieve the texts, just call `text()` of course.

To retrieve the headers and the values we could do something like:

```python
>>> rows = sQ.select('tr')
>>> (rows.select('th') | rows.select('td')).text()
['UPC',
 '9270575728a13a61',
 'Product Type',
 'Books',
 'Price (excl. tax)',
 '£43.30',
<...>
```

What about AJAX? Modern web pages are asynchronous so we cannot click in
a button to open a form and expect to interact with it immediately.

The page needs time to load the form!

It was not needed so far but if you have to, `selectq` has a simple
`wait_for` syntax:

```python
>>> from selectq import wait_for

>>> page_link.click() # reload the page and wait for the book link shows up
>>> wait_for(book_link >= 1)      # byexample: +timeout=35
```

After scrapping all that you want, don't forget to close/quit the
browser:

```python
>>> sQ.browser.quit()       # byexample: +pass -skip +timeout=30
```
