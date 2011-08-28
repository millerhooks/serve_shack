from django.conf.urls.defaults import *
from piston.resource import Resource

from MPResource import MPResource

##class Resource(MPResource):
#    def error_handler(self, error, request, meth, *args,**kwargs):
#	sentry_exception_handler(request=request)
#        return super(Resource, self).error_handler(error, request, meth)

class CsrfExemptResource(MPResource):
    """A Custom Resource that is csrf exempt"""
    def __init__(self, handler, authentication=None):
        super(CsrfExemptResource, self).__init__(handler, authentication)
        self.csrf_exempt = getattr(self.handler, 'csrf_exempt', True)

from handlers import VenueHandler

urlpatterns = patterns('',
    url(r'^venues/$', CsrfExemptResource(VenueHandler)),
)