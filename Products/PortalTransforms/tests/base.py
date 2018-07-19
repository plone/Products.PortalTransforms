# -*- coding: utf-8 -*-
import unittest

from Products.CMFPlone.utils import safe_unicode
from Products.PortalTransforms.testing import PRODUCTS_PORTALTRANSFORMS_INTEGRATION_TESTING  # noqa


class TransformTestCase(unittest.TestCase):

    layer = PRODUCTS_PORTALTRANSFORMS_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        self.transforms = self.portal.portal_transforms

    def _baseAssertEqual(self, first, second, msg=None):
        return unittest.TestCase._baseAssertEqual(
            self, safe_unicode(first), safe_unicode(second), msg)

    def assertMultiLineEqual(self, first, second, msg=None):
        return unittest.TestCase.assertMultiLineEqual(
            self, safe_unicode(first), safe_unicode(second), msg)
