import re


SHORTCODE_EX = re.compile(
    r'\[(\w+)\s*(.*?)\](.*?)\[/\1\]',
    re.MULTILINE
)


ATTR_EX = re.compile(r'([\w-]+)\s*=\s*"(.*?)"|"(.*?)"')


def handle(shortcode, value, func):
    def replace(match):
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

    return SHORTCODE_EX.sub(replace, value)
