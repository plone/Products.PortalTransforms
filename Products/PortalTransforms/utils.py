"""some common utilities
"""
import logging

class TransformException(Exception):
    pass

FB_REGISTRY = None

# logging function
logger = logging.getLogger('PortalTransforms')

def log(message, severity=logging.DEBUG):
    logger.log(severity, message)

# directory where template for the ZMI are located
import os.path
_www = os.path.join(os.path.dirname(__file__), 'www')

def safeToInt(value):
    """Convert value to integer or just return 0 if we can't"""
    try:
        return int(value)
    except (TypeError, ValueError):
        return 0
