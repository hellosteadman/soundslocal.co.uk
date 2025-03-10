from budgie import app, shortcodes, utils
import regex


LINK_TAG_EX = regex.compile(r'''
    \[
        (?P<text>(?:[^\]\\]|\\.)*)
    \]                      # End text
    \(                      # Opening parenthesis for URL and optional title
        \s*
        (?P<url>
            (?:
                <(?P<angle_url>[^>]+)>         # URL in angle brackets
                |
                (?P<plain_url>
                    (?:
                        [^()\s\\]+              # URL characters (no spaces, no parentheses)
                        |\\.
                        | \( (?P>plain_url) \)   # Recursively match nested parentheses
                    )+
                )
            )
        )
        (?:\s+                                  # Optional whitespace before title
            (?P<title>
                (?:
                    " (?: [^"\\] | \\.)* "       # Title in double quotes
                    |
                    ' (?: [^'\\] | \\.)* '       # Title in single quotes
                    |
                    \( (?: [^)\\] | \\.)* \)      # Title in parentheses
                )
            )
        )?
        \s*
    \)
''', regex.VERBOSE)


def handle_shortcode(content, url, **kwargs):
    size = kwargs.get('size', 'lg')

    if size == 'md':
        size = ''   

    classes = ['btn', 'btn-primary', 'rounded-pill']

    if size:
        classes.append('btn-%s' % size)

    return '<p><a href="%s" class="%s">%s</a></p>' % (
        url,
        ' '.join(set(classes)),
        content
    )


@app.transformer('article_schema')
def transform_schema(schema):
    schema['cta'] = None
    return schema


@app.transformer('article_property', prop='cta')
def transform_property(value, prop):
    def replace(match):
        classes = ['btn', 'btn-lg', 'btn-primary', 'rounded-pill', 'btn-cta', 'shadow-lg']

        return '<a href="%(url)s" class="%%s">%(text)s</a>' % (
            match.groupdict()
        ) % ' '.join(classes)

    return utils.mark_safe(LINK_TAG_EX.sub(replace, value))


@app.transformer('article_body', 90)
def cta_transformer(value):
    if not value:
        return ''

    return shortcodes.handle('cta', value, handle_shortcode)
