# -*- coding: utf8  -*-
from __future__ import print_function
from os.path import exists
from plone.registry.interfaces import IRegistry
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.interfaces import IFilterSchema
from Products.PortalTransforms.data import datastream
from Products.PortalTransforms.interfaces import IDataStream
from Products.PortalTransforms.libtransforms.utils import MissingBinary
from Products.PortalTransforms.libtransforms.utils import scrubHTMLNoRaise
from Products.PortalTransforms.testing import \
    PRODUCTS_PORTALTRANSFORMS_INTEGRATION_TESTING
from Products.PortalTransforms.transforms.image_to_bmp import image_to_bmp
from Products.PortalTransforms.transforms.image_to_gif import image_to_gif
from Products.PortalTransforms.transforms.image_to_jpeg import image_to_jpeg
from Products.PortalTransforms.transforms.image_to_pcx import image_to_pcx
from Products.PortalTransforms.transforms.image_to_png import image_to_png
from Products.PortalTransforms.transforms.image_to_ppm import image_to_ppm
from Products.PortalTransforms.transforms.image_to_tiff import image_to_tiff
from Products.PortalTransforms.transforms.markdown_to_html import HAS_MARKDOWN
from Products.PortalTransforms.transforms.textile_to_html import HAS_TEXTILE
from zope.component import getUtility

from .utils import input_file_path
from .utils import load
from .utils import matching_inputs
from .utils import normalize_html
from .utils import output_file_path
from xml.sax.saxutils import unescape

import itertools
import os
import unittest


# we have to set locale because lynx output is locale sensitive !
os.environ['LC_ALL'] = 'C'


class TransformTest(unittest.TestCase):
    layer = PRODUCTS_PORTALTRANSFORMS_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        self.request = self.layer['request']
        self.pt = self.portal.portal_transforms
        registry = getUtility(IRegistry)
        self.settings = registry.forInterface(
            IFilterSchema, prefix="plone")

    def do_convert(self, filename=None):
        if filename is None and exists(self.output + '.nofilename'):
            output = self.output + '.nofilename'
        else:
            output = self.output
        with open(self.input) as fp:
            orig = fp.read()
        data = datastream(self.transform.name())
        res_data = self.transform.convert(orig, data, filename=filename)
        self.assert_(IDataStream.providedBy(res_data))
        got = res_data.getData()
        try:
            output = open(output)
        except IOError:
            import sys
            print('No output file found.', file=sys.stderr)
            print('File {0} created, check it !'.format(self.output),
                file=sys.stderr)
            output = open(output, 'w')
            output.write(got)
            output.close()
            self.assert_(0)
        expected = output.read()
        if self.normalize is not None:
            expected = self.normalize(expected)
            got = self.normalize(got)
        output.close()

        got_start = got.strip()[:20]
        expected_start = expected.strip()[:20]
        msg = 'IN {0}({1}) expected:\n{2}\nbut got:\n{3}'.format(
            self.transform.name(),
            self.input,
            str([ord(x) for x in expected_start]),
            str([ord(x) for x in got_start]),
        )

        self.assertEqual(
            got_start,
            expected_start,
            msg
        )
        self.assertEqual(
            self.subobjects,
            len(res_data.getSubObjects()),
            '%s\n\n!=\n\n%s\n\nIN %s(%s)' % (
                self.subobjects,
                len(res_data.getSubObjects()),
                self.transform.name(),
                self.input
            )
        )

    def testSame(self):
        try:
            self.do_convert(filename=self.input)
        except MissingBinary:
            pass

    def testSameNoFilename(self):
        try:
            self.do_convert()
        except MissingBinary:
            pass

    def __repr__(self):
        return self.transform.name()


