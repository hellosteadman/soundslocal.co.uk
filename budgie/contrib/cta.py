from budgie import app, shortcodes


def handle_shortcode(content, url, **kwargs):
    classes = ['btn', 'btn-primary', 'btn-lg']

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
