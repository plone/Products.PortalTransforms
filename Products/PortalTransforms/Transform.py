from AccessControl import ClassSecurityInfo
from AccessControl.class_init import InitializeClass
from collections import UserDict
from importlib import reload as reload_module
from logging import ERROR
from OFS.SimpleItem import SimpleItem
from Persistence import PersistentMapping
from persistent.list import PersistentList
from Products.CMFCore.permissions import ManagePortal
from Products.CMFCore.utils import getToolByName
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from Products.PortalTransforms.interfaces import ITransform
from Products.PortalTransforms.transforms.broken import BrokenTransform
from Products.PortalTransforms.utils import _www
from Products.PortalTransforms.utils import log
from Products.PortalTransforms.utils import TransformException
from zope.interface import implementer


def import_from_name(module_name):
    """import and return a module by its name"""
    __traceback_info__ = (module_name,)
    m = __import__(module_name)
    try:
        for sub in module_name.split(".")[1:]:
            m = getattr(m, sub)
    except AttributeError as e:
        raise ImportError(str(e))
    return m


def make_config_persistent(kwargs):
    """iterates on the given dictionary and replace list by persistent list,
    dictionary by persistent mapping.
    """
    for key, value in kwargs.items():
        if isinstance(value, type({})):
            p_value = PersistentMapping(value)
            kwargs[key] = p_value
        elif type(value) in (type(()), type([])):
            p_value = PersistentList(value)
            kwargs[key] = p_value


def make_config_nonpersistent(kwargs):
    """iterates on the given dictionary and replace ListClass by python List,
    and DictClass by python Dict
    """
    for key, value in kwargs.items():
        if isinstance(value, PersistentMapping):
            p_value = dict(value)
            kwargs[key] = p_value
        elif isinstance(value, PersistentList):
            p_value = list(value)
            kwargs[key] = p_value


VALIDATORS = {
    "int": int,
    "string": str,
    "list": PersistentList,
    "dict": PersistentMapping,
}


