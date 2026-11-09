from Products.PortalTransforms.data import datastream
from Products.PortalTransforms.Transform import Transform
from Products.PortalTransforms.transforms.broken import BrokenTransform

import gc
import unittest
import weakref


class Marker:
    """A local variable of the loading frame whose lifetime we observe."""


class BrokenTransformTests(unittest.TestCase):
    def _load_broken(self):
        marker = Marker()  # noqa: F841
        ref = weakref.ref(marker)
        try:
            try:
                raise ValueError("inner")
            except ValueError:
                # raised inside a handler, so the error carries a __context__
                raise RuntimeError("Unable to find binary")
        except RuntimeError as err:
            transform = BrokenTransform("broken", "some.module", err)
        return transform, ref

    def test_error_does_not_keep_loading_frames_alive(self):
        # https://github.com/plone/Products.PortalTransforms/issues/112
        transform, ref = self._load_broken()
        gc.collect()
        self.assertIsNone(ref())

    def test_convert_reports_error(self):
        transform, ref = self._load_broken()
        data = datastream("broken")
        with self.assertLogs("PortalTransforms", level="WARNING") as logs:
            result = transform.convert("orig", data)
        self.assertIs(result, data)
        self.assertEqual(data.getData(), "")
        self.assertIn(
            "BROKEN transform broken (some.module). Error: Unable to find binary",
            logs.output[0],
        )


class TransformLoadTests(unittest.TestCase):
    def test_convert_with_unimportable_module_uses_broken_transform(self):
        with self.assertLogs("PortalTransforms", level="ERROR"):
            transform = Transform(
                "broken", "Products.PortalTransforms.transforms.no_such_module"
            )
        self.assertEqual(transform.title, "BROKEN")
        data = datastream("broken")
        with self.assertLogs("PortalTransforms", level="WARNING"):
            result = transform.convert("orig", data)
        self.assertIs(result, data)
        self.assertEqual(data.getData(), "")
