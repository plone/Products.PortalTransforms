from pathlib import Path
from setuptools import find_packages
from setuptools import setup


version = "4.1.0"

long_description = (
    f"{Path('README.rst').read_text()}\n{Path('CHANGES.rst').read_text()}"
)

setup(
    name="Products.PortalTransforms",
    version=version,
    description="MIME based content transformations",
    long_description=long_description,
    long_description_content_type="text/x-rst",
    # Get more strings from
    # https://pypi.org/classifiers/
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Environment :: Web Environment",
        "Framework :: Plone",
        "Framework :: Plone :: 6.0",
        "Framework :: Plone :: Core",
        "Framework :: Zope :: 5",
        "License :: OSI Approved :: GNU General Public License (GPL)",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    keywords="Zope Plone Transform",
    author="Benjamin Saller",
    author_email="plone-developers@lists.sourceforge.net",
    url="https://pypi.org/project/Products.PortalTransforms",
    license="GPL",
    packages=find_packages(),
    namespace_packages=["Products"],
    include_package_data=True,
    zip_safe=False,
    python_requires=">=3.8",
    extras_require=dict(
        test=[
            "plone.app.contenttypes[test]",
            "plone.app.testing",
        ],
    ),
    install_requires=[
        "docutils",
        "DocumentTemplate",
        "Persistence",
        "Products.GenericSetup",
        "setuptools",
        "lxml",
        "lxml_html_clean",
        "persistent",
        "plone.base",
        "plone.registry",
        "plone.intelligenttext",
        "zope.structuredtext",
        "Pillow>=3.1.0",
        "Products.CMFCore",
        "Products.MimetypesRegistry",
        "Zope",
        "Markdown>=2.6.5",
    ],
)
