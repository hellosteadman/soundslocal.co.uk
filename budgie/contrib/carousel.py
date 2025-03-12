from bs4 import BeautifulSoup
from budgie import app
from slugify import slugify
from .media import IMG_TAG_EX, File
import re


START_CAROUSEL_EX = re.compile(r'^=== *(VERTICAL )?CAROUSEL *=== *$')
END_CAROUSEL_EX = re.compile(r'^=== *END (VERTICAL )?CAROUSEL *=== *$')


def render_section(lines, index=0):
    classes = ['carousel-item', 'carousel-item-%d' % (index + 1)]
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
        classes.append('carousel-item-%s' % slugify(soup.text))

    aos = ('data-aos="fade-up" data-aos-delay="%s"' % delay)
    header = ''

    if title:
        header = '<a class="carousel-header" href="javascript:;">%s</a>' % (
            title
        )

    inner = '<div class="carousel-content"><div>%s</div></div>' % (
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


def render_carousel(lines, vertical=False):
    classes = ['carousel']
    html = []

    if vertical:
        classes.append('vertical')
        html.append('<div class="vertical-carousel-wrapper">')

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
def carousel_transformer(value):
    if not value:
        return ''

    lines = []
    carousel = None

    for line in value.splitlines():
        if match := START_CAROUSEL_EX.match(line.strip()):
            if carousel is not None:
                raise Exception('Nested carousels aren\'t supported')

            carousel = {
                'lines': [],
                'vertical': not not match.groups()[0]
            }

            continue

        if match := END_CAROUSEL_EX.match(line.strip()):
            if carousel is None:
                raise Exception('No open carousel to close')

            if match.groups()[0] and not carousel['vertical']:
                raise Exception('Open carousel is not vertical')

            lines.append(
                render_carousel(**carousel)
            )

            carousel = None
            continue

        if carousel is not None:
            carousel['lines'].append(line)
            continue

        lines.append(line)

    return '\n'.join(lines)
