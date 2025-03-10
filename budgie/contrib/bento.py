from bs4 import BeautifulSoup
from budgie import app
from slugify import slugify
import re


START_BOX_EX = re.compile(r'^=== *BENTO BOX *=== *$')
END_BOX_EX = re.compile(r'^=== *END BENTO BOX *=== *$')
COLUMNS_LINE = re.compile(r'^columns: (\d+) *$')
ROWS_LINE = re.compile(r'^rows: (\d+) *$')


def render_box(lines, index=0):
    classes = ['box', 'box-%d' % (index + 1)]
    delay = 100 * (index + 1)
    title = None
    html_lines = []

    for line in lines:
        if not line:
            html_lines.append(line)
            continue

        if line.startswith('#') and not title:
            title = line.lstrip('#').strip()
            html_lines.append(line)
            continue

        if match := COLUMNS_LINE.match(line):
            classes.append(
                'box-columns-%d' % int(
                    match.groups()[0]
                )
            )

            continue

        if match := ROWS_LINE.match(line):
            classes.append(
                'box-rows-%d' % int(
                    match.groups()[0]
                )
            )

            continue

        html_lines.append(line)

    if title:
        soup = BeautifulSoup(
            app.transform('article_body', title),
            'html.parser'
        )

        classes.append('box-%s' % slugify(soup.text))

    aos = ('data-aos="fade-up" data-aos-delay="%s"' % delay)
    html = [
        '<div class="%s" %s>' % (
            ' '.join(classes),
            aos
        ),
        '<div>',
        app.transform('article_body', '\n'.join(html_lines)),
        '</div>'
        '</div>'
    ]

    return ''.join(html)


def render_bento(lines):
    classes = ['bento']
    html = ['<div class="%s">' % ' '.join(classes)]
    box = None
    index = 0

    for line in lines:
        if line.startswith('##'):
            if box is not None:
                html.append(
                    render_box(box, index)
                )

                box = None
                index += 1

            if box is None:
                box = []

        if box is not None:
            box.append(line)

    if box is not None and any(box):
        html.append(
            render_box(box, index)
        )

    html.append('</div>')
    return ''.join(html)


@app.transformer('article_body', 90)
def bento_transformer(value):
    if not value:
        return ''

    lines = []
    bento = None

    for line in value.splitlines():
        if START_BOX_EX.match(line.strip()):
            if bento is not None:
                raise Exception('Nested bento boxes aren\'t supported')

            bento = {
                'lines': []
            }

            continue

        if END_BOX_EX.match(line.strip()):
            if bento is None:
                raise Exception('No open bento box to close')

            lines.append(
                render_bento(**bento)
            )

            bento = None
            continue

        if bento is not None:
            bento['lines'].append(line)
            continue

        lines.append(line)

    return '\n'.join(lines)
