"""
Uses the http://sf.net/projects/rtf2xml bin to do its handy work

"""

from Products.PortalTransforms.interfaces import ITransform
from Products.PortalTransforms.libtransforms.commandtransform import commandtransform
from Products.PortalTransforms.libtransforms.utils import sansext
from zope.interface import implementer

import subprocess


@implementer(ITransform)
class rtf_to_xml(commandtransform):
    __name__ = "rtf_to_xml"
    inputs = ("application/rtf",)
    output = "text/xml"

    binaryName = "rtf2xml"

    def __init__(self):
        commandtransform.__init__(self, binary=self.binaryName)

    def convert(self, data, cache, **kwargs):
        kwargs["filename"] = "unknown.rtf"

        tmpdir, fullname = self.initialize_tmpdir(data, **kwargs)
        xml = self.invokeCommand(tmpdir, fullname)
        path, images = self.subObjects(tmpdir)
        objects = {}
        if images:
            self.fixImages(path, images, objects)
        self.cleanDir(tmpdir)
        cache.setData(xml)
        cache.setSubObjects(objects)
        return cache

    def invokeCommand(self, tmpdir, fullname):
        # FIXME: windows users...
        xmlfile = f"{tmpdir}/{sansext(fullname)}.xml"
        cmd = 'cd "{}" && {} -o {} "{}" 2>error_log 1>/dev/null'.format(
            tmpdir, self.binary, xmlfile, fullname
        )
        subprocess.run(cmd, shell=True)
        try:
            xml = open(xmlfile).read()
        except Exception:
            try:
                return open("%s/error_log" % tmpdir).read()
            except Exception:
                return ""
        return xml


def register():
    return rtf_to_xml()
