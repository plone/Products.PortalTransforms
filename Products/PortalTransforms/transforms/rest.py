from Products.PortalTransforms.interfaces import ITransform
from zope.interface import implements
from reStructuredText import HTML
import sys

class rest:
    r"""Converts from reST to HTML.

      >>> transform = rest()
      >>> class D:
      ...     def setData(self, data):
      ...         self.value = data

      >>> data = transform.convert('*hello world*', D())
      >>> print data.value
      <p><em>hello world</em></p>
      <BLANKLINE>

    We want the 'raw' and 'include' directives to be disabled by
    default:

      >>> try:
      ...     out = transform.convert('.. raw:: html\n  :file: <isonum.txt>', D())
      ... except NotImplementedError:
      ...     print 'Good'
      ... else:
      ...     if "&quot;raw&quot; directive disabled." in out.value:
      ...         print 'Good'
      ...     else:
      ...         print 'Failure'
      Good

      >>> try:
      ...     out = transform.convert('.. include:: <isonum.txt>', D())
      ... except NotImplementedError:
      ...     print 'Good'
      ... else:
      ...     if "&quot;include&quot; directive disabled." in out.value:
      ...         print 'Good'
      ...     else:
      ...         print 'Failure'
      Good
    """
    implements(ITransform)

    __name__ = "rest_to_html"
    inputs  = ("text/x-rst", "text/restructured",)
    output = "text/html"

    def __init__(self, name=None, **kwargs):
        if name:
            self.__name__ = name

        self.config = {
            'inputs': self.inputs,
            'output': self.output,
            'report_level': 2,
            'initial_header_level': 2,
            }

        self.config_metadata = {
            'inputs' :
            ('list', 'Inputs', 'Input(s) MIME type. Change with care.'),
            'initial_header_level' :
            ('int', 'Initial Header Level',
             'Level of first header tag. Setting it to "2" will make '
             'the first header be "<h2>".'),
            'report_level' :
            ('int', 'Report Level',
             'Level of error reporting. Set to "1" will display all '
             'messages. Setting it to "5" will display no messages.'),
            }

        self.config.update(kwargs)


    def name(self):
        return self.__name__

    def convert(self, orig, data, **kwargs):
        # do the format
        encoding        = kwargs.get('encoding', 'utf-8')
        input_encoding  = kwargs.get('input_encoding', encoding)
        output_encoding = kwargs.get('output_encoding', encoding)
        language        = kwargs.get('language', 'en')
        warnings        = kwargs.get('warnings', None)

        initial_header_level = int(self.config.get('initial_header_level', 2))
        report_level = int(self.config.get('report_level', 2))

        settings = {'documentclass': '',
                    'traceback': 1,
                    }

        html = HTML(orig,
                    input_encoding=input_encoding,
                    output_encoding=output_encoding,
                    language_code=language,
                    initial_header_level=initial_header_level,
                    report_level=report_level,
                    warnings=warnings,
                    settings=settings)

        html = html.replace(' class="document"', '', 1)
        data.setData(html)
        return data

def register():
    return rest()
