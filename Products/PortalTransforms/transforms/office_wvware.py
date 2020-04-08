# -*- coding: utf-8 -*-
import os
import six
import subprocess

from Products.PortalTransforms.libtransforms.commandtransform import commandtransform  # noqa
from Products.PortalTransforms.libtransforms.utils import bodyfinder
from Products.PortalTransforms.transforms.safe_html import SafeHTML


class document(commandtransform):

    def __init__(self, name, data):
        """ Initialization: create tmp work directory and copy the
        document into a file"""
        commandtransform.__init__(self, name, binary="wvHtml")
        name = self.name()
        if not name.endswith('.doc'):
            name = name + ".doc"
        self.tmpdir, self.fullname = self.initialize_tmpdir(data,
                                                            filename=name)

    def convert(self):
        "Convert the document"
        tmpdir = self.tmpdir

        # For windows, install wvware from GnuWin32 at
        # C:\Program Files\GnuWin32\bin
        # You can use:
        # wvware.exe -c ..\share\wv\wvHtml.xml --charset=utf-8 -d d:\temp \
        #    d:\temp\test.doc > test.html

        if os.name == 'posix':
            cmd = 'cd "%s" && %s --charset=utf-8 "%s" "%s.html"' % (
                tmpdir, self.binary, self.fullname, self.__name__)
            if six.PY2:
                os.system(cmd)
            else:
                subprocess.run(cmd, shell=True)

    def html(self):
        htmlfile = open("%s/%s.html" % (self.tmpdir, self.__name__), 'r')
        html = htmlfile.read()
        htmlfile.close()
        html = SafeHTML().scrub_html(html)
        body = bodyfinder(html)
        return body
