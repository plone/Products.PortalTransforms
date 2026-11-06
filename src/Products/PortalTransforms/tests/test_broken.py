from Products.PortalTransforms.data import datastream
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
                import no_such_module_for_this_test  # noqa: F401
            except ImportError:
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
