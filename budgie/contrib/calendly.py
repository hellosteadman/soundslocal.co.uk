from bs4 import Tag
from budgie import app


JS = """
document.body.addEventListener('click',
    function (e) {
        var a = e.target.matches('a[href]') ? e.target : e.target.closest('a[href]')

        if (!a) {
            return
        }

        if (a.href.search('//calendly.com/') > -1) {
            e.preventDefault()
            Calendly.initPopupWidget(
                {
                    url: a.href
                }
            )
        }
    },
    false
)
"""


@app.on('inject_head')
def inject_stylesheet(head):
    head.append(
        Tag(
            'html.parser',
            name='link',
            attrs={
                'href': 'https://assets.calendly.com/assets/external/widget.css',
                'rel': 'stylesheet'
            },
            is_xml=False
        )
    )


@app.on('inject_body')
def inject_js(body):
    body.append(
        Tag(
            'html.parser',
            name='script',
            attrs={
                'src': 'https://assets.calendly.com/assets/external/widget.js',
                'async': True
            },
            is_xml=False
        )
    )

    script = Tag(
        'html.parser',
        name='script',
        is_xml=False
    )

    script.string = JS
    body.append(script)
