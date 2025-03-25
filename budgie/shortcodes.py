import re


CONTENT_SHORTCODE_EX = re.compile(
    r'\[(\w+)\s*(.*?)\](.*)\[/\1\]',
    re.MULTILINE
)

SELFCLOSING_SHORTCODE_EX = re.compile(
    r'\[(\w+)\s*(.*?)\]',
    re.MULTILINE
)

ATTR_EX = re.compile(r'([\w-]+)\s*=\s*"(.*?)"|"(.*?)"')


def handle(shortcode, value, func, takes_content=True):
    def handle_content(match):
        tag, raw_attrs, content = match.groups()
        args = []
        kwargs = {}

        if tag != shortcode:
            return '[%(tag)s %(attrs)s]%(content)s[/%(tag)s]' % {
                'tag': tag.strip(),
                'attrs': raw_attrs.strip(),
                'content': content.strip()
            }

        for match in ATTR_EX.findall(raw_attrs):
            if match[2]:
                args.append(match[2])
            else:
                kwargs[match[0]] = match[1]

        return func(content, *args, **kwargs)

    def handle_selfclosing(match):
        tag, raw_attrs = match.groups()
        args = []
        kwargs = {}

        if tag != shortcode:
            return '[%(tag)s %(attrs)s]' % {
                'tag': tag.strip(),
                'attrs': raw_attrs.strip()
            }

        for match in ATTR_EX.findall(raw_attrs):
            if match[2]:
                args.append(match[2])
            else:
                kwargs[match[0]] = match[1]

        return func(*args, **kwargs)

    if takes_content:
        return CONTENT_SHORTCODE_EX.sub(handle_content, value)

    return SELFCLOSING_SHORTCODE_EX.sub(handle_selfclosing, value)
