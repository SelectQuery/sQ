Taken from https://devhints.io/xpath#class-check

```python
>>> from selectq import Selector, Attr as attr, Value as val
>>> sQ = Selector()
```

## Selectors

### Descendant selectors

```python
>>> sQ.select('h1')
sQ .//h1

>>> sQ.select('div').select('p')
sQ .//div//p

>>> sQ.select('ul').children('li')
sQ .//ul/li

>>> sQ.select('ul').children('li').children('a')
sQ .//ul/li/a

>>> sQ.select('div').children()
sQ .//div/*
```

TODO: "/" and "/body"

## Order selectors

```python
>>> sQ.select('ul').children('li').at(0)
sQ .//ul/li[1]

>>> sQ.select('ul').children('li').at(1)
sQ .//ul/li[2]

>>> sQ.select('ul').children('li').at(-1)
sQ .//ul/li[last()]

>>> sQ.select('li', id="id").at(0)
sQ .//li[@id='id'][1]

>>> sQ.select('a').at(0)
sQ .//a[1]

>>> sQ.select('a').at(-1)
sQ .//a[last()]
```

## Attribute selectors

```python
>>> sQ.select('*', id='id')
sQ .//*[@id='id']

>>> sQ.select('*', cls='class')
sQ .//*[@class='class']

>>> sQ.select('input', type="submit")
sQ .//input[@type='submit']

>>> sQ.select('a', id="abc").that("@for='xyz'")
sQ .//a[@id='abc'][@for='xyz']

>>> sQ.select('a', rel=None)
sQ .//a[@rel]

>>> sQ.select('a').that(attr('href').startswith('/'))
sQ .//a[starts-with(@href, '/')]

>>> sQ.select('a').that(attr('href').endswith('.pdf'))
sQ .//a[ends-with(@href, '.pdf')]

>>> sQ.select('a').that(attr('href').contains('://'))
sQ .//a[contains(@href, '://')]

>>> sQ.select('a').that(attr('rel').contains('help'))
sQ .//a[contains(@rel, 'help')]
```

> Note: it would be nice but sadly you cannot do `"help" in attr('rel')`

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

```python
>>> sQ.select('h1').that('not(@id)')
sQ .//h1[not(@id)]

>>> sQ.select('button').that(val("text()") == 'Submit')
sQ .//button[text() = 'Submit']

>>> sQ.select('button').that(val("text()").contains('Go'))
sQ .//button[contains(text(), 'Go')]

>>> sQ.select('product').that((attr("price") > 2.50) & (attr("price") < 5))
sQ .//product[(@price > 2.5) and (@price < 5)]

>>> sQ.select('ul').has_children()
sQ .//ul[*]

>>> sQ.select('ul').has_children("li")
sQ .//ul[li]

>>> sQ.select('a').that(attr('name') | attr('href'))
sQ .//a[@name or @href]

>>> sQ.select('a') | sQ.select('div')
sQ (.//a) | (.//div)
```

## jQuery

```python
>>> sQ.select('ul').children('li').parent()
sQ .//ul/li/..

>>> sQ.select('li').children('ancestor-or-self::section')
sQ .//li/ancestor-or-self::section

>>> sQ.select('a').attr('href')
sQ .//a/@href

>>> sQ.select('span').query('text()')
sQ .//span/text()
```

## Class check

```python
>>> sQ.select('div').that(attr('class').has_word('foobar'))
sQ .//div[contains(concat(' ', normalize-space(@class), ' '), ' foobar ')]
```
