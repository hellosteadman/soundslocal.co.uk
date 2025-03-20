from bs4 import Tag
from budgie import app, settings


@app.on('inject_head')
def inject_js(body):
    body.append(
        Tag(
            'html.parser',
            name='script',
            attrs={
                'src': 'https://plausible.io/js/script.outbound-links.js',
                'defer': True,
                'data-domain': settings.DOMAIN
            },
            is_xml=False
        )
    )
