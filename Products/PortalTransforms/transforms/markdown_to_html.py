# -*- coding: utf-8 -*-
"""
Uses the http://www.freewisdom.org/projects/python-markdown/ module

Author: Tom Lazar <tom@tomster.org> at the archipelago sprint 2006
"""

from Products.PortalTransforms.interfaces import ITransform
from Products.PortalTransforms.utils import log
from zope.interface import implementer


import six


try:
    import markdown as markdown_transformer
except ImportError:
    HAS_MARKDOWN = False
    log('markdown_to_html: Could not import python-markdown.')
else:
    HAS_MARKDOWN = True


@implementer(ITransform)
class markdown(object):

    __name__ = "markdown_to_html"
    inputs = ("text/x-web-markdown",)
    output = "text/html"

    def __init__(self, name=None, enabled_extensions=('markdown.extensions.fenced_code', 'markdown.extensions.nl2br', ), **kwargs):
        self.config = {
            'enabled_extensions': enabled_extensions,
        }

        self.config_metadata = {
            'enabled_extensions': (
                'list',
                'enabled_extensions',
                'Look for available extensions at ' +
                'https://pythonhosted.org/Markdown/extensions/index.html ' +
                'or write your own.'
            ),
        }

        if name:
            self.__name__ = name

    def name(self):
        return self.__name__

    def __getattr__(self, attr):
        if attr in self.config:
            return self.config[attr]
        raise AttributeError(attr)

    def convert(self, orig, data, **kwargs):
        if HAS_MARKDOWN:
            # markdown expects unicode input:
            orig = six.text_type(orig.decode('utf-8'))
            # PortalTransforms, however expects a string as result,
            # so we encode the unicode result back to UTF8:
            html = markdown_transformer \
                .markdown(orig, extensions=self.config.get('enabled_extensions', [])) \
                .encode('utf-8')
        else:
            html = orig
        data.setData(html)
        return data


def register():
    return markdown()
