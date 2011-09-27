from django.conf.urls.defaults import patterns, url

urlpatterns = patterns(
    '',
    (r'^$', 'rdfviewer.views.index'),
    (r'^page$', 'rdfviewer.views.page'),
    (r'^line$', 'rdfviewer.views.line'),
    url(r'^work$', 'rdfviewer.views.viewer', name='work'),
)

