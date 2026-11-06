from Products.PortalTransforms.data import datastream
from Products.PortalTransforms.interfaces import IDataStream
from zope.interface.verify import verifyClass

import unittest


class DataStreamTests(unittest.TestCase):
    def test_implements_interface(self):
        self.assertTrue(verifyClass(IDataStream, datastream))
