from budgie import app
import re


START_GRID_EX = re.compile(r'^=== *GRID OF (\d+)([^=]+)?=== *$')
END_GRID_EX = re.compile(r'^=== *END GRID OF (\d+)([^=]+)?=== *$')


def render_row(lines, width, slug=None, index=0):
    classes = ['cell', 'cell-12', 'cell-tablet-%d' % width]
    delay = 300 * (index + 1)

    if slug:
        classes.append('%s-cell' % slug)

    classes.append('margin-bottom-3')
    html = [
        '<div class="%s" %s>' % (
            ' '.join(classes),
            ('data-aos="fade-up" data-aos-delay="%s"' % delay)
        ),
        '<div>',
        app.transform('article_body', '\n'.join(lines)),
        '</div>'
        '</div>'
    ]

    return ''.join(html)


def render_grid(cells, lines, slug=None):
    classes = ['grid']
    if slug:
        classes.append('%s-grid' % slug)

    html = ['<div class="%s">' % ' '.join(classes)]
    row = None
    width = int(12 / cells)
    index = 0

    for line in lines:
        if line.startswith('##'):
            if row is not None:
                html.append(
                    render_row(row, width, slug, index)
                )

                row = None
                index += 1

            if row is None:
                row = []

        if row is not None:
            row.append(line)

    if row is not None and any(row):
        html.append(
            render_row(row, width, slug, index)
        )

    html.append('</div>')
    return ''.join(html)


@app.transformer('article_body', 90)
def grid_transformer(value):
    if not value:
        return ''

    lines = []
    grid = None

    for line in value.splitlines():
        if match := START_GRID_EX.match(line.strip()):
            if grid is not None:
                raise Exception('Nested grids aren\'t supported')

            groups = match.groups()
            grid = {
                'cells': int(groups[0]),
                'slug': groups[1] and groups[1].lower().strip(),
                'lines': []
            }

            continue

        if match := END_GRID_EX.match(line.strip()):
            if grid is None:
                raise Exception('No open grid to close')

            if grid['cells'] != int(match.groups()[0]):
                raise Exception(
                    'Grid opening and closing show different cell numbers'
                )

            groups = match.groups()
            slug = groups[1] and groups[1].lower().strip()

            if grid['slug'] != slug:
                raise Exception(
                    'Grid opening and closing show different contents'
                )

            lines.append(
                render_grid(**grid)
            )

            grid = None
            continue

        if grid is not None:
            grid['lines'].append(line)
            continue

        lines.append(line)

    return '\n'.join(lines)
