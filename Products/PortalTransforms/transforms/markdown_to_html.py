"""
Uses the http://www.freewisdom.org/projects/python-markdown/ module to do its handy work

author: Tom Lazar <tom@tomster.org> at the archipelago sprint 2006

"""

from Products.PortalTransforms.interfaces import itransform

try:
    import markdown as markdown_transformer
except ImportError:
    HAS_MARKDOWN = False
else:
    HAS_MARKDOWN = True
    

class markdown:
    __implements__ = itransform

    __name__ = "markdown_to_html"
    inputs  = ("text/x-web-markdown",)
    output = "text/html"

    def name(self):
        return self.__name__

    def convert(self, orig, data, **kwargs):
        if HAS_MARKDOWN:
            # markdown expects unicode input:
            orig = unicode(orig.decode('utf-8'))
            # PortalTransforms, however expects a string as result,
            # so we encode the unicode result back to UTF8:
            html = markdown_transformer.markdown(orig).encode('utf-8')
        else:
            html = orig
        data.setData(html)
        return data

def register():
    return markdown()
