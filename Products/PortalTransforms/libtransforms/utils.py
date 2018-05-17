# -*- coding: utf-8 -*-
from Products.CMFPlone.utils import safe_unicode
from Products.PortalTransforms.utils import log

import os
import sys
import warnings


try:
    # Need to be imported before win32api to avoid dll loading
    # problems.
    import pywintypes
    import pythoncom

    import win32api
    WIN32 = True
except ImportError:
    WIN32 = False


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
    Accepts bytes or text. Returns text.
    """
    text = safe_unicode(text)
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


def scrubHTMLNoRaise(html):
    """ Strip illegal HTML tags from string text.  """
    warnings.warn(("Call to deprecated function `scrubHTMLNoRaise` or `scrubHTML`."
                   "Use SafeHTML().scrub_html(html) instead."),
                  category=DeprecationWarning,
                  stacklevel=2)
    from Products.PortalTransforms.transforms.safe_html import SafeHTML
    transform = SafeHTML()
    return transform.scrub_html(html)


# BBB This is not used in this module. Remove with Plone 6.0
scrubHTML = scrubHTMLNoRaise
