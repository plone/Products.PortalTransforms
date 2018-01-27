"""
PortalTransforms setup handlers.
"""
from __future__ import print_function
from Products.CMFCore.utils import getToolByName

from six import StringIO


def correctMapping(out, portal):
    pt = getToolByName(portal, 'portal_transforms')
    pt_ids = pt.objectIds()

    for m_in, m_out_dict in pt._mtmap.items():
        for m_out, transforms in m_out_dict.items():
            for transform in transforms:
                if transform.id not in pt_ids:
                    # error, mapped transform is no object in
                    # portal_transforms. correct it!
                    print(
                        'have to unmap transform ({0}) cause its not in '
                        'portal_transforms ...'.format(transform.id), file=out)
                    try:
                        pt._unmapTransform(transform)
                    except:
                        raise
                    else:
                        print('...ok', file=out)


def updateTransform(out, portal, transform_id):
    print('Update {0}...'.format(transform_id), file=out)
    transform_module = "Products.PortalTransforms.transforms.{0}".format(transform_id)
    pt = getToolByName(portal, 'portal_transforms')
    for item in pt.objectIds():
        transform = getattr(pt, item)
        if transform.id == transform_id and \
                transform.module == transform_module:
            try:
                transform.get_parameter_value('disable_transform')
            except KeyError:
                out.write('  replace {0} ({1}, {2}) ...'.format(
                    item, transform.name(), transform.module))
                try:
                    pt.unregisterTransform(item)
                    pt.manage_addTransform(item, transform_module)
                except:
                    raise
                else:
                    out.write('  ...done')

    out.write('  ...done')


def installPortalTransforms(portal):
    out = StringIO()

    updateTransform(out, portal, 'safe_html')
    updateTransform(out, portal, 'markdown_to_html')

    correctMapping(out, portal)


def setupPortalTransforms(context):
    """
    Setup PortalTransforms step.
    """
    # Only run step if a flag file is present (e.g. not an extension profile)
    if context.readDataFile('portal-transforms-various.txt') is None:
        return
    site = context.getSite()
    installPortalTransforms(site)
