# -*- coding: utf-8 -*-
"""
Uses the http://www.freewisdom.org/projects/python-markdown/ module
Author: Tom Lazar <tom@tomster.org> at the archipelago sprint 2006
"""

from plone.base.interfaces import IMarkupSchema
from plone.base.utils import safe_text
from plone.registry.interfaces import IRegistry
from Products.PortalTransforms.interfaces import ITransform
from Products.PortalTransforms.utils import log
from zope.component import getUtility
from zope.interface import implementer


try:
    import markdown as markdown_transformer
except ImportError:
    HAS_MARKDOWN = False
    log('markdown_to_html: Could not import python-markdown.')
else:
    HAS_MARKDOWN = True

DEFAULT_EXTENSIONS = [
    'markdown.extensions.fenced_code',
    'markdown.extensions.nl2br',
]


@implementer(ITransform)
class markdown(object):

    __name__ = "markdown_to_html"
    inputs = ("text/x-web-markdown",)
    output = "text/html"

    def name(self):
        return self.__name__

    def extensions(self):
        registry = getUtility(IRegistry)
        settings = registry.forInterface(IMarkupSchema, prefix="plone")
        return getattr(settings, 'markdown_extensions', DEFAULT_EXTENSIONS)

    def convert(self, orig, data, **kwargs):
        if HAS_MARKDOWN:
            # markdown expects unicode input:
            html = markdown_transformer.markdown(
                safe_text(orig),
                extensions=self.extensions()
            )
        else:
            html = orig

        data.setData(safe_text(html))
        return data


def register():
    return markdown()
