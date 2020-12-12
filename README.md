
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

## Quick overview

First, open a web page using a browser and get a `sQ` object bound to it:

```python
>>> from selectq import open_browser

>>> sQ = open_browser('https://books.toscrape.com/', 'firefox',
...         headless=True,
...         executable_path='./driver/geckodriver',
...         firefox_binary="/usr/bin/firefox-esr")      # byexample: +timeout=30
```

> Other browsers than Firefox are available. Consult the documentation of
> [selenium](https://selenium-python.readthedocs.io/installation.html#drivers)
> to read more about them and the drivers needed. You will have to
> download the driver of your browser and set the path to it with
> `executable_path`.

Open the page that has science fiction books:

```python
>>> from selectq.predicates import Text, Attr as attr, Value as val

>>> page_link = sQ.select('a', Text.normalize_space() == 'Science Fiction')
>>> page_link.click()
```

And let's choose one of the books

```python
>>> book_link = sQ.select('a', attr('href').contains('william'))
>>> book_link.click()
FAIl
```

What happen? Clicking requires to select one element but it seems that
we are selecting more than one (or even zero).

Let's check that. Here a pretty print is very useful:

```python
>>> book_link.count()
2

>>> book_link.pprint()
<a href="../../../william-shakespeares-star-wars-verily-a-new-hope-william-shakespeares-star-wars-4_871/index.html">
  <img src="../../../../media/cache/02/37/0237b445efc18c5562355a5a2c40889c.jpg" alt="William Shakespeare's Star Wars: Verily, A New Hope (William Shakespeare's Star Wars #4)" class="thumbnail">
</a>
<a href="../../../william-shakespeares-star-wars-verily-a-new-hope-william-shakespeares-star-wars-4_871/index.html" title="William Shakespeare's Star Wars: Verily, A New Hope (William Shakespeare's Star Wars #4)">William Shakespeare's Star Wars: ...<
```

Both links will work, so we pick just the first and we move on

```python
>>> book_link[0].click()
```


```python
>>> sQ.browser.quit()       # byexample: +pass -skip +timeout=30
```