@implementer(ITransform)
class Transform(SimpleItem):
    """A transform is an external method with
    additional configuration information
    """

    meta_type = "Transform"
    meta_types = all_meta_types = ()

    manage_options = (
        {"label": "Configure", "action": "manage_main"},
        {"label": "Reload", "action": "manage_reloadTransform"},
    ) + SimpleItem.manage_options

    manage_main = PageTemplateFile("configureTransform", _www)
    manage_reloadTransform = PageTemplateFile("reloadTransform", _www)
    tr_widgets = PageTemplateFile("tr_widgets", _www)

    security = ClassSecurityInfo()
    __allow_access_to_unprotected_subobjects__ = 1

    def __init__(self, id, module, transform=None):
        self.id = id
        self.module = module
        # DM 2004-09-09: 'Transform' instances are stored as
        #  part of a module level configuration structure
        #  Therefore, they must not contain persistent objects
        self._config = UserDict()
        self._config.__allow_access_to_unprotected_subobjects__ = 1
        self._config_metadata = UserDict()
        self._tr_init(1, transform)

    def __setstate__(self, state):
        """__setstate__ is called whenever the instance is loaded
        from the ZODB, like when Zope is restarted.

        We should reload the wrapped transform at this time
        """
        Transform.inheritedAttribute("__setstate__")(self, state)
        self._tr_init()

    def _tr_init(self, set_conf=0, transform=None):
        """initialize the zope transform by loading the wrapped transform"""
        __traceback_info__ = (self.module,)
        if transform is None:
            transform = self._load_transform()
        else:
            self._v_transform = transform
        # check this is a valid transform
        if not hasattr(transform, "__class__"):
            raise TransformException("Invalid transform : transform is not a class")
        if not ITransform.providedBy(transform):
            raise TransformException(
                "Invalid transform : ITransform is not implemented by %s"
                % transform.__class__
            )
        if not hasattr(transform, "inputs"):
            raise TransformException(
                'Invalid transform : missing required "inputs" attribute'
            )
        if not hasattr(transform, "output"):
            raise TransformException(
                'Invalid transform : missing required "output" attribute'
            )
        # manage configuration
        if set_conf and hasattr(transform, "config"):
            conf = dict(transform.config)
            self._config.update(conf)
            make_config_persistent(self._config)
            if hasattr(transform, "config_metadata"):
                conf = dict(transform.config_metadata)
                self._config_metadata.update(conf)
                make_config_persistent(self._config_metadata)
        transform.config = dict(self._config)
        make_config_nonpersistent(transform.config)
        transform.config_metadata = dict(self._config_metadata)
        make_config_nonpersistent(transform.config_metadata)

        self.inputs = transform.inputs
        self.output = transform.output
        self.output_encoding = getattr(transform, "output_encoding", None)
        return transform

    def _load_transform(self):
        try:
            m = import_from_name(self.module)
        except ImportError as err:
            transform = BrokenTransform(self.id, self.module, err)
            msg = (
                "Cannot register transform %s (ImportError), using "
                "BrokenTransform: Error\n %s" % (self.id, err)
            )
            self.title = "BROKEN"
            log(msg, severity=ERROR)
            return transform
        if not hasattr(m, "register"):
            msg = (
                "Invalid transform module %s: no register function "
                "defined" % self.module
            )
            raise TransformException(msg)
        try:
            transform = m.register()
        except Exception as err:
            transform = BrokenTransform(self.id, self.module, err)
            msg = (
                "Cannot register transform %s, using BrokenTransform: "
                "Error\n %s" % (self.id, err)
            )
            self.title = "BROKEN"
            log(msg, severity=ERROR)
        else:
            self.title = ""
        self._v_transform = transform
        return transform

    @security.private
    def manage_beforeDelete(self, item, container):
        SimpleItem.manage_beforeDelete(self, item, container)
        if self is item:
            # unregister self from catalog on deletion
            tr_tool = getToolByName(self, "portal_transforms")
            tr_tool._unmapTransform(self)

    @security.public
    def get_documentation(self):
        """return transform documentation"""
        if not hasattr(self, "_v_transform"):
            self._load_transform()
        return self._v_transform.__doc__

    @security.public
    def convert(self, *args, **kwargs):
        # return apply the transform and return the result
        if not hasattr(self, "_v_transform"):
            self._load_transform()
        return self._v_transform.convert(*args, **kwargs)

    @security.public
    def name(self):
        """return the name of the transform instance"""
        return self.id

    @security.protected(ManagePortal)
    def get_parameters(self):
        """get transform's parameters names"""
        if not hasattr(self, "_v_transform"):
            self._load_transform()
        keys = sorted(self._v_transform.config.keys())
        return keys

    @security.protected(ManagePortal)
    def get_parameter_value(self, key):
        """get value of a transform's parameter"""
        value = self._config[key]
        type = self.get_parameter_infos(key)[0]
        if type == "dict":
            result = {}
            if value:
                for key, val in value.items():
                    result[key] = val
        elif type == "list":
            result = list(value)
        else:
            result = value
        return result

    @security.protected(ManagePortal)
    def get_parameter_infos(self, key):
        """get information about a parameter

        return a tuple (type, label, description [, type specific data])
        where type in (string, int, list, dict)
              label and description are two string describing the field
        there may be some additional elements specific to the type :
             (key label, value label) for the dict type
        """
        try:
            return tuple(self._config_metadata[key])
        except KeyError:
            return "string", "", ""

    @security.protected(ManagePortal)
    def set_parameters(self, REQUEST=None, **kwargs):
        """set transform's parameters"""
        if not kwargs:
            kwargs = REQUEST.form
        self.preprocess_param(kwargs)
        for param, value in kwargs.items():
            try:
                self.get_parameter_value(param)
            except KeyError:
                log("Warning: ignored parameter %r" % param)
                continue
            meta = self.get_parameter_infos(param)
            self._config[param] = VALIDATORS[meta[0]](value)

        tr_tool = getToolByName(self, "portal_transforms")
        # need to remap transform if necessary (i.e. configurable
        # inputs / output)
        if "inputs" in kwargs or "output" in kwargs:
            tr_tool._unmapTransform(self)
            if not hasattr(self, "_v_transform"):
                self._load_transform()
            self.inputs = kwargs.get("inputs", self._v_transform.inputs)
            self.output = kwargs.get("output", self._v_transform.output)
            tr_tool._mapTransform(self)
        # track output encoding
        if "output_encoding" in kwargs:
            self.output_encoding = kwargs["output_encoding"]
        if REQUEST is not None:
            REQUEST["RESPONSE"].redirect(tr_tool.absolute_url() + "/manage_main")

    @security.protected(ManagePortal)
    def reload(self):
        """reload the module where the transformation class is defined"""
        log("Reloading transform %s" % self.module)
        m = import_from_name(self.module)
        reload_module(m)
        self._tr_init()

    def preprocess_param(self, kwargs):
        """preprocess param fetched from an http post to handle
        optional dictionary
        """
        for param in self.get_parameters():
            if self.get_parameter_infos(param)[0] == "dict":
                try:
                    keys = kwargs[param + "_key"]
                    del kwargs[param + "_key"]
                except Exception:
                    keys = ()
                try:
                    values = kwargs[param + "_value"]
                    del kwargs[param + "_value"]
                except Exception:
                    values = ()
                kwargs[param] = dict = {}
                for key, value in zip(keys, values):
                    key = key.strip()
                    if key:
                        value = value.strip()
                        if value:
                            dict[key] = value


InitializeClass(Transform)
