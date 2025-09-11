from Products.PortalTransforms.libtransforms.commandtransform import commandtransform
from Products.PortalTransforms.libtransforms.utils import bodyfinder
from Products.PortalTransforms.transforms.safe_html import SafeHTML

import os
import subprocess


class document(commandtransform):
    def __init__(self, name, data):
        """Initialization: create tmp work directory and copy the
        document into a file"""
        commandtransform.__init__(self, name, binary="wvHtml")
        name = self.name()
        if not name.endswith(".doc"):
            name = name + ".doc"
        self.tmpdir, self.fullname = self.initialize_tmpdir(data, filename=name)

    def convert(self):
        "Convert the document"
        tmpdir = self.tmpdir

        # For windows, install wvware from GnuWin32 at
        # C:\Program Files\GnuWin32\bin
        # You can use:
        # wvware.exe -c ..\share\wv\wvHtml.xml --charset=utf-8 -d d:\temp \
        #    d:\temp\test.doc > test.html

        if os.name == "posix":
            cmd = 'cd "{}" && {} --charset=utf-8 "{}" "{}.html"'.format(
                tmpdir, self.binary, self.fullname, self.__name__
            )
            subprocess.run(cmd, shell=True)

    def html(self):
        htmlfile = open(f"{self.tmpdir}/{self.__name__}.html")
        html = htmlfile.read()
        htmlfile.close()
        html = SafeHTML().scrub_html(html)
        body = bodyfinder(html)
        return body
