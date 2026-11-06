import importlib
import sys
import unittest


class UnsafeTransformsDeprecationTests(unittest.TestCase):
    def test_import_warns(self):
        for name in list(sys.modules):
            if name.startswith("Products.PortalTransforms.unsafe_transforms"):
                del sys.modules[name]
        with self.assertWarnsRegex(DeprecationWarning, "unsafe_transforms"):
            importlib.import_module("Products.PortalTransforms.unsafe_transforms.xml")
