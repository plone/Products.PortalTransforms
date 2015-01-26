from cgi import escape
from Products.CMFDefault.utils import bodyfinder
from Products.CMFDefault.utils import IllegalHTML
from Products.CMFDefault.utils import NASTY_TAGS
from Products.CMFDefault.utils import VALID_TAGS
from Products.PortalTransforms.interfaces import ITransform
from Products.PortalTransforms.transforms.html5 import html5entities
from Products.PortalTransforms.utils import log
from Products.PortalTransforms.utils import safeToInt
from plone.registry.interfaces import IRegistry
from sgmllib import SGMLParser, SGMLParseError
from zope.component import getUtility
from zope.interface import implements

import logging
import re


# tag mapping: tag -> short or long tag
VALID_TAGS = VALID_TAGS.copy()
NASTY_TAGS = NASTY_TAGS.copy()

# add some tags to allowed types. These should be backported to CMFDefault.
VALID_TAGS['ins'] = 1
VALID_TAGS['del'] = 1
VALID_TAGS['q'] = 1
VALID_TAGS['map'] = 1
VALID_TAGS['area'] = 0
VALID_TAGS['abbr'] = 1
VALID_TAGS['acronym'] = 1
VALID_TAGS['var'] = 1
VALID_TAGS['dfn'] = 1
VALID_TAGS['samp'] = 1
VALID_TAGS['address'] = 1
VALID_TAGS['bdo'] = 1
VALID_TAGS['thead'] = 1
VALID_TAGS['tfoot'] = 1
VALID_TAGS['col'] = 1
VALID_TAGS['colgroup'] = 1

# HTML5 tags that should be allowed:
VALID_TAGS['article'] = 1
VALID_TAGS['aside'] = 1
VALID_TAGS['audio'] = 1
VALID_TAGS['canvas'] = 1
VALID_TAGS['command'] = 1
VALID_TAGS['datalist'] = 1
VALID_TAGS['details'] = 1
VALID_TAGS['dialog'] = 1
VALID_TAGS['figure'] = 1
VALID_TAGS['footer'] = 1
VALID_TAGS['header'] = 1
VALID_TAGS['hgroup'] = 1
VALID_TAGS['keygen'] = 1
VALID_TAGS['mark'] = 1
VALID_TAGS['meter'] = 1
VALID_TAGS['nav'] = 1
VALID_TAGS['output'] = 1
VALID_TAGS['progress'] = 1
VALID_TAGS['rp'] = 1
VALID_TAGS['rt'] = 1
VALID_TAGS['ruby'] = 1
VALID_TAGS['section'] = 1
VALID_TAGS['source'] = 1
VALID_TAGS['time'] = 1
VALID_TAGS['video'] = 1

# add some tags to nasty.
NASTY_TAGS['style'] = 1  # this helps improve Word HTML cleanup.
NASTY_TAGS['meta'] = 1  # allowed by parsers, but can cause unexpected behavior

DEFAULT_CONFIG = {
    'valid_tags': VALID_TAGS,
    'nasty_tags': NASTY_TAGS,
    'stripped_attributes': [
        'lang', 'valign', 'halign', 'border', 'frame', 'rules',
        'cellspacing', 'cellpadding', 'bgcolor'],
    'stripped_combinations': {'table th td': 'width height'},
    'style_whitelist': ['text-align', 'list-style-type', 'float',
                        'padding-left', ],
    'class_blacklist': [],
    'remove_javascript': 1,
    'disable_transform': False,
}

msg_pat = """
<div class="system-message">
<p class="system-message-title">System message: %s</p>
%s</d>
"""

CSS_COMMENT = re.compile(r'/\*.*\*/')