class PILTransformsTest(unittest.TestCase):
    layer = PRODUCTS_PORTALTRANSFORMS_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        self.request = self.layer['request']
        self.pt = self.portal.portal_transforms
        self.mimetypes_registry = getToolByName(self.portal,
                                                'mimetypes_registry')

    def test_image_to_bmp(self):
        self.pt.registerTransform(image_to_bmp())
        imgFile = open(input_file_path('logo.jpg'), 'rb')
        data = imgFile.read()
        self.assertEqual(self.mimetypes_registry.classify(data),
                         'image/jpeg')
        data = self.pt.convertTo(target_mimetype='image/x-ms-bmp', orig=data)
        self.assertEqual(data.getMetadata()['mimetype'], 'image/x-ms-bmp')

    def test_image_to_gif(self):
        self.pt.registerTransform(image_to_gif())
        imgFile = open(input_file_path('logo.png'), 'rb')
        data = imgFile.read()
        self.assertEqual(self.mimetypes_registry.classify(data),
                         'image/png')
        data = self.pt.convertTo(target_mimetype='image/gif', orig=data)
        self.assertEqual(data.getMetadata()['mimetype'], 'image/gif')

    def test_image_to_jpeg(self):
        self.pt.registerTransform(image_to_jpeg())
        imgFile = open(input_file_path('logo.gif'), 'rb')
        data = imgFile.read()
        self.assertEqual(self.mimetypes_registry.classify(data),
                         'image/gif')
        data = self.pt.convertTo(target_mimetype='image/jpeg', orig=data)
        self.assertEqual(data.getMetadata()['mimetype'], 'image/jpeg')

    def test_image_to_png(self):
        self.pt.registerTransform(image_to_png())
        imgFile = open(input_file_path('logo.jpg'), 'rb')
        data = imgFile.read()
        self.assertEqual(self.mimetypes_registry.classify(data),
                         'image/jpeg')
        data = self.pt.convertTo(target_mimetype='image/png', orig=data)
        self.assertEqual(data.getMetadata()['mimetype'], 'image/png')

    def test_image_to_pcx(self):
        self.pt.registerTransform(image_to_pcx())
        imgFile = open(input_file_path('logo.gif'), 'rb')
        data = imgFile.read()
        self.assertEqual(self.mimetypes_registry.classify(data),
                         'image/gif')
        data = self.pt.convertTo(target_mimetype='image/pcx', orig=data)
        self.assertEqual(data.getMetadata()['mimetype'], 'image/pcx')

    def test_image_to_ppm(self):
        self.pt.registerTransform(image_to_ppm())
        imgFile = open(input_file_path('logo.png'), 'rb')
        data = imgFile.read()
        self.assertEqual(self.mimetypes_registry.classify(data),
                         'image/png')
        data = self.pt.convertTo(target_mimetype='image/x-portable-pixmap',
                                 orig=data)
        self.assertEqual(data.getMetadata()['mimetype'],
                         'image/x-portable-pixmap')

    def test_image_to_tiff(self):
        self.pt.registerTransform(image_to_tiff())
        imgFile = open(input_file_path('logo.jpg'), 'rb')
        data = imgFile.read()
        self.assertEqual(self.mimetypes_registry.classify(data),
                         'image/jpeg')
        data = self.pt.convertTo(target_mimetype='image/tiff', orig=data)
        self.assertEqual(data.getMetadata()['mimetype'], 'image/tiff')


class SafeHtmlTransformsTest(unittest.TestCase):
    layer = PRODUCTS_PORTALTRANSFORMS_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        self.request = self.layer['request']
        self.pt = self.portal.portal_transforms
        registry = getUtility(IRegistry)
        self.settings = registry.forInterface(
            IFilterSchema, prefix="plone")
        self.settings.valid_tags.append('style')
        self.settings.valid_tags.remove('h1')
        self.settings.nasty_tags.append('h1')

    def tearDown(self):
        self.settings.valid_tags.remove('style')
        self.settings.valid_tags.append('h1')

    def test_kill_nasty_tags_which_are_not_valid(self):
        self.assertTrue('script' in self.settings.nasty_tags)
        self.assertFalse('script' in self.settings.valid_tags)
        orig = '<p><script>foo</script></p>'
        data_out = '<p/>'
        data = self.pt.convertTo(target_mimetype='text/x-html-safe', orig=orig)
        self.assertEqual(data.getData(), data_out)

        self.assertTrue('h1' in self.settings.nasty_tags)
        self.assertFalse('h1' in self.settings.valid_tags)
        orig = '<p><h1>foo</h1></p>'
        data_out = '<p/>'
        data = self.pt.convertTo(target_mimetype='text/x-html-safe', orig=orig)
        self.assertEqual(data.getData(), data_out)

    def test_entityiref_attributes(self):
        orig = '<a href="&uuml;">foo</a>'
        data_out = '<a href="&#xFC;">foo</a>'
        data = self.pt.convertTo(target_mimetype='text/x-html-safe', orig=orig)
        self.assertEqual(data.getData(), data_out)

    def test_charref_attributes(self):
        orig = '<a href="&#0109;">foo</a>'
        data_out = '<a href="m">foo</a>'
        data = self.pt.convertTo(target_mimetype='text/x-html-safe', orig=orig)
        self.assertEqual(data.getData(), data_out)

    def test_entityiref_data(self):
        orig = '<p>foo &uuml; bar</p>'
        data_out = '<p>foo \xc3\xbc bar</p>'
        data = self.pt.convertTo(target_mimetype='text/x-html-safe', orig=orig)
        self.assertEqual(data.getData(), data_out)

    def test_charref_data(self):
        orig = '<p>bar &#0109; foo</p>'
        data_out = '<p>bar m foo</p>'
        data = self.pt.convertTo(target_mimetype='text/x-html-safe', orig=orig)
        self.assertEqual(data.getData(), data_out)


