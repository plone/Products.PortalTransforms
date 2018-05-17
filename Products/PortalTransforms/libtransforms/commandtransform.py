# -*- coding: utf-8 -*-
from Products.PortalTransforms.interfaces import ITransform
from Products.PortalTransforms.libtransforms.utils import bin_search
from Products.PortalTransforms.libtransforms.utils import getShortPathName
from os.path import basename
from os.path import join
from zope.interface import implementer
import os
import re
import shutil
import six
import subprocess
import tempfile


@implementer(ITransform)
class commandtransform(object):
    """abstract class for external command based transform
    """

    def __init__(self, name=None, binary=None, **kwargs):
        if name is not None:
            self.__name__ = name
        if binary is not None:
            self.binary = bin_search(binary)
            self.binary = getShortPathName(self.binary)

    def name(self):
        return self.__name__

    def initialize_tmpdir(self, data, **kwargs):
        """create a temporary directory, copy input in a file there
        return the path of the tmp dir and of the input file
        """
        tmpdir = tempfile.mktemp()
        os.mkdir(tmpdir)
        filename = kwargs.get("filename", '')
        fullname = join(tmpdir, basename(filename))
        with open(fullname, "wb") as fd:
            fd.write(data)
        return tmpdir, fullname

    def subObjects(self, tmpdir):
        imgs = []
        for f in os.listdir(tmpdir):
            result = re.match("^.+\.(?P<ext>.+)$", f)
            if result is not None:
                ext = result.group('ext')
                if ext in ('png', 'jpg', 'gif'):
                    imgs.append(f)
        path = join(tmpdir, '')
        return path, imgs

    def fixImages(self, path, images, objects):
        for image in images:
            objects[image] = open(join(path, image), 'rb').read()

    def cleanDir(self, tmpdir):
        shutil.rmtree(tmpdir)


@implementer(ITransform)
class popentransform(object):
    """abstract class for external command based transform

    Command must read from stdin and write to stdout
    """

    binaryName = ""
    binaryArgs = ""

    def __init__(self, name=None, binary=None, binaryArgs=None, **kwargs):
        if name is not None:
            self.__name__ = name
        if binary is not None:
            self.binary = bin_search(binary)
        else:
            self.binary = bin_search(self.binaryName)
        if binaryArgs is not None:
            self.binaryArgs = binaryArgs

    def name(self):
        return self.__name__

    def convert(self, data, cache, **kwargs):
        command = "%s %s" % (self.binary, self.binaryArgs)
        if six.PY2:
            cin, couterr = os.popen4(command, 'b')

            cin.write(data)
            cin.close()

            out = couterr.read()
            couterr.close()
        else:
            process = subprocess.run(
                command, shell=True, input=data, stdout=subprocess.PIPE)
            out = process.stdout

        cache.setData(out)
        return cache
