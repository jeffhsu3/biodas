from django.core.exceptions import ImproperlyConfigured
from django.conf.urls.defaults import *
from django.http import HttpResponse
from tastypie.api import Api
from tastypie.resources import Resource
from tastypie.utils.mime import determine_format, build_content_type
from tastypie.utils import trailing_slash

from serializers import top_level_serializer
from utils import add_das_headers 


class DAS(Api):
    """ Container for a Das Server
    """

    def __init__(self, api_name="das", version = '1.6'):
        """ Version needs to be a string because of 1.6E extension
        """
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
            url(r"^(?P<api_name>%s)/sources" % (self.api_name),
                self.wrap_view('top_level'),
                name="api_%s_top_level" % self.api_name),
        ]

        urlpatterns = self.override_urls() + patterns('', *pattern_list)

        for name in sorted(self._registry.keys()):
            self._registry[name].api_name = self.api_name
            pattern_list.append((r"^(?P<api_name>%s)/" % self.api_name,
                                 include(self._registry[name].urls)))

        urlpatterns = self.override_urls() + patterns('',*pattern_list)

        return(urlpatterns)


    def top_level(self, request, api_name=None):
        """
        A view that returns a serialized list of all DAS_sources in registers.
        """
        # :TODO default to xml
        sources = self._registry

        if request.GET:
            capability = request.GET.get('capability')
            s_type = request.GET.get('type')
            authority = request.GET.get('authority')
            version = request.GET.get('version')
            organism = request.GET.get('organism')
            label = request.GET.get('label')
            sources = dict((key, value) for key, value in sources.items() if \
                       value.version == int(version))

        if api_name is None:
            api_name = self.api_name

        #desired_format = determine_format(request, serializer)
        desired_format = 'application/xml'
        options = {}
        response = HttpResponse(content = top_level_serializer(sources),
                     content_type=build_content_type(desired_format))
        response = add_das_headers(response, self.version)
        return response


    def auto_generate_sources(self, path):
        """ Auto generate resources and attach them to the server from all
        files within a folder.  All files must be indexed binary files.
        """
        import os
        pass

