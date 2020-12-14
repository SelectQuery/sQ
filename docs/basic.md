So what is `selectq` (`sQ` for short)?

It is a simple way to find and interact with elements of a web page.

The basic unit of `selectq` are the selections.
With them you can find the elements even if they are arbitrary nested
in the page.

But first we need to us a browser to fetch the page:

```python
>>> from selectq import FileBrowser, Selector

>>> browser = FileBrowser()
```

`sQ` currently supports a *static* browser which can read web pages
and XML like files locally.

Any browser has associated a `selector` object, the main way to interact
with the web page that the browser is, well, browsing.

By convention we call this `sQ`:

```python
>>> sQ = Selector(browser)
```

Let's load this very simple HTML fragment in the browser through
the selector.

```python
>>> sQ.browser.get('./test/ds/ul.html')
```

Select all the list items:

```python
>>> sQ.select('li').pprint()
<li>list item 1</li>
<li>list item 2</li>
<li>list item 3</li>
<li>list item 4</li>
<li>list item 5</li>
<li>list item 6</li>
```

The list items of the `"secondary"` list:

```python
>>> sQ.select(class_='secondary').select('li').pprint()
<li>list item 4</li>
<li>list item 5</li>
<li>list item 6</li>
```

Note how the last `select('li')` is relative to the first
`select(class_='secondary')` and the selection finds the elements
at any *depth*.

You can select the list items that are direct *children*
of the selected `"secondary"` list using `children`:

```python
>>> sQ.select(class_='secondary').children('li').pprint()
<li>list item 4</li>
<li>list item 5</li>
```

If no argument is given, `children` returns all the direct children
of the previous selected element:

```python
>>> sQ.select(class_='secondary').children().pprint()
<li>list item 4</li>
<li>list item 5</li>
<ul value="2">
  <li>list item 6</li>
</ul>
```

And like any other sequence, indexing is supported yielding each
time a (sub)selection:

```python
>>> sel = sQ.select('li')

>>> sel[0].pprint()
<li>list item 1</li>

>>> sel[1].pprint()
<li>list item 2</li>

>>> sel[-1].pprint()
<li>list item 6</li>

>>> sel[-2].pprint()
<li>list item 5</li>

>>> sel[0:4].pprint()
<li>list item 1</li>
<li>list item 2</li>
<li>list item 3</li>
<li>list item 4</li>

>>> sel[1:4].pprint()
<li>list item 2</li>
<li>list item 3</li>
<li>list item 4</li>

>>> sel[3:99].pprint()
<li>list item 4</li>
<li>list item 5</li>
<li>list item 6</li>

>>> sel[:-1].pprint()
<li>list item 1</li>
<li>list item 2</li>
<li>list item 3</li>
<li>list item 4</li>
<li>list item 5</li>

>>> sel[-4:-2].pprint()
<li>list item 3</li>
<li>list item 4</li>

>>> sel[-1:].pprint()
<li>list item 6</li>
```

While `sel[0]` selects the first element of `sel`, `sel.at(0)` selects
the first element of *each* element of `sel`.

```python
>>> sel[0].pprint()
<li>list item 1</li>

>>> sel.at(0).pprint()
<li>list item 1</li>
<li>list item 3</li>
<li>list item 4</li>
<li>list item 6</li>
```

## Predicates

As you guessed `class_` and `id` are shortcuts to select only the elements
that have a particular value for `class` and `id`. Same for `for_`.

Here is another example using another keyword argument:

```python
>>> sQ.select(value=1).pprint()
<ul value="1">
  <li>list item 3</li>
</ul>
```

If the value is `None`, all the elements that have the attribute
regardless of their values will be selected:

```python
>>> sQ.select(value=None).pprint()
<ul value="1">
  <li>list item 3</li>
</ul>
<ul value="2">
  <li>list item 6</li>
</ul>
```

> Note: you cannot do this for `class_` or `for_` but keep
> reading for a workaround.

More complex *predicates* can be build with `Attr` (for attributes) and
`Value` (for values)

```python
>>> from selectq import Attr as attr, Value as val

>>> sQ.select('*', attr('value') <= 1).pprint()
<ul value="1">
  <li>list item 3</li>
</ul>

>>> sQ.select('*', val('count(li)') == 1).pprint()
<ul value="1">
  <li>list item 3</li>
</ul>
<ul value="2">
  <li>list item 6</li>
</ul>
```

A predicate can be as complex as you want:

```python
>>> sQ.select('*', val('text()').contains('item 6') | (attr('value') != 2)).pprint()
<ul value="1">
  <li>list item 3</li>
</ul>
<li>list item 6</li>
```

Passing predicates to `select` is the same that passing those to `that`
which it also accepts a string as a raw predicate.

These three are the same:

```python
>>> sQ.select('*', attr('value') == 1).pprint()
<ul value="1">
  <li>list item 3</li>
</ul>

>>> sQ.select('*').that(attr('value') == 1).pprint()
<ul value="1">
  <li>list item 3</li>
</ul>

>>> sQ.select('*').that('@value = 1').pprint()
<ul value="1">
  <li>list item 3</li>
</ul>
```

The `*` can be omitted:

```python
>>> sQ.select(val('text()').contains('item 6')).pprint()
<li>list item 6</li>
```

## Union and nesting

Selections can be joined together:

```python
>>> all_main_li = sQ.select(id='a').select('li')
>>> all_sec_li = sQ.select(id='b').select('li')

>>> (all_main_li | all_sec_li).pprint()
<li>list item 1</li>
<li>list item 2</li>
<li>list item 3</li>
<li>list item 4</li>
<li>list item 5</li>
<li>list item 6</li>
```

Note that the order of the returned elements is undefined. Here
is an example where we swapped the selections but we still have
the same output than before:

```python
>>> (all_sec_li | all_main_li).pprint()
<li>list item 1</li>
<li>list item 2</li>
<li>list item 3</li>
<li>list item 4</li>
<li>list item 5</li>
<li>list item 6</li>
```

This is because under the hood the selections are transformed in
sets and the sets loose the order.

The good side is that the set allows you to remove duplicated:

```python
>>> (all_sec_li | all_main_li | all_main_li | all_sec_li).pprint()
<li>list item 1</li>
<li>list item 2</li>
<li>list item 3</li>
<li>list item 4</li>
<li>list item 5</li>
<li>list item 6</li>
```

Nesting selections is possible. You can do it with `that`
or with `has_children`.

Both are the same, but `has_children` reads/expresses better
the intention for nested selections while `that` suits better for
predicates.

```python
>>> item1 = sQ.select('li').that(val('text()') == "list item 1")

>>> sQ.select(tag='ul').that(item1).pprint()
<ul class="main" id="a">
  <li>list item 1</li>
  <li>list item 2</li>
  <ul value="1">
    <li>list item 3</li>
  </ul>
</ul>

>>> sQ.select('ul').has_children(item1).pprint()
<ul class="main" id="a">
  <li>list item 1</li>
  <li>list item 2</li>
  <ul value="1">
    <li>list item 3</li>
  </ul>
</ul>
```


