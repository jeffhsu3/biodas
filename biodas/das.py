from django.core.exceptions import ImproperlyConfigured

from tastypie.api import Api

class DasServer(object):
    """ Container for a Das Server
    """

    def __init__(self, das_name):
        self.das_name = das_name
        self._registery = {}

    def segment_request(self, query_func, request):
        pass

    def register(self, source):
        """
        Registers an instance of a ''Source'' subclass with the Server

        """

        source_name = getattr(source, 'source_name', None)

        if source_name is None:
            raise ImproperlyConfigured("Source %r must define a\
                                       'source_name'." % source)

        self._registry[source_name] = source

    def unregister(self, source_name):
        """ If present, unregisters a source from the server.
        """
        if source in self.registry:
            del(self._registry[source_name])


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
            url(r"^(?P<api_name>%s)%s$" % (self.das_name),
                self.wrap_view('top_level'),
                name="api_%s_top_level" % self.das_name),
        ]

        urlpatterns = self.override_urls() + patterns('', *pattern_list)

        for name in sorted(self._registry.keys()):
            self._registry[name].das_name = self.das_name
            pattern_list.append((r"^(?P<api_name>%s$" % (self.das_name, 
                                                         trailing_slash(),
                                                         )

        urlpatterns = self.override_urls() + patterns('', 
                                 *pattern_list
                                )

        return(urlpatterns)

    def auto_generate_sources(self):
        pass



