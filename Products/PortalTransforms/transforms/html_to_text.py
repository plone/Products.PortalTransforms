# -*- coding: utf-8 -*-
from Products.PortalTransforms.libtransforms.retransform import retransform


import six
from six.moves import html_entities


class html_to_text(retransform):
    inputs = ('text/html',)
    output = 'text/plain'


def register():
    def sub_func(matchobj):
        full = matchobj.group()
        ent = matchobj.group(1)
        result = html_entities.name2codepoint.get(ent)
        if result is None:
            if ent.startswith('#'):
                try:
                    number = int(ent[1:])
                    res = six.unichr(number)
                except:
                    res = full
            else:
                res = full
        else:
            res = six.unichr(result)

        if isinstance(full, six.text_type):
            return res
        return res.encode('utf-8')

    return html_to_text(
        "html_to_text",
        (r'(?im)<script [^>]>.*</script>', ' '),
        (r'(?im)<style [^>]>.*</style>', ' '),
        (r'(?im)<head [^>]>.*</head>', ' '),
        (r'(?im)</?(font|em|i|strong|b)(?=\W)[^>]*>', ''),
        (r'(?i)(?m)<[^>]*>', ' '),
        (r'&([a-zA-Z0-9#]*?);', sub_func),
    )
