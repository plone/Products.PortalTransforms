# -*- coding: utf-8 -*-
"""
Uses the xpdf (www.foolabs.com/xpdf)
"""

from Products.PortalTransforms.interfaces import ITransform
from Products.PortalTransforms.libtransforms.commandtransform import popentransform  # noqa
from zope.interface import implementer


@implementer(ITransform)
class pdf_to_text(popentransform):

    __name__ = "pdf_to_text"
    inputs = ('application/pdf',)
    output = 'text/plain'
    output_encoding = 'utf-8'

    __version__ = '2004-07-02.01'

    binaryName = "pdftotext"
    binaryArgs = "%(infile)s -enc UTF-8 -"
    useStdin = False


def register():
    return pdf_to_text()
