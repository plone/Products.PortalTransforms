# -*- coding: utf-8 -*-
import logging
from Products.PortalTransforms.interfaces import ITransform
from zope.interface import implements
from Products.PortalTransforms.utils import log
from lxml import etree
from cStringIO import StringIO
from lxml.html.clean import Cleaner
from lxml.html import fragments_fromstring
from lxml.etree import tostring

# add some tags to nasty.
NASTY_TAGS = frozenset(['style', 'script', 'object', 'applet', 'meta', 'embed'])  # noqa

# tag mapping: tag -> short or long tag
# These are the HTML tags that we will leave intact
VALID_TAGS = {'a': 1,
 'b': 1,
 'base': 0,
 'big': 1,
 'blockquote': 1,
 'body': 1,
 'br': 0,
 'caption': 1,
 'cite': 1,
 'code': 1,
 'dd': 1,
 'div': 1,
 'dl': 1,
 'dt': 1,
 'em': 1,
 'h1': 1,
 'h2': 1,
 'h3': 1,
 'h4': 1,
 'h5': 1,
 'h6': 1,
 'head': 1,
 'hr': 0,
 'html': 1,
 'i': 1,
 'img': 0,
 'kbd': 1,
 'li': 1,
 'meta': 0,
 'ol': 1,
 'p': 1,
 'pre': 1,
 'small': 1,
 'span': 1,
 'strong': 1,
 'sub': 1,
 'sup': 1,
 'table': 1,
 'tbody': 1,
 'td': 1,
 'th': 1,
 'title': 1,
 'tr': 1,
 'tt': 1,
 'u': 1,
 'ul': 1
}

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

_strings = (bytes, str)


class HTMLParser(Cleaner):
    """
    Inherited cleaner class of lxml.html.

    Modified __call__ method of the lxml.html to allow the
    frames tags in the input.
    """

    def __call__(self, doc):
        kill_tags = set(self.kill_tags or ())
        remove_tags = set(self.remove_tags or ())
        if self.frames:
            pass
        if self.embedded:
            for el in list(doc.iter('param')):
                # found_parent = False
                parent = el.getparent()
                while parent is not None and parent.tag not in ('applet', 'object'):
                    parent = parent.getparent()
                if parent is None:
                    el.drop_tree()
            kill_tags.update(('applet',))
            # The alternate contents that are in an iframe are a good fallback:
            remove_tags.update(('embed', 'layer', 'object', 'param'))





class SafeHTML:
    """Simple transform which uses lxml to
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

    def convert(self, orig, data, **kwargs):
        # note if we need an upgrade.
        if 'disable_transform' not in self.config:
            log(logging.ERROR, 'PortalTransforms safe_html transform needs '
                'to be updated. Please re-install the PortalTransforms '
                'product to fix.')

        # if we have a config that we don't want to delete
        # we need a disable option
        if self.config.get('disable_transform'):
            data.setData(orig)
        elif orig == "" or orig == "<html></html>" or orig == "<html />" or orig == "<html/>":
            data.setData('')
        elif '<' not in orig:
            data.setData(orig)  # shortcut for input which is not HTML
        else:
            # append html tag to create a dummy parent for the tree
            html = "<html>%s</html>" % orig
            parser = etree.HTMLParser()
            tree = etree.parse(StringIO(html), parser)
            result = etree.tostring(tree.getroot(), method="html")
            cleaner = Cleaner(kill_tags=self.config['nasty_tags'],
                              page_structure=False,
                              safe_attrs_only=False,
                              embedded=False,
                              style=True)
            safe_html = fragments_fromstring(cleaner.clean_html(result))
            def convert_to_string(fragment):
                return isinstance(fragment, basestring) and fragment.strip() or tostring(fragment).strip()

            safe_html2 = ''.join([convert_to_string(fragment) for fragment in safe_html])

            data.setData(safe_html2)

        return data


def register():
    return SafeHTML()
