from setuptools import setup, find_packages
import os

<<<<<<< HEAD:setup.py
version = '2.0'
=======
version = '1.6.2dev'
>>>>>>> development:setup.py

setup(name='Products.PortalTransforms',
      version=version,
      description="MIME based content transformations",
      long_description=open("README.txt").read() + "\n" + \
                       open("CHANGES.txt").read(),
      classifiers=[
        "Framework :: Zope2",
        "Operating System :: OS Independent",
        ],
      keywords='Zope catalog index',
      author='Benjamin Saller',
      author_email='plone-developers@lists.sourceforge.net',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['Products'],
      include_package_data=True,
      zip_safe=False,
      extras_require=dict(
        test=[
            'zope.testing',
            'Products.Archetypes',
        ]
      ),
      install_requires=[
          'setuptools',
          'plone.intelligenttext',
          'zope.interface',
          'zope.structuredtext',
          'Products.CMFCore',
          'Products.CMFDefault',
          'Products.MimetypesRegistry',
<<<<<<< HEAD:setup.py
          'Acquisition',
          'ZODB3',
          'Zope2',
=======
          'Markdown>=1.7',
>>>>>>> development:setup.py
      ],
      )