def hasScript(s):  # NOQA
    """Dig out evil Java/VB script inside an HTML attribute.

    >>> hasScript(
    ... 'data:text/html;base64,PHNjcmlwdD5hbGVydCgidGVzdCIpOzwvc2NyaXB0Pg==')
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
    s = s.replace('\x00', '')
    s = CSS_COMMENT.sub('', s)
    s = ''.join(s.split()).lower()
    for t in ('script:', 'expression:', 'expression(', 'data:'):
        if t in s:
            return True
    return False


CHR_RE = re.compile(r'\\(\d+)')


def unescape_chr(matchobj):
    try:
        return chr(int(matchobj.group(1), 16))
    except ValueError:
        return matchobj.group(0)


def decode_charref(s):
    s = s.group(1)
    try:
        if s[0] in ['x', 'X']:
            c = int(s[1:], 16)
        else:
            c = int(s)
        c = unichr(c)
        if isinstance(s, str):
            c = c.encode('utf8')
        return c
    except ValueError:
        return '&#' + s + ';'


def decode_entityref(s):
    s = s.group(1)
    try:
        c = html5entities[s + ';']
    except KeyError:
        try:
            c = html5entities[s]
        except KeyError:
            # strip unrecognized entities
            c = u''
    if isinstance(s, str):
        c = c.encode('utf8')
    return c


CHARREF_RE = re.compile(r"&(?:amp;)?#([xX]?[0-9a-fA-F]+);?")
ENTITYREF_RE = re.compile(r"&(\w{1,32});?")


def decode_htmlentities(s):
    # Decode HTML5 entities (numeric or named).
    s = CHR_RE.sub(unescape_chr, s)
    if '&' not in s:
        return s
    s = CHARREF_RE.sub(decode_charref, s)
    return ENTITYREF_RE.sub(decode_entityref, s)


class StrippingParser(SGMLParser):
    """Pass only allowed tags;  raise exception for known-bad.

    Copied from Products.CMFDefault.utils
    Copyright (c) 2001 Zope Corporation and Contributors. All Rights Reserved.
    """

    # This replaces SGMLParser.entitydefs
    entitydefs = html5entities

    def __init__(self, valid, nasty, remove_javascript, raise_error):
        SGMLParser.__init__(self)
        self.result = []
        self.valid = valid
        self.nasty = nasty
        self.remove_javascript = remove_javascript
        self.raise_error = raise_error
        self.suppress = False

    def handle_data(self, data):
        if self.suppress:
            return
        if data:
            self.result.append(escape(data))

    def handle_charref(self, name):
        if self.suppress:
            return
        self.result.append(self.convert_charref(name))

    def handle_comment(self, comment):
        pass

    def handle_decl(self, data):
        pass

    def handle_entityref(self, name):
        if self.suppress:
            return
        self.result.append(self.convert_entityref(name))

    def convert_entityref(self, name):
        if name + ';' in self.entitydefs:
            x = ';'
        elif name in self.entitydefs:
            x = ''
        else:
            x = ';'
        return '&%s%s' % (name, x)

    def convert_charref(self, name):
        return '&#%s;' % name

    def unknown_starttag(self, tag, attrs):
        """ Delete all tags except for legal ones.
        """
        if self.suppress:
            return

        if tag in self.valid:
            self.result.append('<' + tag)

            remove_script = getattr(self, 'remove_javascript', True)

            for k, v in attrs:
                if remove_script and k.strip().lower().startswith('on'):
                    if not self.raise_error:
                        continue
                    else:
                        raise IllegalHTML('Script event "%s" not allowed.' % k)
                elif remove_script and hasScript(v):
                    if not self.raise_error:
                        continue
                    else:
                        raise IllegalHTML('Script URI "%s" not allowed.' % v)
                else:
                    self.result.append(' %s="%s"' % (k, v))

            # UNUSED endTag = '</%s>' % tag
            if safeToInt(self.valid.get(tag)):
                self.result.append('>')
            else:
                self.result.append(' />')
        elif tag in self.nasty:
            self.suppress = True
            if self.raise_error:
                raise IllegalHTML('Dynamic tag "%s" not allowed.' % tag)
        else:
            # omit tag
            pass

    def unknown_endtag(self, tag):
        if tag in self.nasty and tag not in self.valid:
            self.suppress = False
        if self.suppress:
            return
        if safeToInt(self.valid.get(tag)):
            self.result.append('</%s>' % tag)

    def parse_declaration(self, i):
        """Fix handling of CDATA sections. Code borrowed from BeautifulSoup.
        """
        j = None
        if self.rawdata[i:i + 9] == '<![CDATA[':
            k = self.rawdata.find(']]>', i)
            if k == -1:
                k = len(self.rawdata)
            j = k + 3
        else:
            try:
                j = SGMLParser.parse_declaration(self, i)
            except SGMLParseError:
                j = len(self.rawdata)
        return j

    def getResult(self):  # NOQA
        return ''.join(self.result)


def scrubHTML(html, valid=VALID_TAGS, nasty=NASTY_TAGS,  # NOQA
              remove_javascript=True, raise_error=True):

    """ Strip illegal HTML tags from string text.
    """
    parser = StrippingParser(valid=valid, nasty=nasty,
                             remove_javascript=remove_javascript,
                             raise_error=raise_error)
    parser.feed(html)
    parser.close()
    return parser.getResult()


class SafeHTML:
    """Simple transform which uses CMFDefault functions to
    clean potentially bad tags.

    Tags must explicit be allowed in valid_tags to pass. Only
    the tags themself are removed, not their contents. If tags
    are removed and in nasty_tags, they are removed with
    all of their contents.

    Objects will not be transformed again with changed settings.
    You need to clear the cache by e.g.
    1.) restarting your zope or
    2.) empty the zodb-cache via ZMI -> Control_Panel
        -> Database Management -> main || other_used_database
        -> Flush Cache.
    """

    implements(ITransform)

    __name__ = "safe_html"
    inputs = ('text/html', )
    output = "text/x-html-safe"

    def __init__(self, name=None, **kwargs):
        self.config = {
            'inputs': self.inputs,
            'output': self.output,
            'valid_tags': VALID_TAGS,
            'nasty_tags': NASTY_TAGS,
            'stripped_attributes': [
                'lang', 'valign', 'halign', 'border', 'frame', 'rules',
                'cellspacing', 'cellpadding', 'bgcolor'],
            'stripped_combinations': {'table th td': 'width height'},
            'style_whitelist': ['text-align', 'list-style-type', 'float',
                                'padding-left', ],
            'class_blacklist': [],
            'remove_javascript': 1,
            'disable_transform': 0,
        }

        self.config_metadata = {
            'inputs': ('list',
                       'Inputs',
                       'Input(s) MIME type. Change with care.'),
            'valid_tags': ('dict',
                           'valid_tags',
                           'List of valid html-tags, value is 1 if they ' +
                           'have a closing part (e.g. <p>...</p>) and 0 for ' +
                           'empty tags (like <br />). Be carefull!',
                           ('tag', 'value')),
            'nasty_tags': ('dict',
                           'nasty_tags',
                           'Dynamic Tags that are striped with ' +
                           'everything they contain (like applet, object). ' +
                           'They are only deleted if they are not marked ' +
                           'as valid_tags.',
                           ('tag', 'value')),
            'stripped_attributes': ('list',
                                    'stripped_attributes',
                                    'These attributes are stripped from ' +
                                    'any tag.'),
            'stripped_combinations': ('dict',
                                      'stripped_combinations',
                                      'These attributes are stripped from ' +
                                      'any tag.',
                                      ('tag', 'value')),
            'style_whitelist': ('list',
                                'style_whitelist',
                                'These CSS styles are allowed in style ' +
                                'attributes.'),
            'class_blacklist': ('list',
                                'class_blacklist',
                                'These class names are not allowed in ' +
                                'class attributes.'),
            'remove_javascript': ("int",
                                  'remove_javascript',
                                  '1 to remove javascript attributes that ' +
                                  'begin with on (e.g. onClick) and ' +
                                  'attributes where the value starts with ' +
                                  '"javascript:" (e.g. ' +
                                  '<a href="javascript:function()". This ' +
                                  'does not effect <script> tags. 0 to ' +
                                  'leave the attributes.'),
            'disable_transform': ("int",
                                  'disable_transform',
                                  'If 1, nothing is done.'),
        }

        self.config.update(kwargs)

        if name:
            self.__name__ = name

    def name(self):
        return self.__name__

    def __getattr__(self, attr):
        if attr == 'inputs':
            return self.config['inputs']
        if attr == 'output':
            return self.config['output']
        raise AttributeError(attr)

    def _get_config_from_registry(self):
        config = DEFAULT_CONFIG
        config.update({
            'inputs': self.inputs,
            'output': self.output,
        })

        registry = getUtility(IRegistry)

        disable_filtering = registry.records.get('plone.disable_filtering')
        if disable_filtering:
            config['disable_transform'] = disable_filtering.value

        nasty_tags_record = registry.records.get('plone.nasty_tags')
        if nasty_tags_record:
            # self.config should contain a dict with tags as values
            nasty_tags = nasty_tags_record.value
            config['nasty_tags'] = dict.fromkeys(nasty_tags, 1)
            # remove nasty tags from valid_tags
            for tag in nasty_tags:
                if tag in config['valid_tags']:
                    del config['valid_tags'][tag]

        return config

    def convert(self, orig, data, **kwargs):
        self.config = self._get_config_from_registry()

        # note if we need an upgrade.
        if 'disable_transform' not in self.config:
            log(logging.ERROR, 'PortalTransforms safe_html transform needs '
                'to be updated. Please re-install the PortalTransforms '
                'product to fix.')

        # if we have a config that we don't want to delete
        # we need a disable option
        if self.config.get('disable_transform'):
            data.setData(orig)
            return data

        for repeat in range(2):
            try:
                safe = scrubHTML(
                    bodyfinder(orig),
                    valid=self.config.get('valid_tags', {}),
                    nasty=self.config.get('nasty_tags', {}),
                    remove_javascript=self.config.get(
                        'remove_javascript', True),
                    raise_error=False)
            except IllegalHTML, inst:
                data.setData(msg_pat % ("Error", str(inst)))
                break
            else:
                data.setData(safe)
                orig = safe
        return data


def register():
    return SafeHTML()
