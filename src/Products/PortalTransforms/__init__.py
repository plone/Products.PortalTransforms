from Products.PortalTransforms.TransformEngine import TransformTool


PKG_NAME = "PortalTransforms"

tools = (TransformTool,)


def initialize(context):
    from Products.CMFCore import utils

    utils.ToolInit(
        "%s Tool" % PKG_NAME,
        tools=tools,
        icon="tool.gif",
    ).initialize(context)
