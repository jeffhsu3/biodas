from django.core.exceptions import ImproperlyConfigured
from django.conf.urls.defaults import *
from django.http import HttpResponse
#from django.core.serializers import xml
from tastypie.api import Api
from tastypie.resources import Resource
from tastypie.utils.mime import determine_format, build_content_type
from tastypie.utils import trailing_slash

from serializers import DAS_serializer, top_level_serializer



def add_das_headers(response, version = 1.6):
    """ Add DAS specification headers
    """
    if version == 2:
        # :TODO BioDAS 2 specifications
        response['Content-Type'] = 'text/xml'
    else:
        response['Content-Type'] = 'text/xml'
    # :TODO make to specific sources
    response['X-DAS-Version'] = 'DAS/%f' % version
    response['X-DAS-Status'] = 200
    response['X-DAS-Capabilities'] = 'features/1.0;'
    response['X-DAS-Server'] = 'DjangoDas'
    response['Access-Control-Allow-Origin'] = '*'
    response['Access-Control-Expose-Headers'] =\
            'X-DAS-Version, X-DAS-Status, X-DAS-Capabilities, X-DAS-Server'
    return response



def parse_das_request(request):
    """ Parse a das request
    """
    if request.POST:
        seg = request.POST.get('segment')
    try:
        seg = int(seg)
    except ValueError:
        pass


class DAS(Api):
    """ Container for a Das Server
    """

    def __init__(self, api_name="das", version = 1.6):
        self.api_name = api_name
        self._registry = {}
        self._canonicals = {}
        self.version = version


    def override_urls(self):
        """ Providing own URLs or overriding the default URLs.
        """
        return []


    @property
    def urls(self):
        """ Provides URLconf details for the API and all registered sources
        beneth it.
        """

        pattern_list = [
            url(r"^(?P<api_name>%s)%s$" % (self.api_name, trailing_slash()),
                self.wrap_view('top_level'),
                name="api_%s_top_level" % self.api_name),
        ]

        urlpatterns = self.override_urls() + patterns('', *pattern_list)

        for name in sorted(self._registry.keys()):
            self._registry[name].api_name = self.api_name
            pattern_list.append((r"^(?P<api_name>%s/sources%s" % (self.api_name,
                                                         trailing_slash(),
                                                         )))

        urlpatterns = self.override_urls() + patterns('',*pattern_list)

        return(urlpatterns)


    def top_level(self, request, api_name=None):
        """
        A view that returns a serialized list of all DAS_sources in registers.
        """
        # :TODO default to xml
        serializer = DAS_serializer()
        sources = []
        available_resources = {}

        # Make this a form

        if request.POST:
            capability = request.POST.get('capability')
            s_type = request.POST.get('type')
            authority = request.POST.get('authority')
            version = request.POST.get('version')
            organism = request.POST.get('organism')
            label = request.POST.get('label')

        if api_name is None:
            api_name = self.api_name


        #desired_format = determine_format(request, serializer)
        desired_format = 'application/xml'
        options = {}
        response = HttpResponse(content = top_level_serializer(self._registry),
                     content_type=build_content_type(desired_format))
        response = add_das_headers(response)
        return response


    def auto_generate_sources(self, path):
        """ Auto generate resources and attach them to the server from all
        files within a folder.  All files must be indexed binary files.
        """
        import os
        pass



class DAS_source(Resource):
    """
    """

    def query(self, func):
        pass
