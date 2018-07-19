# -*- coding: utf-8 -*-
import six
import unittest

from Products.PortalTransforms.testing import PRODUCTS_PORTALTRANSFORMS_INTEGRATION_TESTING


class TransformTestCase(unittest.TestCase):

    layer = PRODUCTS_PORTALTRANSFORMS_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        self.transforms = self.portal.portal_transforms

    def _baseAssertEqual(self, first, second, msg=None):
        if six.PY3 and isinstance(first, six.binary_type):
            first = first.decode('utf-8')
        return unittest.TestCase._baseAssertEqual(self, first, second, msg)
