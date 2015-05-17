"""some common utilities
"""
import logging


class TransformException(Exception):
    pass

FB_REGISTRY = None

# logging function
logger = logging.getLogger('PortalTransforms')


def log(message, severity=logging.DEBUG):
    logger.log(severity, message)

# directory where template for the ZMI are located
import os.path
_www = os.path.join(os.path.dirname(__file__), 'www')


def safeToInt(value):
    """Convert value to integer or just return 0 if we can't"""
    try:
        return int(value)
    except (TypeError, ValueError):
        return 0


# TODO(gforcada): add AccessControl.SecurityInfo.ModuleSecurityInfo
# security.declarePublic('bodyfinder')
def bodyfinder(text):
    """ Return body or unchanged text if no body tags found.

    Always use html_headcheck() first.
    """
    lowertext = text.lower()
    bodystart = lowertext.find('<body')
    if bodystart == -1:
        return text
    bodystart = lowertext.find('>', bodystart) + 1
    if bodystart == 0:
        return text
    bodyend = lowertext.rfind('</body>', bodystart)
    if bodyend == -1:
        return text
    return text[bodystart:bodyend]


# TODO(gforcada): add AccessControl.SecurityInfo.ModuleSecurityInfo
# security.declarePublic('IllegalHTML')
class IllegalHTML(ValueError):
    """ Illegal HTML error.
    """


# These are the HTML tags that we will leave intact
VALID_TAGS = {
    'a': 1,
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
   # 'link':     1, type="script" hoses us
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
    'ul': 1,
    # add some tags to allowed types.
    'ins': 1,
    'del': 1,
    'q': 1,
    'map': 1,
    'area': 0,
    'abbr': 1,
    'acronym': 1,
    'var': 1,
    'dfn': 1,
    'samp': 1,
    'address': 1,
    'bdo': 1,
    'thead': 1,
    'tfoot': 1,
    'col': 1,
    'colgroup': 1,
# HTML5 tags that should be allowed:
    'article': 1,
    'aside': 1,
    'audio': 1,
    'canvas': 1,
    'command': 1,
    'datalist': 1,
    'details': 1,
    'dialog': 1,
    'figure': 1,
    'footer': 1,
    'header': 1,
    'hgroup': 1,
    'keygen': 1,
    'mark': 1,
    'meter': 1,
    'nav': 1,
    'output': 1,
    'progress': 1,
    'rp': 1,
    'rt': 1,
    'ruby': 1,
    'section': 1,
    'source': 1,
    'time': 1,
    'video': 1,
}

NASTY_TAGS = {
    'script': 1,
    'object': 1,
    'embed': 1,
    'applet': 1,
    'style': 1,  # this helps improve Word HTML cleanup.
    'meta': 1,  # allowed by parsers, but can cause unexpected behavior
}
