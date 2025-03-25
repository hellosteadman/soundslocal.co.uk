from bs4 import Tag
from budgie import app, settings, shortcodes


JS = '(function(w,d,e,u,f,l,n){w[f]=w[f]||function(){(w[f].q=w[f].q||[]).push(arguments);},l=d.createElement(e),l.async=1,l.src=u,n=d.getElementsByTagName(e)[0],n.parentNode.insertBefore(l,n);})(window,document,\'script\',\'https://assets.mailerlite.com/js/universal.js\', \'ml\'); ml(\'account\', \'%s\');'


@app.on('inject_head')
def inject_js(body):
    script = Tag('html.parser', name='script', is_xml=False)
    script.string = JS % settings.MAILERLITE['ACCOUNT_ID']
    body.append(script)


def handle_shortcode(form):
    return (
        '<div class="ml-embedded rounded shadow-lg margin-bottom-5" data-form="%s"></div>'
    ) % form


@app.transformer('article_body', 90)
def ml_transformer(value):
    return shortcodes.handle(
        'mailerlite',
        value,
        handle_shortcode,
        takes_content=False
    )
