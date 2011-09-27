from django.conf.urls.defaults import patterns

urlpatterns = patterns(
    '',
    (r'^page$', 'rdfviewer.views.page'),
    (r'^line$', 'rdfviewer.views.line'),
    (r'^(?P<work_uri>.+)$', 'rdfviewer.views.viewer'),
)

