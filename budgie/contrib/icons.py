from budgie import app
import re


ICON_EX = re.compile(r':([a-z0-9-]+):')
ICON_REPL = r'<i class="bi bi-\g<1>"></i>'


@app.transformer('article_body')
def icon_transformer(value):
    if value:
        return re.sub(ICON_EX, ICON_REPL, value)

    return ''
