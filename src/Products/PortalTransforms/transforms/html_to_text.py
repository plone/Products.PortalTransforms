from html.entities import name2codepoint
from Products.PortalTransforms.libtransforms.retransform import retransform


class html_to_text(retransform):
    inputs = ("text/html",)
    output = "text/plain"


def register():
    def sub_func(matchobj):
        full = matchobj.group()
        ent = matchobj.group(1)
        result = name2codepoint.get(ent)
        if result is None:
            if ent.startswith("#"):
                try:
                    number = int(ent[1:])
                    res = chr(number)
                except Exception:
                    res = full
            else:
                res = full
        else:
            res = chr(result)

        if isinstance(full, str):
            return res
        return res.encode("utf-8")

    return html_to_text(
        "html_to_text",
        (r"(?im)<script [^>]>.*</script>", " "),
        (r"(?im)<style [^>]>.*</style>", " "),
        (r"(?im)<head [^>]>.*</head>", " "),
        (r"(?im)</?(font|em|i|strong|b)(?=\W)[^>]*>", ""),
        (r"(?i)(?m)<[^>]*>", " "),
        (r"&([a-zA-Z0-9#]*?);", sub_func),
    )
