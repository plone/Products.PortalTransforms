from zope.interface import Interface


class IPortalTransformsTool(Interface):
    """Marker interface for the portal_transforms tool."""


class IDataStream(Interface):
    """data stream, is the result of a transform"""

    def setData(value):
        """set the main data produced by a transform,
        i.e. usually a native string"""

    def getData():
        """provide access to the transformed data object,
        i.e. usually a native string
        This data may references subobjects.
        """

    def setSubObjects(objects):
        """set a dict-like object containing subobjects.
        keys should be object's identifier (e.g. usually a filename) and
        values object's content.
        """

    def getSubObjects():
        """return a dict-like object with any optional subobjects associated
        with the data"""

    def getMetadata():
        """return a dict-like object with any optional metadata from
        the transform
        You can modify the returned dictionary to add/change metadata
        """

    def isCacheable():
        """Return a bool which indicates wether the result should be cached

        Default is true
        """

    def setCachable(value):
        """Set cacheable flag to yes or no
        """


class ITransform(Interface):
    """A transformation plugin -- tranform data somehow
    must be threadsafe and stateless"""

    def name(self):
        """return the name of the transform instance"""

    def convert(data, idata, filename=None, **kwargs):
        """convert the data, store the result in idata and return that

        optional argument filename may give the original file name of
        received data

        additional arguments given to engine's convert, convertTo or
        __call__ are passed back to the transform

        The object on which the translation was invoked is available as context
        (default: None)
        """


class IChain(ITransform):

    def registerTransform(transform, condition=None):
        """Append a transform to the chain"""


class IEngine(Interface):

    def registerTransform(transform):
        """register a transform

        transform must implement ITransform
        """

    def unregisterTransform(name):
        """ unregister a transform
        name is the name of a registered transform
        """

    def convertTo(mimetype, orig, data=None, object=None, context=None,
                  **kwargs):
        """Convert orig to a given mimetype

        * orig is a native string

        * data an optional idatastream object. If None a new datastream will be
        created and returned

        * optional object argument is the object on which is bound the data.
        If present that object will be used by the engine to bound cached data.

        * optional context argument is the object on which the transformation
          was called.

        * additional arguments (kwargs) will be passed to the transformations.

        return an object implementing idatastream or None if no path has been
        found.
        """

    def convert(name, orig, data=None, context=None, **kwargs):
        """run a tranform of a given name on data

        * name is the name of a registered transform

        see convertTo docstring for more info
        """

    def __call__(name, orig, data=None, context=None, **kwargs):
        """run a transform by its name, returning the raw data product

        * name is the name of a registered transform.

        return an encoded string.
        see convert docstring for more info on additional arguments.
        """


# BBB
idatastream = IDataStream
ichain = IChain
iengine = IEngine
itransform = ITransform
