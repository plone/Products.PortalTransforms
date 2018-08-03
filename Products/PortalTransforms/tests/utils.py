# -*- coding: utf-8 -*-
from Products.CMFPlone.utils import safe_unicode
from Products.PortalTransforms.transforms.safe_html import html5entities
from os.path import abspath
from os.path import basename
from os.path import dirname
from os.path import join
from sys import modules
from unittest import TestSuite

import glob
import re
import six


def normalize_html(s):
    if six.PY3 and isinstance(s, six.binary_type):
        s = safe_unicode(s)
    s = re.sub(r"&nbsp;", " ", s)
    s = re.sub(r"&#160;", " ", s)
    s = re.sub(r"\s+", " ", s)
    s = re.sub(r"(?s)\s+<", "<", s)
    s = re.sub(r"(?s)>\s+", ">", s)
    s = re.sub(r"\r", "", s)
    s = re.sub(r"<A", "<a", s)
    return s


def html5entity(ent):
    mapped_ent = html5entities[ent]
    if six.PY2:
        mapped_ent = mapped_ent.encode('utf-8')
    return mapped_ent


def build_test_suite(package_name, module_names, required=1):
    """
    Utlitity for building a test suite from a package name
    and a list of modules.

    If required is false, then ImportErrors will simply result
    in that module's tests not being added to the returned
    suite.
    """

    suite = TestSuite()
    try:
        for name in module_names:
            the_name = package_name + '.' + name
            __import__(the_name, globals(), locals())
            suite.addTest(modules[the_name].test_suite())
    except ImportError:
        if required:
            raise
    return suite


PREFIX = abspath(dirname(__file__))


def input_file_path(file):
    return join(PREFIX, 'input', file)


def output_file_path(file):
    return join(PREFIX, 'output', file)


def read_file_data(path, mode='rb'):
    data = None
    with open(path, mode) as fd:
        data = fd.read()
    return data


def matching_inputs(pattern):
    return [basename(path) for path in
            glob.glob(join(PREFIX, "input", pattern))]


def load(dotted_name, globals=None):
    """ load a python module from it's name """
    mod = __import__(dotted_name, globals)
    components = dotted_name.split('.')
    for comp in components[1:]:
        mod = getattr(mod, comp)
    return mod
