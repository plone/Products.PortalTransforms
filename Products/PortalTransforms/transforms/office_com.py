# -*- coding: utf-8 -*-
# Need to be imported first to avoid dll loading problems.
import pythoncom
import pywintypes

from Products.PortalTransforms.libtransforms.commandtransform import commandtransform  # noqa
from Products.PortalTransforms.libtransforms.utils import bodyfinder
from Products.PortalTransforms.transforms.safe_html import SafeHTML
from win32com.client import Dispatch
from win32com.client import constants
from win32com.client import gencache

import os
import os.path
import win32api
import win32com
import win32com.client


class document(commandtransform):

    def __init__(self, name, data):
        """Initialization: create tmp work
        directory and copy the document into a file"""
        commandtransform.__init__(self, name)
        name = self.name()
        if not name.endswith('.doc'):
            name = name + ".doc"
        self.tmpdir, self.fullname = self.initialize_tmpdir(data,
                                                            filename=name)

    def convert(self):
        try:
            # initialize COM for multi-threading, ignoring any errors
            # when someone else has already initialized differently.
            pythoncom.CoInitializeEx(pythoncom.COINIT_MULTITHREADED)
        except pythoncom.com_error:
            pass

        word = Dispatch("Word.Application")
        word.Visible = 0
        word.DisplayAlerts = 0
        doc = word.Documents.Open(self.fullname)
        # Let's set up some html saving options for this document
        doc.WebOptions.RelyOnCSS = 1
        doc.WebOptions.OptimizeForBrowser = 1
        doc.WebOptions.BrowserLevel = 0  # constants.wdBrowserLevelV4
        doc.WebOptions.OrganizeInFolder = 0
        doc.WebOptions.UseLongFileNames = 1
        doc.WebOptions.RelyOnVML = 0
        doc.WebOptions.AllowPNG = 1
        # And then save the document into HTML
        doc.SaveAs(FileName="%s.htm" % (self.fullname),
                   FileFormat=8)  # constants.wdFormatHTML)

        # TODO -- Extract Metadata (author, title, keywords) so we
        # can populate the dublin core
        # Converter will need to be extended to return a dict of
        # possible MD fields

        doc.Close()
        # word.Quit()

    def html(self):
        htmlfile = open(self.fullname + '.htm', 'r')
        html = htmlfile.read()
        htmlfile.close()
        html = SafeHTML().scrub_html(html)
        body = bodyfinder(html)
        return body

# This function has to be done. It's more difficult to delete the temp
# directory under Windows, because there is sometimes a directory in it.
# def cleanDir(self, tmpdir):
