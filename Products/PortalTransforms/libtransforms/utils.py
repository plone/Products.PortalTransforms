import os
import sys
from sgmllib import SGMLParser, SGMLParseError
from htmlentitydefs import entitydefs

try:
    # Need to be imported before win32api to avoid dll loading
    # problems.
    import pywintypes
    import pythoncom

    import win32api
    WIN32 = True
except ImportError:
    WIN32 = False

from Products.PortalTransforms.utils import log


class MissingBinary(Exception):
    pass

envPath = os.environ['PATH']
bin_search_path = [path for path in envPath.split(os.pathsep)
                   if os.path.isdir(path)]

cygwin = 'c:/cygwin'

# cygwin support
if sys.platform == 'win32' and os.path.isdir(cygwin):
    for p in ['/bin', '/usr/bin', '/usr/local/bin']:
        p = os.path.join(cygwin, p)
        if os.path.isdir(p):
            bin_search_path.append(p)

if sys.platform == 'win32':
    extensions = ('.exe', '.com', '.bat', )
else:
    extensions = ()


def bin_search(binary):
    """search the bin_search_path for a given binary returning its fullname or
       raises MissingBinary"""
    mode = os.R_OK | os.X_OK
    for path in bin_search_path:
        for ext in ('', ) + extensions:
            pathbin = os.path.join(path, binary) + ext
            if os.access(pathbin, mode) == 1:
                return pathbin

    raise MissingBinary('Unable to find binary "%s" in %s' %
                        (binary, os.pathsep.join(bin_search_path)))


def getShortPathName(binary):
    if WIN32:
        try:
            binary = win32api.GetShortPathName(binary)
        except win32api.error:
            log("Failed to GetShortPathName for '%s'" % binary)
    return binary


def sansext(path):
    return os.path.splitext(os.path.basename(path))[0]


##########################################################################
# The code below is taken from CMFDefault.utils to remove
# dependencies for Python-only installations
##########################################################################

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


#
#   HTML cleaning code
#

# These are the HTML tags that we will leave intact.  Note that a
# value of 0 means it is an empty tag, like '<br />'.  Also note that
# there currently is a separate list in the safe_html transform, which
# itself is a copy from CMFDefault, with some changes done on the fly.
VALID_TAGS = { 'a'          : 1
             , 'article'    : 1
             , 'aside'      : 1
             , 'audio'      : 1
             , 'b'          : 1
             , 'base'       : 0
             , 'blockquote' : 1
             , 'body'       : 1
             , 'br'         : 0
             , 'canvas'     : 1
             , 'caption'    : 1
             , 'cite'       : 1
             , 'code'       : 1
             , 'command'    : 1
             , 'datalist'   : 1
             , 'dd'         : 1
             , 'details'    : 1
             , 'div'        : 1
             , 'dl'         : 1
             , 'dt'         : 1
             , 'em'         : 1
             , 'figcaption' : 1
             , 'figure'     : 1
             , 'footer'     : 1
             , 'h1'         : 1
             , 'h2'         : 1
             , 'h3'         : 1
             , 'h4'         : 1
             , 'h5'         : 1
             , 'h6'         : 1
             , 'head'       : 1
             , 'header'     : 1
             , 'hgroup'     : 1
             , 'hr'         : 0
             , 'html'       : 1
             , 'i'          : 1
             , 'img'        : 0
             , 'kbd'        : 1
             , 'keygen'     : 1
             , 'li'         : 1
             , 'mark'       : 1
             , 'meta'       : 0
             , 'ol'         : 1
             , 'p'          : 1
             , 'pre'        : 1
             , 'rp'         : 1
             , 'rt'         : 1
             , 'ruby'       : 1
             , 'section'    : 1
             , 'source'     : 1
             , 'span'       : 1
             , 'strike'     : 1
             , 'strong'     : 1
             , 'summary'    : 1
             , 'table'      : 1
             , 'tbody'      : 1
             , 'td'         : 1
             , 'th'         : 1
             , 'thead'      : 1
             , 'time'       : 1
             , 'title'      : 1
             , 'tr'         : 1
             , 'tt'         : 1
             , 'u'          : 1
             , 'ul'         : 1
             , 'video'      : 1
             }

