# -*- coding: utf-8 -*-
import doctest
import unittest


modules = (
    'Products.PortalTransforms.transforms.safe_html',
    'Products.PortalTransforms.transforms.rest',
)


def test_suite():
    return unittest.TestSuite(
        [doctest.DocTestSuite(module=module) for module in modules])
