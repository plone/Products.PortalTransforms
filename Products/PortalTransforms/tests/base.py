# -*- coding: utf-8 -*-
import unittest

from Products.PortalTransforms.testing import PRODUCTS_PORTALTRANSFORMS_INTEGRATION_TESTING  # noqa


class TransformTestCase(unittest.TestCase):

    layer = PRODUCTS_PORTALTRANSFORMS_INTEGRATION_TESTING

    allowed_types = str

    def setUp(self):
        self.portal = self.layer['portal']
        self.transforms = self.portal.portal_transforms
