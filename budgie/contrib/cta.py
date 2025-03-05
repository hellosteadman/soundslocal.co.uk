from budgie import app, shortcodes


def handle_shortcode(content, url, **kwargs):
    size = kwargs.get('size', 'lg')

    if size == 'md':
        size = ''   

    classes = ['btn', 'btn-primary']

    if size:
        classes.append('btn-%s' % size)

    return '<p><a href="%s" class="%s">%s</a></p>' % (
        url,
        ' '.join(set(classes)),
        content
    )


@app.transformer('article_body', 90)
def cta_transformer(value):
    if not value:
        return ''

    return shortcodes.handle('cta', value, handle_shortcode)
