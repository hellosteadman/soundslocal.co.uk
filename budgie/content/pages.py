from budgie import app, build_page
from budgie.models import ModelBase, Collection
from budgie.request import Request
from budgie.templates import Template
from budgie.views import DetailView


class Page(ModelBase):
    objects = Collection()


@app.route('*/', 'page_detail', priority=100)
class PageView(DetailView):
    model = Page


@app.route('', 'index')
class IndexView(DetailView):
    template_name = 'index.html'
    model = Page

    def get_query_args(self):
        return dict(slug='index')


@app.on('build')
def build_pages():
    for obj in Page.objects.all():
        slug = obj.slug
        template_name = ['page_detail.html']

        if obj.slug == 'index':
            template_name.insert(0, 'index.html')
            slug = ''

        template = Template(template_name)
        context = {
            'object': obj,
            'request': Request('/%s/' % slug)
        }

        html = template.render(context)

        if obj.slug == 'index':
            dirname = ''
        else:
            dirname = obj.slug

        build_page(dirname, html)
