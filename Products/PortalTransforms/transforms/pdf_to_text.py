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

    binaryName = "pdftotext"
    binaryArgs = "- -enc UTF-8 -"


def register():
    return pdf_to_text()
