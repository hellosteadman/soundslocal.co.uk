from budgie import app, settings
from budgie.models import ModelBase, Collection
from budgie.request import Request
from budgie.templates import Template
from budgie.views import ListView, DetailView
import os


class Post(ModelBase):
    objects = Collection('blog')


@app.route('blog/', 'post_list', priority=0)
class PostListView(ListView):
    model = Post

    def get_render_context(self):
        return {
            **super().get_render_context(),
            'BLOG_HEADER': settings.BLOG_HEADER,
            'BLOG_DESCRIPTION': settings.BLOG_DESCRIPTION
        }


@app.route('blog/*/', 'post_detail', priority=0)
class PostDetailView(DetailView):
    model = Post


@app.on('build')
def build_posts():
    object_list = []

    for obj in Post.objects.all():
        slug = obj.slug
        template_name = ['post_detail.html']
        template = Template(template_name)
        context = {
            'object': obj,
            'request': Request('/blog/%s/' % slug)
        }

        html = template.render(context)
        dirname = os.path.join(
            settings.BUILD_DIR,
            'blog',
            obj.slug
        )

        os.makedirs(dirname, exist_ok=True)
        filename = os.path.join(dirname, 'index.html')

        with open(filename, 'w') as f:
            f.write(html)
            print('.', filename[len(settings.BUILD_DIR) + 1:])

        object_list.append(obj)

    if not any(object_list):
        return

    template = Template(['post_list.html'])
    context = {
        'BLOG_HEADER': settings.BLOG_HEADER,
        'BLOG_DESCRIPTION': settings.BLOG_DESCRIPTION,
        'object_list': object_list,
        'request': Request('/blog/')
    }

    html = template.render(context)
    dirname = os.path.join(settings.BUILD_DIR, 'blog')
    filename = os.path.join(dirname, 'index.html')

    with open(filename, 'w') as f:
        f.write(html)
        print('.', filename[len(settings.BUILD_DIR) + 1:])
