from Products.MimetypesRegistry import mime_types
from Products.MimetypesRegistry import MimeTypeItem
from Products.PortalTransforms.TransformEngine import TransformTool

# running (required)
# XXX backward compatibility tricks to make old PortalTransform based Mimetypes
import sys


PKG_NAME = 'PortalTransforms'

tools = (
    TransformTool,
)

this_module = sys.modules[__name__]

setattr(this_module, 'mime_types', mime_types)

setattr(this_module, 'MimeTypeItem', MimeTypeItem)

sys.modules['Products.PortalTransforms.zope.MimeTypeItem'] = MimeTypeItem


def initialize(context):
    from Products.CMFCore import utils
    utils.ToolInit("%s Tool" % PKG_NAME,
                   tools=tools,
                   icon="tool.gif",
                   ).initialize(context)
