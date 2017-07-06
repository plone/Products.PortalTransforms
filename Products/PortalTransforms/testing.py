# -*- coding: utf-8 -*-
from plone.app.contenttypes.testing import PLONE_APP_CONTENTTYPES_FIXTURE
from plone.app.testing import PloneSandboxLayer
from plone.app.testing.layers import FunctionalTesting
from plone.app.testing.layers import IntegrationTesting
from zope.configuration import xmlconfig


class ProductsPortalTransformsLayer(PloneSandboxLayer):

    defaultBases = (PLONE_APP_CONTENTTYPES_FIXTURE,)

    def setUpZope(self, app, configurationContext):
        import Products.PortalTransforms
        xmlconfig.file(
            'configure.zcml',
            Products.PortalTransforms,
            context=configurationContext
        )


PRODUCTS_PORTALTRANSFORMS_FIXTURE = ProductsPortalTransformsLayer()

PRODUCTS_PORTALTRANSFORMS_INTEGRATION_TESTING = IntegrationTesting(
    bases=(PRODUCTS_PORTALTRANSFORMS_FIXTURE,),
    name="PortalTransformsLayer:Integration"
)
PRODUCTS_PORTALTRANSFORMS_FUNCTIONAL_TESTING = FunctionalTesting(
    bases=(PRODUCTS_PORTALTRANSFORMS_FIXTURE,),
    name="PortalTransformsLayer:Functional"
)
