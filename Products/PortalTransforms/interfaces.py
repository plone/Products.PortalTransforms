from zope.interface import Interface

from z3.interfaces import IDataStream, IChain, IEngine, ITransform

idatastream = IDataStream
ichain = IChain
iengine = IEngine
itransform = ITransform

class IPortalTransformsTool(Interface):
    """Marker interface for the portal_transforms tool."""
