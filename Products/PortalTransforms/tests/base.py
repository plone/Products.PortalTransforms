# -*- coding: utf-8 -*-
import six
import unittest

from Products.PortalTransforms.testing import PRODUCTS_PORTALTRANSFORMS_INTEGRATION_TESTING  # noqa


class TransformTestCase(unittest.TestCase):

    layer = PRODUCTS_PORTALTRANSFORMS_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        self.transforms = self.portal.portal_transforms

    def _decode(self, first, second):
        if isinstance(first, six.binary_type):
            first = first.decode('unicode-escape')
        if isinstance(second, six.binary_type):
            second = second.decode('unicode-escape')

    def _baseAssertEqual(self, first, second, msg=None):
        self._decode(first, second)
        return unittest.TestCase._baseAssertEqual(self, first, second, msg)

    def assertMultiLineEqual(self, first, second, msg=None):
        self._decode(first, second)
        return unittest.TestCase.assertMultiLineEqual(self, first, second, msg)