# These tags and their complete contents should be removed.  Note that
# parsers may choose to raise an Exception when finding such a nasty
# tag.
NASTY_TAGS = { 'script'     : 1
             , 'object'     : 1
             , 'embed'      : 1
             , 'applet'     : 1
             }


class IllegalHTML(ValueError):
    pass


class StrippingParser(SGMLParser):
    """ Pass only allowed tags;  raise exception for known-bad.  """

    # This replaces SGMLPaser.entitydefs
    entitydefs = entitydefs

    def __init__(self):

        SGMLParser.__init__(self)
        self.result = ""

    def handle_data(self, data):

        if data:
            self.result = self.result + data

    def handle_charref(self, name):

        self.result = "%s&#%s;" % (self.result, name)

    def handle_entityref(self, name):

        if name in self.entitydefs:
            x = ';'
        else:
            # this breaks unstandard entities that end with ';'
            x = ''

        self.result = "%s&%s%s" % (self.result, name, x)

    def unknown_starttag(self, tag, attrs):

        """ Delete all tags except for legal ones.
        """
        if tag in VALID_TAGS:
            self.handle_valid_tag(tag, attrs)
        elif NASTY_TAGS.get(tag):
            self.handle_invalid_tag(tag, attrs)
        else:
            pass  # omit tag

    def handle_javascript_attr(self, k, v):
        if k.lower().startswith('on'):
            raise IllegalHTML('Javascript event "%s" not allowed.' % k)

        if v.lower().startswith('javascript:'):
            raise IllegalHTML('Javascript URI "%s" not allowed.' % v)

        self.result = '%s %s="%s"' % (self.result, k, v)

    def handle_valid_tag(self, tag, attrs):
        self.result = self.result + '<' + tag

        for k, v in attrs:
            self.result = '%s %s' % (self.result,
                    self.handle_javascript_attr(k, v))

        # endTag = '</%s>' % tag
        if VALID_TAGS.get(tag):
            self.result = self.result + '>'
        else:
            self.result = self.result + ' />'

    def handle_invalid_tag(self, tag, attrs):
        raise IllegalHTML('Dynamic tag "%s" not allowed.' % tag)

    def unknown_endtag(self, tag):

        if VALID_TAGS.get(tag):

            self.result = "%s</%s>" % (self.result, tag)
            # remTag = '</%s>' % tag

    def parse_declaration(self, i):
        """Fix handling of CDATA sections. Code borrowed from BeautifulSoup.
        """
        j = None
        if self.rawdata[i:i + 9] == '<![CDATA[':
            k = self.rawdata.find(']]>', i)
            if k == -1:
                k = len(self.rawdata)
            data = self.rawdata[i + 9:k]
            j = k + 3
            self.result.append("<![CDATA[%s]]>" % data)
        else:
            try:
                j = SGMLParser.parse_declaration(self, i)
            except SGMLParseError:
                toHandle = self.rawdata[i:]
                self.result.append(toHandle)
                j = i + len(toHandle)
        return j


class NoRaiseStrippingParser(StrippingParser):

    def handle_javascript_attr(self, k, v):
        if k.lower().startswith('on'):
            return ''

        if v.lower().startswith('javascript:'):
            return ''

        return '%s="%s"' % (k, v)


def scrubHTML(html):
    """ Strip illegal HTML tags from string text.  """
    parser = StrippingParser()
    parser.feed(html)
    parser.close()
    return parser.result


def scrubHTMLNoRaise(html):
    """ Strip illegal HTML tags from string text.  """
    parser = NoRaiseStrippingParser()
    parser.feed(html)
    parser.close()
    return parser.result
