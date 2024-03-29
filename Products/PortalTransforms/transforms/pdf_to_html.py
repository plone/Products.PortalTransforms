"""
Uses the http://sf.net/projects/pdftohtml bin to do its handy work

"""

from Products.PortalTransforms.interfaces import ITransform
from Products.PortalTransforms.libtransforms.commandtransform import commandtransform
from Products.PortalTransforms.libtransforms.utils import bodyfinder
from Products.PortalTransforms.libtransforms.utils import sansext
from zope.interface import implementer

import os
import subprocess


@implementer(ITransform)
class pdf_to_html(commandtransform):
    __name__ = "pdf_to_html"
    inputs = ("application/pdf",)
    output = "text/html"
    output_encoding = "utf-8"

    binaryName = "pdftohtml"
    binaryArgs = "-noframes -enc UTF-8"

    def __init__(self):
        commandtransform.__init__(self, binary=self.binaryName)

    def convert(self, data, cache, **kwargs):
        kwargs["filename"] = "unknown.pdf"

        tmpdir, fullname = self.initialize_tmpdir(data, **kwargs)
        html = self.invokeCommand(tmpdir, fullname)
        path, images = self.subObjects(tmpdir)
        objects = {}
        if images:
            self.fixImages(path, images, objects)
        self.cleanDir(tmpdir)
        cache.setData(bodyfinder(html))
        cache.setSubObjects(objects)
        return cache

    def invokeCommand(self, tmpdir, fullname):
        if os.name == "posix":
            cmd = 'cd "{}" && {} {} "{}" 2>error_log 1>/dev/null'.format(
                tmpdir, self.binary, self.binaryArgs, fullname
            )
        else:
            cmd = 'cd "{}" && {} {} "{}"'.format(
                tmpdir, self.binary, self.binaryArgs, fullname
            )
        subprocess.run(cmd, shell=True)
        try:
            htmlfilename = os.path.join(tmpdir, sansext(fullname) + ".html")
            with open(htmlfilename, "rb") as htmlfile:
                html = htmlfile.read()
        except Exception:
            try:
                with open("%s/error_log" % tmpdir) as fd:
                    error_log = fd.read()
                return error_log
            except Exception:
                return (
                    "transform failed while running %s (maybe this pdf "
                    "file doesn't support transform)" % cmd
                )
        return html


def register():
    return pdf_to_html()
