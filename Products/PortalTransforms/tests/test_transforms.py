# -*- coding: utf8  -*-
from __future__ import print_function
from copy import deepcopy
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.interfaces import IFilterSchema
from Products.PortalTransforms.data import datastream
from Products.PortalTransforms.interfaces import IDataStream
from Products.PortalTransforms.libtransforms.utils import MissingBinary
from Products.PortalTransforms.tests.base import TransformTestCase
from Products.PortalTransforms.tests.utils import html5entity
from Products.PortalTransforms.tests.utils import input_file_path
from Products.PortalTransforms.tests.utils import load
from Products.PortalTransforms.tests.utils import matching_inputs
from Products.PortalTransforms.tests.utils import normalize_html
from Products.PortalTransforms.tests.utils import output_file_path
from Products.PortalTransforms.tests.utils import read_file_data
from Products.PortalTransforms.transforms.image_to_bmp import image_to_bmp
from Products.PortalTransforms.transforms.image_to_gif import image_to_gif
from Products.PortalTransforms.transforms.image_to_jpeg import image_to_jpeg
from Products.PortalTransforms.transforms.image_to_pcx import image_to_pcx
from Products.PortalTransforms.transforms.image_to_png import image_to_png
from Products.PortalTransforms.transforms.image_to_ppm import image_to_ppm
from Products.PortalTransforms.transforms.image_to_tiff import image_to_tiff
from Products.PortalTransforms.transforms.markdown_to_html import HAS_MARKDOWN
from Products.PortalTransforms.transforms.safe_html import SafeHTML
from Products.PortalTransforms.transforms.textile_to_html import HAS_TEXTILE
from os.path import exists
from plone.registry.interfaces import IRegistry
from xml.sax.saxutils import unescape
from zope.component import getUtility

import hashlib
import itertools
import os
import six
import unittest


# we have to set locale because lynx output is locale sensitive !
os.environ['LC_ALL'] = 'C'


