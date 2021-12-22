"""some common utilities
"""
# directory where template for the ZMI are located
import logging
import os.path
import six

try:
    from Products.CMFPlone.utils import safe_nativestring
except ImportError:
    # Not needed for Products.CMFPlone >= 5.2a1
    from Products.CMFPlone.utils import safe_encode
    from Products.CMFPlone.utils import safe_unicode

    def safe_nativestring(value, encoding='utf-8'):
        """Convert a value to str in py2 and to text in py3
        """
        if six.PY2 and isinstance(value, six.text_type):
            value = safe_encode(value, encoding)
        if not six.PY2 and isinstance(value, six.binary_type):
            value = safe_unicode(value, encoding)
        return value


class TransformException(Exception):
    pass


FB_REGISTRY = None

# logging function
logger = logging.getLogger('PortalTransforms')


def log(message, severity=logging.DEBUG):
    logger.log(severity, message)


_www = os.path.join(os.path.dirname(__file__), 'www')


def safeToInt(value):
    """Convert value to integer or just return 0 if we can't"""
    try:
        return int(value)
    except (TypeError, ValueError):
        return 0