class SafeHtmlTransformsWithScriptTest(unittest.TestCase):
    layer = PRODUCTS_PORTALTRANSFORMS_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        self.request = self.layer['request']
        registry = getUtility(IRegistry)
        self.settings = registry.forInterface(
            IFilterSchema, prefix="plone")
        self.settings.valid_tags.append('script')
        self.settings.nasty_tags.remove('script')
        self.pt = self.portal.portal_transforms

    def tearDown(self):
        self.settings.nasty_tags.append('script')
        self.settings.valid_tags.remove('script')

    def test_entities_outside_script(self):
        orig = "<code>a > 0 && b < 1</code>"
        escaped = '<code>a &gt; 0 &amp;&amp; b &lt; 1</code>'
        data = self.pt.convertTo(target_mimetype='text/x-html-safe', orig=orig)
        self.assertEqual(data.getData(), escaped)

    def test_script_and_entities_and_unicode(self):
        all = (''
               # script with not converted entity
               '<script type="text/javascript">$("h1 > ul").hide();</script>',
               # script with not converted entity and unicode
               '<script type="text/javascript">'
               '$("h1 > ul").attr("alt", "Officiële");</script>',
               # script
               '<script type="text/javascript">var el = "test";</script>',
               # entity
               '<p>(KU&nbsp;Loket)</p>',
               # unicode
               '<p>Officiële inschrijvingen </p>',
               )
        for tokens in itertools.product(all, repeat=5):
            orig = ''.join(tokens)
            data = self.pt.convertTo(
                target_mimetype='text/x-html-safe',
                orig=orig
            )
            self.assertEqual(
                unescape(data.getData()), orig.replace('&nbsp;', '\xc2\xa0'))

    def test_script_with_all_entities_and_unicode(self):
        orig = ('<p>Officiële inschrijvingen</p>',
                '<script type="text/javascript">'
                '$("h1 > ul").hide();'
                'entities = "&copy;";'
                '</script>',
                '<p>(KU&nbsp;Loket)</p>',
                )
        escd = ('<p>Officiële inschrijvingen</p>',
                '<script type="text/javascript">'
                '$("h1 > ul").hide();'
                'entities = "&copy;";'
                '</script>',
                '<p>(KU\xc2\xa0Loket)</p>',
                )

        all = zip(orig, escd)
        for tokens in itertools.product(all, repeat=4):
            orig_tokens, escaped_tokens = zip(*tokens)
            orig = ''.join(orig_tokens)
            escaped = ''.join(escaped_tokens)
            data = self.pt.convertTo(
                target_mimetype='text/x-html-safe',
                orig=orig
            )

            self.assertEqual(unescape(data.getData()), escaped)


class WordTransformsTest(unittest.TestCase):
    layer = PRODUCTS_PORTALTRANSFORMS_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        self.request = self.layer['request']
        self.pt = self.portal.portal_transforms
        registry = getUtility(IRegistry)
        self.settings = registry.forInterface(
            IFilterSchema, prefix="plone")

    def test_ignore_javascript_attrs(self):
        wordFile = open(input_file_path('test_js.doc'), 'rb')
        data = wordFile.read()
        # should not throw exception even though it holds javascript link
        self.pt.convertTo(target_mimetype='text/html', orig=data)


class ParsersTestCase(unittest.TestCase):
    layer = PRODUCTS_PORTALTRANSFORMS_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        self.request = self.layer['request']
        self.pt = self.portal.portal_transforms
        registry = getUtility(IRegistry)
        self.settings = registry.forInterface(
            IFilterSchema, prefix="plone")

    def test_javascript_on_attr(self):
        htmlFile = open(input_file_path('test_js_on.html'), 'rb')
        data = htmlFile.read()
        result = scrubHTMLNoRaise(data)
        self.assertTrue('link' in result)

    def test_javascript_uri(self):
        htmlFile = open(input_file_path('test_js_uri.html'), 'rb')
        data = htmlFile.read()
        result = scrubHTMLNoRaise(data)
        self.assertTrue('link' in result)

    def test_invalid_tags(self):
        htmlFile = open(input_file_path('test_invalid_tags.html'), 'rb')
        data = htmlFile.read()
        self.assertEqual(scrubHTMLNoRaise(data).strip(), '')