class TransformTest(TransformTestCase):

    allowed_types = str

    def setUp(self):
        super(TransformTest, self).setUp()
        self.request = self.layer['request']
        registry = getUtility(IRegistry)
        self.settings = registry.forInterface(IFilterSchema, prefix="plone")

    def md5(self, fname):
        hash_md5 = hashlib.md5()
        with open(fname, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
        return hash_md5.hexdigest()

    def do_convert(self, filename=None):
        if filename is None and exists(self.output + '.nofilename'):
            output = self.output + '.nofilename'
        else:
            output = self.output
        orig = read_file_data(self.input)
        data = datastream(self.transform.name())
        res_data = self.transform.convert(orig, data, filename=filename)
        self.assertTrue(IDataStream.providedBy(res_data))
        got = res_data.getData()

        self.assertIsInstance(got, self.allowed_types)
        try:
            expected = read_file_data(self.output)
        except IOError:
            expected = ''
            import sys
            print('No output file found.', file=sys.stderr)
            print(
                'File {0} created, check it !'.format(self.output),
                file=sys.stderr)
            with open(output, 'w') as fd:
                fd.write(got)
            self.assertTrue(0)

        if self.normalize is not None:
            got = self.normalize(got)
            expected = self.normalize(expected)

        # show the first character ord table for debugging
        got_start = got.strip()[:20]
        expected_start = expected.strip()[:20]
        msg = 'IN {0}({1}) expected:\n{2}\nbut got:\n{3}'.format(
            self.transform.name(),
            self.input,
            "%s %s" % (expected_start, str([ord(x) for x in expected_start])),
            "%s %s" % (got_start, str([ord(x) for x in got_start])),
        )

        # compare md5 sum of the whole file content
        self.assertEqual(
            got_start,
            expected_start,
            msg,
        )
        self.assertEqual(
            self.subobjects,
            len(res_data.getSubObjects()),
            '%s\n\n!=\n\n%s\n\nIN %s(%s)' % (
                self.subobjects,
                len(res_data.getSubObjects()),
                self.transform.name(),
                self.input,
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


class PILTransformsTest(TransformTestCase):

    def setUp(self):
        super(PILTransformsTest, self).setUp()
        self.request = self.layer['request']
        self.mimetypes_registry = getToolByName(self.portal,
                                                'mimetypes_registry')

    def guess_mimetype(self, data):
        return str(self.mimetypes_registry.classify(data))

    def assert_image_transformed(self, factory, filename, input_mimetype, target_mimetype):
        self.transforms.registerTransform(factory)
        data = read_file_data(input_file_path(filename))
        self.assertEqual(self.guess_mimetype(data), input_mimetype)
        data = self.transforms.convertTo(target_mimetype=target_mimetype, orig=data)
        self.assertEqual(data.getMetadata()['mimetype'], target_mimetype)

    def test_image_to_bmp(self):
        self.assert_image_transformed(
            image_to_bmp(), 'logo.jpg', 'image/jpeg', 'image/x-ms-bmp')

    def test_image_to_gif(self):
        self.assert_image_transformed(
            image_to_gif(), 'logo.png', 'image/png', 'image/gif')

    def test_image_to_jpeg(self):
        self.assert_image_transformed(
            image_to_jpeg(), 'logo.gif', 'image/gif', 'image/jpeg')

    def test_image_to_png(self):
        self.assert_image_transformed(
            image_to_png(), 'logo.jpg', 'image/jpeg', 'image/png')

    def test_image_to_pcx(self):
        self.assert_image_transformed(
            image_to_pcx(), 'logo.gif', 'image/gif', 'image/pcx')

    def test_image_to_ppm(self):
        self.assert_image_transformed(
            image_to_ppm(), 'logo.png', 'image/png', 'image/x-portable-pixmap')

    def test_image_to_tiff(self):
        self.assert_image_transformed(
            image_to_tiff(), 'logo.jpg', 'image/jpeg', 'image/tiff')


class SafeHtmlTransformsTest(TransformTestCase):

    def setUp(self):
        super(SafeHtmlTransformsTest, self).setUp()
        self.request = self.layer['request']
        registry = getUtility(IRegistry)
        self.settings = registry.forInterface(
            IFilterSchema, prefix="plone")
        self.orig_valid_tags = deepcopy(self.settings.valid_tags)
        self.orig_nasty_tags = deepcopy(self.settings.nasty_tags)
        self.settings.valid_tags.append(u'style')
        self.settings.valid_tags.remove(u'h1')
        self.settings.nasty_tags.append(u'h1')

    def tearDown(self):
        self.settings.valid_tags = self.orig_valid_tags
        self.settings.nasty_tags = self.orig_nasty_tags

    def test_kill_nasty_tags_which_are_not_valid(self):
        self.assertTrue('script' in self.settings.nasty_tags)
        self.assertFalse('script' in self.settings.valid_tags)
        orig = '<p><script>foo</script></p>'
        data_out = '<p></p>'
        data = self.transforms.convertTo(target_mimetype='text/x-html-safe', orig=orig)
        got = data.getData()
        self.assertIsInstance(got, self.allowed_types)
        self.assertEqual(got, data_out)

        self.assertTrue('h1' in self.settings.nasty_tags)
        self.assertFalse('h1' in self.settings.valid_tags)
        orig = '<p><h1>foo</h1></p>'
        data_out = '<p></p>'
        data = self.transforms.convertTo(target_mimetype='text/x-html-safe', orig=orig)
        got = data.getData()
        self.assertIsInstance(got, self.allowed_types)
        self.assertEqual(got, data_out)

    def test_entityiref_attributes(self):
        orig = '<a href="&uuml;">foo</a>'
        data_out = '<a href="%C3%BC">foo</a>'
        data = self.transforms.convertTo(target_mimetype='text/x-html-safe', orig=orig)
        got = data.getData()
        self.assertIsInstance(got, self.allowed_types)
        self.assertEqual(got, data_out)

    def test_charref_attributes(self):
        orig = '<a href="&#0109;">foo</a>'
        data_out = '<a href="m">foo</a>'
        data = self.transforms.convertTo(target_mimetype='text/x-html-safe', orig=orig)
        got = data.getData()
        self.assertIsInstance(got, self.allowed_types)
        self.assertEqual(got, data_out)

    def test_entityiref_data(self):
        orig = '<p>foo &uuml; bar</p>'
        data_out = '<p>foo {} bar</p>'.format(html5entity('uuml;'))
        data = self.transforms.convertTo(target_mimetype='text/x-html-safe', orig=orig)
        got = data.getData()
        self.assertIsInstance(got, self.allowed_types)
        self.assertEqual(got, data_out)

    def test_charref_data(self):
        orig = '<p>bar &#0109; foo</p>'
        data_out = '<p>bar m foo</p>'
        data = self.transforms.convertTo(target_mimetype='text/x-html-safe', orig=orig)
        got = data.getData()
        self.assertIsInstance(got, self.allowed_types)
        self.assertEqual(got, data_out)

    def test_do_not_autoclose_tags(self):
        orig = '<p></p>'
        data_out = '<p></p>'
        data = self.transforms.convertTo(target_mimetype='text/x-html-safe', orig=orig)
        got = data.getData()
        self.assertEqual(got, data_out)


class SafeHtmlTransformsWithScriptTest(TransformTestCase):

    def setUp(self):
        super(SafeHtmlTransformsWithScriptTest, self).setUp()
        self.request = self.layer['request']
        registry = getUtility(IRegistry)
        self.settings = registry.forInterface(
            IFilterSchema, prefix="plone")
        self.orig_valid_tags = deepcopy(self.settings.valid_tags)
        self.orig_nasty_tags = deepcopy(self.settings.nasty_tags)
        self.settings.valid_tags.append(u'script')
        self.settings.nasty_tags.remove(u'script')

    def tearDown(self):
        self.settings.valid_tags = self.orig_valid_tags
        self.settings.nasty_tags = self.orig_nasty_tags

    def test_entities_outside_script(self):
        orig = "<code>a > 0 && b < 1</code>"
        escaped = '<code>a &gt; 0 &amp;&amp; b &lt; 1</code>'
        data = self.transforms.convertTo(target_mimetype='text/x-html-safe', orig=orig)
        got = data.getData()
        self.assertIsInstance(got, self.allowed_types)
        self.assertEqual(got, escaped)

    def test_script_and_entities_and_unicode(self):
        _all = (
           ''
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
        nbsp = html5entity('nbsp;')
        for tokens in itertools.product(_all, repeat=5):
            orig = ''.join(tokens)
            data = self.transforms.convertTo(
                target_mimetype='text/x-html-safe',
                orig=orig
            )
            got = data.getData()
            self.assertIsInstance(got, self.allowed_types)
            self.assertEqual(
                unescape(got),
                orig.replace('&nbsp;', nbsp))

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
                '<p>(KU{}Loket)</p>'.format(html5entity('nbsp;')),
                )

        _all = six.moves.zip(orig, escd)
        for tokens in itertools.product(_all, repeat=4):
            orig_tokens, escaped_tokens = zip(*tokens)
            orig = ''.join(orig_tokens)
            escaped = ''.join(escaped_tokens)
            data = self.transforms.convertTo(
                target_mimetype='text/x-html-safe',
                orig=orig
            )
            got = data.getData()
            self.assertIsInstance(got, self.allowed_types)
            self.assertEqual(unescape(got), escaped)


class SafeHtmlTransformsWithFormTest(TransformTestCase):

    def setUp(self):
        super(SafeHtmlTransformsWithFormTest, self).setUp()
        self.request = self.layer['request']
        registry = getUtility(IRegistry)
        self.settings = registry.forInterface(
            IFilterSchema, prefix="plone")
        self.orig_valid_tags = deepcopy(self.settings.valid_tags)

    def tearDown(self):
        # If this gives a WrongContainedType because some of the tags are
        # strings instead of the expected unicode,
        # then some other test is adding strings and not cleaning up.
        # Note that with valid_tags.append no validation is done,
        # but only when realling setting valid_tags.
        self.settings.valid_tags = self.orig_valid_tags

    def test_form_tag_removed(self):
        orig = "<form><label>Hello</label></form>"
        expected = "Hello"
        data = self.transforms.convertTo(target_mimetype='text/x-html-safe', orig=orig)
        got = data.getData()
        self.assertIsInstance(got, self.allowed_types)
        self.assertEqual(got, expected)

    def test_form_tag_kept(self):
        # Allow form tag
        self.settings.valid_tags.append(u'form')
        orig = "<form><label>Hello</label></form>"
        expected = "<form>Hello</form>"
        data = self.transforms.convertTo(target_mimetype='text/x-html-safe', orig=orig)
        got = data.getData()
        self.assertIsInstance(got, self.allowed_types)
        self.assertEqual(got, expected)

    def test_form_with_input_removed(self):
        orig = (
            '<form>'
            '<label>Hello</label> '
            '<button name="but">Click here</button> '
            '<input type="text" value="hi"/> '
            '<select name="sel"><option value="1">One</option></select> '
            '<textarea name="text">Stuff</textarea>'
            '</form>')
        # Originally, up to and including version 3.1.5, 'Hello    ' was kept.
        # Now, with cleaner.forms = False, more text is kept:
        expected = "Hello Click here  One Stuff"
        data = self.transforms.convertTo(target_mimetype='text/x-html-safe', orig=orig)
        got = data.getData()
        self.assertIsInstance(got, self.allowed_types)
        self.assertEqual(got, expected)

    def test_form_with_input_kept(self):
        # Allow various form related tags
        self.settings.valid_tags.extend(
            'form button input select textarea option label'.split()
        )
        orig = (
            '<form>'
            '<label>Hello</label> '
            '<button name="but">Click here</button> '
            '<input type="text" value="hi"> '
            '<select name="sel"><option value="1">One</option></select> '
            '<textarea name="text">Stuff</textarea>'
            '</form>')
        data = self.transforms.convertTo(target_mimetype='text/x-html-safe', orig=orig)
        got = data.getData()
        self.assertIsInstance(got, self.allowed_types)
        self.assertEqual(got, orig)

    def test_label_tag_removed(self):
        orig = "<form><label>Hello</label></form>"
        expected = "Hello"
        data = self.transforms.convertTo(target_mimetype='text/x-html-safe', orig=orig)
        got = data.getData()
        self.assertIsInstance(got, self.allowed_types)
        self.assertEqual(got, expected)

    def test_label_tag_kept(self):
        # Allow label tag
        self.settings.valid_tags.append(u'label')
        orig = "<form><label>Hello</label></form>"
        expected = "<label>Hello</label>"
        data = self.transforms.convertTo(target_mimetype='text/x-html-safe', orig=orig)
        got = data.getData()
        self.assertIsInstance(got, self.allowed_types)
        self.assertEqual(got, expected)


class WordTransformsTest(TransformTestCase):

    def setUp(self):
        super(WordTransformsTest, self).setUp()
        self.request = self.layer['request']
        registry = getUtility(IRegistry)
        self.settings = registry.forInterface(
            IFilterSchema, prefix="plone")

    def test_ignore_javascript_attrs(self):
        data = read_file_data(input_file_path('test_js.doc'))
        # should not throw exception even though it holds javascript link
        self.transforms.convertTo(target_mimetype='text/html', orig=data)


class ParsersTestCase(TransformTestCase):

    def setUp(self):
        super(ParsersTestCase, self).setUp()
        self.request = self.layer['request']
        registry = getUtility(IRegistry)
        self.settings = registry.forInterface(
            IFilterSchema, prefix="plone")

    def test_javascript_on_attr(self):
        data = read_file_data(input_file_path('test_js_on.html'))
        result = SafeHTML().scrub_html(data)
        self.assertTrue('link' in result)

    def test_javascript_uri(self):
        data = read_file_data(input_file_path('test_js_uri.html'))
        result = SafeHTML().scrub_html(data)
        self.assertTrue('link' in result)

    def test_invalid_tags(self):
        data = read_file_data(input_file_path('test_invalid_tags.html'))
        self.assertEqual(SafeHTML().scrub_html(data).strip(), '')


class RestTransformsTest(unittest.TestCase):

    def test_rest_convert(self):
        # from PloneHotfix20210518
        from Products.PortalTransforms.data import datastream
        from Products.PortalTransforms.transforms.rest import rest

        # Try to convert ReStructuredText resulting in a warning.
        orig = "Hello *world"
        data = datastream("foo")
        transform = rest()
        # With the warnings parameter you could write to the filesystem.
        # With the stylesheet parameter you could read from the filesystem.
        # https://sourceforge.net/p/docutils/bugs/413/
        here = os.path.dirname(__file__)
        warnings_file = os.path.join(here, "write.txt")
        css_file = os.path.join(here, "read.css")
        read_contents = "Arbitrary file read from OS."
        with open(css_file, "w") as css:
            css.write(read_contents)
        bad_keyword_arguments = {
            "warnings": warnings_file,
            "stylesheet": css_file,
        }
        try:
            result = transform.convert(orig, data, **bad_keyword_arguments)
            output = result.getData()
            # There should be a warning for the wrong ReStructuredText.
            self.assertIn("WARNING", output)
            # The contents of the css file should not be in the result.
            self.assertNotIn(read_contents, output)
            self.assertNotIn(css_file, output)
            # No file should have been written to the system.
            self.assertFalse(os.path.exists(warnings_file))
        finally:
            # cleanup
            if os.path.exists(warnings_file):
                os.remove(warnings_file)
            if os.path.exists(css_file):
                os.remove(css_file)


TRANSFORMS_TESTINFO = (
    ('Products.PortalTransforms.transforms.pdf_to_html',
     "demo1.pdf", "demo1.html", normalize_html, 0, str,
     ),
    ('Products.PortalTransforms.transforms.word_to_html',
     "test.doc", "test_word.html", normalize_html, 0, str,
     ),
    ('Products.PortalTransforms.transforms.lynx_dump',
     "test_lynx.html", "test_lynx.txt", None, 0, str,
     ),
    ('Products.PortalTransforms.transforms.html_to_text',
     "test_lynx.html", "test_html_to_text.txt", None, 0, str,
     ),
    ('Products.PortalTransforms.transforms.identity',
     "rest1.rst", "rest1.rst", None, 0, (six.binary_type, six.text_type),
     ),
    ('Products.PortalTransforms.transforms.text_to_html',
     "rest1.rst", "rest1.html", None, 0, str,
     ),
    ('Products.PortalTransforms.transforms.safe_html',
     "test_safehtml.html", "test_safe.html", None, 0, str,
     ),
    ('Products.PortalTransforms.transforms.image_to_bmp',
     "logo.jpg", "logo.bmp", None, 0, six.binary_type,
     ),
    ('Products.PortalTransforms.transforms.image_to_gif',
     "logo.bmp", "logo.gif", None, 0, six.binary_type,
     ),
    ('Products.PortalTransforms.transforms.image_to_jpeg',
     "logo.gif", "logo.jpg", None, 0, six.binary_type,
     ),
    ('Products.PortalTransforms.transforms.image_to_png',
     "logo.bmp", "logo.png", None, 0, six.binary_type,
     ),
    ('Products.PortalTransforms.transforms.image_to_ppm',
     "logo.gif", "logo.ppm", None, 0, six.binary_type,
     ),
    ('Products.PortalTransforms.transforms.image_to_tiff',
     "logo.png", "logo.tiff", None, 0, six.binary_type,
     ),
    ('Products.PortalTransforms.transforms.image_to_pcx',
     "logo.png", "logo.pcx", None, 0, six.binary_type,
     ),
)
if HAS_MARKDOWN:
    TRANSFORMS_TESTINFO = TRANSFORMS_TESTINFO + (
        ('Products.PortalTransforms.transforms.markdown_to_html',
         "markdown.txt", "markdown.html", None, 0, str,
         ),
    )
if HAS_TEXTILE:
    TRANSFORMS_TESTINFO = TRANSFORMS_TESTINFO + (
        ('Products.PortalTransforms.transforms.textile_to_html',
         "input.textile", "textile.html", None, 0, str,
         ),
    )


def initialise(transform, normalize, pattern):
    global TRANSFORMS_TESTINFO
    for fname in matching_inputs(pattern):
        outname = '%s.out' % fname.split('.')[0]
        TRANSFORMS_TESTINFO += (
            (transform, fname, outname, normalize, 0, str,),
        )


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
    for (
        _transform,
        tr_input,
        tr_output,
        _normalize,
        _subobjects,
        _allowed_types,
    ) in test_descr:
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
            allowed_types = _allowed_types
            input = input_file_path(tr_input)
            output = output_file_path(tr_output)
            transform = _transform
            normalize = lambda x, y: _normalize(y)  # noqa
            subobjects = _subobjects

        tests.append(TransformTestSubclass)

    tests.append(PILTransformsTest)
    tests.append(SafeHtmlTransformsTest)
    tests.append(SafeHtmlTransformsWithScriptTest)
    tests.append(SafeHtmlTransformsWithFormTest)
    tests.append(WordTransformsTest)
    tests.append(ParsersTestCase)
    tests.append(RestTransformsTest)
    return tests


def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    for test in make_tests():
        suite.addTest(makeSuite(test))
    return suite
