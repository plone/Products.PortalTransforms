from html.entities import html5 as html5entities
from lxml import etree
from lxml import html
from lxml_html_clean import Cleaner
from plone.base.interfaces import IFilterSchema
from plone.base.utils import safe_bytes
from plone.base.utils import safe_text
from plone.registry.interfaces import IRegistry
from Products.PortalTransforms.interfaces import ITransform
from Products.PortalTransforms.libtransforms.utils import bodyfinder
from zope.component import getUtility
from zope.interface import implementer

import re


_strings = (bytes, str)

CSS_COMMENT = re.compile(r"/\*.*\*/")


def hasScript(s):
    """Dig out evil Java/VB script inside an HTML attribute.
    >>> hasScript(
    ...     'data:text/html;'
    ...     'base64,PHNjcmlwdD5hbGVydCgidGVzdCIpOzwvc2NyaXB0Pg==')
    True
    >>> hasScript('script:evil(1);')
    True
    >>> hasScript('expression:evil(1);')
    True
    >>> hasScript('expression/**/:evil(1);')
    True
    >>> hasScript('http://foo.com/ExpressionOfInterest.doc')
    False
    """
    s = decode_htmlentities(s)
    s = s.replace("\x00", "")
    s = CSS_COMMENT.sub("", s)
    s = "".join(s.split()).lower()
    for t in ("script:", "expression:", "expression(", "data:"):
        if t in s:
            return True
    return False


def unescape_chr(matchobj):
    try:
        return chr(int(matchobj.group(1), 16))
    except ValueError:
        return matchobj.group(0)


def decode_charref(s):
    s = s.group(1)
    try:
        if s[0] in ["x", "X"]:
            c = int(s[1:], 16)
        else:
            c = int(s)
        c = chr(c)
        return c
    except ValueError:
        return "&#" + s + ";"


def decode_entityref(s):
    s = s.group(1)
    try:
        c = html5entities[s + ";"]
    except KeyError:
        try:
            c = html5entities[s]
        except KeyError:
            # strip unrecognized entities
            c = ""
    return c


CHR_RE = re.compile(r"\\(\d+)")
CHARREF_RE = re.compile(r"&(?:amp;)?#([xX]?[0-9a-fA-F]+);?")
ENTITYREF_RE = re.compile(r"&(\w{1,32});?")


def decode_htmlentities(s):
    # Decode HTML5 entities (numeric or named).
    s = CHR_RE.sub(unescape_chr, s)
    if "&" not in s:
        return s
    s = CHARREF_RE.sub(decode_charref, s)
    return ENTITYREF_RE.sub(decode_entityref, s)


@implementer(ITransform)
class SafeHTML:
    """Simple transform which uses lxml to
    clean potentially bad tags.

    We only want security related filtering here, all the rest has to be done
    in TinyMCE & co.

    Tags must explicit be allowed in valid_tags to pass. Only
    the tags themself are removed, not their contents. If tags
    are removed and in nasty_tags, they are removed with
    all of their contents.

    Settings are in plone.registry.

    Objects will not be transformed again with changed settings.
    You need to clear the cache by e.g.
    1.) restarting your zope or
    2.) empty the zodb-cache via ZMI -> Control_Panel
        -> Database Management -> main || other_used_database
        -> Flush Cache.
    """

    __name__ = "safe_html"
    inputs = ("text/html",)
    output = "text/x-html-safe"

    def __init__(self, name=None, **kwargs):
        self.config = {
            "inputs": self.inputs,
            "output": self.output,
        }

        self.config_metadata = {
            "inputs": ("list", "Inputs", "Input(s) MIME type. Change with care."),
        }

        self.config.update(kwargs)

        if name:
            self.__name__ = name

    def name(self):
        return self.__name__

    def __getattr__(self, attr):
        if attr == "inputs":
            return self.config["inputs"]
        if attr == "output":
            return self.config["output"]
        raise AttributeError(attr)

    def convert(self, orig, data, **kwargs):
        registry = getUtility(IRegistry)
        self.settings = registry.forInterface(IFilterSchema, prefix="plone")

        # if we have a config that we don't want to delete
        # we need a disable option
        if self.settings.disable_filtering:
            data.setData(orig)
        else:
            safe_html = self.scrub_html(orig)
            data.setData(safe_html)
        return data

    def cleaner_options(self):
        # Create dictionary of options that we pass to the html cleaner.
        registry = getUtility(IRegistry)
        self.settings = registry.forInterface(IFilterSchema, prefix="plone")

        valid_tags = self.settings.valid_tags
        nasty_tags = [t for t in self.settings.nasty_tags if t not in valid_tags]
        safe_attrs = [i for i in html.defs.safe_attrs]
        safe_attrs.extend(self.settings.custom_attributes)
        remove_script = "script" in nasty_tags and 1 or 0
        options = dict(
            kill_tags=nasty_tags,
            remove_tags=[],
            allow_tags=valid_tags,
            page_structure=False,
            safe_attrs_only=True,
            safe_attrs=safe_attrs,
            embedded=False,
            remove_unknown_tags=False,
            meta=False,
            javascript=remove_script,
            scripts=remove_script,
            forms=False,
            style=False,
        )
        return options

    def scrub_html(self, orig):
        orig_text = safe_text(orig)
        # short cut if no html or script is detected
        if not orig or not (
            hasScript(orig_text)
            or "<" in orig_text
            or any(entity in orig_text for entity in html5entities.values())
        ):
            return orig_text
        # append html tag to create a dummy parent for the tree
        html_parser = html.HTMLParser(encoding="utf-8")
        orig = safe_bytes(orig)
        tag = b"<html"
        if tag in orig.lower():
            # full html
            tree = html.fromstring(orig, parser=html_parser)
            strip_outer = bodyfinder
        else:
            # partial html (i.e. coming from WYSIWYG editor)
            tree = html.fragment_fromstring(
                orig, create_parent=True, parser=html_parser
            )

            def strip_outer(s):
                return s[5:-6]

        for elem in tree.iter(etree.Element):
            if elem is not None:
                for attrib, value in elem.attrib.items():
                    if hasScript(value):
                        del elem.attrib[attrib]

        options = self.cleaner_options()
        cleaner = Cleaner(**options)
        try:
            cleaner(tree)
        except AssertionError:
            # some VERY invalid HTML
            return ""
        # remove all except body or outer div
        result = etree.tounicode(tree, method="html").strip()
        return strip_outer(result)


def register():
    return SafeHTML()
