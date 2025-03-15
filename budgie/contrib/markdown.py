from budgie import app
from budgie.utils import mark_safe
from markdown import markdown


@app.filter('markdown')
def markdown_filter(value):
    if value:
        return mark_safe(
            markdown(
                value.strip(),
                extensions=['smarty']
            )
        )

    return ''


@app.transformer('article_body', 100)
def markdown_transformer(value):
    if value:
        return mark_safe(
            markdown(
                value.strip(),
                extensions=['smarty']
            )
        )

    return ''
