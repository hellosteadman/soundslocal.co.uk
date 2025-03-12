from bs4 import BeautifulSoup
from budgie import app
from slugify import slugify
from .media import IMG_TAG_EX, File
import re


START_ACCORDION_EX = re.compile(r'^=== *(VERTICAL )?ACCORDION *=== *$')
END_ACCORDION_EX = re.compile(r'^=== *END (VERTICAL )?ACCORDION *=== *$')


def render_section(lines, index=0):
    classes = ['accordion-item', 'accordion-item-%d' % (index + 1)]
    delay = 100 * (index + 1)
    title = None
    html_lines = []
    image = None

    if index == 0:
        classes.append('active')

    for line in lines:
        if not line:
            html_lines.append(line)
            continue

        if line.startswith('#') and not title:
            title = line.strip()
            continue

        if match := IMG_TAG_EX.match(line):
            image = match.groups()[1]
            continue

        html_lines.append(line)

    if title:
        title = app.transform('article_body', title)
        soup = BeautifulSoup(title, 'html.parser')
        classes.append('accordion-item-%s' % slugify(soup.text))

    aos = ('data-aos="fade-up" data-aos-delay="%s"' % delay)
    header = ''

    if title:
        header = '<a class="accordion-header" href="javascript:;">%s</a>' % (
            title
        )

    inner = '<div class="accordion-content"><div>%s</div></div>' % (
        app.transform('article_body', '\n'.join(html_lines))
    )

    if image:
        image = (
            '<img src="%s">' % File(image).url()
        )

    html = [
        '<li class="%s" %s>' % (
            ' '.join(classes),
            aos
        ),
        '<div>', (image or ''), header, inner, '</div>'
        '</li>'
    ]

    return ''.join(html)


def render_accordion(lines, vertical=False):
    classes = ['accordion']
    html = []

    if vertical:
        classes.append('vertical')
        html.append('<div class="vertical-accordion-wrapper">')

    html.append('<ul class="%s">' % ' '.join(classes))
    section = None
    index = 0

    for line in lines:
        if line.startswith('## '):
            if section is not None:
                html.append(
                    render_section(section, index)
                )

                section = None
                index += 1

            if section is None:
                section = []

        if section is not None:
            section.append(line)

    if section is not None and any(section):
        html.append(
            render_section(section, index)
        )

    html.append('</ul>')

    if vertical:
        html.append('</div>')

    return ''.join(html)


@app.transformer('article_body', 90)
def accordion_transformer(value):
    if not value:
        return ''

    lines = []
    accordion = None

    for line in value.splitlines():
        if match := START_ACCORDION_EX.match(line.strip()):
            if accordion is not None:
                raise Exception('Nested accordions aren\'t supported')

            accordion = {
                'lines': [],
                'vertical': not not match.groups()[0]
            }

            continue

        if match := END_ACCORDION_EX.match(line.strip()):
            if accordion is None:
                raise Exception('No open accordion to close')

            if match.groups()[0] and not accordion['vertical']:
                raise Exception('Open accordion is not vertical')

            lines.append(
                render_accordion(**accordion)
            )

            accordion = None
            continue

        if accordion is not None:
            accordion['lines'].append(line)
            continue

        lines.append(line)

    return '\n'.join(lines)
