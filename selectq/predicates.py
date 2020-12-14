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

    has = contains

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

    def __contains__(self, s):
        raise Exception(
            "Sorry 'foo in attr' is not supported. Use 'attr.contains(foo)' instead."
        )

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

    def __repr__(self):
        return "Predicate {}".format(self)


class Attr(Value):
    def __str__(self):
        return "@{}".format(self.val)


Text = Value('text()')
