# -*- coding: utf-8 -*-
import six
import unittest

from Products.CMFPlone.interfaces import IFilterSchema
from Products.PortalTransforms.testing import PRODUCTS_PORTALTRANSFORMS_INTEGRATION_TESTING  # noqa
from Products.PortalTransforms.tests.utils import html5entity
from plone.registry.interfaces import IRegistry
from zope.component import getUtility


class TestXSSFilter(unittest.TestCase):
    layer = PRODUCTS_PORTALTRANSFORMS_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        self.request = self.layer['request']
        self.pt = self.portal.portal_transforms
        registry = getUtility(IRegistry)
        self.settings = registry.forInterface(
            IFilterSchema, prefix="plone")
        self.settings.custom_attributes.append('style')

    def tearDown(self):
        self.settings.custom_attributes.remove('style')

    def doTest(self, data_in, data_out):  # noqa
        html = self.pt.convertTo(
            'text/x-html-safe', data_in, mimetype="text/html")
        self.assertEqual(data_out, html.getData())

    def test_1(self):
        data_in = """<html><body><img src="javascript:Alert('XSS');" /></body></html>"""  # noqa
        data_out = '<img/>'
        self.doTest(data_in, data_out)

    def test_2(self):
        data_in = """<img src="javascript:Alert('XSS');" />"""
        data_out = '<img/>'
        self.doTest(data_in, data_out)

    def test_3(self):
        data_in = """<html><body><IMG SRC=&#106;&#97;&#118;&#97;&#115;&#99;&#114;&#105;&#112;&#116;&#58;&#97;&#108;&#101;&#114;&#116;&#40;&#39;&#88;&#83;&#83;&#39;&#41;></body></html>"""  # noqa
        data_out = '<img/>'
        self.doTest(data_in, data_out)

    def test_4(self):
        data_in = """<IMG SRC=&#106;&#97;&#118;&#97;&#115;&#99;&#114;&#105;&#112;&#116;&#58;&#97;&#108;&#101;&#114;&#116;&#40;&#39;&#88;&#83;&#83;&#39;&#41;>"""  # noqa
        data_out = '<img/>'

        self.doTest(data_in, data_out)

    def test_5(self):
        data_in = """<img src="jav
        asc
        ript:Alert('XSS');" />"""
        data_out = '<img/>'
        self.doTest(data_in, data_out)

    def test_6(self):
        data_in = """<img src="jav asc ript:Alert('XSS');"/>"""
        data_out = '<img/>'
        self.doTest(data_in, data_out)

    def test_7(self):
        data_in = """<a href=&#106;&#97;&#118;&#97;&#115;&#99;&#114;&#105;&#112;&#116;&#58;&#97;&#108;&#101;&#114;&#116;&#40;&#39;&#88;&#83;&#83;&#39;&#41;>test med a-tag</a>"""  # noqa
        data_out = """<a>test med a-tag</a>"""
        self.doTest(data_in, data_out)

    def test_8(self):
        data_in = """<div style="bacground:url(jav asc ript:Alert('XSS')">test</div>"""  # noqa
        data_out = """<div>test</div>"""
        self.doTest(data_in, data_out)

    def test_9(self):
        data_in = """<div style="bacground:url(jav
        asc
        ript:
        Alert('XSS')">test</div>"""
        data_out = """<div>test</div>"""
        self.doTest(data_in, data_out)

    def test_10(self):
        data_in = """<div style="bacground:url(&#106;&#97;&#118;&#97;&#115;&#99;&#114;&#105;&#112;&#116;&#58;&#97;&#108;&#101;&#114;&#116;&#40;&#39;&#88;&#83;&#83;&#39;&#41;">test</div>"""  # noqa
        data_out = """<div>test</div>"""
        self.doTest(data_in, data_out)

    def test_11(self):
        data_in = """<div style="bacground:url(v b  sc  ript:msgbox('XSS')">test</div>"""  # noqa
        data_out = '<div>test</div>'
        self.doTest(data_in, data_out)

    def test_12(self):
        data_in = """<img src="vbscript:msgbox('XSS')"/>"""
        data_out = '<img/>'
        self.doTest(data_in, data_out)

    def test_13(self):
        data_in = """<img src="vb
        sc
        ript:msgbox('XSS')"/>"""
        data_out = '<img/>'
        self.doTest(data_in, data_out)

    def test_14(self):
        data_in = """<a href="vbscript:Alert('XSS')">test</a>"""
        data_out = '<a>test</a>'
        self.doTest(data_in, data_out)

    def test_15(self):
        data_in = """<div STYLE="width: expression(window.location='http://www.dr.dk';);">div</div>"""  # noqa
        data_out = '<div>div</div>'
        self.doTest(data_in, data_out)

    def test_16(self):
        data_in = """<div STYLE="width: ex pre ss   io n(window.location='http://www.dr.dk';);">div</div>"""  # noqa
        data_out = """<div>div</div>"""
        self.doTest(data_in, data_out)

    def test_17(self):
        data_in = """<div STYLE="width: ex
        pre
        ss
        io
        n(window.location='http://www.dr.dk';);">div</div>"""
        data_out = """<div>div</div>"""
        self.doTest(data_in, data_out)

    def test_18(self):
        data_in = """<div style="width: 14px;">div</div>"""
        data_out = data_in
        self.doTest(data_in, data_out)

    def test_19(self):
        data_in = """<a href="http://www.headnet.dk">headnet</a>"""
        data_out = data_in
        self.doTest(data_in, data_out)

    def test_20(self):
        data_in = '<img src="http://www.headnet.dk/log.jpg"/>'
        data_out = data_in
        self.doTest(data_in, data_out)

    def test_21(self):
        data_in = """<mustapha name="mustap" tlf="11 11 11 11" address="unknown">bla bla bla</mustapha>"""  # noqa
        data_out = 'bla bla bla'
        self.doTest(data_in, data_out)

    def test_22(self):
        data_in = '<<frame></frame>script>alert("XSS");<<frame></frame>/script>'  # noqa
        data_out = '&lt;script&gt;alert("XSS");&lt;/script&gt;'
        self.doTest(data_in, data_out)

    def test_23(self):
        data_in = """<a href="javascript&amp;#0:alert('1');">click me</a>"""
        data_out = '<a>click me</a>'
        self.doTest(data_in, data_out)

    def test_24(self):
        data_in = """<a href="data:text/html;base64,PHNjcmlwdD5hbGVydCgidGVzdCIpOzwvc2NyaXB0Pg==">click me</a>"""  # noqa
        data_out = '<a>click me</a>'
        self.doTest(data_in, data_out)

    def test_25(self):
        data_in = """<![<a href="javascript:alert('1');">click me</a>"""
        data_out = 'click me'
        self.doTest(data_in, data_out)

    def test_26(self):
        data_in = """<a style="width: expression/**/(alert('xss'))">click me</a>"""  # noqa
        data_out = """<a>click me</a>"""
        self.doTest(data_in, data_out)

    def test_27(self):
        data_in = """<a href=javascript&colon;alert(1)>click me</a>"""
        data_out = '<a>click me</a>'
        self.doTest(data_in, data_out)

    def test_28(self):
        data_in = """<a x="d&#00065;ta&colon&#59;image/svg+xml;charset=utf-8;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciPjxzY3JpcHQ%2BYWxlcnQoMSk8L3NjcmlwdD48L3N2Zz4NCg==" style="-o-link:attr(x);-o-link-source:current">hey</a>"""  # noqa
        data_out = """<a style="-o-link:attr(x);-o-link-source:current">hey</a>"""  # noqa
        self.doTest(data_in, data_out)

    def test_29(self):
        data_in = """<meta name="Description" content="0;url=data&colon;,xss" HTTP-EQUIV="refresh">"""  # noqa
        data_out = ''
        self.doTest(data_in, data_out)

    def test_30(self):
        data_in = """<meta name="Description" content="0;url=javascript&colon;alert(1)" HTTP-EQUIV="refresh">"""  # noqa
        data_out = ''
        self.doTest(data_in, data_out)

    def test_31(self):
        data_in = r"""<div style="width: expression\28write(1)\29;">aasddsa</div>"""  # noqa
        data_out = '<div>aasddsa</div>'
        self.doTest(data_in, data_out)

    def test_32(self):
        data_in = r"""<div style="width: expr\65 ss/*???*/ion(URL=0);">hey</div>"""  # noqa
        data_out = '<div>hey</div>'
        self.doTest(data_in, data_out)

    def test_33(self):
        data_in = r"""<a href="java&Tab;scr&NewLine;ipt:alert(1)">asd</a>"""
        data_out = '<a>asd</a>'
        self.doTest(data_in, data_out)

    def test_34(self):
        data_in = r"""<a href="javasc&baz;ript:alert(1)">asdf</a>"""
        data_out = '<a>asdf</a>'
        self.doTest(data_in, data_out)

    def test_35(self):
        data_in = r"""<![CDATA[><script>alert(1);</script>]]>"""
        data_out = ']]&gt;'
        self.doTest(data_in, data_out)

    def test_36(self):
        data_in = r"""Normal text&mdash;whew."""
        data_out = 'Normal text{}whew.'.format(html5entity('mdash;'))
        self.doTest(data_in, data_out)

    def test_37(self):
        data_in = r"""Normal text&amp;mdash;whew."""
        data_out = 'Normal text&amp;mdash;whew.'
        self.doTest(data_in, data_out)

    def test_38(self):
        data_in = """<p><a href="http://T\\foo\\20111015\\bar.msg">FOO</a></p>"""  # noqa
        self.doTest(data_in, data_in)

    def test_39(self):
        data_in = """<a href="&#42;&Ascr;\xa9"></a>"""
        data_out = '<a href="*&amp;Ascr;&#xA9;"/>'
        self.doTest(data_in, data_out)
