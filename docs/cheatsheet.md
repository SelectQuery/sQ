# XPATH Cheatsheet

Taken from [devhints](https://devhints.io/xpath#class-check).

This is a quick cheatsheet for `selectq` and XPATH.

For an application use you can read [how to parse a local file
tutorial](https://github.com/SelectQuery/sQ/blob/master/docs/filebrowser.md)
and [how to scrap a webpage tutorial](https://github.com/SelectQuery/sQ/blob/master/README.md).

```python
>>> from selectq import Selector, Attr as attr, Value as val, Text
>>> sQ = Selector()
```

## Selectors

### Descendant selectors

Select all the headers 1 (`<h1>` tags):

```python
>>> sQ.select('h1')
sQ .//h1
```

Select all the `<div>` and for each one, select all the paragraphs
`<p>`:

```python
>>> sQ.select('div').select('p')
sQ .//div//p
```

Select all the unordered lists `<ul>` and for each one, select all
the items `<li>` that are an immediate children of the list:

```python
>>> sQ.select('ul').children('li')
sQ .//ul/li
```

Same as above but for each item list `<li>` then select the anchors
`<a>` that are an immediate children of the item:

```python
>>> sQ.select('ul').children('li').children('a')
sQ .//ul/li/a
```

Select all the immediate children of all the `<div>`:

```python
>>> sQ.select('div').children()
sQ .//div/*
```

*TODO*: "/" and "/body"

## Order selectors

Select the first of **each** `<ul>`'s `<li>` children. Therefore
this may select more than one `<li>` if there are multiples `<ul>`.

If you want the first of **all** `<ul>`'s `<li>` children you should
do `sQ.select('ul').children('li')[0]`.

```python
>>> sQ.select('ul').children('li').at(0)
sQ .//ul/li[1]
```

Select the second of **each** `<ul>`'s `<li>` children.

Note that the XPATH indexes starting from 1 but `selectq`, like Python,
indexes starting from 0.

```python
>>> sQ.select('ul').children('li').at(1)
sQ .//ul/li[2]
```

Select the last of **each** `<ul>`'s `<li>` children.

```python
>>> sQ.select('ul').children('li').at(-1)
sQ .//ul/li[last()]
```

Select the first of **all** `<li>` which have an attribute named `id`
valued to `"id"`:

```python
>>> sQ.select('li', id="id").at(0)
sQ .//li[@id='id'][1]
```

Select the first of **all** `<a>`:

```python
>>> sQ.select('a').at(0)
sQ .//a[1]
```

Select the last of **all** `<a>`:

```python
>>> sQ.select('a').at(-1)
sQ .//a[last()]
```

## Attribute selectors

Select all the elements that have an attribute named `id`
valued to `"id"`:

```python
>>> sQ.select('*', id='id')
sQ .//*[@id='id']
```

Select all the elements that have an attribute named `class`
valued to `"class"`.

Because `class` is a reserved word in Python, `selectq` accepts `class_`
as an alias for it:

```python
>>> sQ.select('*', class_='class')
sQ .//*[@class='class']
```

Select all the `<input>` tags that have an attribute named `type`
valued to `"submit"`:

```python
>>> sQ.select('input', type="submit")
sQ .//input[@type='submit']
```

Select all the `<a>` tags that have an attribute named `rel`:

```python
>>> sQ.select('a', rel=None)
sQ .//a[@rel]
```

Select all the `<a>` tags that have an attribute named `id`
valued to `"abc"` that also match the XPATH condition `"@for='xyz'"`.

The `that()` method allows you to write **arbitrary** XPATH conditions.
It is up to you to make them syntactically correct.

```python
>>> sQ.select('a', id="abc").that("@for='xyz'")
sQ .//a[@id='abc'][@for='xyz']
```

Select all the `<a>` tags that have an attribute named `href`
which value starts with `'/'`.

```python
>>> sQ.select('a').that(attr('href').startswith('/'))
sQ .//a[starts-with(@href, '/')]
```

The above is equivallent to set the predicate in the `select` method
call:

```python
>>> sQ.select('a', attr('href').startswith('/'))
sQ .//a[starts-with(@href, '/')]
```


Select all the `<a>` tags that have an attribute named `href`
which value ends with `'.pdf'`.


```python
>>> sQ.select('a').that(attr('href').endswith('.pdf'))
sQ .//a[ends-with(@href, '.pdf')]
```

Select all the `<a>` tags that have an attribute named `href`
which value contains with `'://'`.

```python
>>> sQ.select('a').that(attr('href').contains('://'))
sQ .//a[contains(@href, '://')]
```

Select all the `<a>` tags that have an attribute named `rel`
which value contains with `'help'`.

```python
>>> sQ.select('a').that(attr('rel').contains('help'))
sQ .//a[contains(@rel, 'help')]
```

> Note: it would be nice but sadly you cannot do `"help" in attr('rel')`
> Python enforces the return value of `in` to be boolean and that
> breaks the illusion. `sQ` will fail with a descriptive error:

```python
>>> sQ.select('help' in attr('rel'))        # byexample: +tags
Traceback (most recent call last):
<...>
Exception: Sorry 'foo in attr' is not supported. Use 'attr.contains(foo)' instead.
```

## Siblings

```python
>>> sQ.select('h1').children('following-sibling::ul')
sQ .//h1/following-sibling::ul

>>> sQ.select('h1').children('following-sibling::ul').at(0)
sQ .//h1/following-sibling::ul[1]

>>> sQ.select('h1').children('following-sibling::', id='id')
sQ .//h1/following-sibling::[@id='id']
```

## Other things

Select all the `<h1>` that don't have an attribute named `id`:

```python
>>> sQ.select('h1').that('not(@id)')
sQ .//h1[not(@id)]
```

Select all the `<button>` that have a text equals to 'Submit':

```python
>>> sQ.select('button').that(Text == 'Submit')
sQ .//button[text() = 'Submit']
```

Select all the `<button>` that have a text that contains 'Go':

```python
>>> sQ.select('button').that(Text.contains('Go'))
sQ .//button[contains(text(), 'Go')]
```

Select all the `<product>` that have an attribute named `'price'`
that it is greather than 2.50 *and* lesser than 5:

```python
>>> sQ.select('product').that((attr("price") > 2.50) & (attr("price") < 5))
sQ .//product[(@price > 2.5) and (@price < 5)]
```

Select all the `<ul>` that have at least one child tag:

```python
>>> sQ.select('ul').has_children()
sQ .//ul[*]
```

Select all the `<ul>` that have at least one `<li>` child tag:

```python
>>> sQ.select('ul').has_children("li")
sQ .//ul[li]
```

Select all the `<a>` that have an attribute named `'name'`
*or* and attribute named `'href'`:

```python
>>> sQ.select('a').that(attr('name') | attr('href'))
sQ .//a[@name or @href]
```

Select all the `<a>` and `<div>`. The `|` symbol denotes the *union*
of the two selections:

```python
>>> sQ.select('a') | sQ.select('div')
sQ (.//a) | (.//div)
```

## jQuery

```python
>>> sQ.select('ul').children('li').parent()
sQ .//ul/li/..
```

```python
>>> sQ.select('li').children('ancestor-or-self::section')
sQ .//li/ancestor-or-self::section
```

```python
>>> sQ.select('a').query('@href')
sQ .//a/@href
```

```python
>>> sQ.select('span').query('text()')
sQ .//span/text()
```

## Class check

Select all the `<div>` that have an attribute named `class` that
have the word `'foobar'`. A *word* means that it is separated by spaces
so this predicate is much preciser than a simple `contains`:

```python
>>> sQ.select('div').that(attr('class').has_word('foobar'))
sQ .//div[contains(concat(' ', normalize-space(@class), ' '), ' foobar ')]
```
