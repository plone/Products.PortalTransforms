from DocumentTemplate.html_quote import html_quote
from Products.PortalTransforms.interfaces import ITransform
from plone.base.utils import safe_text
from zope.interface import implementer


@implementer(ITransform)
class TextToHTML:
    """simple transform which wrap raw text in a verbatim environment"""

    __name__ = "text_to_html"
    output = "text/html"

    def __init__(self, name=None, inputs=('text/plain',)):
        self.config = {'inputs': inputs, }
        self.config_metadata = {
            'inputs': (
                'list',
                'Inputs',
                'Input(s) MIME type. Change with care.'),
        }
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
        orig = safe_text(orig)
        # Replaces all line breaks with a br tag, and wraps it in a p tag.
        data.setData('<p>%s</p>' %
                     html_quote(orig.strip()).replace('\n', '<br />'))
        return data


def register():
    return TextToHTML()
