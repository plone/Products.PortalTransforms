# -*- coding: utf-8 -*-
"""
Uses lynx -dump
"""
from Products.PortalTransforms.interfaces import ITransform
from Products.PortalTransforms.libtransforms.commandtransform import \
    popentransform
from zope.interface import implementer


@implementer(ITransform)
class lynx_dump(popentransform):

    __name__ = "lynx_dump"
    inputs = ('text/html',)
    output = 'text/plain'

    __version__ = '2004-07-02.1'

    binaryName = "lynx"
    # XXX does -stdin work on windows?
    binaryArgs = "-dump -stdin -force_html"
    useStdin = True


def register():
    return lynx_dump()
