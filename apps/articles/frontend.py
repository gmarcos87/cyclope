from django.utils.translation import ugettext as _
from django.views.generic.list_detail import object_detail, object_list

from cyclope import site as cyc_site
from cyclope.core import frontend
from cyclope import views

from cyclope.apps.articles.models import Article

class ArticleDetailView(frontend.FrontendView):
    name='detail'
    verbose_name=_('full detail')
    is_default = True
    params = {'queryset': Article.objects,
              'template_object_name': 'article',
             }

    def get_response(self, request, *args, **kwargs):
        return views.object_detail(request, *args, **kwargs)

cyc_site.register_view(StaticPage, StaticPageDetailView())
