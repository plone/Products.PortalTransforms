from setuptools import setup, find_packages

version = '2.1.1'

setup(name='Products.PortalTransforms',
      version=version,
      description="MIME based content transformations",
      long_description=open("README.txt").read() + "\n" + \
                       open("CHANGES.txt").read(),
      classifiers=[
        "Framework :: Zope2",
        "Operating System :: OS Independent",
        ],
      keywords='Zope Plone Transform',
      author='Benjamin Saller',
      author_email='plone-developers@lists.sourceforge.net',
      url='http://pypi.python.org/pypi/Products.PortalTransforms',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['Products'],
      include_package_data=True,
      zip_safe=False,
      extras_require=dict(
        test=[
            'zope.testing',
            'Products.Archetypes',
            'Products.CMFTestCase',
            'Pillow',
        ],
      ),
      install_requires=[
          'setuptools',
          'plone.intelligenttext',
          'zope.interface',
          'zope.structuredtext',
          'Products.CMFCore',
          'Products.CMFDefault',
          'Products.MimetypesRegistry',
          'Acquisition',
          'ZODB3',
          'Zope2',
          'Markdown>=1.7',
      ],
      )
