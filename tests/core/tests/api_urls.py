from django.conf.urls.defaults import *
from core.tests.api import (DAS, BedResource, QTLResource, 
        FileBedResource, FileBamResource, FileBamJsonResource)

api = DAS()
api.register(BedResource())
api.register(QTLResource())
api.register(FileBedResource())
api.register(FileBamResource())
api.register(FileBamJsonResource())

urlpatterns = patterns('',
    (r'^api/', include(api.urls)),
                      )
