from django.conf.urls.defaults import patterns, include, url

urlpatterns = patterns(
    '',
    (r'', include('rdfviewer.urls', namespace='rdfviewer'))
)

import settings
if settings.TEMPLATE_DEBUG:
    urlpatterns = patterns(
        '',
        (r'^site_media/(?P<path>.*)$', 'django.views.static.serve', 
         {'document_root': settings.MEDIA_ROOT}),
    ) + urlpatterns
