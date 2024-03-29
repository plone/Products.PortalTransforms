"""
Uses the http://freshmeat.net/projects/rtfconverter/ bin to do its handy work
"""

from Products.PortalTransforms.interfaces import ITransform
from Products.PortalTransforms.libtransforms.commandtransform import commandtransform
from Products.PortalTransforms.libtransforms.utils import bodyfinder
from Products.PortalTransforms.libtransforms.utils import sansext
from zope.interface import implementer

import subprocess


@implementer(ITransform)
class rtf_to_html(commandtransform):
    __name__ = "rtf_to_html"
    inputs = ("application/rtf",)
    output = "text/html"

    binaryName = "rtf-converter"

    def __init__(self):
        commandtransform.__init__(self, binary=self.binaryName)

    def convert(self, data, cache, **kwargs):
        kwargs["filename"] = "unknown.rtf"

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
        # FIXME: windows users...
        htmlfile = f"{tmpdir}/{sansext(fullname)}.html"
        cmd = 'cd "{}" && {} -o {} "{}" 2>error_log 1>/dev/null'.format(
            tmpdir, self.binary, htmlfile, fullname
        )
        subprocess.run(cmd, shell=True)
        try:
            html = open(htmlfile).read()
        except Exception:
            try:
                return open("%s/error_log" % tmpdir).read()
            except Exception:
                return ""
        return html


def register():
    return rtf_to_html()
