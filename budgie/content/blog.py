from budgie import app, settings, build_page
from budgie.models import ModelBase, Collection
from budgie.request import Request
from budgie.templates import Template
from budgie.utils import now
from budgie.views import ListView, DetailView
from datetime import datetime, date
from dateutil.parser import parse as parse_date
from pytz import timezone


class Post(ModelBase):
    objects = Collection('blog')


@app.route('blog/', 'post_list', priority=0)
class PostListView(ListView):
    model = Post

    def get_query_args(self):
        return dict(
            published__lte=now()
        )

    def get_render_context(self):
        return {
            **super().get_render_context(),
            'BLOG_HEADING': settings.BLOG['HEADING'],
            'BLOG_DESCRIPTION': settings.BLOG['DESCRIPTION']
        }


@app.route('blog/*/', 'post_detail', priority=0)
class PostDetailView(DetailView):
    model = Post


@app.on('build')
def build_posts():
    object_list = []

    for obj in Post.objects.filter(
        published__lte=now()
    ):
        slug = obj.slug
        template_name = ['post_detail.html']
        template = Template(template_name)
        context = {
            'object': obj,
            'request': Request('/blog/%s/' % slug)
        }

        html = template.render(context)
        build_page('blog/%s' % slug, html)
        object_list.append(obj)

    if not any(object_list):
        return

    template = Template(['post_list.html'])
    context = {
        'BLOG_HEADING': settings.BLOG['HEADING'],
        'BLOG_DESCRIPTION': settings.BLOG['DESCRIPTION'],
        'object_list': object_list,
        'request': Request('/blog/')
    }

    html = template.render(context)
    build_page('blog/', html)


@app.transformer('article_schema')
def transform_schema(schema):
    schema['published'] = None
    schema['tags'] = []
    return schema


@app.transformer('article_property', prop=('tags'))
def transform_tags(value, prop):
    return tuple(sorted(set(value)))


@app.transformer('article_property', prop=('published'))
def transform_published(value, prop):
    if isinstance(value, str):
        value = parse_date(value)

    if isinstance(value, date) and not isinstance(value, datetime):
        value = datetime(
            value.year,
            value.month,
            value.day,
            0,
            0,
            0,
            0,
            tzinfo=timezone(settings.TIMEZONE)
        )

    return value