TRANSFORMS_TESTINFO = (
    ('Products.PortalTransforms.transforms.pdf_to_html',
     "demo1.pdf", "demo1.html", normalize_html, 0,
     ),
    ('Products.PortalTransforms.transforms.word_to_html',
     "test.doc", "test_word.html", normalize_html, 0,
     ),
    ('Products.PortalTransforms.transforms.lynx_dump',
     "test_lynx.html", "test_lynx.txt", None, 0,
     ),
    ('Products.PortalTransforms.transforms.html_to_text',
     "test_lynx.html", "test_html_to_text.txt", None, 0,
     ),
    ('Products.PortalTransforms.transforms.identity',
     "rest1.rst", "rest1.rst", None, 0,
     ),
    ('Products.PortalTransforms.transforms.text_to_html',
     "rest1.rst", "rest1.html", None, 0,
     ),
    ('Products.PortalTransforms.transforms.safe_html',
     "test_safehtml.html", "test_safe.html", None, 0,
     ),
    ('Products.PortalTransforms.transforms.image_to_bmp',
     "logo.jpg", "logo.bmp", None, 0,
     ),
    ('Products.PortalTransforms.transforms.image_to_gif',
     "logo.bmp", "logo.gif", None, 0,
     ),
    ('Products.PortalTransforms.transforms.image_to_jpeg',
     "logo.gif", "logo.jpg", None, 0,
     ),
    ('Products.PortalTransforms.transforms.image_to_png',
     "logo.bmp", "logo.png", None, 0,
     ),
    ('Products.PortalTransforms.transforms.image_to_ppm',
     "logo.gif", "logo.ppm", None, 0,
     ),
    ('Products.PortalTransforms.transforms.image_to_tiff',
     "logo.png", "logo.tiff", None, 0,
     ),
    ('Products.PortalTransforms.transforms.image_to_pcx',
     "logo.png", "logo.pcx", None, 0,
     ),
)
if HAS_MARKDOWN:
    TRANSFORMS_TESTINFO = TRANSFORMS_TESTINFO + (
        ('Products.PortalTransforms.transforms.markdown_to_html',
         "markdown.txt", "markdown.html", None, 0,
         ),
    )
if HAS_TEXTILE:
    TRANSFORMS_TESTINFO = TRANSFORMS_TESTINFO + (
        ('Products.PortalTransforms.transforms.textile_to_html',
         "input.textile", "textile.html", None, 0,
         ),
    )


def initialise(transform, normalize, pattern):
    global TRANSFORMS_TESTINFO
    for fname in matching_inputs(pattern):
        outname = '%s.out' % fname.split('.')[0]
        TRANSFORMS_TESTINFO += ((transform, fname, outname, normalize, 0),)


# ReST test cases
initialise('Products.PortalTransforms.transforms.rest', normalize_html,
           "rest*.rst")
# Python test cases
initialise('Products.PortalTransforms.transforms.python', normalize_html,
           "*.py")

# FIXME missing tests for image_to_html, st

TR_NAMES = None


def make_tests(test_descr=TRANSFORMS_TESTINFO):
    """generate tests classes from test info

    return the list of generated test classes
    """
    tests = []
    for _transform, tr_input, tr_output, _normalize, _subobjects in test_descr:
        # load transform if necessary
        if isinstance(_transform, type('')):
            try:
                _transform = load(_transform).register()
            except MissingBinary:
                # we are not interessted in tests with missing binaries
                continue
            except Exception:
                import traceback
                traceback.print_exc()
                continue

        if TR_NAMES is not None and not _transform.name() in TR_NAMES:
            print('skip test for {0}'.format(_transform.name()))
            continue

        class TransformTestSubclass(TransformTest):
            input = input_file_path(tr_input)
            output = output_file_path(tr_output)
            transform = _transform
            normalize = lambda x, y: _normalize(y)  # noqa
            subobjects = _subobjects

        tests.append(TransformTestSubclass)

    tests.append(PILTransformsTest)
    tests.append(SafeHtmlTransformsTest)
    tests.append(SafeHtmlTransformsWithScriptTest)
    tests.append(WordTransformsTest)
    tests.append(ParsersTestCase)
    return tests


def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    for test in make_tests():
        suite.addTest(makeSuite(test))
    return suite
