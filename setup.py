from setuptools import find_packages
from setuptools import setup


version = '3.2.2'

setup(name='Products.PortalTransforms',
      version=version,
      description="MIME based content transformations",
      long_description=open("README.rst").read() + "\n" +
      open("CHANGES.rst").read(),
      classifiers=[
          "Development Status :: 5 - Production/Stable",
          "Framework :: Plone",
          "Framework :: Plone :: 5.2",
          "Framework :: Plone :: 6.0",
          "Framework :: Plone :: Core",
          "Framework :: Zope :: 4",
          "Framework :: Zope :: 5",
          "License :: OSI Approved :: GNU General Public License (GPL)",
          "Operating System :: OS Independent",
          "Programming Language :: Python",
          "Programming Language :: Python :: 2",
          "Programming Language :: Python :: 2.7",
          "Programming Language :: Python :: 3",
          "Programming Language :: Python :: 3.7",
          "Programming Language :: Python :: 3.8",
          "Programming Language :: Python :: 3.9",
          "Programming Language :: Python :: 3.10",
          "Programming Language :: Python :: 3.11",
      ],
      keywords='Zope Plone Transform',
      author='Benjamin Saller',
      author_email='plone-developers@lists.sourceforge.net',
      url='https://pypi.org/project/Products.PortalTransforms',
      license='GPL',
      packages=find_packages(),
      namespace_packages=['Products'],
      include_package_data=True,
      zip_safe=False,
      python_requires=">=2.7,!=3.0.*,!=3.1.*,!=3.2.*,!=3.3.*,!=3.4.*,!=3.5.*",
      extras_require=dict(
          test=[
              'zope.testing',
              'Pillow',
          ],
      ),
      install_requires=[
          'setuptools',
          'six',
          'plone.intelligenttext',
          'zope.interface',
          'zope.structuredtext',
          'Pillow>=3.1.0',
          'Products.CMFCore',
          'Products.MimetypesRegistry',
          'Acquisition',
          'ZODB',
          'Zope',
          'Markdown>=2.6.5',
      ],
)
