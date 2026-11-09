from Products.PortalTransforms.interfaces import ITransform
from Products.PortalTransforms.utils import log
from zope.interface import implementer

import logging


@implementer(ITransform)
class BrokenTransform:
    __name__ = "broken transform"
    inputs = ("BROKEN",)
    output = "BROKEN"

    def __init__(self, id, module, error):
        self.id = id
        self.module = module
        # Keep only the message. An exception instance would keep its
        # traceback, and with it every frame of the request that loaded the
        # transform, alive for as long as the Transform stays in the ZODB
        # connection cache.
        self.error = str(error)

    def name(self):
        return self.__name__

    def convert(self, orig, data, **kwargs):
        # do the format
        msg = "Calling convert on BROKEN transform {} ({}). Error: {}".format(
            self.id,
            self.module,
            self.error,
        )
        log(msg, severity=logging.WARNING)
        data.setData("")
        return data


def register():
    pass
