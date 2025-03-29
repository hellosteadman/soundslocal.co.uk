from budgie import app
import re

START_SECTION_EX = re.compile(r'^=== (WRAPPED )?([^=]+)? *SECTION *=== *$')
END_SECTION_EX = re.compile(r'^=== *END([^=]+)? *SECTION *=== *$')


def render_section(lines, slug=None, wrapped=False):
    classes = ['section']
    if slug:
        classes.append(f'{slug}-section')

    html = [
        '<div class="%s" %s>' % (
            ' '.join(classes),
            'data-aos="fade-up"'
        )
    ]

    text = '\n'.join(lines)
    html += app.transform('article_body', text)
    html.append('</div>')

    if wrapped:
        return '<div class="%swrapper">%s</div>' % (
            slug and ('%s-' % slug) or '',
            ''.join(html)
        )

    return ''.join(html)


@app.transformer('article_body', 90)
def section_transformer(value):
    if not value:
        return ''

    lines = []
    section_stack = []

    for line in value.splitlines():
        stripped_line = line.strip()

        if match := END_SECTION_EX.match(stripped_line):
            if not section_stack:
                raise Exception('No open section to close')

            groups = match.groups()
            slug = groups[0].lower().strip() if groups[0] else None
            section = section_stack.pop()

            if section['slug'] and section['slug'] != slug:
                raise Exception('Mismatched section tags')

            rendered_section = render_section(**section)

            if section_stack:
                section_stack[-1]['lines'].append(rendered_section)
            else:
                lines.append(rendered_section)

            continue

        if match := START_SECTION_EX.match(stripped_line):
            groups = match.groups()[1:]
            wrapped = not not match.groups()[0]
            section = {
                'slug': groups[0].lower().strip() if groups[0] else None,
                'wrapped': wrapped,
                'lines': []
            }

            section_stack.append(section)
            continue

        if section_stack:
            section_stack[-1]['lines'].append(line)
        else:
            lines.append(line)

    if section_stack:
        raise Exception('Unclosed section detected')

    return '\n'.join(lines)
